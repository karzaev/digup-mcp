import asyncio
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from digup_mcp.config import Config, configuration, data_directory, discover_binary
from digup_mcp.engine import Engine

FIXTURE = Path(__file__).with_name("fake_digup.py").resolve()


class ConfigTests(unittest.TestCase):
    def test_mac_and_linux_data_defaults(self):
        with patch("sys.platform", "darwin"), patch("pathlib.Path.home", return_value=Path("/home/test")):
            self.assertEqual(data_directory(), Path("/home/test/Library/Application Support/DigUp"))
        with patch("sys.platform", "linux"), patch.dict(os.environ, {"XDG_DATA_HOME": "/data"}):
            self.assertEqual(data_directory(), Path("/data/digup"))

    def test_explicit_configuration_wins_and_missing_index_is_not_created(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, "Existing index"):
                configuration(FIXTURE, root, root)
            self.assertEqual(list(root.iterdir()), [])
            (root / "index.sqlite").touch()
            with patch.dict(os.environ, {"DIGUP_BINARY": "/wrong", "DIGUP_INDEX": "/wrong", "DIGUP_MODELS": "/wrong"}):
                config = configuration(FIXTURE, root, root)
            self.assertEqual(config.binary, FIXTURE)
            self.assertEqual(config.models, root.resolve())
            with self.assertRaisesRegex(ValueError, "positive"):
                configuration(FIXTURE, root, root, timeout=0)

    def test_path_discovery_keeps_linux_helper_in_place(self):
        with patch("sys.platform", "linux"), patch("shutil.which", return_value=str(FIXTURE)):
            self.assertEqual(discover_binary(), FIXTURE)


class EngineTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        (self.root / "index.sqlite").touch()
        (self.root / "code.sqlite").touch()
        self.engine = Engine(Config(FIXTURE, self.root, self.root, 2))

    async def asyncTearDown(self):
        await self.engine.close()
        self.directory.cleanup()

    async def test_search_events_passage_and_concurrent_calls(self):
        found = await self.engine.request("search", q="a note", code=True, meaning=True)
        self.assertTrue(found["meaning"])
        self.assertEqual(found["hits"][0]["kind"], "code")
        passage = await self.engine.request("text", segment=42, code=True)
        self.assertEqual(passage["text"], "Original indexed passage")
        results = await asyncio.gather(*[self.engine.request("status") for _ in range(4)])
        self.assertTrue(all(result["files"] == 1 for result in results))

    async def test_document_search_selects_the_whole_existing_index(self):
        found = await self.engine.request("search", q="a note", meaning=True)
        self.assertEqual([hit["path"] for hit in found["hits"]], ["/fixture/vault/note.md"])

    async def test_errors_restart_the_engine(self):
        for query, expected in [("error", "fixture engine error"), ("exit", "exited"),
                                ("bad-id", "mismatched"), ("invalid-json", "invalid JSON")]:
            with self.subTest(query=query):
                with self.assertRaisesRegex(RuntimeError, expected):
                    await self.engine.request("search", q=query)
                self.assertIsNone(self.engine.process)
                self.assertEqual((await self.engine.request("status"))["files"], 1)

    async def test_timeout_stops_child_and_next_call_can_restart(self):
        self.engine.config = Config(FIXTURE, self.root, self.root, .5)
        with self.assertRaisesRegex(RuntimeError, "timed out"):
            await self.engine.request("search", q="timeout")
        self.assertIsNone(self.engine.process)
        self.assertEqual((await self.engine.request("status"))["files"], 1)

    async def test_incompatible_handshake_has_actionable_error(self):
        with patch.dict(os.environ, {"DIGUP_TEST_BAD_READY": "1"}):
            with self.assertRaisesRegex(RuntimeError, "compatible"):
                await self.engine.request("status")


class MCPClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_sdk_initialization_discovery_search_passage_and_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "index.sqlite").touch()
            params = StdioServerParameters(command=sys.executable, args=["-m", "digup_mcp.server", "--binary", str(FIXTURE),
                                           "--index", directory, "--models", directory])
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    initialized = await session.initialize()
                    self.assertEqual(initialized.serverInfo.name, "digup-mcp")
                    tools = await session.list_tools()
                    self.assertEqual({tool.name for tool in tools.tools}, {"search", "get_passage", "status"})
                    result = await session.call_tool("search", dict(query="a note", limit=3))
                    self.assertFalse(result.isError)
                    data = result.structuredContent
                    self.assertTrue(data["meaning"])
                    self.assertEqual(data["hits"][0]["segment_id"], 42)
                    passage = await session.call_tool("get_passage", dict(segment_id=42))
                    self.assertEqual(passage.structuredContent["text"], "Original indexed passage")
                    fallback = await session.call_tool("search", dict(query="keyword-only"))
                    self.assertFalse(fallback.structuredContent["meaning"])
                    self.assertIn("keyword-only", fallback.structuredContent["warning"])
                    self.assertFalse((await session.call_tool("status")).isError)
                    for bad_args in [dict(query=" "), dict(query="x", limit=0), dict(query="x", code=True, kinds=["doc"])]:
                        self.assertTrue((await session.call_tool("search", bad_args)).isError)
                    self.assertTrue((await session.call_tool("get_passage", dict(segment_id=0))).isError)


if __name__ == "__main__":
    unittest.main()
