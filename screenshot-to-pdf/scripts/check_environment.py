#!/usr/bin/env python3
"""只读环境检查：查找可用的 Chromium 内核浏览器，输出状态与缺失项。

用法：
    python check_environment.py [--browser <可执行文件绝对路径>]

输出（stdout，UTF-8）：
    status: ready | partial | needs_setup
    browser: <找到的可执行文件路径，未找到则为空>
    issues: <缺失项说明列表>

退出码：0 = ready/partial，2 = needs_setup。不修改任何配置、不访问网络。
"""

import argparse
import json
import os
import sys
from pathlib import Path

MIN_PYTHON = (3, 10)

CANDIDATES = {
    "win32": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ],
    "darwin": [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ],
    "linux": [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/microsoft-edge",
        "/usr/bin/microsoft-edge-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ],
}

PATH_NAMES = ["chrome.exe", "msedge.exe", "google-chrome", "microsoft-edge", "chromium"]


def find_browser(explicit: str | None) -> str | None:
    if explicit:
        p = Path(explicit)
        return str(p) if p.is_file() else None
    for c in CANDIDATES.get(sys.platform, []):
        if Path(c).is_file():
            return c
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    for name in PATH_NAMES:
        for d in path_dirs:
            p = Path(d) / name
            if p.is_file():
                return str(p)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="检查 PDF 导出所需浏览器环境（只读）")
    parser.add_argument("--browser", help="浏览器可执行文件绝对路径", default=None)
    args = parser.parse_args()

    issues = []
    if sys.version_info < MIN_PYTHON:
        issues.append(
            f"Python 版本过低：需要 {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+，当前 {sys.version.split()[0]}"
        )

    browser = find_browser(args.browser)
    if browser is None:
        if args.browser:
            issues.append(f"--browser 指定的路径不可执行：{args.browser}")
        else:
            issues.append("未找到 Chrome/Edge/Chromium 浏览器，请安装其一或用 --browser 指定路径")

    status = "needs_setup" if browser is None or issues else "ready"
    print(json.dumps({"status": status, "browser": browser, "issues": issues}, ensure_ascii=False))
    return 0 if status != "needs_setup" else 2


if __name__ == "__main__":
    sys.exit(main())
