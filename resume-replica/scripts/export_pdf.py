#!/usr/bin/env python3
"""把 HTML 复刻稿用 Chromium 无头模式导出为 PDF，并做最小结果验证。

用法：
    python export_pdf.py <HTML绝对路径> <PDF输出绝对路径> [--browser <可执行文件路径>]

行为：
    1. 校验输入 HTML 存在、输出目录可写；
    2. 查找浏览器（优先 --browser，其次常见路径与 PATH）；
    3. 以无头模式 --print-to-pdf 导出，禁用页眉页脚；
    4. 验证输出文件存在、非空，并扫描 PDF 结构统计页数；
    5. stdout 输出 JSON 结果。

输出 JSON 字段：
    ok          是否成功
    browser     使用的浏览器路径
    pdf         输出 PDF 绝对路径
    bytes       文件大小
    pages       从 PDF 对象结构扫描出的页数（启发式，供页数自检参考）
    error       失败原因

退出码：0 = 成功；2 = 浏览器缺失；3 = 转换失败；4 = 输出校验失败。
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

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
    for name in PATH_NAMES:
        for d in os.environ.get("PATH", "").split(os.pathsep):
            p = Path(d) / name
            if p.is_file():
                return str(p)
    return None


def count_pages(pdf_path: Path) -> int:
    """启发式统计页数：统计 /Type /Page（排除 /Pages）对象个数。"""
    data = pdf_path.read_bytes()
    return len(re.findall(rb"/Type\s*/Page(?![s/])", data))


def main() -> int:
    parser = argparse.ArgumentParser(description="HTML 导出 PDF（Chromium 无头打印）")
    parser.add_argument("html", help="HTML 复刻稿绝对路径")
    parser.add_argument("pdf", help="PDF 输出绝对路径")
    parser.add_argument("--browser", default=None, help="浏览器可执行文件绝对路径")
    args = parser.parse_args()

    html_path = Path(args.html).resolve()
    pdf_path = Path(args.pdf).resolve()

    if not html_path.is_file():
        print(json.dumps({"ok": False, "error": f"HTML 不存在：{html_path}"}, ensure_ascii=False))
        return 3
    out_dir = pdf_path.parent
    if not out_dir.is_dir():
        print(json.dumps({"ok": False, "error": f"输出目录不存在：{out_dir}"}, ensure_ascii=False))
        return 3

    browser = find_browser(args.browser)
    if browser is None:
        print(json.dumps(
            {"ok": False, "error": "未找到 Chrome/Edge/Chromium，请先安装或用 --browser 指定路径"},
            ensure_ascii=False,
        ))
        return 2

    url = html_path.as_uri()
    with tempfile.TemporaryDirectory(prefix="replica_pdf_") as tmp:
        cmd = [
            browser,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--user-data-dir={tmp}",
            f"--print-to-pdf={pdf_path}",
            url,
        ]
        try:
            proc = subprocess.run(
                cmd, capture_output=True, timeout=120,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except subprocess.TimeoutExpired:
            print(json.dumps({"ok": False, "browser": browser, "error": "浏览器导出超时（120s）"}, ensure_ascii=False))
            return 3
        except OSError as exc:
            print(json.dumps({"ok": False, "browser": browser, "error": f"启动浏览器失败：{exc}"}, ensure_ascii=False))
            return 3

    if not pdf_path.is_file():
        stderr_tail = (proc.stderr or b"").decode("utf-8", "replace")[-500:]
        print(json.dumps(
            {"ok": False, "browser": browser, "error": f"未生成 PDF。浏览器日志尾部：{stderr_tail}"},
            ensure_ascii=False,
        ))
        return 3

    size = pdf_path.stat().st_size
    if size < 1000:
        print(json.dumps(
            {"ok": False, "browser": browser, "bytes": size, "error": "PDF 文件过小，内容可能为空"},
            ensure_ascii=False,
        ))
        return 4

    try:
        pages = count_pages(pdf_path)
    except Exception:
        pages = None

    print(json.dumps(
        {"ok": True, "browser": browser, "pdf": str(pdf_path), "bytes": size, "pages": pages},
        ensure_ascii=False,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
