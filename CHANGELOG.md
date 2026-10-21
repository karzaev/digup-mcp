# Changelog

## 0.1.0 — 2026-10-21

- Added a standalone macOS/Linux MCP adapter using the official Python MCP SDK and DigUp's existing process API.
- Added whole-index document/code search, indexed passage retrieval and engine status.
- Added installed-engine discovery, explicit portable configuration and isolated-package installation instructions.
- Added process protocol and SDK client tests, with MCP SDK `1.30.0` and transitive dependency resolution recorded in
  `uv.lock` and exported wheel-install constraints. A wheel and source distribution built successfully; the wheel is
  installed in an isolated environment outside the source checkout.
- Eight tests passed on both macOS/Python 3.14 and Ubuntu 22.04.5 ARM64/Python 3.12.15. Verified the compatible fork's
  real engine on both: CLI indexing/search, SDK stdio initialization, semantic MCP search and source passage retrieval.
- Codex MCP calls succeeded against the installed Mac engine and the Linux MCP/engine stack. The Mac check used a
  real Obsidian note; Linux used synthetic Git-backed vault notes. The Linux CLI paraphrase check lowered the z gate
  to zero for its three-document corpus; MCP used a literal query at normal defaults and reported `meaning=true`.
- Codex registration points to the installed `~/.local/bin/digup-mcp`, without source or `.dev` paths. Original
  released packages are not claimed as runtime-verified; upstream protocol/source compatibility is documented.
