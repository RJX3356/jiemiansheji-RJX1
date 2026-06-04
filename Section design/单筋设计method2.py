"""
单筋矩形截面正截面受弯配筋计算（已知弯矩 M，求受拉钢筋面积 As）
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


def input_int(prompt: str, *, min_val: int = 1) -> int:
    """循环读取整数，直到合法为止。"""
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("  ⚠ 输入为空，请重新输入")
            continue
        try:
            val = int(raw)
        except ValueError:
            print(f"  ⚠ 「{raw}」不是有效整数，请重新输入")
            continue
        if val < min_val:
            print(f"  ⚠ 值必须 ≥ {min_val}，请重新输入")
            continue
        return val


# ── 输入截面参数 ──────────────────────────────
print("=" * 54)
print("  单筋矩形截面正截面受弯配筋计算")
print("=" * 54)

b   = input_float("混凝土截面宽度 b (mm):            ")
h   = input_float("混凝土截面高度 h (mm):            ")
M   = input_float("弯矩设计值 M (kN·m):              ")
fc  = input_float("混凝土轴心抗压强度设计值 fc (MPa): ")
ft  = input_float("混凝土轴心抗拉强度设计值 ft (MPa): ")
fy  = input_float("受拉钢筋抗拉强度设计值 fy (MPa):  ")
c   = input_float("混凝土保护层厚度 c (mm):          ")
α1  = input_float("受压区等效矩形应力图系数 α₁:      ")
ξb  = input_float("相对界限受压区高度 ξb:             ")
D   = input_float("箍筋直径 D (mm):                  ")
d0  = input_float("拟用受拉钢筋直径 d (mm):           ")

# ── 几何参数 ──────────────────────────────────
layer = input("钢筋层数 (1 / 2): ").strip()
if layer == "1":
    a = c + D + d0 / 2
else:
    a = c + D + d0 + 25 / 2            # 默认两层

h0 = h - a                             # 截面有效高度

print("\n" + "─" * 54)
print(f"  受拉钢筋合力点至受拉边缘距离  a   = {a:.1f} mm")
print(f"  截面有效高度                  h0  = {h0:.1f} mm")

# ── 截面抵抗矩系数 & 相对受压区高度 ──────────
M_nmm = M * 1e6                        # kN·m → N·mm
αs    = M_nmm / (α1 * fc * b * h0 ** 2)
αs_max = ξb * (1 - 0.5 * ξb)          # 界限抵抗矩系数

print("\n" + "─" * 54)
print("  受压区计算：")
print(f"    截面抵抗矩系数      αs      = {αs:.4f}")
print(f"    界限抵抗矩系数      αs_max  = {αs_max:.4f}  (ξb={ξb})")

# ── 超筋检查 ────────────────────────────────
if αs > αs_max:
    print(f"\n  ❌ 超筋！αs ({αs:.4f}) > αs_max ({αs_max:.4f})")
    print(f"     弯矩过大，截面尺寸不足")
    print(f"     建议：增大 b/h，或提高混凝土等级")
    exit(1)

if αs > 0.5:
    print(f"\n  ❌ αs = {αs:.4f} > 0.5，超出单筋矩形截面理论极限")
    print(f"     建议：增大截面尺寸或改用双筋截面")
    exit(1)

ξ = 1 - math.sqrt(1 - 2 * αs)

print(f"    相对受压区高度      ξ       = {ξ:.4f}")
print(f"    ✓ 适筋范围  ξ ({ξ:.4f}) ≤ ξb ({ξb:.4f})")

# ── 计算 As ─────────────────────────────────
# 法一：As = ξ · b · h0 · α₁ · fc / fy
# 法二：As = M / [fy · h0 · (1 - 0.5ξ)]
As  = ξ * b * h0 * α1 * fc / fy
As2 = M_nmm / (fy * h0 * (1 - 0.5 * ξ))   # 互相验证
print(f"\n  计算受拉钢筋面积  As  = {As:.1f} mm²  (检验: {As2:.1f} mm²)")

# ── 配筋率校核 ────────────────────────────────
ρ      = As / (b * h0)
ρ_min1 = 0.45  * ft / fy * h / h0
ρ_min2 = 0.002 * h / h0
ρ_min  = max(ρ_min1, ρ_min2)

print("\n" + "─" * 54)
print("  配筋率校核：")
print(f"    计算配筋率      ρ      = {ρ:.4%}")
print(f"    最小配筋率(1)   ρ_min1 = {ρ_min1:.4%}")
print(f"    最小配筋率(2)   ρ_min2 = {ρ_min2:.4%}")
print(f"    最小配筋率取大   ρ_min = {ρ_min:.4%}")

if ρ < ρ_min:
    As = ρ_min * b * h0
    print(f"  ⚠ 配筋率不足，按最小配筋率取值")
    print(f"    调整后 As = {As:.1f} mm²  →  ρ = {ρ_min:.4%}")
    print(f"  ✓ 满足少筋下限，不会发生少筋破坏")
else:
    print(f"  ✓ 配筋率满足要求，不会发生少筋破坏")

# ── 选筋 ─────────────────────────────────────
print("\n" + "─" * 54)
print("  选筋：")
print(f"    所需 As = {As:.1f} mm²")
print(f"    拟用直径 d = {d0:.0f} mm  (单根面积 = {math.pi * d0**2 / 4:.1f} mm²)")

# 根据用户已选的直径，反算最少根数
A_single = math.pi * d0 ** 2 / 4
n_min = math.ceil(As / A_single)
print(f"    最少需要 {n_min} 根")

n = input_int(f"  请确定钢筋根数 n (≥{n_min}): ", min_val=n_min)

As_real = n * A_single
print(f"    实际配筋面积  As_real = {As_real:.1f} mm²")

# ── 钢筋排列宽度验算 ──────────────────────────
# 一排时：b_need = n·d + (n-1)·25 + 2·(c+D)
b_need_1 = n * d0 + (n - 1) * 25 + 2 * (c + D)
print(f"\n  钢筋排列宽度（一层）: {b_need_1:.0f} mm  ≤  b = {b:.0f} mm")

if b_need_1 <= b:
    print(f"  ✓ 单层可放下")
else:
    print(f"  ⚠ 单层放不下，建议分两层或改用较小直径钢筋")
    b_need_2 = math.ceil(n / 2) * d0 + (math.ceil(n / 2) - 1) * 25 + 2 * (c + D)
    print(f"    两层估算宽度: {b_need_2:.0f} mm")
    if b_need_2 <= b:
        print(f"    ✓ 分两层可放下（注意需重新迭代 h0）")
    else:
        print(f"    ⚠ 仍放不下，请减小钢筋直径或加大截面宽度")

print("\n" + "=" * 54)
print("  计算完成")
print("=" * 54)
