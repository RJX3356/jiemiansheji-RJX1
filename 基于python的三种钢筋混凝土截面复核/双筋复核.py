"""
双筋矩形截面正截面受弯承载力验算（已知 As, As'，验算 Mu ≥ M）
规范依据：GB 50010-2010
"""

import math


# ═══════════════════════════════════════════════════════════════
#  安全输入
# ═══════════════════════════════════════════════════════════════

def input_float(prompt: str, *, min_val: float = 0.0) -> float:
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("  ⚠ 输入为空，请重输")
            continue
        try:
            v = float(raw)
        except ValueError:
            print(f"  ⚠ 「{raw}」不是数字，请重输")
            continue
        if v < min_val:
            print(f"  ⚠ 需 ≥ {min_val}，请重输")
            continue
        return v


def input_int(prompt: str, *, min_val: int = 1) -> int:
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("  ⚠ 输入为空，请重输")
            continue
        try:
            v = int(raw)
        except ValueError:
            print(f"  ⚠ 「{raw}」不是整数，请重输")
            continue
        if v < min_val:
            print(f"  ⚠ 需 ≥ {min_val}，请重输")
            continue
        return v


# ═══════════════════════════════════════════════════════════════

print("=" * 56)
print("  双筋矩形截面正截面受弯承载力验算")
print("=" * 56)

b   = input_float("截面宽度 b (mm):                    ")
h   = input_float("截面高度 h (mm):                    ")
M   = input_float("弯矩设计值 M (kN·m):                ")
fc  = input_float("混凝土轴心抗压强度 fc (MPa):         ")
ft  = input_float("混凝土轴心抗拉强度 ft (MPa):         ")
fy  = input_float("受拉钢筋抗拉强度 fy (MPa):          ")
fy1 = input_float("受压钢筋抗压强度 fy' (MPa):         ")
c   = input_float("保护层厚度 c (mm):                  ")
α1  = input_float("等效矩形应力图系数 α₁:              ")
ξb  = input_float("相对界限受压区高度 ξb:               ")
D   = input_float("箍筋直径 D (mm):                    ")

# ── 受拉钢筋 ──
print()
n   = input_int  ("受拉钢筋根数 n:   ")
d   = input_float("受拉钢筋直径 d (mm): ")

# ── 受压钢筋 ──
n1  = input_int  ("受压钢筋根数 n':  ")
d1  = input_float("受压钢筋直径 d' (mm): ")

# ═══════════════════════════════════════════════════════════════
#  几何参数
# ═══════════════════════════════════════════════════════════════

layer_t = input("\n受拉钢筋层数 (1 / 2): ").strip()
layer_c = input("受压钢筋层数 (1 / 2): ").strip()
layer_t = 2 if layer_t != "1" else 1
layer_c = 2 if layer_c != "1" else 1

if layer_t == 1:
    a = c + D + d / 2
else:
    a = c + D + d + 25 / 2

if layer_c == 1:
    a1 = c + D + d1 / 2
else:
    a1 = c + D + d1 + 25 / 2

h0 = h - a

print(f"\n  拉筋合力点至受拉边缘    a   = {a:.1f} mm")
print(f"  压筋合力点至受压边缘    a'  = {a1:.1f} mm")
print(f"  截面有效高度            h0  = {h0:.1f} mm")

# ═══════════════════════════════════════════════════════════════
#  钢筋面积
# ═══════════════════════════════════════════════════════════════

As  = n  * math.pi * d  ** 2 / 4
As1 = n1 * math.pi * d1 ** 2 / 4     # ✅ 修正：原版漏用 n1，用了 n

print(f"\n  受拉钢筋面积  As  = {As:.1f} mm²")
print(f"  受压钢筋面积  As' = {As1:.1f} mm²")

# ═══════════════════════════════════════════════════════════════
#  配筋率校核
# ═══════════════════════════════════════════════════════════════

ρ      = As / (b * h0)
ρ_min1 = 0.45  * ft / fy * h / h0
ρ_min2 = 0.002 * h / h0
ρ_min  = max(ρ_min1, ρ_min2)

