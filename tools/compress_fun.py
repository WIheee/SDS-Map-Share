#!/usr/bin/env python3
"""
Compress all .fun files under public/map/fun/ into individual .7z archives.

Uses the system 7z command. Archives are named <filename>.7z and contain
only the original .fun file (no directory structure). By default, original
.fun files are DELETED after successful compression. Use --keep-original
to retain them.

Requirements:
  - 7z command available (install via: apt install p7zip-full, brew install p7zip, pkg install p7zip)
"""

import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path

# 7z compression arguments: ultra compression, multi-threading, solid archive
COMPRESS_ARGS = [
    'a',                # add files
    '-t7z',             # 7z format
    '-mx=9',            # ultra compression
    '-mfb=273',         # fast bytes (dictionary size)
    '-ms=on',           # solid mode
    '-mmt=on',          # multi-threading
    '-m0=LZMA2',        # compression method
    '-y',               # assume Yes on all queries
]

def check_7z() -> bool:
    """Verify 7z is available. If running on Termux, offer to install."""
    if shutil.which('7z') is not None:
        return True

    logging.error("7z command not found.")
    # Try automatic installation on Termux
    if Path('/data/data/com.termux').exists():
        logging.info("Termux environment detected. Attempting to install p7zip...")
        try:
            subprocess.run(['pkg', 'install', 'p7zip', '-y'], check=True)
            logging.info("p7zip installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Automatic installation failed: {e}")
    else:
        logging.error("Please install 7z manually (e.g., sudo apt install p7zip-full, brew install p7zip)")
    return False

def compress_file(input_file: Path, keep_original: bool = False, skip_existing: bool = True) -> bool:
    """Compress a single .fun file into a .7z archive in the same directory."""
    if not input_file.exists():
        logging.warning(f"Input file missing: {input_file}")
        return False

    output_file = input_file.with_suffix('.7z')

    if output_file.exists():
        if skip_existing:
            logging.info(f"Skipping {input_file.name}: {output_file.name} already exists")
            return True
        else:
            logging.info(f"Overwriting existing archive: {output_file.name}")
            output_file.unlink()

    # Run 7z from the file's directory to avoid storing path components
    cmd = ['7z'] + COMPRESS_ARGS + [str(output_file.resolve()), input_file.name]

    logging.debug(f"Running command: {' '.join(cmd)} in {input_file.parent}")
    try:
        result = subprocess.run(
            cmd,
            cwd=str(input_file.parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        if not output_file.exists():
            logging.error(f"Compression of {input_file.name} did not produce an archive")
            return False

        orig_size = input_file.stat().st_size
        comp_size = output_file.stat().st_size
        ratio = (1 - comp_size / orig_size) * 100 if orig_size > 0 else 0.0
        logging.info(
            f"Compressed {input_file.name} -> {output_file.name} "
            f"({orig_size // 1024}KB to {comp_size // 1024}KB, {ratio:.1f}% saved)"
        )

        if not keep_original:
            input_file.unlink()
            logging.debug(f"Deleted original file: {input_file.name}")

        return True

    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.strip() if e.stderr else str(e)
        logging.error(f"Compression failed for {input_file.name}: {err_msg}")
        # Clean up partial archive if it exists
        if output_file.exists():
            output_file.unlink()
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Compress .fun files under a directory into individual .7z archives."
    )
    parser.add_argument(
        '--directory', '-d',
        default='public/map/fun',
        help='Root directory to search for .fun files (default: public/map/fun)'
    )
    parser.add_argument(
        '--keep-original',
        action='store_true',
        help='Keep original .fun files after compression (default: delete them)'
    )
    parser.add_argument(
        '--no-skip-existing',
        action='store_true',
        help='Overwrite existing .7z archives instead of skipping them'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s: %(message)s'
    )

    base_dir = Path(args.directory)
    if not base_dir.is_dir():
        logging.error(f"Directory '{base_dir}' does not exist.")
        sys.exit(1)

    if not check_7z():
        logging.error("Cannot continue without 7z.")
        sys.exit(1)

    fun_files = sorted(base_dir.rglob('*.fun'))
    if not fun_files:
        logging.info("No .fun files found.")
        return

    logging.info(f"Found {len(fun_files)} .fun file(s). Starting compression...")

    success_count = 0
    for file_path in fun_files:
        if compress_file(
            file_path,
            keep_original=args.keep_original,
            skip_existing=not args.no_skip_existing
        ):
            success_count += 1

    logging.info(f"Completed: {success_count}/{len(fun_files)} files compressed successfully.")
    if args.keep_original:
        logging.info("Original .fun files were kept.")
    else:
        logging.info("Original .fun files were deleted after compression.")

if __name__ == '__main__':
    main()