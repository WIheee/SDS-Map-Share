#!/usr/bin/env python3
"""
Delete a map entry by ID.
Python handles interaction and JSON modification; shell commands handle file deletion.
Usage: python tools/rm_map.py
"""

import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
JSON_DIR = BASE / "src" / "data" / "map" / "json"


def find_map_by_id(map_id: int):
    """Search all JSON files for a map with the given ID."""
    for json_file in JSON_DIR.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        if not isinstance(data, list):
            continue

        for idx, item in enumerate(data):
            if isinstance(item, dict) and item.get("id") == map_id:
                return json_file, idx, item
    return None, None, None


def delete_resource_by_shell(resource_path: str):
    """Delete a resource file using 'rm -f'. Missing files are ignored."""
    if not resource_path:
        return

    # Map /map/... to public/map/...
    if resource_path.startswith('/map/'):
        target = BASE / 'public' / resource_path[1:]  # remove leading slash
    else:
        target = BASE / resource_path.lstrip('/')

    cmd = ['rm', '-f', str(target)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  Deleted: {target}")
    else:
        print(f"  Deletion failed: {target}")


def main():
    print("=" * 50)
    print("Map Deletion Tool (Python + Shell)")
    print("=" * 50)

    try:
        map_id = int(input("Enter map ID to delete: ").strip())
    except ValueError:
        print("Error: Please enter a valid numeric ID.")
        return

    json_file, idx, map_data = find_map_by_id(map_id)
    if json_file is None:
        print(f"Error: No map found with ID {map_id}.")
        return

    print("\nFound map:")
    print(f"  ID: {map_data['id']}")
    print(f"  Title: {map_data['title']}")
    print(f"  Category: {', '.join(map_data.get('category', []))}")
    print(f"  Author: {map_data.get('author', 'Unknown')}")
    print()

    confirm = input("Confirm deletion? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Deletion cancelled.")
        return

    # 1. Delete resource files using shell
    print("\nDeleting resource files...")
    if "image" in map_data:
        delete_resource_by_shell(map_data["image"])
    if "file" in map_data:
        delete_resource_by_shell(map_data["file"])

    # 2. Remove entry from JSON using Python
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading JSON file: {e}")
        return

    if not isinstance(data, list):
        print("Error: JSON data format is invalid (expected a list).")
        return

    new_data = [item for item in data if not (isinstance(item, dict) and item.get('id') == map_id)]

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print(f"\nMap ID {map_id} has been deleted. JSON updated.")
    print("=" * 50)


if __name__ == "__main__":
    main()