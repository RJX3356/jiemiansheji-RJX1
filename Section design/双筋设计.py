"""
双筋矩形截面正截面受弯配筋计算（已知 M → As, As'）
规范依据：GB 50010-2010

两种模式：
  模式 1 — 已知 As'（压筋已配），求 As
  模式 2 — As' 未知，按 ξ = ξb 同时设计压筋和拉筋
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
#  数据结构
# ═══════════════════════════════════════════════════════════════

class Section:
    def __init__(self):
        self.b   = 0.0    # 截面宽度 mm
        self.h   = 0.0    # 截面高度 mm
        self.M   = 0.0    # 弯矩设计值 kN·m
        self.fc  = 0.0    # 混凝土抗压强度 MPa
        self.fy  = 0.0    # 受拉钢筋抗拉强度 MPa
        self.fy1 = 0.0    # 受压钢筋抗压强度 MPa
        self.c   = 0.0    # 保护层 mm
        self.α1  = 0.0    # 等效矩形应力图系数
        self.ξb  = 0.0    # 界限相对受压区高度
        self.D   = 0.0    # 箍筋直径 mm

        # 计算量
        self.a   = 0.0    # 拉筋合力点至受拉边缘 mm
        self.a1  = 0.0    # 压筋合力点至受压边缘 → 实际存的是 a' = c+D+d1/2（至受压边缘）
        self.h0  = 0.0    # 截面有效高度 mm
        self.x   = 0.0    # 受压区高度 mm
        self.As  = 0.0    # 受拉钢筋面积 mm²
        self.As1 = 0.0    # 受压钢筋面积 mm²

        # 选筋结果
        self.n   = 0      # 受拉钢筋根数
        self.d   = 0.0    # 受拉钢筋直径 mm
        self.n1  = 0      # 受压钢筋根数
        self.d1  = 0.0    # 受压钢筋直径 mm


# ═══════════════════════════════════════════════════════════════
#  输入 & 几何
# ═══════════════════════════════════════════════════════════════

def input_params(sec: Section):
    print("=" * 56)
    print("  双筋矩形截面正截面受弯配筋计算")
    print("=" * 56)

    sec.b   = input_float("截面宽度 b (mm):                    ")
    sec.h   = input_float("截面高度 h (mm):                    ")
    sec.M   = input_float("弯矩设计值 M (kN·m):                ")
    sec.fc  = input_float("混凝土轴心抗压强度 fc (MPa):         ")
    sec.fy  = input_float("受拉钢筋抗拉强度 fy (MPa):          ")
    sec.fy1 = input_float("受压钢筋抗压强度 fy' (MPa):         ")
    sec.c   = input_float("保护层厚度 c (mm):                  ")
    sec.α1  = input_float("等效矩形应力图系数 α₁:              ")
    sec.ξb  = input_float("相对界限受压区高度 ξb:               ")
    sec.D   = input_float("箍筋直径 D (mm):                    ")


def calc_geometry(sec: Section, d: float, d1: float, layer_t: int = 2, layer_c: int = 1):
    """
    d, d1: 拉/压筋直径
    layer_t: 拉筋层数 (1 或 2)
    layer_c: 压筋层数 (1 或 2)
    """
    # 受拉钢筋合力点至受拉边缘
    if layer_t == 1:
        sec.a = sec.c + sec.D + d / 2
    else:
        sec.a = sec.c + sec.D + d + 25 / 2

    # 受压钢筋合力点至受压边缘（a'）
    if layer_c == 1:
        sec.a1 = sec.c + sec.D + d1 / 2
    else:
        sec.a1 = sec.c + sec.D + d1 + 25 / 2

    sec.h0 = sec.h - sec.a

    print(f"\n  拉筋合力点至受拉边缘    a   = {sec.a:.1f} mm")
    print(f"  压筋合力点至受压边缘    a'  = {sec.a1:.1f} mm")
    print(f"  截面有效高度            h0  = {sec.h0:.1f} mm")


# ═══════════════════════════════════════════════════════════════
#  模式 1：已知 As'，求 As
# ═══════════════════════════════════════════════════════════════

def mode_1_As1_known(sec: Section):
    """压筋已配好，求拉筋"""
    M_nmm = sec.M * 1e6

    # 受压钢筋能贡献的弯矩
    M_as1 = sec.fy1 * sec.As1 * (sec.h0 - sec.a1)
    M_conc = M_nmm - M_as1                    # 混凝土需承担的部分

    print(f"\n  弯矩分解：")
    print(f"    总弯矩设计值          M     = {M_nmm:.1f} N·mm = {sec.M:.3f} kN·m")
    print(f"    压筋承受弯矩          M_as1 = {M_as1:.1f} N·mm = {M_as1/1e6:.3f} kN·m")
    print(f"    混凝土需承担弯矩      M_c   = {M_conc:.1f} N·mm = {M_conc/1e6:.3f} kN·m")

    if M_conc <= 0:
        print(f"  ⚠ M_c ≤ 0，压筋已足够甚至多余，按构造配拉筋")
        # 此时 x 极小，偏安全按 x = 2a' 处理
        sec.As = M_nmm / (sec.fy * (sec.h0 - sec.a1))
        sec.x  = 2 * sec.a1
        print(f"  受拉钢筋面积  As = {sec.As:.1f} mm²")
        return

    # 判别式：x = h0 - √(h0² - 2·M_c/(α1·fc·b))
    discriminant = sec.h0 ** 2 - 2 * M_conc / (sec.α1 * sec.fc * sec.b)

    if discriminant < 0:
        print(f"\n  ❌ 判别式 < 0，混凝土无法承担 M_c = {M_conc/1e6:.3f} kN·m")
        print(f"     需要更多受压钢筋，将按 ξ=ξb 重新设计")
        # 自动转入 ξ=ξb 设计
        As1_new = (M_nmm - sec.α1 * sec.fc * sec.b * sec.h0 ** 2 * sec.ξb * (1 - 0.5 * sec.ξb)) / (sec.fy1 * (sec.h0 - sec.a1))
        if As1_new <= 0:
            print(f"     ξ=ξb 时 As1' ≤ 0，单筋即可，但当前为双筋模式，请检查输入")
            exit(1)
        sec.As1 = As1_new
        print(f"     重新计算 As1' = {sec.As1:.1f} mm²")
        sec.As  = (sec.fy1 * sec.As1 + sec.α1 * sec.fc * sec.b * sec.ξb * sec.h0) / sec.fy
        sec.x   = sec.ξb * sec.h0
        print(f"     受拉钢筋面积  As  = {sec.As:.1f} mm²")
        return

    sec.x = sec.h0 - math.sqrt(discriminant)
    ξ = sec.x / sec.h0

    print(f"  受压区高度        x  = {sec.x:.1f} mm")
    print(f"  相对受压区高度    ξ  = {ξ:.4f}")

    if ξ > sec.ξb:
        # 超筋：压筋未屈服，按 ξ = ξb 重算
        print(f"\n  ⚠ ξ ({ξ:.4f}) > ξb ({sec.ξb:.4f})，压筋未屈服")
        print(f"     按 ξ = ξb 重新设计受压钢筋 →")
        As1_new = (M_nmm - sec.α1 * sec.fc * sec.b * sec.h0 ** 2 * sec.ξb * (1 - 0.5 * sec.ξb)) / (sec.fy1 * (sec.h0 - sec.a1))
        if As1_new <= 0:
            print(f"     ξ=ξb 时 As1' ≤ 0，单筋截面即可满足")
            print(f"     建议：改用单筋截面设计，或增大截面尺寸")
            exit(1)
        sec.As1 = As1_new
        print(f"     受压钢筋面积  As1' = {sec.As1:.1f} mm²")
        sec.As  = (sec.fy1 * sec.As1 + sec.α1 * sec.fc * sec.b * sec.ξb * sec.h0) / sec.fy
        sec.x   = sec.ξb * sec.h0
        print(f"     受拉钢筋面积  As   = {sec.As:.1f} mm²")

    elif sec.x < 2 * sec.a1:
        # x < 2a'：压筋合力点太靠近中和轴
        print(f"\n  ⚠ x ({sec.x:.1f}) < 2a' ({2*sec.a1:.1f})，压筋合力点太靠近中和轴")
        print(f"     偏安全取：As = M / [fy·(h0 - a')]")
        sec.As = M_nmm / (sec.fy * (sec.h0 - sec.a1))
        print(f"     受拉钢筋面积  As  = {sec.As:.1f} mm²")

    else:
        # 适筋，2a' ≤ x ≤ ξb·h0
        print(f"  ✓ 适筋范围：2a' ({2*sec.a1:.1f}) ≤ x ≤ ξb·h0 ({sec.ξb*sec.h0:.1f})")
        sec.As = (sec.α1 * sec.fc * sec.b * sec.x + sec.fy1 * sec.As1) / sec.fy
        print(f"  As = (α1·fc·b·x + fy'·As1') / fy = {sec.As:.1f} mm²")

    print()


# ═══════════════════════════════════════════════════════════════
#  模式 2：As' 未知，按 ξ = ξb 同时设计
# ═══════════════════════════════════════════════════════════════

def mode_2_design_both(sec: Section):
    """压筋未知，取 ξ = ξb 进行双筋设计"""
    M_nmm = sec.M * 1e6

    # 单筋矩形截面在 ξb 下的最大抵抗弯矩
    M_single_max = sec.α1 * sec.fc * sec.b * sec.h0 ** 2 * sec.ξb * (1 - 0.5 * sec.ξb)

    print(f"\n  单筋截面最大抵抗弯矩（ξ=ξb）:")
    print(f"    M_single_max = {M_single_max:.1f} N·mm = {M_single_max/1e6:.3f} kN·m")
    print(f"    弯矩设计值   M = {M_nmm:.1f} N·mm = {sec.M:.3f} kN·m")

    if M_nmm <= M_single_max:
        print(f"\n  ⚠ M ≤ M_single_max，单筋截面即可满足，无需双筋！")
        print(f"     建议改用单筋矩形截面配筋计算")
        # 仍给出双筋参考结果
        sec.As1 = 0
        αs = M_nmm / (sec.α1 * sec.fc * sec.b * sec.h0 ** 2)
        ξ = 1 - math.sqrt(1 - 2 * αs)
        sec.As = sec.α1 * sec.fc * sec.b * sec.h0 * ξ / sec.fy
        sec.x  = ξ * sec.h0
        print(f"     按单筋计算结果：As = {sec.As:.1f} mm², ξ = {ξ:.4f}")
        return

    # 需要双筋，ξ = ξb
    ΔM = M_nmm - M_single_max
    sec.As1 = ΔM / (sec.fy1 * (sec.h0 - sec.a1))
    sec.As  = (sec.fy1 * sec.As1 + sec.α1 * sec.fc * sec.b * sec.ξb * sec.h0) / sec.fy
    sec.x   = sec.ξb * sec.h0

    print(f"\n  超出部分弯矩   ΔM = {ΔM:.1f} N·mm = {ΔM/1e6:.3f} kN·m")
    print(f"  受压钢筋面积   As' = {sec.As1:.1f} mm²")
    print(f"  受拉钢筋面积   As  = {sec.As:.1f} mm²")
    print(f"  ξ = ξb = {sec.ξb:.4f}  ✓")
    print()


# ═══════════════════════════════════════════════════════════════
#  选筋 & 排列验算
# ═══════════════════════════════════════════════════════════════

def select_bars(sec: Section):
    """选筋并验算排列宽度"""
    # ── 受拉钢筋 ──
    print("─" * 56)
    print("  选筋：受拉钢筋")
    sec.d = input_float("  受拉钢筋直径 d (mm): ")
    A_t  = math.pi * sec.d ** 2 / 4
    n_min_t = max(1, math.ceil(sec.As / A_t))
    print(f"  单根面积 = {A_t:.1f} mm²，最少需 {n_min_t} 根")
    sec.n = input_int(f"  受拉钢筋根数 n (≥{n_min_t}): ", min_val=n_min_t)
    print(f"  实际受拉面积 = {sec.n * A_t:.1f} mm² (≥ {sec.As:.1f}) ✓\n")

    # ── 受压钢筋 ──
    print("  选筋：受压钢筋")
    sec.d1 = input_float("  受压钢筋直径 d' (mm): ")
    A_c  = math.pi * sec.d1 ** 2 / 4
    n_min_c = max(1, math.ceil(sec.As1 / A_c))
    print(f"  单根面积 = {A_c:.1f} mm²，最少需 {n_min_c} 根")
    sec.n1 = input_int(f"  受压钢筋根数 n' (≥{n_min_c}): ", min_val=n_min_c)
    print(f"  实际受压面积 = {sec.n1 * A_c:.1f} mm² (≥ {sec.As1:.1f}) ✓\n")


def check_arrangement(sec: Section) -> bool:
    """验算上下排钢筋排列宽度"""
    b_t = sec.n * sec.d + (sec.n - 1) * 25 + 2 * (sec.c + sec.D)
    b_c = sec.n1 * sec.d1 + (sec.n1 - 1) * 25 + 2 * (sec.c + sec.D)

    print("─" * 56)
    print("  排列宽度验算：")
    print(f"    受拉钢筋排列宽度  b_t = {b_t:.0f} mm")
    print(f"    受压钢筋排列宽度  b_c = {b_c:.0f} mm")
    print(f"    截面宽度          b   = {sec.b:.0f} mm")

    ok = True
    if b_t > sec.b:
        print(f"    ⚠ 受拉钢筋放不下！建议减小直径或分两层")
        ok = False
    if b_c > sec.b:
        print(f"    ⚠ 受压钢筋放不下！建议减小直径或分两层")
        ok = False
    if ok:
        print(f"    ✓ 上下排均放得下")
    print()
    return ok


# ═══════════════════════════════════════════════════════════════
#  主流程
# ═══════════════════════════════════════════════════════════════

def main():
    sec = Section()
    input_params(sec)

    # 输入钢筋直径（用于初算 a / a'）
    print()
    d0  = input_float("拟用受拉钢筋直径 d (mm):  ")
    d10 = input_float("拟用受压钢筋直径 d' (mm): ")

    lt = input("受拉钢筋层数 (1 / 2): ").strip()
    lc = input("受压钢筋层数 (1 / 2): ").strip()
    lt = 2 if lt != "1" else 1
    lc = 2 if lc != "1" else 1

    calc_geometry(sec, d0, d10, lt, lc)

    # 选择模式
    print()
    mode = input("受压钢筋是否已配好？(1=已配好 / 2=从头设计): ").strip()

    if mode == "1":
        sec.As1 = input_float("请输入受压钢筋总截面面积 As' (mm²): ")
        print()
        mode_1_As1_known(sec)
    else:
        mode_2_design_both(sec)

    if sec.As <= 0:
        print("  ❌ 计算异常，As ≤ 0，请检查输入参数")
        exit(1)

    # 选筋 & 排列
    print(f"\n  计算结果汇总：")
    print(f"    受压钢筋面积  As' = {sec.As1:.1f} mm²")
    print(f"    受拉钢筋面积  As  = {sec.As:.1f} mm²")
    print()

    while True:
        select_bars(sec)
        if check_arrangement(sec):
            break
        print("  → 请调整钢筋直径重新选筋：\n")

    print("=" * 56)
    print("  ✅ 双筋截面设计完成")
    print("=" * 56)


if __name__ == "__main__":
    main()
