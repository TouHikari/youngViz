import numpy as np

# 定义物理常数或默认参数 (可选)
DEFAULT_LAMBDA_NM = 550e-9  # 默认波长 (m)
DEFAULT_D_MM = 0.1e-3     # 默认缝间距 (m)
DEFAULT_CAP_D_M = 1.0      # 默认屏缝距离 (m)
SCREEN_WIDTH_MM = 20e-3   # 模拟屏幕的总宽度 (m)
NUM_PIXELS = 1000         # 屏幕分辨率 (像素点数)

# 计算屏幕坐标 (只需计算一次)
x_coords_m = np.linspace(-SCREEN_WIDTH_MM / 2, SCREEN_WIDTH_MM / 2, NUM_PIXELS)
x_coords_mm = x_coords_m * 1000 # 转换为毫米用于绘图

def calculate_intensity(lambda_nm, d_mm, D_m):
    """
    根据给定的参数计算杨氏双缝干涉的光强分布。

    Args:
        lambda_nm (float): 光的波长 (单位: nm)。
        d_mm (float): 双缝间距 (单位: mm)。
        D_m (float): 屏缝距离 (单位: m)。

    Returns:
        tuple: 包含屏幕位置坐标 (mm) 和对应的相对光强数组 (0到1)。
               (x_coords_mm, intensity)
    """
    # 单位转换
    lambda_ = lambda_nm * 1e-9  # nm to m
    d = d_mm * 1e-3       # mm to m
    D = D_m               # m

    # 避免除零错误 (也检查 d)
    if lambda_ == 0 or D == 0 or d == 0:
        # print("警告: 计算中遇到除零或输入参数为零。") # 可选的警告信息
        return x_coords_mm, np.ones_like(x_coords_m) * 0.5 # 例如返回均匀光强

    # 计算相位差因子 (π * d * x) / (λ * D)
    # 使用全局的 x_coords_m
    phi_factor = (np.pi * d * x_coords_m) / (lambda_ * D)

    # 计算相对光强 I/Imax = cos^2(phi_factor)
    intensity = np.cos(phi_factor)**2

    return x_coords_mm, intensity

# 可以添加一个函数计算理论条纹间距
def calculate_fringe_spacing(lambda_nm, d_mm, D_m):
    """计算理论条纹间距 (mm)"""
    if d_mm == 0: return float('inf') # 避免除零
    lambda_ = lambda_nm * 1e-9
    d = d_mm * 1e-3
    D = D_m
    delta_x_m = (lambda_ * D) / d
    return delta_x_m * 1000 # m to mm
