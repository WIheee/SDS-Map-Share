#!/usr/bin/env python3
"""
Delete a map entry by UUID.
Python handles both interaction/JSON modification and file deletion,
so the script is fully cross-platform (Windows / macOS / Linux).

Usage:
  python tools/rm_map.py                      # 交互式输入单个 ID
  python tools/rm_map.py <id>                 # 直接删除指定 ID
  python tools/rm_map.py <id1> <id2> ...      # 批量删除
  python tools/rm_map.py --dry-run <id>       # 只预览，不实际删除
  python tools/rm_map.py --yes <id>           # 跳过确认
"""

import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
JSON_DIR = BASE / "src" / "data" / "map" / "json"
PUBLIC_DIR = BASE / "public"


def is_safe_target(target: Path) -> bool:
    """确保删除目标位于 public/ 目录内，防止路径穿越。"""
    try:
        target.resolve().relative_to(PUBLIC_DIR.resolve())
        return True
    except ValueError:
        return False


def find_maps_by_id(map_id: str):
    """在所有 JSON 文件中查找指定 ID 的所有条目。

    返回：[(json_file_path, map_data), ...]，可能为空、也可能多条（重复 id）。
    """
    hits = []
    for json_file in JSON_DIR.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(data, list):
            continue
        for item in data:
            if isinstance(item, dict) and item.get("id") == map_id:
                hits.append((json_file, item))
    return hits


def delete_resource(resource_path: str, dry_run: bool = False) -> bool:
    """删除资源文件。返回是否成功（不存在也算成功）。

    所有删除路径必须位于 public/ 内，否则拒绝。
    """
    if not resource_path:
        return True

    # /map/... -> public/map/...
    if resource_path.startswith('/map/'):
        target = PUBLIC_DIR / resource_path[1:]
    else:
        target = (BASE / resource_path.lstrip('/')).resolve()

    if not is_safe_target(target):
        print(f"  [拒绝] 路径越界，跳过：{target}")
        return False

    if dry_run:
        exists = "存在" if target.exists() else "不存在"
        print(f"  [dry-run] 将删除: {target}（{exists}）")
        return True

    try:
        target.unlink(missing_ok=True)
        print(f"  已删除: {target}")
        return True
    except OSError as e:
        print(f"  删除失败: {target} ({e})")
        return False


def format_categories(value) -> str:
    """兼容 category 是字符串或数组两种情况。"""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return ', '.join(str(x) for x in value)
    return ''


def preview(map_data: dict) -> None:
    print("  找到地图:")
    print(f"    ID:       {map_data.get('id', '')}")
    print(f"    标题:     {map_data.get('title', '')}")
    print(f"    分类:     {format_categories(map_data.get('category'))}")
    print(f"    作者:     {map_data.get('author', 'Unknown')}")
    print(f"    封面:     {map_data.get('image', '')}")
    print(f"    地图文件: {map_data.get('file', '')}")


def remove_entry_from_json(json_file: Path, map_id: str, dry_run: bool = False) -> bool:
    """从 JSON 文件中移除指定 ID 的所有条目。返回是否成功。"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"  [ERROR] 读取失败 {json_file.name}: {e}")
        return False

    if not isinstance(data, list):
        print(f"  [ERROR] {json_file.name} 格式无效（期望数组）")
        return False

    new_data = [
        item for item in data
        if not (isinstance(item, dict) and item.get("id") == map_id)
    ]

    if len(new_data) == len(data):
        return True

    if dry_run:
        print(f"  [dry-run] 将从 {json_file.name} 移除 {len(data) - len(new_data)} 条")
        return True

    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        print(f"  已更新: {json_file.name}（移除 {len(data) - len(new_data)} 条）")
        return True
    except OSError as e:
        print(f"  [ERROR] 写入失败 {json_file.name}: {e}")
        return False


def delete_one(map_id: str, dry_run: bool = False, skip_confirm: bool = False) -> bool:
    """删除单张地图。返回是否成功。"""
    hits = find_maps_by_id(map_id)

    if not hits:
        print(f"\n[未找到] ID: {map_id}")
        return False

    print(f"\n{'=' * 50}")
    print(f"ID: {map_id}（找到 {len(hits)} 条记录）")
    print('=' * 50)
    for json_file, map_data in hits:
        print(f"\n  JSON: {json_file.name}")
        preview(map_data)

    if not skip_confirm and not dry_run:
        confirm = input("\n确认删除以上所有记录？(y/N): ").strip().lower()
        if confirm != 'y':
            print("已取消。")
            return False

    # 事务性：先改 JSON，再删文件
    # 这样即使删文件失败，最坏也只是留下孤儿文件，不会出现死链
    print("\n[1/2] 更新 JSON...")
    json_ok = True
    for json_file, _ in hits:
        if not remove_entry_from_json(json_file, map_id, dry_run):
            json_ok = False

    if not json_ok and not dry_run:
        print("\n[中止] JSON 更新失败，未删除任何文件。")
        return False

    print("\n[2/2] 删除资源文件...")
    for _, map_data in hits:
        delete_resource(map_data.get("image", ""), dry_run)
        delete_resource(map_data.get("file", ""), dry_run)

    print(f"\n[done] ID {map_id} 处理完成。")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="按 UUID 删除地图条目及其资源文件。"
    )
    parser.add_argument(
        "ids", nargs="*",
        help="要删除的地图 ID（可多个）。留空则交互式输入。"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="只预览，不实际删除任何文件或改动 JSON"
    )
    parser.add_argument(
        "--yes", "-y", action="store_true",
        help="跳过确认提示"
    )
    args = parser.parse_args()

    print("=" * 50)
    print("Map Deletion Tool")
    if args.dry_run:
        print("模式: DRY-RUN（不会实际删除）")
    print("=" * 50)

    ids = list(args.ids)
    if not ids:
        raw = input("输入要删除的地图 ID（多个用空格分隔）: ").strip()
        if not raw:
            print("未输入 ID，退出。")
            return
        ids = raw.split()

    success = 0
    for map_id in ids:
        if delete_one(map_id, dry_run=args.dry_run, skip_confirm=args.yes):
            success += 1

    print("\n" + "=" * 50)
    print(f"完成: {success}/{len(ids)} 成功")
    if args.dry_run:
        print("（dry-run 模式，未实际修改）")
    print("=" * 50)


if __name__ == "__main__":
    main()