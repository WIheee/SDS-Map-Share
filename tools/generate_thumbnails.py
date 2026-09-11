#!/usr/bin/env python3
"""
SDS Map Thumbnail Generator
- 移植自 SDSmapViewer 的方块样式与层次逻辑
- 以出生点为中心，固定视野，16:9 输出
- 用 Pillow 替代 pygame，Termux 可跑
- 缩略图输出到与 .fun / .7z 相同文件夹
- 压缩逻辑与 compress_images.py 保持一致
"""

import math
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("[错误] 缺少 Pillow，请运行: pip install Pillow")
    sys.exit(1)

try:
    import sdsmap
except ImportError:
    print("[错误] 缺少 sdsmap")
    sys.exit(1)

# ==================== 配置 ====================
SCAN_ROOT = Path("/storage/emulated/0/sds")
OUTPUT_SIZE = (1600, 900)      # 16:9 输出尺寸
MAX_CANVAS = 6000              # 单边最大像素，防内存溢出

# ---- 视野大小（世界单位）----
# 方块默认 2.5 单位。数值越小，画面越放大。
# 参考：15≈12个方块   30≈24个方块   60≈48个方块   120≈96个方块
VIEW_HALF_WIDTH = 300

# ---- 压缩参数（与 compress_images.py 保持一致）----
TARGET_SIZE = 60 * 1024        # 目标：≤60 KB
QUALITY_START = 90             # 起始质量
QUALITY_END = 5                # 最低质量
QUALITY_STEP = 5               # 每次降低幅度
# =============================================

# 渲染好的方块图缓存
BLOCK_CACHE = {}


# ==========================================
# 层次排序（从 SDSmapViewer 移植）
# ==========================================
def get_layer_index(block_id: int) -> int:
    ORBS = [18, 19, 20, 21, 29, 30]
    SPIKED_BALLS = [24]
    TILEABLE_AND_OUTLINES = [0, 1, 3, 4, 5, 6, 12, 14, 16, 17, 23, 31, 33]
    BOOSTERS = [7]
    UNTILEABLE = [2, 8, 9, 10, 11, 13, 15, 28, 32]

    if block_id in ORBS:
        return 6
    if block_id in SPIKED_BALLS:
        return 5
    if block_id in TILEABLE_AND_OUTLINES:
        return 4
    if block_id in BOOSTERS:
        return 3
    if block_id in UNTILEABLE:
        return 2
    return 1


