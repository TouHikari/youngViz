import numpy as np

# --- 物理常数与默认参数 ---
# (单位尽量使用国际标准单位 MKS)
DEFAULT_LAMBDA_M = 550e-9   # 默认波长 (m),  550 nm
DEFAULT_D_M = 0.1e-3      # 默认缝间距 (m), 0.1 mm
DEFAULT_CAP_D_M = 1.0     # 默认屏缝距离 (m), 1.0 m
SCREEN_WIDTH_M = 20e-3    # 模拟屏幕的总宽度 (m), 20 mm
NUM_PIXELS = 1000         # 屏幕分辨率 (像素点数)

# --- 预计算屏幕坐标 ---
# 屏幕中心为 x=0，范围从 -SCREEN_WIDTH_M / 2 到 +SCREEN_WIDTH_M / 2
x_coords_m = np.linspace(-SCREEN_WIDTH_M / 2, SCREEN_WIDTH_M / 2, NUM_PIXELS)
# 转换为毫米，方便后续绘图使用
x_coords_mm = x_coords_m * 1000

def calculate_intensity(lambda_m: float, d_m: float, cap_d_m: float) -> tuple[np.ndarray, np.ndarray]:
    """
    计算杨氏双缝干涉在屏幕上的相对光强分布。

    基于公式: I/I_max = cos^2(pi * d * x / (lambda * D))

    Args:
        lambda_m (float): 光的波长 (单位: m)。
        d_m (float): 双缝间距 (单位: m)。
        cap_d_m (float): 屏缝距离 (单位: m)。

    Returns:
        tuple[np.ndarray, np.ndarray]:
            - x_coords_mm (np.ndarray): 屏幕位置坐标数组 (单位: mm)。
            - intensity (np.ndarray): 对应的相对光强数组 (范围 0 到 1)。
    """
    # 检查输入参数有效性，防止除零等问题
    if lambda_m <= 0 or cap_d_m <= 0 or d_m <= 0:
        print(f"警告: 输入参数无效 (lambda={lambda_m}, d={d_m}, D={cap_d_m})。返回均匀光强。")
        # 返回一个均匀分布作为错误情况下的默认值
        return x_coords_mm, np.ones_like(x_coords_m) * 0.5

    # 计算相位差因子: phi_factor = (pi * d * x) / (lambda * D)
    # 注意：这里直接使用预计算的 x_coords_m (单位: m)
    phi_factor = (np.pi * d_m * x_coords_m) / (lambda_m * cap_d_m)

    # 计算相对光强 I/I_max = cos^2(phi_factor)
    intensity = np.cos(phi_factor)**2

    return x_coords_mm, intensity

def calculate_fringe_spacing(lambda_m: float, d_m: float, cap_d_m: float) -> float:
    """
    计算理论上的干涉条纹间距。

    基于公式: Δx = (lambda * D) / d

    Args:
        lambda_m (float): 光的波长 (单位: m)。
        d_m (float): 双缝间距 (单位: m)。
        cap_d_m (float): 屏缝距离 (单位: m)。

    Returns:
        float: 理论条纹间距 (单位: mm)。如果无法计算（如 d_m 为 0），返回无穷大。
    """
    if d_m <= 0:
        print("警告: 缝间距 d <= 0，无法计算条纹间距。")
        return float('inf') # 无法形成干涉，间距视为无穷大

    # 计算条纹间距 (单位: m)
    delta_x_m = (lambda_m * cap_d_m) / d_m

    # 转换为毫米返回
    return delta_x_m * 1000