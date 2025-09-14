#!/usr/bin/env python3
"""
Inject FEAST theme assets (_sass and _includes) into a local Jekyll site
when `color_scheme: feast` is specified in docs/_config.yml.

Intended for use in both local development and CI pipelines.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import yaml

CONFIG_PATH = Path("docs/_config.yml")
TEMP_CLONE_DIR = Path("_feast_temp")
REMOTE_REPO_URL = "https://github.com/FEASTorg/FEASTorg.github.io.git"
WANTED_COLOR_SCHEME = "feast"


def load_color_scheme(config_path: Path) -> str | None:
    """Return the color_scheme from a Jekyll config.yml file, or None if not found or invalid."""
    if not config_path.exists():
        return None
    try:
        with config_path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return str(config.get("color_scheme", "")).strip().lower()
    except (yaml.YAMLError, OSError):
        return None


def clone_theme_repo() -> bool:
    """Clone the remote theme repository to a temporary directory. Returns True if successful."""
    print(f"🔄 Cloning theme repo to {TEMP_CLONE_DIR}...")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", REMOTE_REPO_URL, str(TEMP_CLONE_DIR)],
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git clone failed: {e}")
        print(
            f"⚠ Could not clone to '{TEMP_CLONE_DIR}'. "
            "If you're running this locally, try deleting the directory manually."
        )
        return False


def copy_theme_assets() -> None:
    """Copy the _sass and _includes folders from the cloned repo to the local docs/ directory."""
    for folder in ["_sass", "_includes"]:
        src = TEMP_CLONE_DIR / folder
        dst = Path("docs") / folder
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)


def safe_rmtree(path: Path) -> bool:
    """Safely remove a directory, returning True if successful."""
    try:
        shutil.rmtree(path)
        return True
    except (PermissionError, OSError) as e:
        print(f"⚠ Could not delete '{path}': {e}")
        return False


def main() -> None:
    """Main logic for checking theme and injecting assets if needed."""
    color_scheme = load_color_scheme(CONFIG_PATH)

    if color_scheme != WANTED_COLOR_SCHEME:
        msg = (
            f"{CONFIG_PATH} not found"
            if color_scheme is None
            else f"color_scheme is '{color_scheme}'"
        )
        print(f"⏭ {msg}, skipping injection.")
        return

    print(
        f"🎨 Detected color_scheme: '{WANTED_COLOR_SCHEME}' — injecting theme assets..."
    )

    if TEMP_CLONE_DIR.exists():
        if not safe_rmtree(TEMP_CLONE_DIR):
            print(
                f"⚠ Directory '{TEMP_CLONE_DIR}' not fully removed. You may need to delete it manually."
            )
            print("⛔ Aborting to avoid clone conflict.")
            sys.exit(1)

    if not clone_theme_repo():
        sys.exit(1)

    copy_theme_assets()
    safe_rmtree(TEMP_CLONE_DIR)

    print("✅ Theme assets injected: _sass and _includes updated.")


if __name__ == "__main__":
    main()
