"""
单筋矩形截面正截面受弯承载力验算（已知 As，验算 Mu）
规范依据：GB 50010-2010（混凝土结构设计规范）
"""

import math


# ── 安全输入函数 ──────────────────────────────
def input_float(prompt: str, *, min_val: float = 0.0) -> float:
    """循环读取浮点数，直到合法为止。"""
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("  ⚠ 输入为空，请重新输入")
            continue
        try:
            val = float(raw)
        except ValueError:
            print(f"  ⚠ 「{raw}」不是有效数字，请重新输入")
            continue
        if val < min_val:
            print(f"  ⚠ 值必须 ≥ {min_val}，请重新输入")
            continue
        return val


# ── 输入截面参数 ──────────────────────────────
print("=" * 54)
print("  单筋矩形截面正截面受弯承载力验算")
print("=" * 54)

b   = input_float("混凝土截面宽度 b (mm):            ")
h   = input_float("混凝土截面高度 h (mm):            ")
M   = input_float("弯矩设计值 M (kN·m):              ")
fc  = input_float("混凝土轴心抗压强度设计值 fc (MPa): ")
ft  = input_float("混凝土轴心抗拉强度设计值 ft (MPa): ")
fy  = input_float("受拉钢筋抗拉强度设计值 fy (MPa):  ")
As  = input_float("纵向受拉钢筋总截面面积 As (mm²):  ",
                  min_val=0.0)
c   = input_float("混凝土保护层厚度 c (mm):          ")
xsh = input_float("受压区等效矩形应力图系数 α₁:      ")
ξb  = input_float("相对界限受压区高度 ξb:             ")
D   = input_float("箍筋直径 D (mm):                  ")
d   = input_float("受拉钢筋直径 d (mm):              ")

# ── 几何参数 ──────────────────────────────────
layer = input("钢筋层数 (1 / 2): ").strip()
if layer == "1":
    a = c + D + d / 2
else:
    a = c + D + d + 25 / 2               # 默认两层

h0 = h - a                               # 截面有效高度

print("\n" + "─" * 54)
print(f"  受拉钢筋合力点至受拉边缘距离  a   = {a:.1f} mm")
print(f"  截面有效高度                  h0  = {h0:.1f} mm")

# ── 相对受压区高度计算 ────────────────────────
ξ = fy * As / (xsh * fc * b * h0)

print("\n" + "─" * 54)
print(f"  相对受压区高度  ξ  = {ξ:.4f}")

if ξ > ξb:
    print(f"  ⚠ 超筋！ξ ({ξ:.4f}) > ξb ({ξb:.4f})")
    print(f"     将取 ξ = ξb 按界限配筋计算 Mu（实际承载力低于此值）")
    ξ = ξb
else:
    print(f"  ✓ 适筋范围  ξ ({ξ:.4f}) ≤ ξb ({ξb:.4f})")

# ── 受压区高度 ────────────────────────────────
x = ξ * h0
print(f"  受压区高度      x   = {x:.1f} mm")

# ── 配筋率校核 ────────────────────────────────
ρ  = As / (b * h0)
ρ_min1 = 0.45  * ft / fy * h / h0
ρ_min2 = 0.002 * h / h0
ρ_min  = max(ρ_min1, ρ_min2)

print("\n" + "─" * 54)
print("  配筋率校核：")
print(f"    实际配筋率      ρ     = {ρ:.4%}")
print(f"    最小配筋率(1)   ρ_min1 = {ρ_min1:.4%}  (0.45·ft/fy·h/h0)")
print(f"    最小配筋率(2)   ρ_min2 = {ρ_min2:.4%}  (0.002·h/h0)")
print(f"    最小配筋率取大值 ρ_min = {ρ_min:.4%}")

if ρ < ρ_min:
    print(f"  ⚠ 配筋率不足！ρ ({ρ:.4%}) < ρ_min ({ρ_min:.4%})")
else:
    print(f"  ✓ 配筋率满足要求")

# ── 受弯承载力计算 ────────────────────────────
Mu      = xsh * fc * b * h0 ** 2 * ξ * (1 - 0.5 * ξ)   # N·mm
Mu_kNm  = Mu / 1e6                                       # N·mm → kN·m
M_nmm   = M  * 1e6                                       # kN·m → N·mm

print("\n" + "─" * 54)
print(f"  受弯承载力  Mu  = {Mu:.1f} N·mm = {Mu_kNm:.3f} kN·m")
print(f"  弯矩设计值  M   = {M:.3f} kN·m")
print(f"  安全裕度         {Mu_kNm / M:.2%}")

if M_nmm <= Mu:
    print("\n  ✅ 正截面承载力满足要求！")
else:
    print(f"\n  ❌ 正截面承载力不足 — 差 {M - Mu_kNm:.3f} kN·m")
    print(f"     建议：增大截面尺寸、提高混凝土等级或增加配筋")

print("=" * 54)
