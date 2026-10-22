# Changelog

## Unreleased — 2026-10-22

- Added a step-by-step Hermes Desktop walkthrough for each user's local macOS/Linux DigUp index: component
  installation links, local connection/profile selection, current Connectors form fields, a CLI alternative,
  MCP reload and verification against a known file and its indexed passage. Codex is not a prerequisite.
- Checked Hermes commands and UI labels against official documentation and public source. Checked Markdown links,
  heading anchors, shell-example syntax and whitespace. This is documentation-only; Hermes was not installed or
  connected for a runtime test, and local indexes, models and client settings were not changed.
- Added the portable `skills/digup/SKILL.md` workflow and Codex UI metadata. It uses the existing MCP search,
  passage and status tools, preserves main/code index selection, and explains the current folder-scope limitation.
- Added Codex and Claude Code skill installation/invocation instructions to the README and Russian guide,
  including separate Claude STDIO registration. Installed an independent copy in the local Codex user skills folder;
  no MCP runtime or Codex configuration change was needed.
- Both the repository skill and installed copy pass the skill validator. The user confirmed `/digup` appears in
  the desktop Codex suggestions. A read-only skill smoke test returned semantic results (`meaning=true`) and
  retrieved indexed text; the exact requested document title was not found, so this does not certify index coverage.
  Independent review checked tool parameters, portable installation and invocation. Claude Code was documented,
  not installed or runtime-tested in this check.
- Reworked the README into a complete installation walkthrough: explains DigUp, the MCP adapter and Codex;
  links downloads; covers model/index preparation, uv/Python setup, ZIP installation, desktop/CLI connection,
  a first real search, headless Linux paths and common errors. Moved contributor/build commands to the end.
- Verified the public ZIP installation in a temporary Python 3.12 tool environment using the documented command;
  installed version 0.1.1 with 30 pinned packages. Help/version checks still passed after renaming the source folder.
  Temporary files were removed; the user's installed MCP and Codex settings were not changed.
- Checked document links, shell-example syntax and Markdown whitespace. Documentation-only change.

## 0.1.1 — 2026-10-22

- Prepared the independent repository for public MIT distribution. The existing `LICENSE` and package metadata
  already declare MIT. Added public-upstream installation links, a clone command and explicit compatibility guidance:
  a private fork is not required; App Store packaging is not claimed as verified.
- Fixed empty document results with original DigUp 0.6.2: start its search service with `/` as the explicit
  whole-index scope. This queries existing indexed paths without crawling or adding a folder filter.
- Added a regression reproducing the empty-root behavior. It failed before the fix; all nine adapter tests pass.
  Built and installed version 0.1.1 with the same locked dependency versions.
- Verified the installed adapter against the original public macOS DigUp 0.6.2 DMG (build 13): three synthetic
  documents indexed, SDK initialization/status passed, two semantic queries returned the correct files, and indexed
  passages matched their source texts. No custom DigUp build was used for this check.
- Added a Russian user guide covering everyday Codex requests, document/code search, passages, index scope,
  normal installed paths and troubleshooting. Linked it from the README.
- Verified the guide against current tool definitions and official Codex MCP documentation. Live tools in this
  Codex chat successfully returned status, semantic search (`meaning=true`) and a real Obsidian passage.
- Checked Markdown links and whitespace; Codex configuration is unchanged.

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
