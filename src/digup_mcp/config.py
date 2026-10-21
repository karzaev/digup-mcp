"""Installed engine discovery and explicit configuration; no checkout-specific paths."""

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import sys


@dataclass(frozen=True)
class Config:
    binary: Path
    index: Path
    models: Path
    timeout: float = 120


def data_directory() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support/DigUp"
    if sys.platform.startswith("linux"):
        return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "digup"
    raise ValueError("digup-mcp supports macOS and Linux")


def discover_binary() -> Path:
    candidates = []
    if sys.platform == "darwin":
        candidates += [Path("/Applications/DigUp.app/Contents/Helpers/digup"),
                       Path.home() / "Applications/DigUp.app/Contents/Helpers/digup"]
    candidates += [Path("/opt/digup/bin/digup")]
    if sys.platform.startswith("linux"):
        candidates += [Path("/usr/lib/DigUp/helper/digup"), Path("/usr/local/lib/DigUp/helper/digup")]
        shell = shutil.which("digup-shell")
        if shell:
            candidates.append(Path(shell).resolve().parent.parent / "lib/DigUp/helper/digup")
    found = shutil.which("digup")
    if found:
        candidates.append(Path(found))
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate.resolve()
    raise ValueError("DigUp CLI not found. Set --binary or DIGUP_BINARY to the installed helper. "
                     "On Linux keep the executable beside its packaged libraries.")


def configuration(binary=None, index=None, models=None, timeout=120) -> Config:
    base = data_directory()
    executable = binary or os.environ.get("DIGUP_BINARY")
    executable = Path(executable).expanduser().resolve() if executable else discover_binary()
    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise ValueError(f"DigUp executable is missing or not executable: {executable}")
    folder = Path(index or os.environ.get("DIGUP_INDEX") or base / (
        "index.noindex" if sys.platform == "darwin" else "index")).expanduser().resolve()
    if not (folder / "index.sqlite").is_file():
        raise ValueError(f"Existing index.sqlite not found in {folder}; index your files with DigUp first")
    model_folder = Path(models or os.environ.get("DIGUP_MODELS") or base / "Models").expanduser().resolve()
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    return Config(executable, folder, model_folder, timeout)
