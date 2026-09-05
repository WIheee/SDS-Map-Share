#!/usr/bin/env python3
"""
Image compression script: convert all images under public/map/image/ to WebP
and compress to below 60 KB. Images that are already WebP and smaller than 60 KB
are skipped.
Dependency: Pillow (pip install Pillow)
"""

import os
import sys
from PIL import Image

TARGET_SIZE = 60 * 1024  # 60 KB
QUALITY_START = 90
QUALITY_END = 5
QUALITY_STEP = 5

def compress_to_webp(input_path, output_path):
    """
    Attempt to compress the image at input_path into a WebP file no larger than
    TARGET_SIZE. Returns (success_flag, final_size).
    """
    try:
        img = Image.open(input_path)
        # Ensure the image mode is suitable for WebP saving
        if img.mode == 'RGBA':
            pass  # save as is
        elif img.mode == 'P':
            img = img.convert('RGBA' if img.info.get('transparency') is not None else 'RGB')
        elif img.mode not in ('RGB', 'RGBA', 'LA'):
            img = img.convert('RGB')

        # Try decreasing quality levels
        for quality in range(QUALITY_START, QUALITY_END - 1, -QUALITY_STEP):
            img.save(output_path, 'webp', quality=quality, lossless=False, method=6)
            size = os.path.getsize(output_path)
            if size <= TARGET_SIZE:
                return True, size

        # Last resort: lowest quality
        img.save(output_path, 'webp', quality=QUALITY_END, lossless=False, method=6)
        size = os.path.getsize(output_path)
        return size <= TARGET_SIZE, size

    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False, 0

def main():
    base_dir = 'public/map/image'
    if not os.path.isdir(base_dir):
        print(f"Error: directory {base_dir} does not exist. Run this script from the project root.")
        sys.exit(1)

    # Supported image extensions
    extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp')

    processed = 0
    skipped = 0
    failed = 0

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in extensions:
                continue

            input_path = os.path.join(root, file)
            # Skip if already WebP and below target size
            if ext == '.webp' and os.path.getsize(input_path) <= TARGET_SIZE:
                print(f"Skipping {input_path} (already WebP and below 60 KB)")
                skipped += 1
                continue

            # Build output path (change extension to .webp)
            base_name = os.path.splitext(file)[0]
            output_path = os.path.join(root, base_name + '.webp')
            temp_path = output_path + '.tmp'

            print(f"Processing {input_path} -> {output_path}")

            success, final_size = compress_to_webp(input_path, temp_path)

            if success:
                # Replace target file with temporary file
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(temp_path, output_path)
                # Delete original file if it is not the output file
                if input_path != output_path and os.path.exists(input_path):
                    os.remove(input_path)
                print(f"   Success, size {final_size/1024:.1f} KB")
                processed += 1
            else:
                # On failure, delete temporary file and keep original
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                print(f"   Compression failed (still larger than 60 KB), keeping original file")
                failed += 1

    print("\n" + "=" * 50)
    print(f"Statistics: {processed} compressed, {skipped} skipped, {failed} failed")
    print("Done.")

if __name__ == '__main__':
    main()