#!/usr/bin/env python3
"""
Image compression script: convert all images under a target dir to WebP
and compress to below 60 KB. Images that are already WebP and smaller than
60 KB are skipped.
Dependency: Pillow (pip install Pillow)

Usage:
  python tools/compress_images.py                     # 默认 public/map/image
  python tools/compress_images.py --dir public/team   # 指定目录
  python tools/compress_images.py --max-dim 1920      # 长边上限
"""

import argparse
import os
import sys
import tempfile

from PIL import Image

TARGET_SIZE = 60 * 1024
QUALITY_START = 90
QUALITY_END = 5
QUALITY_STEP = 5
DEFAULT_MAX_DIM = 1920
DEFAULT_DIR = 'public/map/image'

EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp')


def compress_to_webp(input_path: str, output_path: str,
                     target_size: int = TARGET_SIZE,
                     max_dim: int = DEFAULT_MAX_DIM):
    """Compress input_path into a WebP at output_path <= target_size.

    返回 (success_flag, final_size)。
    """
    try:
        img = Image.open(input_path)

        if img.mode == 'P':
            img = img.convert('RGBA' if img.info.get('transparency') is not None else 'RGB')
        elif img.mode not in ('RGB', 'RGBA', 'LA'):
            img = img.convert('RGB')

        # 长边超限先等比缩小，避免超大图反复编码卡死
        if max_dim > 0 and max(img.size) > max_dim:
            ratio = max_dim / max(img.size)
            img = img.resize(
                (max(1, int(img.width * ratio)), max(1, int(img.height * ratio))),
                Image.Resampling.LANCZOS,
            )

        for quality in range(QUALITY_START, QUALITY_END - 1, -QUALITY_STEP):
            img.save(output_path, 'webp', quality=quality, lossless=False, method=6)
            size = os.path.getsize(output_path)
            if size <= target_size:
                return True, size

        # 最低质量兜底
        img.save(output_path, 'webp', quality=QUALITY_END, lossless=False, method=6)
        size = os.path.getsize(output_path)
        return size <= target_size, size

    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False, 0


def main():
    parser = argparse.ArgumentParser(description="压缩目录下图片为 ≤60KB 的 WebP。")
    parser.add_argument('--dir', '-d', default=DEFAULT_DIR,
                        help=f'目标目录（默认 {DEFAULT_DIR}）')
    parser.add_argument('--max-dim', type=int, default=DEFAULT_MAX_DIM,
                        help=f'长边像素上限（默认 {DEFAULT_MAX_DIM}，0 表示不限制）')
    parser.add_argument('--target-kb', type=int, default=TARGET_SIZE // 1024,
                        help='目标大小 KB（默认 60）')
    args = parser.parse_args()

    target_size = args.target_kb * 1024
    base_dir = args.dir

    if not os.path.isdir(base_dir):
        print(f"Error: directory {base_dir} does not exist.")
        sys.exit(1)

    processed = 0
    skipped = 0
    failed_files = []

    for root, _dirs, files in os.walk(base_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in EXTENSIONS:
                continue

            input_path = os.path.join(root, file)

            # 已是 WebP 且不超标 → 直接跳过
            if ext == '.webp' and os.path.getsize(input_path) <= target_size:
                print(f"Skipping {input_path} (already WebP and below {args.target_kb} KB)")
                skipped += 1
                continue

            base_name = os.path.splitext(file)[0]
            output_path = os.path.join(root, base_name + '.webp')

            # 用 mkstemp 生成唯一临时文件，避免并发/重名冲突
            fd, temp_path = tempfile.mkstemp(suffix='.webp.tmp', dir=root)
            os.close(fd)

            print(f"Processing {input_path} -> {output_path}")

            success, final_size = compress_to_webp(
                input_path, temp_path,
                target_size=target_size, max_dim=args.max_dim,
            )

            if success:
                # 原子替换
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(temp_path, output_path)
                if input_path != output_path and os.path.exists(input_path):
                    os.remove(input_path)
                print(f"   Success, size {final_size/1024:.1f} KB")
                processed += 1
            else:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                print(f"   Compression failed (still larger than {args.target_kb} KB), keeping original")
                failed_files.append(input_path)

    print("\n" + "=" * 50)
    print(f"Statistics: {processed} compressed, {skipped} skipped, {len(failed_files)} failed")
    if failed_files:
        print("\nFailed files:")
        for p in failed_files:
            print(f"  - {p}")
    print("Done.")


if __name__ == '__main__':
    main()