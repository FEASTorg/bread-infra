#!/usr/bin/env python3
"""
Inject FEAST theme assets (_sass and _includes) into a local Jekyll site
when `color_scheme: feast` is specified in docs/_config.yml.

Robust against transient CI failures (e.g., GitHub clone flakiness), and includes
retry logic, folder verification, and clear logging for debugging.
"""

import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml

CONFIG_PATH = Path("docs/_config.yml")
TEMP_CLONE_DIR = Path("_feast_temp")
REMOTE_REPO_URL = "https://github.com/FEASTorg/FEASTorg.github.io.git"
WANTED_COLOR_SCHEME = "feast"
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5  # seconds


def log_banner():
    """Print a banner to indicate the start of the script."""
    print("=" * 50)
    print("🚀 Starting FEAST theme asset injection")
    print("=" * 50)


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


def clone_theme_repo(retries: int = RETRY_ATTEMPTS, delay: int = RETRY_DELAY) -> bool:
    """
    Clone the remote theme repository to a temporary directory with retries.
    Returns True if successful.
    """
    print(f"🔄 Cloning theme repo to {TEMP_CLONE_DIR}...")
    for attempt in range(1, retries + 1):
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", REMOTE_REPO_URL, str(TEMP_CLONE_DIR)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            print(f"✅ Clone successful on attempt {attempt}")
            return True
        except subprocess.CalledProcessError as e:
            print(
                f"❌ Clone attempt {attempt} failed.\n{e.output.decode(errors='ignore')}"
            )
            if attempt < retries:
                print(f"⏳ Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("⛔ All attempts to clone the theme repo failed.")
    return False


def copy_theme_assets() -> None:
    """Copy the _sass and _includes folders from the cloned repo to the local docs/ directory."""
    for folder in ["_sass", "_includes"]:
        src = TEMP_CLONE_DIR / folder
        dst = Path("docs") / folder
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)


def verify_assets() -> bool:
    """Verify that the _sass and _includes folders exist and are non-empty."""
    success = True
    for folder in ["_sass", "_includes"]:
        path = Path("docs") / folder
        if not path.exists() or not any(path.iterdir()):
            print(f"🚨 Missing or empty: docs/{folder}/ — injection likely failed.")
            success = False
        else:
            print(f"✅ Verified: docs/{folder}/ has {len(list(path.iterdir()))} items.")
    return success


def safe_rmtree(path: Path) -> bool:
    """Safely remove a directory, returning True if successful."""
    try:
        shutil.rmtree(path)
        return True
    except (PermissionError, OSError) as e:
        print(f"⚠ Could not delete '{path}': {e}")
        return False


def main() -> None:
    """Main script logic for injecting FEAST theme assets."""
    log_banner()

    if not CONFIG_PATH.exists():
        print(f"⛔ Missing: {CONFIG_PATH} — cannot determine color_scheme.")
        sys.exit(1)

    color_scheme = load_color_scheme(CONFIG_PATH)
    if color_scheme != WANTED_COLOR_SCHEME:
        msg = f"color_scheme is '{color_scheme}'"
        print(f"⏭ {msg}, skipping injection.")
        return

    print(
        f"🎨 Detected color_scheme: '{WANTED_COLOR_SCHEME}' — proceeding with injection."
    )

    if TEMP_CLONE_DIR.exists():
        if not safe_rmtree(TEMP_CLONE_DIR):
            print(
                f"⛔ Failed to clean temp dir '{TEMP_CLONE_DIR}'. Aborting to avoid conflicts."
            )
            sys.exit(1)

    if not clone_theme_repo():
        sys.exit(1)

    copy_theme_assets()
    safe_rmtree(TEMP_CLONE_DIR)

    if not verify_assets():
        print("❌ Asset verification failed. Please inspect logs.")
        sys.exit(1)

    print("✅ Theme assets injected and verified successfully.")


if __name__ == "__main__":
    main()
