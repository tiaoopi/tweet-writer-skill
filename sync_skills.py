# -*- coding: utf-8 -*-
"""同步本地 WorkBuddy 技能到 writer-skill 仓库。

规则：
1. 扫描 C:\\Users\\liaozhifei\\.workbuddy\\skills\\ 下的所有技能目录；
2. 覆盖式复制到 D:\\datas\\AI实验室\\skill\\writer-skill\\ 下（同名目录整体同步）；
3. 若有变化则 git add / commit / push；无变化则跳过。

用法：python sync_skills.py
退出码：0 = 成功（无论有无变化），非 0 = 出错。
"""
import os
import shutil
import subprocess
import sys
import datetime

SRC = r"C:\Users\liaozhifei\.workbuddy\skills"
REPO = r"D:\datas\AI实验室\skill\writer-skill"

# 不参与同步的条目（迁移标记等）
IGNORE = {
    ".disable_to_model_invocation_migration.json",
    ".model_invocation_to_override_migration.json",
}


def log(msg):
    print("[%s] %s" % (datetime.datetime.now().strftime("%H:%M:%S"), msg), flush=True)


def run(args, cwd=REPO):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, shell=False)


def list_skill_dirs(root):
    out = []
    for name in sorted(os.listdir(root)):
        if name in IGNORE or name.startswith("."):
            continue
        p = os.path.join(root, name)
        if os.path.isdir(p) and os.path.exists(os.path.join(p, "SKILL.md")):
            out.append(name)
    return out


def sync_one(name):
    """把单个技能目录覆盖同步到仓库，返回 True 表示有变化。"""
    src = os.path.join(SRC, name)
    dst = os.path.join(REPO, name)
    changed = False

    # 判断是否需要更新：递归比较文件内容与清单
    def snapshot(root):
        snap = {}
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git")]
            for f in filenames:
                if f.startswith("."):
                    continue
                fp = os.path.join(dirpath, f)
                rel = os.path.relpath(fp, root)
                try:
                    with open(fp, "rb") as fh:
                        snap[rel] = fh.read()
                except Exception:
                    snap[rel] = b""
        return snap

    src_snap = snapshot(src)
    dst_snap = snapshot(dst) if os.path.isdir(dst) else {}
    if src_snap != dst_snap:
        changed = True

    if changed:
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", ".git", "*.pyc"))
    return changed


def main():
    if not os.path.isdir(SRC):
        log("ERROR: 源目录不存在: %s" % SRC)
        return 2
    if not os.path.isdir(os.path.join(REPO, ".git")):
        log("ERROR: 仓库目录不是 git 仓库: %s" % REPO)
        return 2

    skills = list_skill_dirs(SRC)
    log("发现 %d 个技能: %s" % (len(skills), ", ".join(skills)))

    changed_skills = []
    for name in skills:
        if sync_one(name):
            changed_skills.append(name)
            log("  已同步(有变化): %s" % name)
        else:
            log("  无变化: %s" % name)

    # 检查仓库整体是否有改动
    st = run(["git", "status", "--porcelain"])
    if not st.stdout.strip():
        log("仓库无任何改动，跳过 commit/push。")
        return 0

    log("检测到改动，开始提交并推送……")
    run(["git", "add", "-A"])
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    names = ", ".join(changed_skills) if changed_skills else "更新技能"
    msg = "sync skills (%s) @ %s" % (names, stamp)
    c = run(["git", "commit", "-m", msg])
    if c.returncode != 0 and "nothing to commit" not in (c.stdout + c.stderr):
        log("commit 输出: %s" % (c.stdout + c.stderr))
    log(c.stdout.strip() or c.stderr.strip())

    p = run(["git", "push", "origin", "main"])
    log("push 输出: %s" % ((p.stdout + p.stderr).strip() or "(空)"))
    if p.returncode != 0:
        log("ERROR: push 失败，请检查网络/凭证。")
        return 1
    log("完成：已推送到 origin/main。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
