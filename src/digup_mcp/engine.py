"""Translate requests to DigUp search-service without reading its database ourselves."""

import asyncio
import json
import os

from .config import Config


class Engine:
    def __init__(self, config: Config):
        self.config = config
        self.process = None
        self.lock = asyncio.Lock()
        self.sequence = 0

    async def _stop(self):
        process, self.process = self.process, None
        if process is None:
            return
        if process.returncode is None:
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), 3)
            except TimeoutError:
                process.kill()
                await process.wait()
        if process.stdin:
            process.stdin.close()

    async def close(self):
        async with self.lock:
            await self._stop()

    async def _line(self):
        line = await self.process.stdout.readline()
        if not line:
            raise RuntimeError("DigUp search-service exited. Check the installed executable and MCP stderr.")
        try:
            reply = json.loads(line)
        except (ValueError, UnicodeDecodeError) as error:
            raise RuntimeError("DigUp returned invalid JSON; this build may be incompatible") from error
        if not isinstance(reply, dict):
            raise RuntimeError("DigUp returned an unexpected protocol message")
        return reply

    async def _start(self):
        # DigUp 0.6.2 requires an explicit search scope; '/' selects the whole index without crawling.
        args = [str(self.config.binary), "search-service", "/", "--index", str(self.config.index)]
        if (self.config.index / "code.sqlite").is_file():
            # This scope selects all existing code hits; search-service never crawls it.
            args += ["--code-root", "/"]
        env = dict(os.environ, DIGUP_MODELS=str(self.config.models))
        env.pop("DIGUP_WORKER_DIR", None)
        self.process = await asyncio.create_subprocess_exec(
            *args, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
            env=env, limit=4 * 1024 * 1024)
        ready = await self._line()
        if ready.get("event") != "ready":
            raise RuntimeError("DigUp did not complete the search-service handshake; use a compatible build")

    async def request(self, operation: str, **fields) -> dict:
        async with self.lock:
            try:
                async with asyncio.timeout(self.config.timeout):
                    if self.process is None or self.process.returncode is not None:
                        await self._stop()
                        await self._start()
                    self.sequence += 1
                    message = dict(id=self.sequence, op=operation, **fields)
                    self.process.stdin.write((json.dumps(message) + "\n").encode())
                    await self.process.stdin.drain()
                    while True:
                        reply = await self._line()
                        # The encoder sends ready/idle/unavailable events between replies.
                        if "event" in reply and "id" not in reply:
                            continue
                        if reply.get("id") != self.sequence:
                            raise RuntimeError("DigUp returned a mismatched request ID")
                        if reply.get("ok") is False:
                            raise RuntimeError(reply.get("error", "DigUp request failed"))
                        reply.pop("id", None)
                        return reply
            except BaseException as error:
                await self._stop()
                if isinstance(error, TimeoutError):
                    raise RuntimeError("DigUp request timed out; the next request will restart the search service") from error
                raise
