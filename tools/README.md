# SDS-Map-Share 工具集使用说明

本目录包含用于管理地图资源的一系列 Python 工具，支持地图的添加（交互式与批量自动）、删除、图片和地图文件压缩以及目录结构导出。

## 环境要求

- Python 3.8+
- 依赖库（仅 `compress_images.py` 需要 Pillow）：
  ```bash
  pip install Pillow
  ```
- 压缩地图文件（.fun -> .7z）需要系统安装 `7z` 命令：
  - Linux (Debian/Ubuntu): `sudo apt install p7zip-full`
  - macOS: `brew install p7zip`
  - Termux (Android): `pkg install p7zip`

所有脚本均需在项目根目录下执行（即 `SDS-Map-Share/` 目录），因为它们会基于当前路径定位 `public/` 和 `src/` 目录。

---

## 工具列表

### 1. `add_map.py` – 交互式单地图上传

**用途**：通过命令行交互输入地图信息，手动指定图片和 `.fun` 文件路径，上传单张地图。

**使用方法**：
```bash
python tools/add_map.py
```

**交互流程**：
1. 输入地图名称、描述
2. 输入图片路径（绝对路径或相对路径）
3. 输入地图文件路径（`.fun` 文件）
4. 选择分类（输入数字，多个用逗号分隔：1-对战，2-观赏，3-机关，4-生存）
5. 输入作者名和可选的作者主页链接
6. 确认信息后上传

**文件处理**：
- 图片复制到 `public/map/image/{分类}/` 并重命名为 `{标题}.扩展名`
- 地图文件复制到 `public/map/fun/{分类}/` 并重命名为 `{标题}.fun`
- 自动调用压缩脚本（图片 → webp，地图 → .7z）
- 更新 `src/data/map/json/{分类}.json`，自动分配自增 ID

---

### 2. `auto_add_map.py` – 批量自动扫描上传

**用途**：扫描指定目录（默认 `/storage/emulated/0/sds/`）下的所有子文件夹，自动读取每个文件夹内的 `config.json` 并自动检测图片和 `.fun` 文件，批量一键上传。

**使用方法**：
```bash
python tools/auto_add_map.py
```

**目录结构要求**：
```
/storage/emulated/0/sds/
├── config.json                 # （可选）全局配置
├── 地图A/
│   ├── config.json            # 地图元数据
│   ├── cover.jpg              # 任意图片（自动检测）
│   └── map.fun                # 任意 .fun 文件（自动检测）
└── 地图B/
    ├── config.json
    ├── screenshot.png
    └── level.fun
```

**地图 `config.json` 格式**：
```json
{
  "title": "地图名称",
  "description": "地图描述",
  "category": ["对战", "观赏"],
  "author": "作者名",
  "authorUrl": "https://..."   // 可选
}
```
- `category` 为数组，可选值：`对战`、`观赏`、`机关`、`生存`
- 封面图和 `.fun` 文件**无需在配置中指定**，脚本自动查找文件夹内第一个图片文件（支持 `.jpg/.jpeg/.png/.gif/.bmp/.webp`）和第一个 `.fun` 文件。

**全局配置（可选）** `/storage/emulated/0/sds/config.json`：
```json
{
  "defaultAuthor": "匿名",
  "defaultCategory": ["生存"],
  "autoCompress": true,
  "skipInvalid": true
}
```
- `defaultAuthor`：当地图配置未提供作者时使用的默认值
- `defaultCategory`：当分类无效或为空时使用的默认分类
- `autoCompress`：是否自动调用压缩脚本
- `skipInvalid`：遇到无效地图时是否跳过继续处理

**处理流程**：
1. 扫描 `/storage/emulated/0/sds/` 下所有非隐藏子文件夹
2. 对每个文件夹读取 `config.json`，验证必填字段
3. 自动检测图片和 `.fun` 文件
4. 将文件重命名为 `标题.扩展名` 并复制到 `public/map/` 对应分类目录
5. 调用压缩脚本
6. 更新 JSON 数据文件，分配自增 ID

---

### 3. `compress_images.py` – 图片压缩为 WebP

**用途**：遍历 `public/map/image/` 下所有图片（包括子目录），将其转换为 WebP 格式并压缩至 60KB 以下。原图会在成功转换后被删除，已为 WebP 且小于 60KB 的图片会被跳过。

