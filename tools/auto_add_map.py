#!/usr/bin/env python3
"""
Automatic Map Adding Tool - batch add maps with one click
Usage: python tools/auto_add_map.py
Scans all map folders under /storage/emulated/0/sds/,
reads config.json for metadata (title, description, category, author),
auto-detects cover image and .fun file inside the folder,
renames them to the title, copies them to the project directory,
and updates the corresponding JSON data file.
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

# ==================== Configuration ====================
SCAN_ROOT = Path("/storage/emulated/0/sds")

BASE = Path(__file__).parent.parent
PUBLIC_MAP = BASE / "public" / "map"
JSON_DIR = BASE / "src" / "data" / "map" / "json"
TOOLS = BASE / "tools"

# Category mapping - DO NOT MODIFY
CATEGORY_MAP = {
    "1": "对战",
    "2": "观赏",
    "3": "趣味",
    "4": "跑酷",
    "5": "其他"
}
CATEGORY_EN = {
    "对战": "battle",
    "观赏": "scenery",
    "趣味": "fun",
    "跑酷": "parkour",
    "其他": "other"
}

# Allowed image extensions for auto-detection
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
# ======================================================


def sanitize_filename(name: str) -> str:
    """Clean filename: keep Chinese, letters, digits, underscore, dot, hyphen."""
    name = name.strip()
    name = re.sub(r'\s+', '_', name)
    name = re.sub(r'[^\w\u4e00-\u9fff\-_.]', '', name)
    return name


def load_global_config(root: Path) -> dict:
    """Load global configuration (optional)."""
    config_path = root / "config.json"
    defaults = {
        "defaultAuthor": "Anonymous",
        "defaultCategory": ["其他"],
        "autoCompress": True,
        "skipInvalid": True
    }
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                defaults.update(user_config)
        except Exception:
            print("[WARN] Invalid global config file, using defaults.")
    return defaults


def load_map_config(folder: Path) -> Optional[dict]:
    """Load config.json for a single map folder."""
    config_path = folder / "config.json"
    if not config_path.exists():
        return None
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"  [ERROR] Failed to parse config.json: {e}")
        return None


def detect_assets(folder: Path) -> Tuple[Optional[Path], Optional[Path]]:
    """
    Auto-detect cover image and map file inside the folder.
    Returns (image_path, fun_path) where either can be None.
    """
    image_path = None
    fun_path = None

    # Look for first image file
    for ext in IMAGE_EXTENSIONS:
        matches = list(folder.glob(f"*{ext}"))
        if matches:
            image_path = matches[0]
            break

    # Look for first .fun file
    fun_matches = list(folder.glob("*.fun"))
    if fun_matches:
        fun_path = fun_matches[0]

    return image_path, fun_path


def validate_config(data: dict, global_config: dict) -> dict:
    """
    Validate and complete map configuration.
    No longer checks for file existence; files are auto-detected later.
    """
    required = ["title", "description", "category", "author"]
    for field in required:
        if field not in data or not data[field]:
            print(f"  [ERROR] Missing required field: {field}")
            return None

    # Validate category
    valid_categories = ['对战', '观赏', '趣味', '跑酷', '其他']
    if isinstance(data["category"], str):
        data["category"] = [data["category"]]
    data["category"] = [c for c in data["category"] if c in valid_categories]
    if not data["category"]:
        data["category"] = global_config["defaultCategory"]

    data.setdefault("authorUrl", "")
    return data


def get_next_id() -> int:
    """Get the next available ID."""
    max_id = 0
    for f in JSON_DIR.glob("*.json"):
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "id" in item:
                        max_id = max(max_id, item["id"])
        except (json.JSONDecodeError, OSError):
            continue
    return max_id + 1


def run_compress(script: str) -> bool:
    """Run a compression script."""
    sp = TOOLS / script
    if not sp.exists():
        print(f"  [WARN] Compression script not found: {sp}")
        return False
    try:
        subprocess.run([sys.executable, str(sp)], check=True, cwd=str(BASE))
        return True
    except subprocess.CalledProcessError:
        print(f"  [WARN] {script} execution failed")
        return False


def process_map(folder: Path, config: dict, global_config: dict,
                map_id: int, img_src: Path, fun_src: Path) -> bool:
    """
    Process a single map:
    1. Use title, description, categories, author from config
    2. Rename provided image and .fun files to title‑based names
    3. Copy to project directories
    4. Update JSON
    """
    title = config["title"]
    description = config["description"]
    categories = config["category"]
    author = config["author"]
    author_url = config.get("authorUrl", "")

    main_cat = categories[0]
    cat_en = CATEGORY_EN[main_cat]
    safe_title = sanitize_filename(title)

    # ---- Copy cover image ----
    img_ext = img_src.suffix.lower()
    img_dst_dir = PUBLIC_MAP / "image" / cat_en
    img_dst_dir.mkdir(parents=True, exist_ok=True)
    img_dst = img_dst_dir / (safe_title + img_ext)
    shutil.copy2(img_src, img_dst)
    print(f"  Cover image: {img_src.name} -> {safe_title}{img_ext}")

    # ---- Copy map file ----
    fun_dst_dir = PUBLIC_MAP / "fun" / cat_en
    fun_dst_dir.mkdir(parents=True, exist_ok=True)
    fun_dst = fun_dst_dir / (safe_title + ".fun")
    shutil.copy2(fun_src, fun_dst)
    print(f"  Map file: {fun_src.name} -> {safe_title}.fun")

    # ---- Compress ----
    if global_config.get("autoCompress", True):
        run_compress("compress_images.py")
        run_compress("compress_fun.py")

    # ---- Generate URLs (prefer compressed files if present) ----
    img_webp = img_dst_dir / (safe_title + ".webp")
    fun_7z = fun_dst_dir / (safe_title + ".7z")
    image_url = f"/map/image/{cat_en}/{img_webp.name if img_webp.exists() else img_dst.name}"
    file_url = f"/map/fun/{cat_en}/{fun_7z.name if fun_7z.exists() else fun_dst.name}"

    # ---- Write JSON ----
    map_data = {
        "id": map_id,
        "title": title,
        "description": description,
        "image": image_url,
        "file": file_url,
        "category": categories,
        "author": author
    }
    if author_url:
        map_data["authorUrl"] = author_url

    json_path = JSON_DIR / f"{cat_en}.json"
    if json_path.exists():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = []
        except Exception:
            data = []
    else:
        data = []

    # Remove duplicate ID (overwrite)
    data = [item for item in data if not (isinstance(item, dict) and item.get("id") == map_id)]
    data.append(map_data)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  Success: {title} (ID: {map_id})")
    return True


def main():
    """Main entry point."""
    PUBLIC_MAP.mkdir(parents=True, exist_ok=True)
    (PUBLIC_MAP / "image").mkdir(parents=True, exist_ok=True)
    (PUBLIC_MAP / "fun").mkdir(parents=True, exist_ok=True)
    JSON_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Automatic Map Adding Tool (auto_add_map.py)")
    print("=" * 60)

    if not SCAN_ROOT.exists():
        print(f"[ERROR] Directory not found: {SCAN_ROOT}")
        print("Please create the 'sds' folder under /storage/emulated/0/ and place map data inside.")
        return

    global_config = load_global_config(SCAN_ROOT)
    print(f"Global config: defaultAuthor={global_config['defaultAuthor']}")

    folders = [f for f in SCAN_ROOT.iterdir() if f.is_dir() and not f.name.startswith('.')]
    if not folders:
        print("[WARN] No map folders found.")
        return

    print(f"\nFound {len(folders)} folder(s):")
    for f in folders:
        print(f"  - {f.name}")
    print("-" * 60)

    next_id = get_next_id()
    success_count = 0
    failed_count = 0

    for folder in folders:
        print(f"\n[{next_id}] Processing: {folder.name}")

        raw_config = load_map_config(folder)
        if raw_config is None:
            if global_config.get("skipInvalid", True):
                print("  WARN: Skipping - config.json missing")
                failed_count += 1
                continue
            else:
                print("  ERROR: config.json missing")
                return

        config = validate_config(raw_config, global_config)
        if config is None:
            if global_config.get("skipInvalid", True):
                print("  WARN: Skipping - invalid config")
                failed_count += 1
                continue
            else:
                print("  ERROR: Invalid config")
                return

        # Auto-detect assets
        img_src, fun_src = detect_assets(folder)
        if img_src is None:
            print("  WARN: Skipping - no image file found in folder")
            if global_config.get("skipInvalid", True):
                failed_count += 1
                continue
            else:
                print("  ERROR: No cover image found")
                return
        if fun_src is None:
            print("  WARN: Skipping - no .fun file found in folder")
            if global_config.get("skipInvalid", True):
                failed_count += 1
                continue
            else:
                print("  ERROR: No .fun file found")
                return

        if process_map(folder, config, global_config, next_id, img_src, fun_src):
            success_count += 1
            next_id += 1
        else:
            failed_count += 1

    print("\n" + "=" * 60)
    print("Upload complete!")
    print(f"  Success: {success_count} map(s)")
    print(f"  Failed: {failed_count} map(s)")
    print("=" * 60)


if __name__ == "__main__":
    main()