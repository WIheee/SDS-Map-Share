#!/usr/bin/env python3
"""
Directory tree and file content exporter.
Generates a tree.txt file with directory structure and optionally file contents.
"""

import fnmatch
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Optional, Set, Tuple

MAX_FILE_SIZE = 1024 * 1024  # 1 MB
OUTPUT_FILE = "tree.txt"

DEFAULT_SKIP_PATTERNS = [
    "LICENSE"
    "README.md",
    ".git/",
    "node_modules/",
    "pack_icon.png",
    "*.pyc",
    "*.log",
    "*.svg",
    "*.png",
    "pnpm-lock.yaml",
    "package-lock.json",
    "tree.txt",
    "t",
    "a",
    "tools/"
]

# Load additional custom skip patterns from .skip_patterns if present
SKIP_PATTERNS_FILE = ".skip_patterns"
if Path(SKIP_PATTERNS_FILE).exists():
    with open(SKIP_PATTERNS_FILE, "r", encoding="utf-8") as f:
        extra_patterns = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]
    DEFAULT_SKIP_PATTERNS.extend(extra_patterns)


def should_skip(path: str) -> bool:
    """Check if a path should be skipped based on patterns."""
    path_obj = Path(path)
    parts = path_obj.parts
    name = path_obj.name

    for pattern in DEFAULT_SKIP_PATTERNS:
        pattern = pattern.strip()
        if not pattern:
            continue

        # Directory pattern (ends with '/')
        if pattern.endswith("/"):
            dir_name = pattern[:-1]
            if dir_name in parts:
                return True
        # File or name pattern
        else:
            if fnmatch.fnmatch(name, pattern):
                return True
    return False


def build_tree(
    directory: Path,
    prefix: str = "",
    include_hidden: bool = False,
    visited: Optional[Set[Path]] = None
) -> List[str]:
    """Recursively build a visual tree representation of the directory."""
    if visited is None:
        visited = set()

    real_path = directory.resolve()
    if real_path in visited:
        return [f"{prefix}[symlink loop]"]

    visited.add(real_path)

    try:
        entries = list(os.scandir(real_path))
    except PermissionError:
        return [f"{prefix}[permission denied]"]

    # Filter hidden entries and skipped paths
    entries = [
        entry for entry in entries
        if (include_hidden or not entry.name.startswith("."))
        and not should_skip(entry.path)
    ]

    # Sort directories first, then files, alphabetically
    entries.sort(key=lambda e: (not e.is_dir(), e.name.lower()))

    lines = []
    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{entry.name}")

        if entry.is_dir():
            extension = "    " if is_last else "│   "
            lines.extend(
                build_tree(
                    Path(entry.path),
                    prefix + extension,
                    include_hidden,
                    visited
                )
            )

    return lines


def read_file_safely(path: Path) -> str:
    """Read file content with size and encoding checks."""
    try:
        size = path.stat().st_size
        if size > MAX_FILE_SIZE:
            return f"[file too large: {size} bytes]"
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "[encoding error]"
    except Exception as e:
        return f"[error: {e}]"


def collect_files(root: Path, include_hidden: bool) -> List[Path]:
    """Collect all files under root that should be processed."""
    root = root.resolve()
    files = []

    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        dirpath = Path(dirpath)

        # Skip the entire directory if it matches patterns
        if should_skip(dirpath):
            dirnames[:] = []
            continue

        # Filter hidden directories and files if needed
        if not include_hidden:
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            filenames = [f for f in filenames if not f.startswith(".")]

        for filename in filenames:
            file_path = dirpath / filename
            if not should_skip(file_path):
                files.append(file_path)

    return files


def get_user_input() -> Tuple[Path, bool, bool]:
    """Get directory path, hidden file option, and content inclusion option from user."""
    print("=== Directory Tree & Content Exporter ===")

    dir_input = input("Directory path (Enter for current): ").strip()
    directory = Path(dir_input) if dir_input else Path.cwd()
    if not directory.is_dir():
        sys.exit("Invalid directory path.")

    include_hidden = input("Include hidden files? (y/N): ").strip().lower() == "y"
    include_content = input("List file contents? (y/N): ").strip().lower() == "y"

    return directory, include_hidden, include_content


def main() -> None:
    directory, include_hidden, include_content = get_user_input()
    root = directory.resolve()

    # Build directory tree
    tree_lines = [root.name]
    tree_lines.extend(build_tree(root, include_hidden=include_hidden))

    contents: List[Tuple[str, str]] = []
    if include_content:
        print("Collecting files...")
        files = collect_files(root, include_hidden)
        print(f"Files to read: {len(files)}")

        if files:
            # Read files concurrently
            with ThreadPoolExecutor() as executor:
                file_contents = list(executor.map(read_file_safely, files))

            for file_path, content in zip(files, file_contents):
                relative_path = str(file_path.relative_to(root))
                contents.append((relative_path, content))

            print(f"Successfully read {len(contents)} files.")

    # Write output
    output_path = Path.cwd() / OUTPUT_FILE
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("Project Directory and File Contents (skipped items are hidden)\n")
        f.write("\n".join(tree_lines))

        if contents:
            f.write("\n")
            for rel_path, content in contents:
                f.write(f"{rel_path}{{\n{content.rstrip()}\n}}")

    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()