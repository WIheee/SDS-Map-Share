#!/usr/bin/env python3
"""
地图上传工具 - 支持多分类，文件以地图名称命名
使用方式：python tools/upload_map.py
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
    """清理文件名，保留中文、字母、数字、下划线、点、横线，替换空格为下划线"""
    name = name.strip()
    name = re.sub(r'\s+', '_', name)                     # 空格 -> 下划线
    name = re.sub(r'[^\w\u4e00-\u9fff\-_.]', '', name)   # 移除非法字符
    return name


def get_next_id():
    max_id = 0
    for f in JSON_DIR.glob("*.json"):
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "id" in item:
                        max_id = max(max_id, item["id"])
        except:
            pass
    return max_id + 1


def run_compress(script, *args):
    sp = TOOLS / script
    if not sp.exists():
        print(f"警告: {script} 不存在，跳过")
        return False
    try:
        subprocess.run([sys.executable, str(sp)] + list(args), check=True, cwd=str(BASE))
        return True
    except:
        return False


def copy_and_compress_image(src: Path, cat_en: str, title: str) -> str:
    """复制图片并用地图名称命名，压缩后返回 webp 路径"""
    dst_dir = PUBLIC_MAP / "image" / cat_en
    dst_dir.mkdir(parents=True, exist_ok=True)

    src = Path(src)
    base = sanitize_filename(title)
    ext = src.suffix.lower()
    # 如果原图不是 webp，先复制为原格式，压缩后生成 webp
    dst = dst_dir / (base + ext)
    shutil.copy2(src, dst)

    # 调用压缩脚本（处理整个目录）
    run_compress("compress_images.py")

    # 检查是否生成了 webp
    webp = dst_dir / (base + ".webp")
    if webp.exists():
        return f"/map/image/{cat_en}/{webp.name}"
    else:
        # 未生成 webp（可能已经是 webp 且<80KB），使用原文件
        return f"/map/image/{cat_en}/{dst.name}"


def copy_and_compress_fun(src: Path, cat_en: str, title: str) -> str:
    """复制 .fun 文件并用地图名称命名，压缩后返回 .7z 路径"""
    dst_dir = PUBLIC_MAP / "fun" / cat_en
    dst_dir.mkdir(parents=True, exist_ok=True)

    src = Path(src)
    base = sanitize_filename(title)
    dst = dst_dir / (base + ".fun")
    shutil.copy2(src, dst)

    # 调用压缩脚本
    run_compress("compress_fun.py")

    # 检查是否生成了 .7z
    sevenz = dst_dir / (base + ".7z")
    if sevenz.exists():
        return f"/map/fun/{cat_en}/{sevenz.name}"
    else:
        # 压缩失败，返回 .fun
        return f"/map/fun/{cat_en}/{dst.name}"


def update_json(cat_en: str, map_data: dict):
    path = JSON_DIR / f"{cat_en}.json"
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except:
                data = []
    else:
        data = []
    data.append(map_data)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    print("=" * 50)
    print("地图上传工具 (支持多分类，文件以地图名命名)")
    print("=" * 50)

    title = input("地图名称: ").strip()
    if not title:
        print("错误: 地图名称不能为空")
        return

    desc = input("地图描述: ").strip()
    if not desc:
        print("错误: 地图描述不能为空")
        return

    img = input("地图图片(路径): ").strip()
    if not img or not Path(img).exists():
        print("错误: 图片路径无效")
        return

    fun = input("地图文件(路径): ").strip()
    if not fun or not Path(fun).exists():
        print("错误: 地图文件路径无效")
        return

    print("分类(输入数字,多个用逗号分隔): 1-对战 2-观赏 3-机关 4-生存")
    cat_input = input("分类: ").strip()
    cat_nums = [c.strip() for c in cat_input.split(',') if c.strip()]
    categories = []
    for num in cat_nums:
        cat = CATEGORY_MAP.get(num)
        if cat:
            categories.append(cat)
    if not categories:
        print("错误: 没有有效的分类")
        return

    author = input("作者名: ").strip()
    if not author:
        print("错误: 作者名不能为空")
        return

    new_id = get_next_id()
    print(f"分配 ID: {new_id}")

    # 主分类（第一个）用于文件存放目录
    main_cat = categories[0]
    cat_en = CATEGORY_EN[main_cat]

    print("处理图片...")
    image_url = copy_and_compress_image(Path(img), cat_en, title)
    print(f"图片: {image_url}")

    print("处理地图文件...")
    file_url = copy_and_compress_fun(Path(fun), cat_en, title)
    print(f"文件: {file_url}")

    map_data = {
        "id": new_id,
        "title": title,
        "description": desc,
        "image": image_url,
        "file": file_url,
        "category": categories,
        "author": author
    }

    update_json(cat_en, map_data)

    print("=" * 50)
    print("上传成功！")
    print(f"ID: {new_id}")
    print(f"标题: {title}")
    print(f"分类: {', '.join(categories)}")
    print(f"作者: {author}")
    print("=" * 50)


if __name__ == "__main__":
    main()