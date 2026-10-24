# 版式测量与边界判断

## 一、判断截图边界

文档本体的判定信号（按优先级）：

1. **承载内容的矩形区**：文档内容集中在一块背景纯净（多为白色）的矩形内，矩形外是浏览器边框、标签栏、工具栏、桌面壁纸等。只复刻矩形内的部分。
2. **水印处理**：截图平台加在文档页面上的半透明水印（斜向文字、Logo）属于平台元素，不属于文档本体，复刻时直接去掉，不画进复刻稿。
3. **多截图拼接**：几张截图的版式（字号、板块结构、配色）一致且内容前后衔接，视为同一文档的连续部分；否则按独立文档分别复刻。
4. **判断不了就问**：截图被其他窗口遮挡、边界不清晰时，向用户确认文档范围，不自行猜测。

## 二、像素测量法

以文档本体区域的宽度为基准换算比例：

- A4 纸在 CSS 中宽 210mm ≈ 794px（96dpi）。设截图中文档本体宽 W 像素，则 **比例尺 = 794 ÷ W**。
- 截图中测得某段间距为 p 像素 → CSS 像素值 ≈ p × 比例尺。
- 字号估算：中文方块字高度 ≈ 字号。测一行文字的行高像素 h → 字号 ≈ h × 比例尺，就近取整到 0.5px。
- 配色：从截图采样代表性像素（标题色、标签底色、分隔线色），换算十六进制。
- 页数：根据截图总高与单页文档区域高的比例，结合内容截断位置判断原版页数。

## 三、字体替代表

| 截图中的字体特征 | 替代方案（font-family 按顺序） |
|---|---|
| 中文黑体（最常见） | "Microsoft YaHei", "PingFang SC", sans-serif |
| 中文宋体/衬线 | SimSun, "Songti SC", serif |
| 中文楷体 | KaiTi, "Kaiti SC", cursive |
| 英文无衬线 | Arial, Helvetica, sans-serif |
| 英文衬线 | Georgia, "Times New Roman", serif |
| 等宽 | Consolas, "Courier New", monospace |

英文/数字单独成行时，font-family 要把西文字体放中文字体前面，避免数字字形不一致。

## 四、HTML 骨架模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
  @page { size: A4; margin: 0; }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 210mm; min-height: 297mm; background: #fff; }
  body { font-family: "Microsoft YaHei", sans-serif; color: #111;
         font-size: 12.5px; line-height: 1.75; padding: 26px 55px 30px 55px; }
</style>
</head>
<body>
  <!-- 文档内容 -->
</body>
</html>
```

## 五、间距紧凑起步（防溢出）

单页文档极易因间距偏大溢出成两页。写初稿时就按紧凑值起步：

- 页边距：上下 26px、左右 55px 起
- 板块间距（section 之间）：24px 起
- 板块标题下分隔线与内容：12px 起
- 列表项之间：5px 起
- 条目之间：10px 起

导出后若页数仍多于原版，按 SKILL.md「边界与降级」的压缩顺序逐档回调，每次只改一档、重新导出验证。

## 六、常见版式元素的复刻要点

- **居中页眉**：姓名/标题居中加粗，联系信息多行居中，行距 1.9 左右。
- **通栏分隔线**：板块标题下方 `border-bottom` 贯通内容区全宽，1.5px 深色。
- **左右分栏条目**：条目名左对齐加粗、时间右对齐，用 flex + `justify-content: space-between`。
- **小标签**：如「211」类色块标签，行高 1、小字号、圆角 3px、白字底色。
- **项目符号**：用 `::before` 画圆点，缩进对齐。
