"""
T形截面正截面受弯承载力验算
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
print("  T形截面正截面受弯承载力验算")
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
As  = input_float("纵向受拉钢筋总截面面积 As (mm²):  ",
                  min_val=0.0)    # As 可以为 0（理论分析）
c   = input_float("混凝土保护层厚度 c (mm):          ")
xsh = input_float("受压区等效矩形应力图系数 α₁:      ")
ξb  = input_float("相对界限受压区高度 ξb:             ")
D   = input_float("箍筋直径 D (mm):                  ")
d   = input_float("下部受拉钢筋直径 d (mm):           ")

# ── 几何参数 ──────────────────────────────────
# 两层钢筋时：a = c + D + d + 25/2
# 一层钢筋时：a = c + D + d/2
layer = input("钢筋层数 (1 / 2): ").strip()
if layer == "1":
    a = c + D + d / 2
else:
    a = c + D + d + 25 / 2     # 默认两层

h0 = h - a                     # 截面有效高度

# ── 配筋率校核 ────────────────────────────────
ρ  = As / (b * h0)             # ✅ 修正：加了括号
ρ_min = max(
    0.45 * ft * h  / (fy * h0),
    0.002 * h      / h0
)

print("\n" + "─" * 54)
print(f"  受拉钢筋合力点至受拉边缘距离  a   = {a:.1f} mm")
print(f"  截面有效高度                  h0  = {h0:.1f} mm")
print(f"  实际配筋率                    ρ   = {ρ:.4%}")
print(f"  最小配筋率                    ρ_min = {ρ_min:.4%}")
if ρ < ρ_min:
    print(f"  ⚠ 配筋率不足！ρ ({ρ:.4%}) < ρ_min ({ρ_min:.4%})")
else:
    print(f"  ✓ 配筋率满足要求")

# ── 判断 T 形截面类型 ────────────────────────
# 第一类 T 形：As * fy ≤ α₁ * fc * bf * hf  → 中和轴在翼缘内
# 第二类 T 形：As * fy >  α₁ * fc * bf * hf  → 中和轴进入腹板

tension_force  = fy  * As               # 受拉钢筋合力
flange_press   = xsh * fc * bf * hf     # 翼缘全压合力

print("\n" + "─" * 54)
print("  截面类型判定：")
print(f"    受拉钢筋合力  fy·As         = {tension_force:.1f} N")
print(f"    翼缘全压合力  α₁·fc·bf·hf  = {flange_press:.1f} N")

if tension_force <= flange_press:
    # ── 第一类 T 形截面（按宽 bf 的矩形截面计算）──
    print("    → 第一类 T 形截面（中和轴在翼缘内）\n")

    ξ = fy * As / (xsh * fc * bf * h0)
    print(f"    相对受压区高度  ξ  = {ξ:.4f}")

    if ξ > ξb:
        print(f"  ⚠ 超筋！ξ ({ξ:.4f}) > ξb ({ξb:.4f})，取 ξ = ξb 计算")
        ξ = ξb

    Mu = xsh * fc * bf * h0 ** 2 * ξ * (1 - 0.5 * ξ)
    Mu_kNm = Mu / 1e6       # N·mm → kN·m

    print(f"    受弯承载力  Mu  = {Mu:.1f} N·mm = {Mu_kNm:.2f} kN·m")

else:
    # ── 第二类 T 形截面 ────────────────────────
    print("    → 第二类 T 形截面（中和轴进入腹板）\n")

    # 翼缘挑出部分对应的受拉钢筋面积
    As1 = xsh * fc * (bf - b) * hf / fy
    As2 = As - As1

    print(f"    翼缘挑出部分对应受拉钢筋  As1 = {As1:.1f} mm²")
    print(f"    肋部受压区对应受拉钢筋    As2 = {As2:.1f} mm²")

    if As2 < 0:
        print("  ⚠ As2 < 0，截面参数可能不合理，停止计算")
        exit(1)

    # 腹板部分的相对受压区高度
    x   = fy * As2 / (xsh * fc * b)
    ξ   = x / h0

    print(f"    腹板受压区高度            x   = {x:.1f} mm")
    print(f"    肋部相对受压区高度        ξ   = {ξ:.4f}")

    # 翼缘挑出部分的抵抗力矩（力臂 = h0 - hf/2）
    Mu1 = fy * As1 * (h0 - hf / 2)

    if ξ <= ξb:
        # 适筋：按实际 ξ 计算肋部贡献
        Mu2 = xsh * fc * b * h0 ** 2 * ξ * (1 - 0.5 * ξ)
    else:
        # 超筋：取 ξ = ξb 计算
        print(f"  ⚠ 超筋！ξ ({ξ:.4f}) > ξb ({ξb:.4f})，取 ξ = ξb")
        Mu2 = xsh * fc * b * h0 ** 2 * ξb * (1 - 0.5 * ξb)

    Mu = Mu1 + Mu2
    Mu_kNm = Mu / 1e6

    print(f"    翼缘挑出部分贡献  Mu1 = {Mu1:.1f}  N·mm = {Mu1/1e6:.2f} kN·m")
    print(f"    肋部贡献          Mu2 = {Mu2:.1f}  N·mm = {Mu2/1e6:.2f} kN·m")

# ── 承载力判定 ────────────────────────────────
M_Nmm = M * 1e6       # kN·m → N·mm
print("\n" + "─" * 54)
print(f"  弯矩设计值    M   = {M:.3f}  kN·m")
print(f"  受弯承载力    Mu  = {Mu_kNm:.3f}  kN·m")
print(f"  安全裕度           {Mu_kNm / M:.2%}")

if M_Nmm <= Mu:
    print("\n  ✅ 正截面承载力满足要求！")
else:
    print(f"\n  ❌ 正截面承载力不足 — 差 {M - Mu_kNm:.2f} kN·m")

print("=" * 54)
