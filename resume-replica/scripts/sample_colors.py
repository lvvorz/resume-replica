#!/usr/bin/env python3
"""sample_colors.py — 截图颜色程序化采样（完整档文档强制步骤）

用法:
    python sample_colors.py <截图1> [截图2 ...]

输出每张截图的分类颜色报告（色频 top3 + 通栏长条检测），
供复刻时填色使用。禁止肉眼估色替代本脚本。

退出码: 0=正常, 2=缺少 Pillow 或输入文件不存在
"""

import sys
from collections import Counter
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: 未安装 Pillow，无法程序化采样。")
    print("降级：按 references/layout-measurement.md 「手动采样」小节执行，")
    print("并用任意图像查看器的取色器核对至少 3 个代表色。")
    sys.exit(2)

QUANT = 16          # 颜色量化步长（足够区分色相，抗 JPEG 噪点）
LINE_MIN_FRAC = 0.5  # 通栏长条的最小宽度占比


def classify(px):
    """把像素归入颜色类别；返回 (类别名, 量化色) 或 None。"""
    r, g, b = px
    avg = (r + g + b) / 3
    q = tuple(v // QUANT * QUANT for v in px)
    # 藏青/深蓝装饰块、技能条（深且偏蓝）
    if avg < 100 and b - r > 35 and b > 70:
        return ("深蓝装饰/技能条", q)
    # 蓝色标签底（含灰蓝，如 #5a6e82）
    if b - r > 25 and b > 120 and r < 180 and 90 <= avg:
        return ("蓝色标签", q)
    # 暖色/橙色标签
    if r - b > 35 and r > 170 and g > 70:
        return ("暖色标签", q)
    # 深色文字
    if avg < 120:
        return ("深色文字", q)
    return None


def long_lines(img, w, h):
    """检测通栏长条（分隔线、色带）：行内连续近似同色且宽度过半。"""
    px = img.load()
    found = []
    for y in range(h):
        run_start = None
        run_color = None
        x = 0
        while x < w:
            p = px[x, y]
            nonwhite = not (p[0] > 240 and p[1] > 240 and p[2] > 240)
            if nonwhite:
                if run_start is None:
                    run_start = x
                    run_color = p
                elif sum(abs(p[i] - run_color[i]) for i in range(3)) > 30:
                    if x - run_start >= w * LINE_MIN_FRAC:
                        found.append((y, run_start, x, run_color))
                    run_start = x
                    run_color = p
            else:
                if run_start is not None and x - run_start >= w * LINE_MIN_FRAC:
                    found.append((y, run_start, x, run_color))
                run_start = None
            x += 1
        if run_start is not None and w - run_start >= w * LINE_MIN_FRAC:
            found.append((y, run_start, w, run_color))
    # 合并相邻行（同一根线只报一次）
    merged = []
    for y, x0, x1, c in found:
        if sum(c) / 3 > 230:
            continue  # 近白背景行不算长条
        qc = tuple(v // QUANT * QUANT for v in c)
        if merged and y - merged[-1][0] <= 2 and merged[-1][3] == qc:
            merged[-1][0] = y
        else:
            merged.append([y, x0, x1, qc])
    return merged


def report(path):
    img = Image.open(path).convert("RGB")
    w, h = img.size
    small = img.resize((min(w, 800), max(1, round(h * min(w, 800) / w))))
    sw, sh = small.size
    px = small.load()

    cats = {}
    for y in range(sh):
        for x in range(sw):
            r = classify(px[x, y])
            if r:
                cats.setdefault(r[0], Counter())[r[1]] += 1

    print(f"\n## {Path(path).name} ({w}x{h})")
    for name in ("深蓝装饰/技能条", "蓝色标签", "暖色标签", "深色文字"):
        if name in cats:
            top = " ".join(
                "#%02x%02x%02x(n=%d)" % (c[0], c[1], c[2], n)
                for c, n in cats[name].most_common(3)
            )
            print(f"- {name}: {top}")
    lines = long_lines(img, w, h)
    if lines:
        print("- 通栏长条(>50%宽，分隔线/色带):")
        for y, x0, x1, c in lines:
            print(f"    y={y} 宽={x1 - x0}px #%02x%02x%02x" % c)


def main():
    files = sys.argv[1:]
    if not files:
        print(__doc__)
        return 2
    for f in files:
        if not Path(f).is_file():
            print(f"ERROR: 文件不存在: {f}")
            return 2
    for f in files:
        report(f)
    print("\n说明: 复刻填色以本报告为准；交付时在颜色对照表逐项列出「原版采样值 vs 复刻值」。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
