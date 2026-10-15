#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_library.py —— 把本地 ~/.workbuddy/skills 下的技能同步到 WorkBuddy 资料库(网盘)。

能力：
  1. 扫描本地技能目录（含 SKILL.md 的文件夹），计算内容指纹(hash)；
  2. 与 library_map.json 中记录的 hash 比对，无变化则跳过；
  3. 有变化的：已有 node_id -> 覆盖更新（链接不变）；新增 -> 在「技能备份」目录下新建，并回写 node_id；
  4. 同步 library_map.json。

依赖资料库内置脚本 drive/upload_drive_file.py（由 WorkBuddy 会话环境提供鉴权）。
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# 本地技能源目录
SKILLS_SRC = Path(os.path.expanduser("~")) / ".workbuddy" / "skills"
# 脚本所在目录即仓库根
REPO = Path(__file__).resolve().parent
MAP_FILE = REPO / "library_map.json"
LOG_FILE = REPO / "library_sync.log"

# 资料库内置脚本目录（可被环境变量覆盖）
LIB_SKILL_DIR = Path(
    os.environ.get(
        "CODEBUDDY_LIBRARY_DIR",
        r"D:\Program Files\wb\WorkBuddy\resources\app.asar.unpacked\resources\plugins\workbuddy-builtin\skills\library",
    )
)
UPLOAD_SCRIPT = LIB_SKILL_DIR / "drive" / "upload_drive_file.py"

# 参与同步的技能（当前 writer 系列）
SYNC_SKILLS = [
    "tweet-writer",
    "tweet-rewriter",
    "image-tweet-writer",
    "wechat-article-to-poster",
]


def log(msg: str) -> None:
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def find_python() -> str:
    """优先用系统 python（含验证过的环境），否则用当前解释器。"""
    for p in (
        r"C:\Users\liaozhifei\AppData\Local\Microsoft\WindowsApps\python.exe",
        sys.executable,
    ):
        if p and os.path.exists(p):
            return p
    return sys.executable


def dir_hash(path: Path) -> str:
    """目录内容指纹：按相对路径排序后逐个文件哈希。"""
    h = hashlib.sha256()
    files = sorted(
        (p for p in path.rglob("*") if p.is_file()),
        key=lambda p: str(p.relative_to(path)).lower(),
    )
    for p in files:
        rel = str(p.relative_to(path)).replace("\\", "/")
        h.update(rel.encode("utf-8"))
        with open(p, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                h.update(chunk)
    return h.hexdigest()[:16]


def make_zip(skill: str, dest_dir: Path) -> Path:
    src = SKILLS_SRC / skill
    out = dest_dir / skill
    archive = shutil.make_archive(str(out), "zip", str(SKILLS_SRC), skill)
    return Path(archive)


def upload(zip_path: Path, file_name: str, node_id: str = "") -> tuple[bool, str, str]:
    """调用资料库上传脚本。返回 (ok, node_id, message)。"""
    py = find_python()
    cmd = [py, str(UPLOAD_SCRIPT), str(zip_path), "--file-name", file_name]
    if node_id:
        cmd += ["--node-id", node_id]
    else:
        cmd += ["--parent-id", MAP.get("parent_id", "")]
    # 关键：剥离代理环境变量。本地代理会导致网盘直传 PUT 失败。
    env = {k: v for k, v in os.environ.items()
           if k.lower() not in ("http_proxy", "https_proxy", "all_proxy")}
    p = subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env
    )
    out = (p.stdout or "") + (p.stderr or "")
    new_id = ""
    for line in out.splitlines():
        if line.startswith("KS_DRIVE_UPLOAD_OK "):
            try:
                payload = json.loads(line[len("KS_DRIVE_UPLOAD_OK "):])
                new_id = payload.get("node_block_id", "")
            except json.JSONDecodeError:
                pass
    ok = p.returncode == 0 and bool(new_id)
    return ok, new_id or node_id, out.strip()


def main() -> int:
    global MAP
    if not UPLOAD_SCRIPT.exists():
        log(f"ERROR: 找不到资料库上传脚本: {UPLOAD_SCRIPT}")
        return 1

    MAP = json.loads(MAP_FILE.read_text(encoding="utf-8")) if MAP_FILE.exists() else {}
    MAP.setdefault("skills", {})
    skills_map = MAP["skills"]

    # 自动发现：本地存在、且在同步白名单内的技能
    targets = [s for s in SYNC_SKILLS if (SKILLS_SRC / s / "SKILL.md").exists()]

    changed = 0
    failed = 0
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for skill in targets:
            src = SKILLS_SRC / skill
            h = dir_hash(src)
            entry = skills_map.get(skill, {})
            if entry.get("hash") == h and entry.get("node_id"):
                log(f"跳过 {skill}（无变化）")
                continue

            zip_path = make_zip(skill, tmp)
            file_name = f"{skill}.zip"
            node_id = entry.get("node_id", "")
            action = "覆盖更新" if node_id else "新建上传"
            ok, new_id, msg = upload(zip_path, file_name, node_id)
            if ok:
                skills_map[skill] = {"node_id": new_id, "hash": h}
                changed += 1
                log(f"{action}成功：{skill} -> {new_id}")
            else:
                failed += 1
                log(f"ERROR: {skill} {action}失败：{msg}")

    MAP_FILE.write_text(
        json.dumps(MAP, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    if failed:
        log(f"完成：成功 {changed} 个，失败 {failed} 个（详见上方错误）。")
        return 1
    if changed:
        log(f"完成：本次同步 {changed} 个技能到资料库。")
    else:
        log("完成：所有技能均无变化，无需同步。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
