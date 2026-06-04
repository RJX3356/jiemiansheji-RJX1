"""
T形截面正截面受弯配筋计算（已知弯矩，求受拉钢筋面积 As）
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
print("  T形截面正截面受弯配筋计算")
print("=" * 54)

b   = input_float("混凝土截面宽度 b (mm):            ")
h   = input_float("混凝土截面高度 h (mm):            ")
bf  = input_float("T形截面翼缘宽度 bf (mm):          ")
hf  = input_float("T形截面翼缘高度 hf (mm):          ")
M   = input_float("弯矩设计值 M (kN·m):              ")
fc  = input_float("混凝土轴心抗压强度设计值 fc (MPa): ")
ft  = input_float("混凝土轴心抗拉强度设计值 ft (MPa): ")
fy  = input_float("受拉钢筋抗拉强度设计值 fy (MPa):  ")
fy1 = input_float("受压钢筋抗压强度设计值 fy' (MPa):  ")
c   = input_float("混凝土保护层厚度 c (mm):          ")
xsh = input_float("受压区等效矩形应力图系数 α₁:      ")
ξb  = input_float("相对界限受压区高度 ξb:             ")
D   = input_float("箍筋直径 D (mm):                  ")
d   = input_float("下部受拉钢筋直径 d (mm):           ")

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

# ── 截面类型判定 ──────────────────────────────
# 翼缘全压时能抵抗的最大弯矩（中和轴恰好在翼缘下缘）
Mf = xsh * fc * bf * hf * (h0 - hf / 2)   # N·mm
M_nmm = M * 1e6                            # kN·m → N·mm

print("\n" + "─" * 54)
print("  截面类型判定：")
print(f"    翼缘全压抵抗弯矩  Mf = {Mf:.1f} N·mm = {Mf/1e6:.2f} kN·m")
print(f"    弯矩设计值        M  = {M_nmm:.1f} N·mm = {M:.2f} kN·m")

if M_nmm <= Mf:
    # ── 第一类 T 形截面（按 bf × h 矩形截面计算）──
    print("    → 第一类 T 形截面（中和轴在翼缘内）\n")

    αs = M_nmm / (xsh * fc * bf * h0 ** 2)
    αs_max = ξb * (1 - 0.5 * ξb)

    if αs > αs_max:
        print(f"  ❌ 超筋！αs ({αs:.4f}) > αs_max ({αs_max:.4f})")
        print(f"     弯矩过大，截面无法承载，建议增大截面或提高混凝土等级")
        exit(1)

    if αs > 0.5:
        print(f"  ❌ αs = {αs:.4f} > 0.5，弯矩超出单筋截面极限")
        exit(1)

    ξ  = 1 - math.sqrt(1 - 2 * αs)

    print(f"    截面抵抗矩系数  αs = {αs:.4f}  (界限值 αs_max = {αs_max:.4f})")
    print(f"    相对受压区高度  ξ  = {ξ:.4f}")

    # αs 已 ≤ αs_max，ξ 必然 ≤ ξb，无需再判超筋
    As = ξ * bf * h0 * xsh * fc / fy

else:
    # ── 第二类 T 形截面 ────────────────────────
    print("    → 第二类 T 形截面（中和轴进入腹板）\n")

    # 翼缘挑出部分贡献的弯矩（bf - b 部分全压）
    M1 = xsh * fc * hf * (bf - b) * (h0 - hf / 2)

    # 腹板需承担的剩余弯矩
    M2 = M_nmm - M1

    print(f"    翼缘挑出部分承担的弯矩  M1 = {M1:.1f}  N·mm = {M1/1e6:.2f} kN·m")
    print(f"    腹板需承担的剩余弯矩    M2 = {M2:.1f}  N·mm = {M2/1e6:.2f} kN·m")

    if M2 < 0:
        print("  ⚠ M2 < 0，翼缘已足够，不应进入第二类；参数可能有误")
        exit(1)

    # 按单筋矩形截面求腹板受压区高度
    αs2 = M2 / (xsh * fc * b * h0 ** 2)
    αs_max = ξb * (1 - 0.5 * ξb)       # 界限受压区抵抗矩系数

    if αs2 > αs_max:
        print(f"  ❌ 超筋！αs2 ({αs2:.4f}) > αs_max ({αs_max:.4f})")
        print(f"     腹板弯矩 M2 ({M2/1e6:.2f} kN·m) 过大，截面无法承载")
        print(f"     建议：增大截面尺寸 b/h，或提高混凝土等级")
        exit(1)

    if αs2 > 0.5:
        print(f"  ❌ αs2 = {αs2:.4f} > 0.5，弯矩超出单筋矩形截面极限")
        print(f"     建议：增大截面尺寸或采用双筋截面")
        exit(1)

    ξ2  = 1 - math.sqrt(1 - 2 * αs2)
    x   = ξ2 * h0

    print(f"    腹板截面抵抗矩系数  αs2 = {αs2:.4f}  (界限值 αs_max = {αs_max:.4f})")
    print(f"    腹板相对受压区高度  ξ2  = {ξ2:.4f}")
    print(f"    腹板受压区高度      x   = {x:.1f} mm")

    # 总受拉钢筋面积 = 翼缘挑出部分对应 + 腹板对应
    As = (xsh * fc * hf * (bf - b) + xsh * fc * b * x) / fy

# ── 配筋率校核 ────────────────────────────────
ρ  = As / (b * h0)
ρ_min = max(
    0.45 * ft * h  / (fy * h0),
    0.002 * h      / h0
)

print("\n" + "─" * 54)
print(f"  计算所需受拉钢筋面积  As_cal = {As:.1f} mm²")
print(f"  实际配筋率            ρ      = {ρ:.4%}")
print(f"  最小配筋率            ρ_min  = {ρ_min:.4%}")

if ρ < ρ_min:
    As = ρ_min * b * h
    print(f"  ⚠ 配筋率不足，按最小配筋率取值")
    print(f"    调整后受拉钢筋面积  As = {As:.1f} mm²")
else:
    print(f"  ✓ 配筋率满足要求")

print(f"\n  ✅ 最终受拉钢筋面积  As = {As:.1f} mm²")
print("=" * 54)
