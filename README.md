# digup-mcp

Search the files that [DigUp](https://github.com/ARahim3/DigUp) has indexed, directly from Codex.
For example: “Use DigUp to find my notes about knowledge management, then show the matching passages and file paths.”

Works on **macOS and Linux**, with the original public DigUp application or a compatible CLI installation.
A private fork is not required.

Русское руководство пользователя: [как пользоваться DigUp MCP в Codex](docs/usage.ru.md).

## What you need, and why

There are three separate parts:

| Part | What it does | Where to get it |
| --- | --- | --- |
| **DigUp** | Reads the folders you choose, downloads its search model and builds the local index. | [Original DigUp releases](https://github.com/ARahim3/DigUp/releases) |
| **digup-mcp** | Connects that existing index to an AI client. This repository contains this adapter. | [Download this repository](https://github.com/karzaev/digup-mcp/archive/refs/heads/main.zip) |
| **Codex** | The application where you ask questions and use the search results. | Use your existing Codex client, or follow the [official Codex CLI setup](https://learn.chatgpt.com/docs/codex/cli). |

The adapter is written in Python. The instructions below use **uv** to install Python and keep the adapter's
dependencies in a separate environment; you do not need a separate Python installer or a manual MCP SDK installation.

```text
Codex ── MCP ── digup-mcp ── DigUp search-service ── DigUp engine/model/index
```

**Installing this adapter alone does not index your files.** First set up DigUp, then install the adapter and connect
it to Codex. If DigUp already searches your files, skip to [step 2](#2-install-uv-and-python).

## Install

### 1. Install DigUp and prepare its index

**On a Mac:** open [DigUp's releases](https://github.com/ARahim3/DigUp/releases), download the Mac `.dmg`, open it,
and drag **DigUp.app** into **Applications**. The current upstream Mac application requires Apple Silicon and
macOS 14 or later. Original DigUp **0.6.2** has been tested with this adapter.

**On a Linux desktop:** download the appropriate Linux package from
[DigUp's releases](https://github.com/ARahim3/DigUp/releases) and follow its
[Linux installation instructions](https://github.com/ARahim3/DigUp#install). For a Debian/Ubuntu package, use the
downloaded `.deb`; keep the packaged helper and its libraries together. Do not install Debian's unrelated program
named `digup`. For a VPS without a desktop, see [the headless setup below](#linux-without-a-graphical-session).

Then, in DigUp:

1. Open the application.
2. Select the folders you want to search, such as Documents or your Obsidian vault.
3. Let DigUp download its model and index those folders. Its initial model download is about 865 MB; indexing time
   depends on the amount and type of content.
4. Search for a file you know is in a selected folder. Confirm that DigUp finds it before continuing.

This prepares the data MCP will search. You can keep using your existing DigUp installation and index;
there is no need to build a custom desktop app or create a second index for MCP.

### 2. Install uv and Python

Open **Terminal** on macOS, or a terminal on Linux. Run the
[official uv installer](https://docs.astral.sh/uv/getting-started/installation/):

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Close and reopen the terminal so it picks up the installed command. Then run:

```sh
uv --version
uv python install 3.12
```

The first command should print a uv version. The second installs the Python runtime that will run this adapter;
it does not replace your system Python. See [uv's Python guide](https://docs.astral.sh/uv/guides/install-python/).
If uv is already installed, you can skip its installer.

### 3. Download and install digup-mcp

Download [digup-mcp as a ZIP](https://github.com/karzaev/digup-mcp/archive/refs/heads/main.zip) and extract it.
Open a terminal in the extracted **digup-mcp-main** folder. For example, if you extracted it in Downloads:

```sh
cd "$HOME/Downloads/digup-mcp-main"
```

Use your actual extraction location if it is different. If you already use Git, you can instead run
`git clone https://github.com/karzaev/digup-mcp.git` and `cd digup-mcp`.

From the folder containing **pyproject.toml** and **constraints.txt**, run:

```sh
uv tool install --python 3.12 --constraints constraints.txt .
```

The final `.` means “install the package from this folder.” uv builds the adapter and installs its dependencies
in an isolated tool environment. `constraints.txt` keeps those dependencies at the project's recorded versions.
The installed program works independently of the extracted source folder.

If uv reports that its command directory is missing from your PATH, run `uv tool update-shell` and reopen the
terminal. Then check:

```sh
digup-mcp --help
```

You should see the adapter's options. This confirms installation; the real search check is in
[step 5](#try-your-first-search). Do not leave a bare `digup-mcp` running in a terminal: it waits for an MCP client
to send requests and does not open a search window.

## Connect Codex

This is **step 4**. Choose the desktop settings or CLI option below; you only need one.
Codex will start the adapter automatically when it needs it.

### Through the desktop application

First, print the full path to the installed adapter:

```sh
printf '%s/digup-mcp\n' "$(uv tool dir --bin)"
```

Copy the result, for example `/Users/yourname/.local/bin/digup-mcp` on a Mac or
`/home/yourname/.local/bin/digup-mcp` on Linux. Then open **Settings → MCP servers → Add server** and enter:

| Field | Value |
| --- | --- |
| Name | `digup` |
| Transport | `STDIO` — a program running on your computer |
| Command | The full path you just copied |
| Arguments | Leave empty for the standard DigUp installation. |

Save, restart the MCP connection and start a new chat. The local adapter does not need a server URL or API key.
For the client-specific controls, see the [official Codex MCP documentation](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

### Through the Codex CLI

If you already use `codex` in a terminal, register the installed adapter with:

```sh
codex mcp add digup -- "$(uv tool dir --bin)/digup-mcp"
codex mcp get digup
```

The second command should show an enabled `digup` server and the installed command path.
It checks registration, not whether a document can be found. Start a new Codex session for the next step.

If `codex` is not installed, either use the desktop settings above or install the CLI using the
[official setup instructions](https://learn.chatgpt.com/docs/codex/cli). That setup also explains signing in.
This MCP connection is local to the computer running Codex; configuring it does not expose another machine's files.

## Try your first search

This is **step 5**. In a new Codex chat, ask:

> Use DigUp to find a document called “Project plan”. Show its path and retrieve the matching passage.

Replace “Project plan” with the name or distinctive words from a file you found in DigUp in step 1.
Successful verification means Codex used the DigUp `search` tool, returned the expected file, then retrieved its
text with `get_passage`. Ask whether semantic search actually ran: `meaning: true` in the search reply confirms it;
`meaning: false` with a warning means the response used words only.

After that, use ordinary requests such as “Find my notes about…”, “Search only PDF documents”, or
“Find the code that retries a failed request”. The [Russian user guide](docs/usage.ru.md) has more examples.

You can close the DigUp window for searches against the existing index. Keep its indexing process running when you
want new and changed files to be picked up automatically. Docker is not required for this setup.

## Linux without a graphical session

**This section starts with a working DigUp CLI and its native libraries already installed on the VPS.**
This adapter does not supply that engine. A public Linux package may provide its helper at
`/usr/lib/DigUp/helper/digup`; the helper can run without opening the graphical shell.

For a public source build, follow the upstream project's
[native dependency instructions](https://github.com/ARahim3/DigUp#build-from-source), then build only the CLI with
`swift build -c release --product digup`. That is a build command, not a complete installation: keep the required
native libraries with the executable. Copying a developer-build executable alone can break library discovery.

After you have a working CLI, prepare its model and index. In the example below, replace `/absolute/path/to/digup`
with your real executable and `/absolute/path/to/notes` with the folder you want to index:

```sh
digup_cli=/absolute/path/to/digup
digup_data="${XDG_DATA_HOME:-$HOME/.local/share}/digup"
"$digup_cli" download-model --to "$digup_data/Models"
DIGUP_MODELS="$digup_data/Models" "$digup_cli" index /absolute/path/to/notes --index "$digup_data/index"
DIGUP_MODELS="$digup_data/Models" "$digup_cli" search "words from a known note" --index "$digup_data/index" --json
```

Install this adapter with steps 2–3, then use this connection command instead of the default one in step 4:

```sh
codex mcp add digup -- "$(uv tool dir --bin)/digup-mcp" \
  --binary "$digup_cli" --index "$digup_data/index" --models "$digup_data/Models"
```

Run it in the same terminal where you set `digup_cli` and `digup_data`, or substitute their full paths.
Codex, MCP and the index all run on that Linux machine. No graphical session is needed; this package does not
provide a network MCP endpoint to a different machine's index.

## Configure DigUp paths

For a standard Mac installation, the adapter finds `/Applications/DigUp.app/Contents/Helpers/digup` automatically
(also checked under `~/Applications`). It uses the existing Application Support index and model directories.
For a custom location, pass these options as server arguments in the desktop settings or after the command in
`codex mcp add`:

| Option | Environment alternative | Default |
| --- | --- | --- |
| `--binary` | `DIGUP_BINARY` | Installed Mac app helper; Linux package helper; then `digup` on PATH |
| `--index` | `DIGUP_INDEX` | Mac: `~/Library/Application Support/DigUp/index.noindex`; Linux: `$XDG_DATA_HOME/digup/index` |
| `--models` | `DIGUP_MODELS` | Mac: `~/Library/Application Support/DigUp/Models`; Linux: `$XDG_DATA_HOME/digup/Models` |
| `--timeout` | — | 120 seconds per engine request |

Options take precedence over environment variables. Without `XDG_DATA_HOME`, Linux uses `~/.local/share`.
Linux discovery also checks `/opt/digup/bin/digup`, `/usr/lib/DigUp/helper/digup`, `/usr/local/lib/DigUp/helper/digup`
and a helper beside a discovered `digup-shell` installation. If another program called `digup` is on PATH,
set `--binary` explicitly. Different package layouts may need explicit index/model paths as well.

## Troubleshooting

| What you see | What to check |
| --- | --- |
| `uv: command not found` | Reopen the terminal after running the uv installer; check its final PATH instructions. |
| `digup-mcp: command not found` | Run `uv tool update-shell`, reopen the terminal, or use the full path printed in step 4. |
| uv says the tool is already installed | For an intentional update, download the new source and repeat the install command with `--force`, then restart the MCP connection. |
| `DigUp CLI not found` | Check the app/helper installation. For a custom layout, set `--binary`. Keep Linux libraries with the helper. |
| `Existing index.sqlite not found` | Complete indexing in DigUp, or set `--index` to its actual index directory. MCP does not build a new index. |
| Codex cannot see the tools | Check the `digup` server in MCP settings, restart its connection and start a new chat. |
| A known file is missing | First search for it in DigUp itself; check selected folders and indexing progress. |
| `meaning: false` with a warning | Read the warning; the model could not provide semantic search. Check the existing DigUp model installation. |
| `vectors: 0` / `encoder: stopped` | These can describe an idle model; try a search before concluding that the disk index is empty. |

## Compatibility and implementation

The engine must provide `search-service` with the JSON `ready` handshake and `search`, `text`, `status` and `reload`
operations. The adapter checks the handshake on its first tool call. It uses the official Python MCP SDK and
the existing DigUp service; it does not implement another indexer, read SQLite directly or download its own model.
DigUp's service may maintain its normal logs, caches and database schema, as when used by the application.

Original macOS DigUp 0.6.2 is runtime-tested below. Compatible public source builds and forks can use the same
adapter without rebuilding it with the desktop app. An App Store edition would need to expose the compatible
helper and accessible data paths; such packaging has not been tested here and its availability is not assumed.

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

On 2026-10-22, MCP **0.1.1** was tested with the original public
[DigUp 0.6.2 macOS release](https://github.com/ARahim3/DigUp/releases/tag/v0.6.2), build 13:
its bundled helper indexed three synthetic notes in a fresh index, then the installed MCP passed SDK initialization,
tool discovery, status, two semantic searches at normal defaults, and source-matching passage retrieval.
No custom DigUp build or private fork was used in that check. Nine adapter tests passed, including the regression
for the explicit whole-index scope required by DigUp 0.6.2.

On 2026-10-21 a compatible development build (upstream base `7db9537`, app metadata `0.6.1`, build 12) was tested:

- macOS on Apple Silicon, Swift 6.4, Python 3.14: installed `/Applications/DigUp.app` helper, existing main/code
  indexes, semantic search and source passage retrieval. A real Git-backed Obsidian note was indexed and found via
  CLI, the installed MCP wheel, and Codex's MCP tool calls.
- Ubuntu 22.04.5/aarch64 in Docker, Swift 6.4.1, Python 3.12.15: three synthetic Git-backed vault notes without
  `.obsidian` were indexed by the shared CLI. The Linux MCP package searched that index with `meaning=true` and
  returned a source-matching passage. Codex on the Mac invoked that Linux MCP/engine through a local container
  transport; no Codex credentials or personal notes were copied into Linux.
- Eight adapter tests passed on each platform. The Linux paraphrase CLI check used `--zgate 0` because its tiny
  three-document corpus cannot reach the default semantic z-score gate; MCP used `V60 coffee` at normal defaults.

App Store editions and original Linux release packages have not been runtime-tested here. If a code index is first
created after the MCP service starts, restart MCP to detect it.

## Development and release

`src/digup_mcp/` contains discovery, the process transport and SDK tool definitions. Tests use a fake process speaking
the real DigUp protocol and an official MCP SDK client. They do not index or read personal files.

For development, from a checkout:

```sh
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
uv build
```

This creates a development environment, runs the tests and builds the wheel/source archive in `dist/`.
These steps are not required for the normal installation above. To distribute an already-built wheel:

```sh
uv tool install --python 3.12 --constraints constraints.txt dist/digup_mcp-0.1.1-py3-none-any.whl
```

`uv.lock` records the development environment; `constraints.txt` exports its runtime dependency versions for tool
installation. The package also pins MCP SDK `1.30.0`. After changing the lock, regenerate the constraints with:

```sh
uv export --frozen --no-dev --no-emit-project --no-hashes --format requirements.txt --output-file constraints.txt
```

Before claiming a real engine/platform combination is verified, test CLI indexing/search, MCP initialization,
semantic search and passage retrieval against that installed engine and record the actual build and platform.
Do not infer semantic success from a valid connection or a keyword-only response.

The MCP adapter is independently versioned. Release compatibility follows the engine's process protocol; desktop
updates need no adapter change while that protocol remains compatible. Upstream protocol changes require an adapter
test/update rather than a rewrite of DigUp's search logic.

## License

[MIT](LICENSE), the same license used by the upstream DigUp project. DigUp itself is installed separately.
