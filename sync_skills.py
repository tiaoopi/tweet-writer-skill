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

# 各技能在 README「技能一览」表中的触发示例（新技能若不在此表，留空即可，介绍仍会自动收录）
TRIGGERS = {
    "tweet-writer": '"写推文 / 把这篇写成推文 / 发一条推"',
    "tweet-rewriter": '"仿写推文 / 照这个风格写推 / 模仿这条"',
    "image-tweet-writer": '"读图写推文 / 看这张图写条推"',
    "wechat-article-to-poster": '"读取公众号文章 / 把这篇公众号做成贴图"',
}


def log(msg):
    print("[%s] %s" % (datetime.datetime.now().strftime("%H:%M:%S"), msg), flush=True)


def run(args, cwd=REPO):
    env = os.environ.copy()
    # 显式指定本地代理与凭证 helper，避免沙箱/非交互环境下 SSL 握手失败或读不到凭证
    env.setdefault("HTTP_PROXY", "http://127.0.0.1:7890")
    env.setdefault("HTTPS_PROXY", "http://127.0.0.1:7890")
    env.setdefault("http_proxy", "http://127.0.0.1:7890")
    env.setdefault("https_proxy", "http://127.0.0.1:7890")
    env.pop("GIT_TERMINAL_PROMPT", None)
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, shell=False, env=env)


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


def parse_frontmatter(path):
    """从 SKILL.md 提取 frontmatter 中的 name / description（单行）。"""
    name, desc = None, None
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read(8192)
    except Exception:
        return name, desc
    if text.startswith("---"):
        lines = text.split("\n")
        in_fm = False
        for ln in lines:
            s = ln.strip()
            if s == "---":
                if in_fm:
                    break
                in_fm = True
                continue
            if in_fm and s.startswith("name:"):
                name = s[len("name:"):].strip()
            elif in_fm and s.startswith("description:"):
                desc = s[len("description:"):].strip()
                # description 可能很长且含 markdown，截断到合理长度
                if len(desc) > 160:
                    desc = desc[:157].rstrip() + "..."
    return name, desc


def update_readme(skills):
    """根据技能 frontmatter 自动刷新 README 的「技能一览」表，返回 True 表示有改动。"""
    readme = os.path.join(REPO, "README.md")
    if not os.path.exists(readme):
        log("WARN: README.md 不存在，跳过索引更新")
        return False
    with open(readme, "r", encoding="utf-8") as f:
        content = f.read()

    rows = []
    for name in skills:
        fp = os.path.join(SRC, name, "SKILL.md")
        _, desc = parse_frontmatter(fp)
        if not desc:
            desc = "（见 SKILL.md）"
        desc = desc.replace("|", "\\|").replace("\n", " ")
        trig = TRIGGERS.get(name, "")
        rows.append("| [%s](./%s/) | %s | %s |" % (name, name, desc, trig))
    table = (
        "## 📦 技能一览\n\n"
        "| 技能 | 一句话介绍 | 触发示例 |\n"
        "|---|---|---|\n"
        + "\n".join(rows) + "\n"
    )

    start = content.find("## 📦 技能一览")
    if start == -1:
        log("WARN: README 中未找到「技能一览」小节，跳过索引更新")
        return False
    nxt = content.find("\n## ", start + 1)
    end = nxt if nxt != -1 else len(content)
    new_content = content[:start] + table + "\n" + content[end:].lstrip("\n")
    if new_content != content:
        with open(readme, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_content)
        return True
    return False


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

    # 刷新 README 技能索引（每次同步都根据本地技能列表重建）
    if update_readme(skills):
        log("README 技能索引已更新。")

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

    # 推送：显式指定代理与凭证 helper，兼容 WorkBuddy 会话内的凭证代理
    PUSH = ["git", "-c", "http.proxy=http://127.0.0.1:7890",
            "-c", "credential.helper=helper-selector", "push", "origin", "main"]
    p = run(PUSH)
    log("push 输出: %s" % ((p.stdout + p.stderr).strip() or "(空)"))
    if p.returncode != 0:
        log("push 失败，尝试 rebase 后重推……")
        run(["git", "-c", "http.proxy=http://127.0.0.1:7890", "pull", "--rebase", "origin", "main"])
        p = run(PUSH)
        log("二次 push 输出: %s" % ((p.stdout + p.stderr).strip() or "(空)"))
        if p.returncode != 0:
            log("ERROR: push 失败，请检查网络/凭证。")
            return 1
    log("完成：已推送到 origin/main。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