print("\n" + "─" * 56)
print("  配筋率校核：")
print(f"    实际配筋率      ρ     = {ρ:.4%}")
print(f"    最小配筋率(1)   ρ_min1 = {ρ_min1:.4%}")
print(f"    最小配筋率(2)   ρ_min2 = {ρ_min2:.4%}")
print(f"    最小配筋率取大   ρ_min = {ρ_min:.4%}")

if ρ < ρ_min:
    print(f"  ⚠ 配筋率不足！少筋破坏风险")
else:
    print(f"  ✓ 配筋率满足要求")

# ═══════════════════════════════════════════════════════════════
#  受压区高度 & 承载力
# ═══════════════════════════════════════════════════════════════

x = (fy * As - fy1 * As1) / (α1 * fc * b)

print("\n" + "─" * 56)
print(f"  受压区高度  x  = {x:.1f} mm")
print(f"  2a' = {2*a1:.1f} mm")
print(f"  ξb·h0 = {ξb * h0:.1f} mm")

if x < 0:
    print(f"\n  ❌ x < 0，受压钢筋面积过大或受拉钢筋不足，计算无意义")
    exit(1)

M_nmm = M * 1e6                          # kN·m → N·mm

if x < 2 * a1:                            # ✅ 修正：原版错用 2*a
    # 压筋位置太靠近中和轴，偏安全不计压筋贡献
    print(f"\n  ⚠ x ({x:.1f}) < 2a' ({2*a1:.1f})，压筋合力点太靠近中和轴")
    print(f"     偏安全取 x = 2a'，Mu = fy·As·(h0 - a')")
    Mu = fy * As * (h0 - a1)

elif x > ξb * h0:
    # 超筋，受压区混凝土先压碎，取 ξ = ξb
    print(f"\n  ⚠ x ({x:.1f}) > ξb·h0 ({ξb*h0:.1f})，超筋")
    print(f"     取 ξ = ξb 计算 Mu")
    ξ = ξb
    Mu = α1 * fc * b * ξ * h0 * (h0 - ξ * h0 / 2) + fy1 * As1 * (h0 - a1)

else:
    # 适筋，正常双筋截面
    print(f"\n  ✓ 适筋：2a' ≤ x ≤ ξb·h0")
    ξ = x / h0
    print(f"    相对受压区高度  ξ  = {ξ:.4f}")
    Mu = α1 * fc * b * x * (h0 - x / 2) + fy1 * As1 * (h0 - a1)

Mu_kNm = Mu / 1e6

print(f"\n  受弯承载力  Mu  = {Mu:.1f} N·mm = {Mu_kNm:.3f} kN·m")
print(f"  弯矩设计值  M   = {M:.3f} kN·m")
print(f"  安全裕度         {Mu_kNm / M:.2%}")

# ═══════════════════════════════════════════════════════════════
#  钢筋排列宽度验算
# ═══════════════════════════════════════════════════════════════

b_t = n  * d  + (n  - 1) * 25 + 2 * (c + D)
b_c = n1 * d1 + (n1 - 1) * 25 + 2 * (c + D)

print("\n" + "─" * 56)
print("  排列宽度验算：")
print(f"    受拉钢筋排列宽度  b_t = {b_t:.0f} mm")
print(f"    受压钢筋排列宽度  b_c = {b_c:.0f} mm")
print(f"    截面宽度          b   = {b:.0f} mm")

if b_t <= b and b_c <= b:
    print(f"    ✓ 上下排均放得下")
else:
    if b_t > b:
        print(f"    ⚠ 受拉钢筋放不下")
    if b_c > b:
        print(f"    ⚠ 受压钢筋放不下")

# ═══════════════════════════════════════════════════════════════
#  最终判定
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 56)
if M_nmm <= Mu:
    print("  ✅ 正截面承载力满足要求")
else:
    print(f"  ❌ 正截面承载力不足 — 差 {M - Mu_kNm:.3f} kN·m")
    print(f"     建议：增大截面、提高混凝土等级或增加配筋")
print("=" * 56)
