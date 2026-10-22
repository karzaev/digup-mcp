# digup-mcp

A standalone MCP adapter for an **installed DigUp search engine and its existing index**, on macOS and Linux.
It lets Codex and other MCP clients search local files without opening DigUp's search window.

Русское руководство пользователя: [как пользоваться DigUp MCP в Codex](docs/usage.ru.md).

The adapter uses the official Python MCP SDK. It calls DigUp's existing `search-service` process protocol;
it does not implement another indexer, query the SQLite schema, bundle a model, or require a custom DigUp fork.

```text
Codex ── MCP ── digup-mcp ── DigUp search-service ── DigUp engine/model/index
```

## Prerequisites and compatibility

- macOS or Linux, Python 3.12 or newer, and [uv](https://docs.astral.sh/uv/) for the installation commands below.
- DigUp installed with its model downloaded and files indexed.
- Its CLI must provide `search-service`, with the JSON `ready` handshake and `search`, `text`, `status`, and `reload`
  operations. The adapter checks the handshake when its first tool runs; incompatible builds report an error.

The protocol was inspected in upstream `ARahim3/DigUp` revision `7db9537`, whose Mac bundle metadata is version
`0.6.1` (build 12). This is **source compatibility evidence**, not a claim that every released `0.6.1` package or
an App Store build has been tested. Verification results for this adapter are recorded in `CHANGELOG.md`.

On macOS the stock source build packages the full CLI inside `DigUp.app/Contents/Helpers/digup`.
On Linux distributions may bundle it in the application's resource `helper/` directory.
**Keep the Linux helper beside its native libraries**; copying the executable alone can break its library paths.
An original DigUp build or any compatible fork can be used. The adapter need not be rebuilt with the desktop app.

## Install

From a checkout, install the locked development environment:

```sh
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
```

Build a wheel, then install that wheel into an isolated tool environment. The installed command does not depend on
the checkout remaining in place:

```sh
uv build
uv tool install --constraints constraints.txt dist/digup_mcp-0.1.0-py3-none-any.whl
digup-mcp --help
```

`uv.lock` pins the development environment and transitive dependencies; the package also pins MCP SDK `1.30.0`.
`constraints.txt` exports the same resolved versions for wheel/tool installation on both platforms. Ship it beside
the wheel and use it during installation. Regenerate it after changing the lock with
`uv export --frozen --no-dev --no-emit-project --no-hashes --format requirements.txt --output-file constraints.txt`.

## Configure DigUp paths

Explicit command-line arguments override environment variables and defaults:

| Option | Environment | Default |
|---|---|---|
| `--binary` | `DIGUP_BINARY` | Mac app helper; Linux standalone/package helper; then `digup` on PATH |
| `--index` | `DIGUP_INDEX` | Mac: `~/Library/Application Support/DigUp/index.noindex`; Linux: `$XDG_DATA_HOME/digup/index` |
| `--models` | `DIGUP_MODELS` | Mac: `~/Library/Application Support/DigUp/Models`; Linux: `$XDG_DATA_HOME/digup/Models` |
| `--timeout` | — | 120 seconds per engine request |

Without `XDG_DATA_HOME`, Linux uses `~/.local/share`. On Mac discovery checks `/Applications` and `~/Applications`.
On Linux it checks `/opt/digup/bin/digup`, `/usr/lib/DigUp/helper/digup`, `/usr/local/lib/DigUp/helper/digup`, and
the `lib/DigUp/helper/` directory beside the installation prefix of a discovered `digup-shell`.
If another program named `digup` is on PATH, point `--binary` at DigUp's actual helper.

Example with an explicit Linux package helper:

```sh
digup-mcp --binary /path/to/installed/DigUp/helper/digup
```

No index is created when the configured `index.sqlite` is missing. DigUp remains responsible for indexing; the
adapter does not invoke `index`, `index-service` or model-download commands. DigUp's search service itself may
maintain its normal logs, caches and database schema, exactly as when used by the application.

## Connect Codex

Use the installed command, not a path to Python or a development checkout:

```sh
codex mcp add digup -- digup-mcp
```

If the desktop client's PATH does not include the installed tool directory, use the absolute path printed by
`command -v digup-mcp` instead. If discovery needs an explicit DigUp executable:

```sh
codex mcp add digup -- digup-mcp --binary /path/to/installed/digup
```

After adding the server, reload MCP connections or start a new Codex chat. Check it with `codex mcp get digup`.
On a VPS run the same adapter with the locally installed Linux CLI and its local index. A network MCP endpoint or
remote access to another machine's files is not provided by this package.

## Tools

- **`search(query, limit=10, code=false, kinds=null, meaning=true)`** searches the entire existing main index, or
  the separate code index with `code=true`. It returns the engine's paths, excerpts, segment IDs, scores and
  page/time/line coordinates. `meaning` in the reply indicates whether semantic matching actually ran. A warning
  identifies keyword-only fallback when semantic matching was requested. `kinds` accepts `doc`, `pdf`, `image`,
  `screenshot`, `audio`, and `video` for the main index.
- **`get_passage(segment_id, code=false)`** asks DigUp for indexed text. Use a segment ID from search and the same
  `code` value. Images/audio may have no text, and indexed text can lag the source file.
- **`status()`** returns DigUp's existing index counts and encoder state. `vectors` and `code_vectors` are
  currently loaded-vector counts, so zero while idle does not prove that the disk index is empty.

Search requests ask DigUp to reload its view of the index before searching. The existing service controls the model's
lifetime. Adapter diagnostics and engine diagnostics go to stderr; stdout is reserved for the SDK's MCP transport.

## Obsidian and local data

The adapter can search only what DigUp indexed. A Git-backed Obsidian vault may be skipped by affected DigUp versions
because `.git` marks a code project. That is an indexer issue: fixing it and indexing the omitted notes is separate
from installing this adapter. A fork with that fix can be used without changing the adapter.

Index each computer's local copy of a Git-synchronized vault on that computer. Paths and indexes are local; this
package does not synchronize SQLite databases. Models, indexes, retrieved passages and user notes are never part of
the package or this repository. Retrieved passages returned to an MCP client enter that client's conversation context.

## Verified builds

On 2026-10-21 the compatible `karzaev/DigUp` fork (upstream base `7db9537`, app metadata `0.6.1`, build 12) was tested:

- macOS on Apple Silicon, Swift 6.4, Python 3.14: installed `/Applications/DigUp.app` helper, existing main/code
  indexes, semantic search and source passage retrieval. A real Git-backed Obsidian note was indexed and found via
  CLI, the installed MCP wheel, and Codex's MCP tool calls.
- Ubuntu 22.04.5/aarch64 in Docker, Swift 6.4.1, Python 3.12.15: three synthetic Git-backed vault notes without
  `.obsidian` were indexed by the shared CLI. The Linux MCP package searched that index with `meaning=true` and
  returned a source-matching passage. Codex on the Mac invoked that Linux MCP/engine through a local container
  transport; no Codex credentials or personal notes were copied into Linux.
- Eight adapter tests passed on each platform. The Linux paraphrase CLI check used `--zgate 0` because its tiny
  three-document corpus cannot reach the default semantic z-score gate; MCP used `V60 coffee` at normal defaults.

Original released DigUp packages have not been runtime-tested here. Compatibility with them is based on the inspected
upstream process protocol above. If a code index is first created after the MCP service starts, restart MCP to detect it.

## Development and release

`src/digup_mcp/` contains discovery, the process transport and SDK tool definitions. Tests use a fake process speaking
the real DigUp protocol and an official MCP SDK client. They do not index or read personal files.

Before claiming a real engine/platform combination is verified, test CLI indexing/search, MCP initialization,
semantic search and passage retrieval against that installed engine and record the actual build and platform.
Do not infer semantic success from a valid connection or a keyword-only response.

The MCP adapter is independently versioned. Release compatibility follows the engine's process protocol; desktop
updates need no adapter change while that protocol remains compatible. Upstream protocol changes require an adapter
test/update rather than a rewrite of DigUp's search logic.
