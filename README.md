# writer-skill · 中文内容创作技能集

> 一组适用于 **WorkBuddy**（及兼容 Claude Skills 体系）的中文写作/贴图技能包。把想要的技能文件夹复制到 `~/.workbuddy/skills/` 即可用一句话触发。

## 📦 技能一览

| 技能 | 一句话介绍 | 触发示例 |
|---|---|---|
| [image-tweet-writer](./image-tweet-writer/) | 读图写推文技能——**必须先读取用户提供的图片**（截图、海报、图表、聊天记录、文章截图等），看懂图里的文字与画面，再据此写出一条 ≤100 字的中文推特推文：开头用诱惑性提问勾人、语气接地气像唠嗑、排版有换行、带推特大众常用表情。当用户发来图片并说"读图写推文 / 看这张图写条推 / 照这张图发推 / 这图能写... | "读图写推文 / 看这张图写条推" |
| [reverse-engineer-anything](./reverse-engineer-anything/) | Reverse engineer native, managed, Electron/JavaScript, packaged, firmware, and browser targets with REA. Use shipped-artifact or requested runtime evidence t... |  |
| [tweet-rewriter](./tweet-rewriter/) | 仿写推文技能——把已有的一篇文章、一条推文或一段内容，**先完整读取原文**，再按原意用自己的话重写成一条新推文：模仿原文的换行节奏、说话口气和抓眼球的写法，与原文文字重叠不超过 30%（不照抄原句），并带上推特平台大众常用的表情。当用户要求"仿写推文 / 照这个风格写推 / 模仿这条推 / 改写成推文 / 仿一... | "仿写推文 / 照这个风格写推 / 模仿这条" |
| [tweet-writer](./tweet-writer/) | 把一篇文章、一段素材或一个话题写成一条中文推特推文（≤100 字）。当用户要求"写推文/写推特/发一条推/tweet/把这篇写成推文"，并希望内容接地气、口语化、开头有勾人的诱惑性提问、有换行排版、带推特常用表情时使用。只要话题能跟钱挂上钩就优先多写"钱/搞钱/亏钱"等利益话题，尽量少讨论政治与色情。适用于内容总... | "写推文 / 把这篇写成推文 / 发一条推" |
| [wechat-article-to-poster](./wechat-article-to-poster/) | 读公众号文章 → 生成微信贴图 + 短文案的技能。当用户给出一条微信公众号文章链接（mp.weixin.qq.com/...），要求"读取公众号文章""把这篇公众号做成贴图""公众号转贴图""生成微信贴图""文章转图文卡片"时使用。**必须先抓取并读完整篇文章正文**，再提炼核心，产出**≤3 张**「深色科技风... | "读取公众号文章 / 把这篇公众号做成贴图" |

## 🚀 安装

1. clone 本仓库：
   ```bash
   git clone https://github.com/tiaoopi/writer-skill.git
   ```
2. 把想要的 **技能文件夹** 整个复制到 WorkBuddy 的技能目录：
   - Windows：`C:\Users\<用户名>\.workbuddy\skills\`
   - macOS / Linux：`~/.workbuddy/skills/`
3. 刷新或重启 WorkBuddy，技能即生效。

> 目录应为 `...\.workbuddy\skills\<技能名>\SKILL.md`（`SKILL.md` 必须在技能文件夹顶层）。

## 🔄 同步与维护

技能会被同步到**两个地方**，都由 WorkBuddy 定时任务（每天 06:00）自动执行：

### 1. 本 GitHub 仓库（版本管理）
- `sync_skills.py`：把本地 `.workbuddy/skills/` 下的技能同步到本仓库并 push，**并自动刷新上面的「技能一览」表**——新增技能会被自动收录进 README，无需手动改。
- 手动运行：`python sync_skills.py`

### 2. WorkBuddy 资料库（手机端可取用备份）
- `sync_library.py`：把每个技能打包成 zip 备份到资料库「**技能备份**」文件夹。
- 已有技能 → **覆盖更新**（链接不变、不产生重复）；新增技能 → 自动新建并记录节点 ID。
- 节点映射与内容指纹记录在 `library_map.json`，**无变化自动跳过**。
- 手动运行：`python sync_library.py`
- 手机端：在 WorkBuddy「资料库 → 技能备份」中直接下载对应 zip。

> 注意：资料库里的 zip 是**备份/取用**用途，把它下载到手机后，仍需放入设备的 `.workbuddy/skills/` 目录才是可触发的技能。

## 🔒 安全性

- 所有技能均为 **纯 Markdown 规则包**，不含任何脚本 / 可执行代码
- 不联网、不读取文件、不访问凭证，仅提供写作规则与范例
- （仓库根目录的 `sync_*.py` 为同步工具脚本，不属于技能本体）

## 📄 License

MIT（可自由使用、修改、分发，请保留出处）。
