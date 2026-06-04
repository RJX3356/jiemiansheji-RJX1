"""
单筋矩形截面正截面受弯配筋计算（已知 M → As → 选筋 → 排列验算）
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
#  截面参数数据结构
# ═══════════════════════════════════════════════════════════════

class Section:
    """矩形截面全部参数"""
    def __init__(self):
        self.b   = 0.0   # 截面宽度 mm
        self.h   = 0.0   # 截面高度 mm
        self.M   = 0.0   # 弯矩设计值 kN·m
        self.fc  = 0.0   # 混凝土抗压强度 MPa
        self.ft  = 0.0   # 混凝土抗拉强度 MPa
        self.fy  = 0.0   # 钢筋抗拉强度 MPa
        self.c   = 0.0   # 保护层厚度 mm
        self.α1  = 0.0   # 等效矩形应力图系数
        self.ξb  = 0.0   # 界限相对受压区高度
        self.D   = 0.0   # 箍筋直径 mm
        self.d   = 0.0   # 钢筋直径 mm

        # 计算中间量
        self.a   = 0.0   # 钢筋合力点至受拉边缘距离 mm
        self.h0  = 0.0   # 截面有效高度 mm
        self.αs  = 0.0   # 截面抵抗矩系数
        self.ξ   = 0.0   # 相对受压区高度
        self.As  = 0.0   # 所需受拉钢筋面积 mm²
        self.ρ   = 0.0   # 实际配筋率
        self.n   = 0     # 钢筋根数


def input_params(sec: Section):
    """输入全部截面参数"""
    print("=" * 54)
    print("  单筋矩形截面正截面受弯配筋计算")
    print("=" * 54)

    sec.b  = input_float("混凝土截面宽度 b (mm):              ")
    sec.h  = input_float("混凝土截面高度 h (mm):              ")
    sec.M  = input_float("弯矩设计值 M (kN·m):                ")
    sec.fc = input_float("混凝土轴心抗压强度设计值 fc (MPa):   ")
    sec.ft = input_float("混凝土轴心抗拉强度设计值 ft (MPa):   ")
    sec.fy = input_float("受拉钢筋抗拉强度设计值 fy (MPa):    ")
    sec.c  = input_float("混凝土保护层厚度 c (mm):            ")
    sec.α1 = input_float("受压区等效矩形应力图系数 α₁:        ")
    sec.ξb = input_float("相对界限受压区高度 ξb:               ")
    sec.D  = input_float("箍筋直径 D (mm):                    ")
    sec.d  = input_float("受拉钢筋直径 d (mm):                ")


# ═══════════════════════════════════════════════════════════════
#  各计算步骤（纯函数，不 IO，不修改 sec 以外的状态）
# ═══════════════════════════════════════════════════════════════

def calc_geometry(sec: Section, layer: int = 2):
    """计算 a、h0"""
    if layer == 1:
        sec.a = sec.c + sec.D + sec.d / 2
    else:
        sec.a = sec.c + sec.D + sec.d + 25 / 2
    sec.h0 = sec.h - sec.a

    print(f"\n  受拉钢筋合力点至边缘  a  = {sec.a:.1f} mm")
    print(f"  截面有效高度          h0 = {sec.h0:.1f} mm")


def calc_xi(sec: Section) -> bool:
    """
    计算 αs 和 ξ，返回是否适筋。
    不适筋时报错退出（不在 while 里死循环）。
    """
    M_nmm = sec.M * 1e6                       # kN·m → N·mm
    sec.αs = M_nmm / (sec.α1 * sec.fc * sec.b * sec.h0 ** 2)
    αs_max = sec.ξb * (1 - 0.5 * sec.ξb)

    print(f"\n  截面抵抗矩系数  αs     = {sec.αs:.4f}")
    print(f"  界限抵抗矩系数  αs_max = {αs_max:.4f}  (ξb={sec.ξb})")

    if sec.αs > αs_max:
        print(f"\n  ❌ 超筋！αs ({sec.αs:.4f}) > αs_max ({αs_max:.4f})")
        print(f"     弯矩过大、截面尺寸不足，请增大 b/h 或提高混凝土等级")
        return False

    if sec.αs > 0.5:
        print(f"\n  ❌ αs = {sec.αs:.4f} > 0.5，超出单筋矩形截面理论极限")
        return False

    sec.ξ = 1 - math.sqrt(1 - 2 * sec.αs)

    print(f"  相对受压区高度  ξ      = {sec.ξ:.4f}")
    print(f"  ✓ 适筋（ξ ≤ ξb）\n")
    return True


def calc_As(sec: Section) -> bool:
    """
    计算 As 并校核最小配筋率。
    不足时自动按最小配筋率取值，返回 True。
    """
    # 所需受拉钢筋面积
    sec.As = sec.ξ * sec.b * sec.h0 * sec.α1 * sec.fc / sec.fy
    print(f"  计算所需受拉钢筋面积  As = {sec.As:.1f} mm²")

    # 配筋率校核
    sec.ρ  = sec.As / (sec.b * sec.h0)
    ρ_min1 = 0.45  * sec.ft / sec.fy * sec.h / sec.h0
    ρ_min2 = 0.002 * sec.h / sec.h0
    ρ_min  = max(ρ_min1, ρ_min2)

    print(f"  配筋率        ρ      = {sec.ρ:.4%}")
    print(f"  最小配筋率(1) ρ_min1 = {ρ_min1:.4%}")
    print(f"  最小配筋率(2) ρ_min2 = {ρ_min2:.4%}")
    print(f"  最小配筋率    ρ_min  = {ρ_min:.4%}")

    if sec.ρ < ρ_min:
        sec.As = ρ_min * sec.b * sec.h0
        sec.ρ  = ρ_min
        print(f"  ⚠ 配筋率不足，已按最小配筋率取值 → As = {sec.As:.1f} mm²")
    else:
        print(f"  ✓ 配筋率满足要求，不会发生少筋破坏")

    print()
    return True


def select_bars(sec: Section):
    """选筋：确认直径 → 计算最少根数 → 用户确认根数"""
    A1 = math.pi * sec.d ** 2 / 4
    n_min = max(1, math.ceil(sec.As / A1))

    print(f"  拟用直径 d = {sec.d:.0f} mm，单根面积 = {A1:.1f} mm²")
    print(f"  最少需要 {n_min} 根")

    sec.n = input_int(f"  请确定钢筋根数 n (≥{n_min}): ", min_val=n_min)
    As_real = sec.n * A1
    print(f"  实际配筋面积 = {As_real:.1f} mm² (≥ {sec.As:.1f} mm²) ✓\n")


def check_arrangement(sec: Section) -> bool:
    """验算钢筋排列宽度，放不下返回 False"""
    b_need = sec.n * sec.d + (sec.n - 1) * 25 + 2 * (sec.c + sec.D)
    print(f"  钢筋排列宽度  b_need = {b_need:.0f} mm")
    print(f"  截面宽度      b      = {sec.b:.0f} mm")

    if b_need <= sec.b:
        print(f"  ✓ 单层放得下\n")
        return True
    else:
        print(f"  ⚠ 单层放不下！")
        print(f"     建议：分两层排布 / 减小钢筋直径 / 加大截面宽度\n")
        return False


# ═══════════════════════════════════════════════════════════════
#  主流程
# ═══════════════════════════════════════════════════════════════

def main():
    sec = Section()
    input_params(sec)

    layer = input("钢筋层数 (1 / 2): ").strip()
    layer = 2 if layer != "1" else 1

    calc_geometry(sec, layer)

    if not calc_xi(sec):
        exit(1)

    calc_As(sec)

    select_bars(sec)

    while not check_arrangement(sec):
        print("  → 请调整钢筋参数：")
        sec.d = input_float("  新钢筋直径 d (mm): ")
        calc_geometry(sec, layer)

        # 改钢筋直径后 ξ 变化很小，通常不会超筋；但仍需校核
        if not calc_xi(sec):
            print("  → 改直径后超筋，请同时加大截面")
            exit(1)

        calc_As(sec)
        select_bars(sec)

    print("=" * 54)
    print("  ✅ 计算完成 — 截面设计满足要求")
    print("=" * 54)


if __name__ == "__main__":
    main()
