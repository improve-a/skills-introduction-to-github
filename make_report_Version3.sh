#!/usr/bin/env bash
set -euo pipefail

# 1) 生成图像
python3 scripts/analyze_magnetics.py

# 2) 用 Pandoc + XeLaTeX 渲染 PDF（自动嵌入 figs/*.png）
pandoc report.md \
  --from gfm \
  --pdf-engine=xelatex \
  --output report.pdf

echo "OK: report.pdf 已生成（位于项目根目录）"