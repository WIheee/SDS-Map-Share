#!/usr/bin/env python3
"""
Delete a map entry by UUID.
Python handles both interaction/JSON modification and file deletion,
so the script is fully cross-platform (Windows / macOS / Linux).

Usage: python tools/rm_map.py
"""

import json
from pathlib import Path

BASE = Path(__file__).parent.parent
JSON_DIR = BASE / "src" / "data" / "map" / "json"


def find_map_by_id(map_id: str):
    """Search all JSON files for a map with the given ID."""
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
                return json_file, item
    return None, None


def delete_resource(resource_path: str) -> None:
    """Delete a resource file. Missing files are silently ignored."""
    if not resource_path:
        return

    # Map /map/... to public/map/...
    if resource_path.startswith('/map/'):
        target = BASE / 'public' / resource_path[1:]
    else:
        target = BASE / resource_path.lstrip('/')

    try:
        target.unlink(missing_ok=True)
        print(f"  Deleted: {target}")
    except OSError as e:
        print(f"  Deletion failed: {target} ({e})")


def main():
    print("=" * 50)
    print("Map Deletion Tool")
    print("=" * 50)

    map_id = input("Enter map ID (UUID) to delete: ").strip()
    if not map_id:
        print("Error: Map ID cannot be empty.")
        return

    json_file, map_data = find_map_by_id(map_id)
    if json_file is None:
        print(f"Error: No map found with ID {map_id}.")
        return

    print("\nFound map:")
    print(f"  ID: {map_data['id']}")
    print(f"  Title: {map_data.get('title', '')}")
    print(f"  Category: {', '.join(map_data.get('category', []))}")
    print(f"  Author: {map_data.get('author', 'Unknown')}")
    print()

    confirm = input("Confirm deletion? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Deletion cancelled.")
        return

    # 1. Delete resource files
    print("\nDeleting resource files...")
    if "image" in map_data:
        delete_resource(map_data["image"])
    if "file" in map_data:
        delete_resource(map_data["file"])

    # 2. Remove entry from JSON
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading JSON file: {e}")
        return

    if not isinstance(data, list):
        print("Error: JSON data format is invalid (expected a list).")
        return

    new_data = [item for item in data
                if not (isinstance(item, dict) and item.get('id') == map_id)]

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print(f"\nMap ID {map_id} has been deleted. JSON updated.")
    print("=" * 50)


if __name__ == "__main__":
    main()