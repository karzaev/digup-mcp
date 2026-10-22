#!/usr/bin/env python3
"""A protocol fixture, not a search implementation or a real index."""

import json
import os
import sys
import time

assert sys.argv[1] == "search-service"
document_scope = sys.argv[2:3] == ["/"]
print(json.dumps({"event": "ready" if not os.environ.get("DIGUP_TEST_BAD_READY") else "unsupported"}), flush=True)
for line in sys.stdin:
    message = json.loads(line)
    op, ident = message["op"], message["id"]
    reply = {"id": ident, "ok": True}
    if op == "search":
        query = message["q"]
        if query == "timeout":
            time.sleep(5)
        if query == "exit":
            sys.exit(7)
        if query == "bad-id":
            ident += 1
        if query == "invalid-json":
            print("not json", flush=True)
            continue
        print(json.dumps({"event": "encoder", "state": "ready"}), flush=True)
        if query == "error":
            reply = dict(id=ident, ok=False, error="fixture engine error")
        else:
            code = message.get("code", False)
            reply = dict(id=ident, hits=[dict(path="/fixture/vault/note.md", segment_id=42,
                                             excerpt="Original indexed passage", kind="code" if code else "doc")]
                         if code or document_scope else [],
                         meaning=message.get("meaning", True) and query != "keyword-only", strong=1,
                         ms=dict(embed=1, search=2))
    elif op == "text":
        reply = dict(id=ident, text="Original indexed passage", code=message.get("code", False))
    elif op == "status":
        reply = dict(id=ident, files=1, searchable=1, vectors=0, encoder="stopped")
    elif op == "reload":
        reply = dict(id=ident, ok=True, vectors=1)
    else:
        reply = dict(id=ident, ok=False, error="unknown operation")
    print(json.dumps(reply), flush=True)
