---
title: 铁磁材料基本磁化曲线与磁滞回线测量报告
author: improve-a
date: "\today"
fontsize: 12pt
geometry: margin=2.5cm
mainfont: "Noto Serif CJK SC"
sansfont: "Noto Sans CJK SC"
monofont: "JetBrains Mono"
header-includes:
  - \usepackage{xeCJK}
  - \setCJKmainfont{Noto Serif CJK SC}
---

# 1 实验目的
- 测得两种材料的基本磁化曲线与磁滞回线；
- 由回线求饱和磁感应 $B_s$、剩余磁感应 $B_r$、矫顽场 $H_c$、方形比 $S=B_r/B_s$；
- 基于标定常数将仪器读数换算为 SI 单位，估计初始相对磁导率 $\mu_{r,0}$，比较软/硬磁特性。

# 2 原理与标定
- 激磁场：$H=\dfrac{N_1}{L R_1}U_H$。
  - 样品1：$k_H=160\ \mathrm{A\,m^{-1}\,V^{-1}}$；样品2：$k_H=240\ \mathrm{A\,m^{-1}\,V^{-1}}$。
- 磁感应：$B=\dfrac{C_2R_2}{N_2S}U_B=k_B\,U_B$，$k_B=8.333\ \mathrm{T\,V^{-1}}$（即 $0.008333\ \mathrm{T/mV}$）。
- 回线面积 $W_h=\oint H\,\mathrm{d}B$（每周单位体积磁滞损耗）。

# 3 原始数据与处理
- 数据见 data/*.csv；脚本 scripts/analyze_magnetics.py 自动换算并绘图到 figs/ 目录。
- 数值方法：线性插值求 $H_c$（$B=0$ 截距）与 $B_r$（$H=0$ 截距）；鞋带公式计算回线面积。

# 4 结果（SI 单位）
- 样品1：$B_s\approx 1.000$ T，$B_r\approx 0.708$ T，$H_c\approx 192$ A/m，$S\approx 0.708$，$\mu_{r,0}\approx 3.43\times10^3$，$W_h\approx 3.25\times10^2$ J/m³/周。
- 样品2：$B_s\approx 1.083$ T，$B_r\approx 0.750$ T，$H_c\approx 96$ A/m，$S\approx 0.692$，$\mu_{r,0}\approx 4.15\times10^3$，$W_h\approx 1.53\times10^2$ J/m³/周。

# 5 图（自动生成并内嵌）

![样品1 基本磁化曲线（SI）](figs/sample1_base_SI.png)

![样品1 磁滞回线（SI）](figs/sample1_hyst_SI.png)

![样品2 基本磁化曲线（SI）](figs/sample2_base_SI.png)

![样品2 磁滞回线（SI）](figs/sample2_hyst_SI.png)

# 6 讨论与结论
- 样品2为软磁材料（小 $H_c$、大 $\mu_{r,0}$、小损耗），更适合交流磁路；样品1相对更“硬”，损耗更大。
- 两者 $B_s$ 约 1 T 量级，符合常见铁基磁性材料范围。

# 7 不确定度（模板）
- 请按仪器分辨率、标定误差与插值传播误差评定 $u(H_c)$、$u(B_r)$ 与 $u(W_h)$；如提供具体参数，我可补充定量不确定度表。