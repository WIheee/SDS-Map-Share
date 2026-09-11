# SDS-Map-Share · 工具集

本目录包含项目使用的全部自动化脚本。所有脚本都**只需 Python 3.10+**，除 `generate_thumbnails.py` 外无第三方依赖。

## 脚本一览

| 脚本 | 用途 | 需要运行？ |
|---|---|---|
| `auto_add_map.py` | **一键批量添加地图**（主力脚本） | 每次加图时运行 |
| `generate_thumbnails.py` | 批量生成地图缩略图（无需进游戏） | 加图前运行（可选） |
| `rm_map.py` | 按 UUID 删除地图 | 需要删图时 |
| `compress_images.py` | 图片压缩到 ≤60 KB | 被 `auto_add_map.py` 自动调用 |
| `compress_fun.py` | `.fun` 压缩成 `.7z` | 被 `auto_add_map.py` 自动调用 |
| `tree.py` | 导出项目结构（给 AI 或备份用） | 按需 |
| `rewrite_i18n_email.py` | 一次性重写公告页 + 语言文件 | **只需运行一次** |

---

## 环境准备

### 必需

- **Python 3.10+**
- **7-Zip 命令行工具**（`7z` 命令）
  - Termux / Android：`pkg install p7zip`
  - Debian / Ubuntu：`sudo apt install p7zip-full`
  - macOS：`brew install p7zip`
  - Windows：安装 [7-Zip](https://www.7-zip.org/)，把安装目录加入 `PATH`

### 缩略图生成额外需要

- **Pillow**：`pip install Pillow`
- **sdsmap**：`pip install sdsmap`

---

## 标准工作流

### 加一张新地图

```
1. 在 /storage/emulated/0/sds/ 下建一个文件夹（名字随意，比如 仙境/）
2. 把 .fun 文件放进去
3. 在文件夹里放一个 config.json（可选，见下文）
4. （可选）运行 generate_thumbnails.py 生成缩略图
5. 运行 auto_add_map.py 一键添加到项目
```

### 删除一张地图

```
1. 打开 src/data/map/json/ 找到目标地图的 UUID
2. 运行 rm_map.py，粘贴 UUID
3. 确认删除（同时会删掉 .webp 和 .7z）
```

---

## 脚本详解

### `auto_add_map.py` — 一键添加

**用途**：扫描 `sds/` 目录下所有地图文件夹，自动完成重命名、复制、压缩、写 JSON 的全流程。

**用法**：
```bash
cd <项目根目录>
python tools/auto_add_map.py
```

**它做了什么**：
1. 扫描 `/storage/emulated/0/sds/` 下的每个文件夹
2. 读取文件夹内的 `config.json`（标题、描述、分类、作者）
3. 自动识别文件夹内的图片（截图 / 缩略图）和 `.fun` 文件
4. 按标题重命名，复制到 `public/map/image/<分类>/` 和 `public/map/fun/<分类>/`
5. 用 UUID 作为唯一 ID，写入 `src/data/map/json/<分类>.json`
6. 全部完成后**统一压缩一次**（图片 → WebP、`.fun` → `.7z`）

**文件夹结构要求**：
```
/storage/emulated/0/sds/仙境/
├── config.json          # 必需：元数据
├── 仙境.fun             # 必需：地图文件
└── 仙境.webp            # 可选：封面图（没有的话用自动生成的缩略图）
```

**`config.json` 示例**：
```json
{
  "title": "仙境",
  "description": "四周白茫茫的，仿佛只有自己，宛如水墨画一般的地图",
  "category": ["对战", "观赏"],
  "author": "WLurker",
  "authorUrl": ""
}
```

**分类可选值**：`对战` / `观赏` / `趣味` / `跑酷` / `其他`。第一个分类决定文件放进哪个目录。

**全局配置**（可选）：在 `/storage/emulated/0/sds/config.json` 放一份默认值：
```json
{
  "defaultAuthor": "WIhee",
  "defaultCategory": ["其他"],
  "autoCompress": true,
  "skipInvalid": true
}
```

**注意**：此脚本**不做备份**，会覆盖同名文件。建议先 `git commit` 再跑。

---

### `generate_thumbnails.py` — 生成缩略图

**用途**：直接解析 `.fun` 文件，用程序化渲染生成 16:9 缩略图。**无需进游戏截图**。

**用法**：
```bash
python tools/generate_thumbnails.py
```

**输出**：每个地图文件夹里生成 `<文件夹名>.webp`。

**可调参数**（文件顶部）：
| 参数 | 默认 | 说明 |
|---|---|---|
| `VIEW_HALF_WIDTH` | `300` | 视野半宽（世界单位）。越小越放大，越大越广角 |
| `OUTPUT_SIZE` | `(1600, 900)` | 输出分辨率 |
| `TARGET_SIZE` | `60 * 1024` | 目标文件大小上限 |

**原理**：用 `sdsmap` 解析 `.fun` 得到方块列表 → 用 Pillow 按 `id` 逐块绘制（颜色和形状参照 SDSmapViewer）→ 以出生点为中心裁剪 16:9 → 循环降质压缩到 ≤60 KB。

**依赖**：需要 `Pillow` 和 `sdsmap`。

**已知限制**：地图极大时可能内存不足。渲染的是俯视平面图，没有游戏里的光影效果。

---

### `rm_map.py` — 删除地图

**用途**：按 UUID 删除一条地图记录及其关联文件。

**用法**：
```bash
python tools/rm_map.py
# 按提示粘贴 UUID
```

**它做了什么**：从 JSON 中移除条目，同时删除对应的 `.webp` 和 `.7z` 文件。

**跨平台**：使用 `Path.unlink()` 而非 `rm -f`，Windows / macOS / Linux / Termux 都能跑。

---

### `compress_images.py` — 图片压缩

**用途**：把 `public/map/image/` 下的所有图片压到 ≤60 KB 的 WebP。

**用法**：
```bash
python tools/compress_images.py
```

**通常不需要手动运行**：`auto_add_map.py` 会自动调用它。

**依赖**：`pip install Pillow`

**特性**：
- 已是 WebP 且 <60 KB 的图片直接跳过（幂等）
- 循环降质：从 quality=90 开始，每次 -5，直到 ≤60 KB
- 降到底仍超标的会保留原文件并提示失败

---

### `compress_fun.py` — 地图压缩

**用途**：把 `public/map/fun/` 下的所有 `.fun` 文件压成独立的 `.7z`。

**用法**：
```bash
python tools/compress_fun.py
```

**参数**：
| 参数 | 说明 |
|---|---|
| `--directory <路径>` | 搜索根目录（默认 `public/map/fun`） |
| `--keep-original` | 保留原 `.fun`（默认压缩后删除） |
| `--no-skip-existing` | 覆盖已存在的 `.7z`（默认跳过） |
| `--verbose` | 输出详细日志 |

**通常不需要手动运行**：`auto_add_map.py` 会自动调用它。

**Termux 支持**：脚本会检测 Termux 环境并尝试自动 `pkg install p7zip`。

---

### `tree.py` — 导出项目结构

**用途**：生成 `tree.txt`，包含完整的目录结构和文件内容，适合给 AI 分析或做代码存档。

**用法**：
```bash
python tools/tree.py
# 按提示输入：
#   Directory path: .    （或直接回车）
#   Include hidden files? n
#   List file contents? y
```

**输出**：项目根目录的 `tree.txt`。

**跳过规则**：可在项目根放一份 `.skip_patterns` 文件自定义额外忽略项。

---

### `rewrite_i18n_email.py` — 一次性重写

**用途**：完整重写 `AnnouncementView.vue` 和所有语言 JSON。**只需运行一次**，之后除非要改邮箱或群链接，否则不用再碰。

**用法**：
```bash
python tools/rewrite_i18n_email.py
```

**改邮箱**：编辑脚本顶部的 `EMAIL` 常量，重跑即可。

---

## 常见问题

### Q：`7z: command not found`

安装 7-Zip：
- Termux：`pkg install p7zip`
- Linux：`sudo apt install p7zip-full`
- macOS：`brew install p7zip`

### Q：`ModuleNotFoundError: No module named 'PIL'`

```bash
pip install Pillow
```

### Q：`ModuleNotFoundError: No module named 'sdsmap'`

```bash
pip install sdsmap
```

Termux 上如果 `pip install` 编译失败，参考 `generate_thumbnails.py` 的文件头注释。

### Q：添加地图后网站没更新

检查两件事：
1. `src/data/map/json/<分类>.json` 里有没有新条目
2. `public/map/image/` 和 `public/map/fun/` 里有没有新文件

都有的话，重启 dev server（`npm run dev`）或重新 build。

### Q：UUID 会不会重复

理论上可能，实际不会。`uuid4` 有 122 位随机位，生成 10 亿个碰撞概率约 1.7×10⁻¹⁸。

### Q：`.webp` 和 `.jpg` 冲突怎么办

`auto_add_map.py` 的 `detect_assets` 会抓文件夹里的**第一个**图片。如果同时有手动截图和自动生成的缩略图，可能抓错。

**建议**：一个文件夹里**只留一张图**，要么全是手动截图，要么全是自动缩略图。

---

## 目录约定

```
<项目根>/
├── tools/                      # 本目录
├── public/
│   └── map/
│       ├── image/<分类>/       # 封面图（WebP）
│       └── fun/<分类>/         # 地图文件（.7z）
└── src/data/map/json/          # 地图元数据

/storage/emulated/0/sds/        # 地图源文件夹（不在项目里）
├── config.json                 # 全局默认配置（可选）
└── <地图名>/
    ├── config.json             # 单图元数据
    ├── <任意名>.fun            # 源地图文件
    └── <任意名>.webp           # 封面图
```

---

## 添加新脚本的建议

如果你要往 `tools/` 里加新脚本，遵循现有风格：

1. **单文件、无外部依赖**（除 Pillow / sdsmap 这类明确需要的）
2. **文件顶部写 docstring**，说明用途和用法
3. **路径用 `Path(__file__).parent.parent`** 定位项目根
4. **不生成备份**，依赖 git 做版本管理
5. **幂等**：重复运行无害
6. **提供 CLI 提示**（`input()` 或 `argparse`）

参考 `rm_map.py` 的结构最简单，`auto_add_map.py` 最完整。