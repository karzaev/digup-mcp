---
name: digup
description: Search existing DigUp indexes for local documents, notes and source code, and retrieve matching passages through DigUp MCP. Use when the user selects DigUp or wants to search their indexed local files.
---

# DigUp

Use the connected DigUp MCP server for the user's search request. The server exposes
`search`, `get_passage` and `status`; their namespace depends on the client.
If those tools are unavailable, explain that the DigUp MCP connection is required.
Do not silently substitute a web search or a filesystem scan.

## Search and retrieve

- Pass the user's subject to `search(query=...)`. Search by meaning and words by default;
  use `meaning=false` when the user explicitly requests keyword-only search.
- Use the main index by default. Set `code=true` for source code; keep the same `code`
  value when retrieving its passages.
- For requested file types, use `kinds`: `doc`, `pdf`, `image`, `screenshot`, `audio`,
  or `video`. Do not combine `kinds` with `code=true`.
- Start with the default result limit. Refine the query or increase `limit` up to 50
  when the results do not answer the request.
- For relevant hits, call `get_passage` with the returned `segment_id` before quoting
  text or drawing conclusions beyond the search excerpt. Some media has no indexed text.

Show useful matches with their file paths and available page, time or line coordinates.
Distinguish source text from your summary. If a requested document is not found, report
that the search did not find it; this does not establish that the file is absent from disk.

## Scope and search state

Search covers the existing index, not every file on the computer. There is currently no
folder or vault parameter. If the user requests a particular folder, explain this limit;
you may select matching paths from the returned hits, but that selection can miss results
because the engine limits hits before it is filtered. Do not claim an exhaustive folder search.

Check the search reply's `meaning` and `warning`. If semantic search was requested but
the reply has `meaning=false`, state that only keyword search ran and give the reported
reason. Use `status` when diagnosing the connection or index, rather than before every search.
Zero loaded vectors or a stopped encoder during idle time alone do not prove index loss.

DigUp owns indexing and model installation. This skill only uses the existing search
tools; changing indexing rules or rebuilding the index is a separate task.
