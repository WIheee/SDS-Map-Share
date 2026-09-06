#!/usr/bin/env python3
"""
Map Upload Tool - Supports multiple categories, files named after map title.
Usage: python tools/upload_map.py
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
PUBLIC_MAP = BASE / "public" / "map"
JSON_DIR = BASE / "src" / "data" / "map" / "json"
TOOLS = BASE / "tools"

# ---- 修复：分类用中文，与前端 CATEGORIES 保持一致 ----
CATEGORY_MAP = {
    "1": "对战",
    "2": "观赏",
    "3": "机关",
    "4": "生存"
}
CATEGORY_EN = {
    "对战": "battle",
    "观赏": "scenery",
    "机关": "mechanism",
    "生存": "survival"
}


def sanitize_filename(name: str) -> str:
    """Sanitize filename: keep word characters, hyphens, and dots; replace spaces with underscores."""
    name = name.strip()
    name = re.sub(r'\s+', '_', name)
    name = re.sub(r'[^\w\-.]', '', name, flags=re.UNICODE)
    return name


def get_input(prompt: str, validator, error_msg: str = "Invalid input, please try again.") -> str:
    """Prompt for input and retry until validator passes."""
    while True:
        value = input(prompt).strip()
        if validator(value):
            return value
        print(f"[ERROR] {error_msg}")


def non_empty(value: str) -> bool:
    return bool(value)


def file_exists(value: str) -> bool:
    return bool(value) and Path(value).exists()


def categories_valid(value: str) -> bool:
    if not value:
        return False
    nums = [c.strip() for c in value.split(',') if c.strip()]
    return bool(nums) and all(num in CATEGORY_MAP for num in nums)


def get_next_id() -> int:
    """Scan all JSON files and return max ID + 1."""
    max_id = 0
    for f in JSON_DIR.glob("*.json"):
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "id" in item:
                        max_id = max(max_id, item["id"])
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            continue
    return max_id + 1


def run_compress(script: str) -> bool:
    """Run a compression script in the tools directory."""
    sp = TOOLS / script
    if not sp.exists():
        print(f"[WARN] Compression script not found: {sp}")
        return False
    try:
        subprocess.run([sys.executable, str(sp)], check=True, cwd=str(BASE))
        return True
    except subprocess.CalledProcessError:
        print(f"[WARN] {script} failed to execute")
        return False


def copy_file(src: Path, dest_dir: Path, base_name: str, ext: str, compressed_ext: str) -> tuple[Path, Path]:
    """Copy a file to destination directory and return both target path and expected compressed path."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    dst = dest_dir / (base_name + ext)
    shutil.copy2(src, dst)
    compressed = dest_dir / (base_name + compressed_ext)
    return dst, compressed


def update_json(cat_en: str, map_data: dict) -> None:
    """Update the JSON file for the given category."""
    path = JSON_DIR / f"{cat_en}.json"
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = []
        except (json.JSONDecodeError, OSError):
            data = []
    else:
        data = []

    # Remove any existing entry with the same ID (overwrite)
    existing = any(isinstance(item, dict) and item.get("id") == map_data["id"] for item in data)
    if existing:
        print(f"[WARN] ID {map_data['id']} already exists, overwriting.")
    data = [item for item in data if not (isinstance(item, dict) and item.get("id") == map_data["id"])]
    data.append(map_data)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    # Ensure required directories exist
    PUBLIC_MAP.mkdir(parents=True, exist_ok=True)
    (PUBLIC_MAP / "image").mkdir(parents=True, exist_ok=True)
    (PUBLIC_MAP / "fun").mkdir(parents=True, exist_ok=True)
    JSON_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 50)
    print("Map Upload Tool (supports multiple categories, files named after map title)")
    print("=" * 50)

    title = get_input("Map name: ", non_empty, "Map name cannot be empty.")
    desc = get_input("Description: ", non_empty, "Description cannot be empty.")
    img = get_input("Image path: ", file_exists, "Image path does not exist or is invalid.")
    fun = get_input("Map file path: ", file_exists, "Map file path does not exist or is invalid.")

    print("\nCategories (enter numbers, comma-separated): 1-Battle 2-Scenery 3-Mechanism 4-Survival")
    cat_input = get_input("Category: ", categories_valid, "Please select valid categories (1-4).")
    categories = [CATEGORY_MAP[num.strip()] for num in cat_input.split(',') if num.strip()]

    author = get_input("Author name: ", non_empty, "Author name cannot be empty.")

    author_url = input("Author URL (optional, press Enter to skip): ").strip()
    if not author_url:
        author_url = ""

    print("\n" + "=" * 50)
    print("Please confirm the following information:")
    print(f"  Title: {title}")
    print(f"  Description: {desc}")
    print(f"  Categories: {', '.join(categories)}")
    print(f"  Author: {author}")
    print(f"  Author URL: {author_url if author_url else '(not set)'}")
    confirm = input("\nConfirm upload? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Upload cancelled.")
        return

    new_id = get_next_id()
    print(f"Assigned ID: {new_id}")

    main_cat = categories[0]
    cat_en = CATEGORY_EN[main_cat]

    print("Processing image...")
    img_ext = Path(img).suffix.lower()
    img_dst, img_comp = copy_file(Path(img), PUBLIC_MAP / "image" / cat_en, sanitize_filename(title), img_ext, ".webp")

    print("Processing map file...")
    fun_dst, fun_comp = copy_file(Path(fun), PUBLIC_MAP / "fun" / cat_en, sanitize_filename(title), ".fun", ".7z")

    run_compress("compress_images.py")
    run_compress("compress_fun.py")

    image_url = f"/map/image/{cat_en}/{img_comp.name if img_comp.exists() else img_dst.name}"
    file_url = f"/map/fun/{cat_en}/{fun_comp.name if fun_comp.exists() else fun_dst.name}"

    print(f"   Image: {image_url}")
    print(f"   File: {file_url}")

    map_data = {
        "id": new_id,
        "title": title,
        "description": desc,
        "image": image_url,
        "file": file_url,
        "category": categories,  # ← 现在是中文了
        "author": author
    }
    if author_url:
        map_data["authorUrl"] = author_url

    update_json(cat_en, map_data)

    print("=" * 50)
    print("Upload successful!")
    print(f"  ID: {new_id}")
    print(f"  Title: {title}")
    print(f"  Categories: {', '.join(categories)}")
    print(f"  Author: {author}")
    if author_url:
        print(f"  Author URL: {author_url}")
    print("=" * 50)


if __name__ == "__main__":
    main()