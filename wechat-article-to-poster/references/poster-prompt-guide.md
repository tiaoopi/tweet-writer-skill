# 贴图 SVG 规范：模板、配色、转换、正反例

## 一、总体要求

| 项目 | 要求 |
|---|---|
| 张数 | **≤3 张**（能 1 张讲清就 1 张） |
| 尺寸 | 1080 × 1920（竖版手机比例） |
| 风格 | 深色科技风（深蓝渐变底 + 青/紫强调） |
| 每行字数 | ≤22 字 |
| 整图正文 | 合计 ≤180 字 |
| 交付 | PNG + **SVG 代码原文**都要给用户 |

## 二、标准 SVG 模板（1 张承载全部要点）

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0b1020"/>
      <stop offset="100%" stop-color="#141f3d"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#22d3ee"/>
      <stop offset="100%" stop-color="#a78bfa"/>
    </linearGradient>
  </defs>

  <rect width="1080" height="1920" fill="url(#bg)"/>
  <circle cx="930" cy="150" r="220" fill="#22d3ee" opacity="0.08"/>
  <circle cx="110" cy="1790" r="260" fill="#a78bfa" opacity="0.08"/>

  <!-- 大标题：两行，白 + 浅蓝，第二行是"钩子" -->
  <text x="540" y="130" text-anchor="middle" font-family="'PingFang SC','Microsoft YaHei',sans-serif"
        font-size="52" font-weight="800" fill="#ffffff">第一行标题</text>
  <text x="540" y="195" text-anchor="middle" font-family="'PingFang SC','Microsoft YaHei',sans-serif"
        font-size="52" font-weight="800" fill="#7dd3fc">第二行标题（钩子）</text>
  <rect x="360" y="230" width="360" height="4" rx="2" fill="url(#accent)" opacity="0.9"/>
  <text x="540" y="285" text-anchor="middle" font-family="'PingFang SC','Microsoft YaHei',sans-serif"
        font-size="26" fill="#a9b7d0">副标题或吐槽一句 😂</text>

  <!-- 内容卡（按需复制 2~4 个，每个 y 递增 300 左右） -->
  <rect x="60" y="330" width="960" height="270" rx="24" fill="#121a33" stroke="#26345c" stroke-width="2"/>
  <text x="100" y="390" font-family="'PingFang SC','Microsoft YaHei',sans-serif"
        font-size="30" font-weight="800" fill="#7dd3fc">卡片小标题</text>
  <text x="100" y="440" font-family="'PingFang SC','Microsoft YaHei',sans-serif"
        font-size="23" fill="#c7d2e8">要点一行，≤22 字</text>
  <text x="100" y="485" font-family="'PingFang SC','Microsoft YaHei',sans-serif"
        font-size="23" fill="#c7d2e8">要点一行，≤22 字</text>
  <text x="100" y="530" font-family="'PingFang SC','Microsoft YaHei',sans-serif"
        font-size="23" fill="#c7d2e8">要点一行，≤22 字</text>

  <!-- 金句/总结卡：换底色 + 青色描边，视觉突出 -->
  <rect x="60" y="1200" width="960" height="240" rx="24" fill="#0f2b3a" stroke="#22d3ee" stroke-width="2"/>
  <text x="100" y="1260" font-family="'PingFang SC','Microsoft YaHei',sans-serif"
        font-size="30" font-weight="800" fill="#7dd3fc">一句话总结</text>
  <text x="100" y="1310" font-family="'PingFang SC','Microsoft YaHei',sans-serif"
        font-size="24" fill="#c7d2e8">总结第一行</text>
  <text x="100" y="1355" font-family="'PingFang SC','Microsoft YaHei',sans-serif"
        font-size="24" fill="#7dd3fc">点睛一句 🌟</text>
</svg>
```

## 三、配色速查

| 用途 | 色值 |
|---|---|
| 背景渐变 | `#0b1020 → #141f3d`（对角线） |
| 内容卡底 / 描边 | `#121a33` / `#26345c` |
| 金句卡底 / 描边 | `#0f2b3a` / `#22d3ee` |
| 大标题（两行） | `#ffffff` / `#7dd3fc` |
| 卡内小标题 | `#7dd3fc`（加粗） |
| 正文 | `#c7d2e8` |
| 辅助/吐槽行 | `#a9b7d0` |
| 强调渐变条 | `#22d3ee → #a78bfa` |
| 光晕圆 | 青/紫各一，`opacity 0.08`，放对角 |

## 四、排版细则

- 卡片高度按行数算：高度 ≈ 行数 × 45 + 顶部标题区 90 + 上下内边距。
- 相邻卡片间距 24~30px；文字左缘统一 `x=100`（卡片 x=60 时）。
- emoji 直接写在 `<text>` 末尾（🤔 😂 💸 🌟 👇 …），1~3 个，别堆。
- 大标题两行分色是"钩子"的一部分：第一行陈述、第二行亮反差。

## 五、SVG → PNG 转换

```python
import resvg_py
png = resvg_py.svg_to_bytes(svg_string=svg_code)
open("poster-01.png", "wb").write(bytes(png))
```

- 已验证：中文（微软雅黑）+ 彩色 emoji 渲染正常（系统 python 已装 `resvg-py`）。
- 转换后逐张检查：错字、文字溢出卡片、密度过满 → 改 SVG 重转。

## 六、正反例

**❌ 反例**：
- 一张图塞 8 个要点、每行 30+ 字 → 眼睛疼；
- 生成 5~7 张图组 → 太多，没人翻完；
- 只给 PNG 不给 SVG → 用户没法改字复用。

**✅ 正例**：
- 1 张 1080×1920 深色卡：双色大标题 + 3 个内容卡（每卡 2~3 行短句）+ 1 个青边金句卡；
- 交付 = PNG + 短文案（≤200 字）+ **SVG 代码原文**。
