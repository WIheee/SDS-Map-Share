#!/usr/bin/env python3
import os, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import fnmatch

MAX_SIZE = 1024 * 1024
DEFAULT_SKIP_PATTERNS = [
    "LICENSE",
    "README.md",
    ".git/",
    "node_modules/",
    "pack_icon.png",
    "*.pyc",
    "*.log",
    "*.svg",
    "*.png",
    "pnpm-lock.yaml",
    "package-lock.json",
    "tree.txt" ,
    "t",
    "a"
]
# 加载外部自定义
SKIP_PATTERNS_FILE = ".skip_patterns"
if Path(SKIP_PATTERNS_FILE).exists():
    with open(SKIP_PATTERNS_FILE, "r", encoding="utf-8") as f:
        extra = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    DEFAULT_SKIP_PATTERNS.extend(extra)

def should_skip(path):
    path_obj = Path(path)
    parts = path_obj.parts
    name = path_obj.name
    for pat in DEFAULT_SKIP_PATTERNS:
        pat = pat.strip()
        if not pat:
            continue
        if pat.endswith('/'):  # 目录模式
            dir_name = pat[:-1]
            if dir_name in parts:
                return True
        else:
            if fnmatch.fnmatch(name, pat):
                return True
    return False

def tree(dir_path, prefix="", hidden=False, visited=None):
    if visited is None:
        visited = set()
    real_path = Path(dir_path).resolve()
    if real_path in visited:
        return [f"{prefix}[循环链接]"]
    visited.add(real_path)
    lines = []
    try:
        entries = list(os.scandir(real_path))
    except PermissionError:
        return [f"{prefix}[权限不足]"]
    # 过滤隐藏 && 过滤跳过项（完全隐藏）
    entries = [e for e in entries if (hidden or not e.name.startswith('.')) and not should_skip(e.path)]
    entries.sort(key=lambda e: (not e.is_dir(), e.name.lower()))
    for i, e in enumerate(entries):
        is_last = i == len(entries) - 1
        lines.append(f"{prefix}{'└── ' if is_last else '├── '}{e.name}")
        if e.is_dir():
            lines.extend(tree(e.path, prefix + ("    " if is_last else "│   "), hidden, visited))
    return lines

def read_file(p):
    try:
        size = os.path.getsize(p)
        if size > MAX_SIZE:
            return f"[过大 {size} 字节]"
        with open(p, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        return "[编码错误]"
    except Exception as e:
        return f"[错误: {e}]"

def collect_files(root, hidden):
    root_path = Path(root).resolve()
    tasks = []
    for dp, dn, fn in os.walk(root_path, topdown=True):
        dp_path = Path(dp)
        if should_skip(dp_path):   # 整个目录跳过
            dn[:] = []
            continue
        if not hidden:
            dn[:] = [d for d in dn if not d.startswith('.')]
            fn = [f for f in fn if not f.startswith('.')]
        for f in fn:
            fp = Path(dp) / f
            if not should_skip(fp):
                tasks.append(fp)
    return tasks

def main():
    print("=== 目录树 + 内容导出（完全隐藏跳过项） ===")
    d = input("目录路径（回车=当前）: ").strip() or os.getcwd()
    if not Path(d).is_dir():
        sys.exit("路径无效")
    hidden = input("包含隐藏文件？(y/N): ").strip().lower() == 'y'
    embed = input("列出文件内容？(y/N): ").strip().lower() == 'y'

    root = Path(d).resolve()
    tree_lines = [root.name]
    tree_lines.extend(tree(root, hidden=hidden))

    contents = []
    if embed:
        print("收集文件...")
        tasks = collect_files(root, hidden)
        print(f"待读取文件数: {len(tasks)}")
        if tasks:
            with ThreadPoolExecutor() as ex:
                results = list(ex.map(read_file, tasks))
            for p, c in zip(tasks, results):
                contents.append((str(p.relative_to(root)), c))
            print(f"成功读取 {len(contents)} 个文件")

    out_path = Path.cwd() / "tree.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("项目目录及文件内容（跳过项已完全隐藏）\n")
        f.write("\n".join(tree_lines))
        if contents:
            f.write("\n")
            for rp, c in contents:
                f.write(f"{rp}{{\n{c.rstrip()}\n}}")
    print(f"保存至 {out_path}")

if __name__ == "__main__":
    main()