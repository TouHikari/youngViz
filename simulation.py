# youngViz/simulation.py
import numpy as np
from . import config # 在包内使用相对导入

def calculate_intensity(lambda_m: float, d_m: float, cap_d_m: float) -> tuple[np.ndarray, np.ndarray] | None:
    """
    计算屏幕上的相对光强分布。

    Args:
        lambda_m (float): 光的波长 (单位: m)。
        d_m (float): 双缝间距 (单位: m)。
        cap_d_m (float): 屏缝距离 (单位: m)。

    Returns:
        tuple[np.ndarray, np.ndarray]: 包含 (x坐标数组(mm), 相对光强数组(0-1)) 的元组。
                                        如果输入无效，返回 None。
    """
    # 检查输入参数有效性
    if lambda_m <= 0 or cap_d_m <= 0 or d_m <= 0:
        print(f"警告: 输入参数无效 (lambda={lambda_m}, d={d_m}, D={cap_d_m})。无法计算光强。")
        return None # 返回 None 表示计算失败

    # 使用 config 中预计算的屏幕坐标 (单位: m)
    x_m = config.X_COORDS_M

    # 计算相位差因子: phi_factor = (pi * d * x) / (lambda * D)
    phi_factor = (np.pi * d_m * x_m) / (lambda_m * cap_d_m)

    # 计算相对光强 I/I_max = cos^2(phi_factor)
    intensity = np.cos(phi_factor)**2

    # 返回毫米单位的坐标和光强数据
    return config.X_COORDS_MM, intensity

def calculate_fringe_spacing(lambda_m: float, d_m: float, cap_d_m: float) -> float | None:
    """
    计算理论上的干涉条纹间距。

    Args:
        lambda_m (float): 光的波长 (单位: m)。
        d_m (float): 双缝间距 (单位: m)。
        cap_d_m (float): 屏缝距离 (单位: m)。

    Returns:
        float | None: 理论条纹间距 (单位: mm)。
                      如果 d_m <= 0，返回 float('inf')。
                      如果其他参数无效，返回 None。
    """
    if d_m <= 0:
        print("警告: 缝间距 d <= 0，条纹间距为无穷大。")
        return float('inf')
    if lambda_m <= 0 or cap_d_m <= 0:
        print(f"警告: 无效参数 (lambda={lambda_m}, D={cap_d_m})，无法计算条纹间距。")
        return None

    # 计算条纹间距 (单位: m)
    delta_x_m = (lambda_m * cap_d_m) / d_m

    # 转换为毫米返回
    return delta_x_m * 1000

def calculate_path_phase_diff(x_mm: float, d_m: float, cap_d_m: float, lambda_m: float) -> tuple[float | None, float | None]:
    """
    计算屏幕上某点 x 的近似光程差和相位差。

    Args:
        x_mm (float): 屏幕上的位置 (单位: mm)。
        d_m (float): 双缝间距 (单位: m)。
        cap_d_m (float): 屏缝距离 (单位: m)。
        lambda_m (float): 光的波长 (单位: m)。

    Returns:
        tuple[float | None, float | None]: 包含 (光程差(m), 相位差(rad)) 的元组。
                                           如果计算失败（如除零），返回 (None, None)。
    """
    try:
        if cap_d_m <= 0:
            raise ValueError("屏缝距离 D 必须大于 0。")
        if lambda_m <= 0:
            raise ValueError("波长 lambda 必须大于 0。")

        x_m = x_mm * 1e-3 # 毫米转换为米

        # 近似光程差: delta = d * sin(theta) ≈ d * x / D
        path_diff = (d_m * x_m) / cap_d_m

        # 相位差: delta_phi = (2 * pi / lambda) * delta
        phase_diff = (2 * np.pi * path_diff) / lambda_m

        return path_diff, phase_diff

    except ValueError as ve:
        print(f"警告: 计算光程差/相位差时出错 - {ve}")
        return None, None
    except Exception as e:
        print(f"错误: 计算光程差/相位差时发生意外错误: {e}")
        return None, None