# ==========================================
# 单块方块渲染（从 Pygame 移植到 Pillow）
# ==========================================
def render_block_image(b_id: int, w: float, h: float, rotation: float):
    UNTILEABLE_IDS = [2, 7, 8, 9, 10, 11, 13, 15, 18, 19, 20, 21,
                      24, 28, 29, 30, 32]

    bw = int(abs(w))
    bh = int(abs(h))
    if bw <= 0 or bh <= 0:
        return None

    rotation = int(rotation or 0) % 360
    cache_key = (b_id, bw, bh, rotation, w < 0, h < 0)
    if cache_key in BLOCK_CACHE:
        return BLOCK_CACHE[cache_key]

    img = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = bw / 2, bh / 2

    # ---- 安全绘制辅助 ----
    def rect_full(color):
        d.rectangle([0, 0, bw - 1, bh - 1], fill=color)

    def rect_outline(color, width):
        d.rectangle([0, 0, bw - 1, bh - 1], outline=color, width=width)

    def safe_rect(x0, y0, x1, y1, **kwargs):
        """确保坐标有序且为整数，避免 Pillow 报 y1 < y0"""
        x0, x1 = sorted([int(x0), int(x1)])
        y0, y1 = sorted([int(y0), int(y1)])
        if x1 <= x0:
            x1 = x0 + 1
        if y1 <= y0:
            y1 = y0 + 1
        d.rectangle([x0, y0, x1, y1], **kwargs)

    def circle(cx0, cy0, r, fill=None, outline=None, width=1):
        """半径取绝对值，过小时跳过，避免 bbox 反序"""
        r = abs(r)
        if r < 0.5:
            return
        bbox = [cx0 - r, cy0 - r, cx0 + r, cy0 + r]
        if fill is not None:
            d.ellipse(bbox, fill=fill)
        if outline is not None:
            d.ellipse(bbox, outline=outline, width=width)

    # ---- 逐 id 绘制 ----
    if b_id == 0:
        rect_full((139, 69, 19))
        rect_outline((34, 139, 34), 3)

    elif b_id == 1:
        rect_full((255, 105, 180))
        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            circle(cx + dx * (bw / 2 - 4), cy + dy * (bh / 2 - 4), 3, fill=(50, 50, 50))

    elif b_id == 2:
        rect_full((20, 20, 20))

    elif b_id == 3:
        rect_full((160, 82, 45))
        d.line([(0, cy), (bw, cy)], fill=(100, 50, 20), width=2)

    elif b_id == 4:
        rect_full((128, 0, 128))

    elif b_id == 23:
        rect_full((0, 128, 0))

    elif b_id == 5:
        rect_full((255, 215, 0))
        rect_outline((184, 134, 11), 4)

    elif b_id == 7:
        rect_full((255, 255, 0, 150))
        d.polygon([(bw / 2, bh - 5), (bw / 2 - 10, bh / 2), (bw / 2 + 10, bh / 2)],
                  fill=(255, 140, 0))

    elif b_id in (8, 9, 10):
        bottom = (0, 128, 128) if b_id == 8 else (0, 100, 0) if b_id == 9 else (200, 0, 0)
        safe_rect(0, 0, bw - 1, bh // 2, fill=(255, 255, 255))
        safe_rect(0, bh // 2, bw - 1, bh - 1, fill=bottom)
        if b_id == 10:
            circle(cx, bh, 8, fill=(100, 100, 100))

    elif b_id == 11:
        circle(cx, cy, bw / 2, outline=(0, 0, 255), width=4)
        circle(cx, cy, bw / 4, fill=(255, 255, 0))

    elif b_id == 12:
        rect_full((128, 128, 128))
        rect_outline((200, 200, 200), 2)

    elif b_id == 14:
        rect_full((40, 40, 40))
        d.polygon([(cx, cy - 10), (cx - 10, cy + 5), (cx + 10, cy + 5)],
                  fill=(255, 255, 255))

    elif b_id == 16:
        rect_full((200, 0, 0))

    elif b_id == 13:
        circle(cx, cy, bw / 2, fill=(150, 150, 150))
        circle(cx, cy, bw / 2, outline=(0, 0, 0), width=5)

    elif b_id == 15:
        rect_full((200, 0, 0))
        rect_outline((255, 100, 100), 3)
        circle(cx, cy, bw / 3, outline=(255, 255, 255), width=3)

    elif b_id == 17:
        rect_outline((0, 0, 255), 3)

    elif b_id == 6:
        rect_full((80, 20, 20))
        d.line([(0, 0), (bw, bh)], fill=(255, 0, 0), width=2)
        rect_outline((255, 255, 0), 2)

    elif b_id == 24:
        circle(cx, cy, bw / 2, fill=(200, 0, 0))
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            ex = cx + math.cos(rad) * (bw / 2 + 5)
            ey = cy + math.sin(rad) * (bh / 2 + 5)
            d.line([(cx, cy), (ex, ey)], fill=(150, 0, 0), width=3)

    elif b_id in (18, 19, 20, 21, 29, 30):
        color = (200, 0, 0) if b_id in (29, 30) else (255, 255, 0)
        circle(cx, cy, bw / 2, fill=color)
        circle(cx, cy, bw / 2, outline=(0, 0, 0), width=3)
        if b_id in (21, 30):
            circle(cx, cy, bw / 4, fill=(0, 0, 0))
        else:
            d.line([(cx - bw / 4, cy), (cx + bw / 4, cy)], fill=(0, 0, 0), width=3)

    elif b_id == 28:
        rect_full((150, 0, 200))
        circle(cx, cy, bw / 3, outline=(255, 0, 255), width=2)
        circle(cx, cy, bw / 6, outline=(255, 0, 255), width=2)

    elif b_id == 31:
        rect_full((30, 30, 30))
        d.line([(cx, cy - 10), (cx, cy + 10)], fill=(255, 255, 255), width=3)
        d.line([(cx - 10, cy), (cx + 10, cy)], fill=(255, 255, 255), width=3)

    elif b_id == 32:
        rect_full((173, 216, 230))
        safe_rect(0, bh // 3, bw - 1, bh * 2 // 3, fill=(0, 0, 139))

    elif b_id == 33:
        rect_full((255, 255, 255, 50))
        rect_outline((255, 255, 255), 2)

    else:
        rect_outline((255, 0, 255), 2)

    # 负缩放翻转
    if b_id in UNTILEABLE_IDS:
        flip_x = w < 0
        flip_y = h < 0
        if flip_x and flip_y:
            img = img.transpose(Image.ROTATE_180)
        elif flip_x:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        elif flip_y:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)

    # 旋转
    if rotation != 0:
        img = img.rotate(rotation, expand=True, resample=Image.BICUBIC)

    BLOCK_CACHE[cache_key] = img
    return img


# ==========================================
# 解析 .fun / 从 .7z 解压
# ==========================================
def extract_fun_from_7z(archive: Path, tmp_dir: Path):
    try:
        subprocess.run(
            ["7z", "x", str(archive), f"-o{tmp_dir}", "-y"],
            check=True, capture_output=True, text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"  [解压失败] {archive.name}: {e}")
        return None
    funs = list(Path(tmp_dir).rglob("*.fun"))
    return funs[0] if funs else None


def load_map_data(fun_path: Path):
    data = sdsmap.decode_map_file(str(fun_path))
    if not isinstance(data, dict):
        return None

    raw_blocks = list(reversed(data.get("blocks", [])))
    raw_blocks.sort(key=lambda b: get_layer_index(b.get("id", 0)))

    blocks = []
    for b in raw_blocks:
        pos = b.get("position") or {}
        sc = b.get("scale") or {}
        blocks.append({
            "id": int(b.get("id", 0)),
            "x": float(pos.get("x", 0.0)),
            "y": float(pos.get("y", 0.0)),
            "w": float(sc.get("x", 2.5)),
            "h": float(sc.get("y", 2.5)),
            "rot": float(b.get("rotation", 0) or 0),
        })

    bg = data.get("background") or {}
    c1 = bg.get("color1") if isinstance(bg, dict) else None
    if isinstance(c1, dict) and all(k in c1 for k in ("r", "g", "b")):
        bg_color = (int(c1["r"]), int(c1["g"]), int(c1["b"]), 255)
    else:
        bg_color = (30, 30, 40, 255)

    # 出生点
    spawn = data.get("spawn") or {}
    spawn_pos = spawn.get("position") if isinstance(spawn, dict) else None
    if isinstance(spawn_pos, dict):
        spawn_x = float(spawn_pos.get("x", 0.0))
        spawn_y = float(spawn_pos.get("y", 0.0))
    else:
        spawn_x, spawn_y = 0.0, 0.0

    return {
        "blocks": blocks,
        "bg_color": bg_color,
        "spawn_x": spawn_x,
        "spawn_y": spawn_y,
    }


# ==========================================
# 渲染整张缩略图（spawn 居中，固定视野，16:9）
# ==========================================
def render_thumbnail(map_data, output_path: Path) -> bool:
    blocks = map_data["blocks"]
    if not blocks:
        return False

    spawn_x = map_data["spawn_x"]
    spawn_y = map_data["spawn_y"]

    # 固定视野，以 spawn 为中心
    half_w = VIEW_HALF_WIDTH
    half_h = half_w * 9 / 16      # 16:9

    view_min_x = spawn_x - half_w
    view_max_x = spawn_x + half_w
    view_min_y = spawn_y - half_h
    view_max_y = spawn_y + half_h
    span_x = half_w * 2
    span_y = half_h * 2

    # 画布像素尺寸
    scale = min(MAX_CANVAS / span_x, MAX_CANVAS / span_y)
    canvas_w = max(200, int(span_x * scale))
    canvas_h = max(200, int(span_y * scale))

    canvas = Image.new("RGBA", (canvas_w, canvas_h), map_data["bg_color"])

    def w2p(wx, wy):
        """世界坐标 → 像素坐标（y 轴翻转，spawn 在画面正中）"""
        px = (wx - view_min_x) * scale
        py = canvas_h - (wy - view_min_y) * scale
        return px, py

    # 逐块贴图（视野外的跳过）
    for b in blocks:
        radius = math.hypot(abs(b["w"]), abs(b["h"])) / 2 + 2
        if (b["x"] + radius < view_min_x or b["x"] - radius > view_max_x or
                b["y"] + radius < view_min_y or b["y"] - radius > view_max_y):
            continue

        signed_w = b["w"] * scale
        signed_h = -b["h"] * scale   # y 轴翻转

        cx, cy = w2p(b["x"], b["y"])
        block_img = render_block_image(b["id"], signed_w, signed_h, b["rot"])
        if block_img is None:
            continue

        rect_x = int(cx - block_img.width / 2)
        rect_y = int(cy - block_img.height / 2)
        canvas.paste(block_img, (rect_x, rect_y), block_img)

    # 缩放到目标尺寸
    canvas = canvas.convert("RGB").resize(OUTPUT_SIZE, Image.Resampling.LANCZOS)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 循环降质，直到 ≤ TARGET_SIZE（与 compress_images.py 逻辑一致）
    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    for quality in range(QUALITY_START, QUALITY_END - 1, -QUALITY_STEP):
        canvas.save(temp_path, "WEBP", quality=quality, lossless=False, method=6)
        if temp_path.stat().st_size <= TARGET_SIZE:
            break

    # 原子替换
    if output_path.exists():
        output_path.unlink()
    temp_path.rename(output_path)
    return True


# ==========================================
# 主流程
# ==========================================
def process_folder(folder: Path) -> bool:
    name = folder.name
    print(f"\n处理: {name}")

    fun_files = list(folder.glob("*.fun"))
    tmp_dir = None
    if fun_files:
        fun_path = fun_files[0]
    else:
        archives = list(folder.glob("*.7z"))
        if not archives:
            print("  [跳过] 没有 .fun 或 .7z")
            return False
        tmp_dir = tempfile.mkdtemp()
        fun_path = extract_fun_from_7z(archives[0], Path(tmp_dir))
        if not fun_path:
            print("  [跳过] .7z 里没有 .fun")
            return False

    try:
        map_data = load_map_data(fun_path)
    except Exception as e:
        print(f"  [解析失败] {e}")
        return False

    if not map_data or not map_data["blocks"]:
        print("  [跳过] 地图为空")
        return False

    # 输出到与 .fun / .7z 相同的文件夹
    output_path = folder / f"{name}.webp"
    if render_thumbnail(map_data, output_path):
        size_kb = output_path.stat().st_size / 1024
        print(f"  [完成] {output_path.name} ({len(map_data['blocks'])} 个方块, {size_kb:.1f} KB)")
        return True
    return False


def main():
    print("=" * 50)
    print("SDS 缩略图生成器 (spawn 居中 + 固定视野 + 60KB 压缩)")
    print("=" * 50)

    if not SCAN_ROOT.exists():
        print(f"[错误] 目录不存在: {SCAN_ROOT}")
        sys.exit(1)

    folders = [
        f for f in SCAN_ROOT.iterdir()
        if f.is_dir() and not f.name.startswith(".") and f.name != "thumbnails"
    ]
    if not folders:
        print("[提示] 没有找到地图文件夹")
        return

    print(f"找到 {len(folders)} 个文件夹\n")

    success = 0
    for folder in folders:
        if process_folder(folder):
            success += 1

    print("\n" + "=" * 50)
    print(f"完成: 成功 {success}/{len(folders)}")
    print(f"输出: 各地图文件夹内")
    print("=" * 50)


if __name__ == "__main__":
    main()