# 环境与配置指南

本 Skill 有三个依赖：`chromium-browser`（浏览器）、`python-runtime`（Python 运行时）、`screenshot-reading`（多模态读图能力）。下面按依赖逐一说明。

## 依赖一：chromium-browser（导出 PDF 用的浏览器）

本 Skill 导出 PDF 依赖本机安装的 Chromium 内核浏览器（Google Chrome 或 Microsoft Edge），通过无头打印模式把 HTML 转成 PDF。无需登录、无需账号、不涉及任何凭据。

### 检查是否已安装

`scripts/check_environment.py` 会自动在常见安装路径和系统 PATH 中查找，直接运行即可。

手动确认：

- **Windows**：查看 `C:\Program Files\Google\Chrome\Application\chrome.exe` 或 `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`
- **macOS**：`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` 或 `/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge`
- **Linux**：执行 `which google-chrome` 或 `which microsoft-edge`

### 未安装时

- Google Chrome 官方主页与下载：https://www.google.com/chrome/
- Microsoft Edge 官方主页与下载（Windows 通常已预装）：https://www.microsoft.com/edge

任装其一即可，无需同时安装。

### 验证可用

```text
python scripts/check_environment.py
```

输出 `ready` 和一个浏览器路径即通过。

### 故障处理

| 现象 | 处理 |
|---|---|
| check 报 needs_setup 但浏览器明明装着 | 用 `--browser` 参数把浏览器可执行文件绝对路径传给 `check_environment.py` 和 `export_pdf.py` |
| 导出报「启动浏览器失败」 | 关闭正在运行的该浏览器全部窗口后重试；仍失败时用 `--browser` 指定另一个浏览器 |
| 导出日志里出现与本任务无关的扩展报错 | 无害，是浏览器加载本机扩展的警告，不影响 PDF 生成，忽略 |
| 生成的 PDF 页边距不对/带页眉页脚 | 确认 `export_pdf.py` 使用了 `--no-pdf-header-footer`，且 HTML 里有 `@page { margin: 0 }` |

## 依赖二：python-runtime（运行脚本）

脚本（`check_environment.py`、`export_pdf.py`）只依赖 Python 标准库，需要 Python 3.10 或更高版本。

- WorkBuddy 宿主环境自带 Python 3.10+ 时**无需任何配置**。
- 独立运行脚本的环境，从官方主页 https://www.python.org/ 下载安装，文档见 https://docs.python.org/3/。
- 验证：`python --version` 显示 3.10 或更高。

## 依赖三：screenshot-reading（多模态读图能力）

边界判断、逐字提取、版式测量、预览对照都依赖宿主模型的读图能力，无需配置：

- 用户在会话中成功发送截图即视为可用。
- 不可用（环境不支持图片输入）时无法开始复刻，如实告知用户。

宿主平台说明文档：https://www.workbuddy.cn/docs/workbuddy/Overview

## 降级方案

浏览器始终无法使用时，手动降级：把 HTML 复刻稿交给用户，让用户用任意浏览器打开后「打印 → 另存为 PDF」，纸张选 A4、边距选无。此方式的页数未经脚本验证，交付时必须标注。