**使用方法**：
```bash
python tools/compress_images.py
```

**压缩策略**：
- 从质量 90 开始逐步降低至 5，步长 5，直到文件大小 ≤ 60KB
- 若最低质量仍大于 60KB，保留原始文件（不删除）
- 依赖 Pillow 库，请先安装

---

### 4. `compress_fun.py` – 地图文件压缩为 7z

**用途**：遍历 `public/map/fun/` 下所有 `.fun` 文件，使用系统 `7z` 命令压缩为 `.7z` 归档，压缩完成后**默认删除原始 `.fun` 文件**（可加 `--keep-original` 保留）。

**使用方法**：
```bash
python tools/compress_fun.py
```

**选项**：
- `--directory DIR`：指定扫描目录（默认 `public/map/fun`）
- `--keep-original`：保留原始 `.fun` 文件
- `--no-skip-existing`：覆盖已存在的 `.7z` 文件（默认跳过）
- `--verbose`：输出详细日志

**示例**：
```bash
# 压缩所有 .fun，并保留原文件
python tools/compress_fun.py --keep-original

# 指定目录并强制覆盖已有 7z
python tools/compress_fun.py --directory public/map/fun/battle --no-skip-existing
```

---

### 5. `rm_map.py` – 删除地图条目（含文件清理）

**用途**：根据地图 ID 删除地图条目，同时删除对应的图片和 `.7z`/`.fun` 文件（使用 Shell `rm -f` 命令）。

**使用方法**：
```bash
python tools/rm_map.py
```

**交互流程**：
1. 输入要删除的地图 ID
2. 显示地图信息（标题、分类、作者）
3. 确认删除后，自动删除 `image` 和 `file` 字段指向的资源文件
4. 从对应的 JSON 文件中移除该条目

---

### 6. `tree.py` – 导出目录树与文件内容

**用途**：生成 `tree.txt` 文件，包含目录结构和可选的文件内容，便于分享项目结构或调试。

**使用方法**：
```bash
python tools/tree.py
```

**交互选项**：
- 输入要导出的目录（直接回车表示当前目录）
- 是否包含隐藏文件（y/N）
- 是否列出文件内容（y/N）

**输出文件**：`tree.txt`（位于项目根目录）

---

## 改造说明（从手动到自动化）

- 原有 `add_map.py` 为交互式单次上传，适合少量、精细控制。
- 新增 `auto_add_map.py` 实现了完全自动化：用户只需将地图素材按规范放入 `/storage/emulated/0/sds/` 下的子文件夹，并编写简洁的 `config.json`，运行一次即可批量处理所有地图。该脚本自动检测图片和 `.fun` 文件，省去手动输入路径和重复操作的麻烦。
- 压缩脚本独立出来，可在上传后自动调用，也可单独运行以重新压缩所有资源。
- 删除工具 `rm_map.py` 整合了 JSON 修改和文件删除，确保数据一致性。

整个工具链的设计遵循“配置驱动、自动检测、一键完成”的理念，大幅提高了地图管理效率。

---

## 常见问题

**Q：`auto_add_map.py` 扫描不到我的文件夹？**  
A：请确认扫描根目录是否为 `/storage/emulated/0/sds/`，如果你的手机存储挂载点不同，可修改脚本中的 `SCAN_ROOT` 变量。

**Q：压缩图片时提示 `ModuleNotFoundError: No module named 'PIL'`？**  
A：执行 `pip install Pillow` 安装依赖。

**Q：压缩地图文件时提示 `7z command not found`？**  
A：安装 p7zip（参考环境要求章节）。在 Termux 中可使用 `pkg install p7zip`。

**Q：`add_map.py` 和 `auto_add_map.py` 分配的 ID 会重复吗？**  
A：不会。所有工具共用 `get_next_id()` 函数，扫描所有 JSON 文件获取最大 ID 并加 1，保证全局唯一且永不回收。

**Q：我想修改默认分类或作者，应该怎么做？**  
A：在 `auto_add_map.py` 中调整 `defaults` 字典内的值，或使用全局 `config.json` 覆盖。

---

## 维护者

如有问题或建议，请联系项目维护者。