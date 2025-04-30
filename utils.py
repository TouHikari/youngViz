# youngViz/utils.py
import numpy as np
import tkinter as tk
import tkinter.font as tkFont
from . import config # 相对导入 config

def wavelength_to_rgb(wavelength_nm: float) -> tuple[float, float, float]:
    """
    将可见光波长（nm）近似转换为 RGB 颜色值（0-1范围）。
    算法基于网上常见的近似实现。

    Args:
        wavelength_nm (float): 波长，单位纳米 (nm)。

    Returns:
        tuple[float, float, float]: 对应的 RGB 元组，每个分量在 0 到 1 之间。
    """
    w = float(wavelength_nm)
    R, G, B = 0.0, 0.0, 0.0

    # 波长到 RGB 的近似映射
    if 380 <= w < 440: R = -(w - 440) / (440 - 380); G = 0.0; B = 1.0
    elif 440 <= w < 490: R = 0.0; G = (w - 440) / (490 - 440); B = 1.0
    elif 490 <= w < 510: R = 0.0; G = 1.0; B = -(w - 510) / (510 - 490)
    elif 510 <= w < 580: R = (w - 510) / (580 - 510); G = 1.0; B = 0.0
    elif 580 <= w < 645: R = 1.0; G = -(w - 645) / (645 - 580); B = 0.0
    elif 645 <= w <= 750: R = 1.0; G = 0.0; B = 0.0
    else: # 超出范围时返回灰色或黑色
        return (0.1, 0.1, 0.1) # 返回一个暗灰色避免全黑

    # 强度因子调整
    factor = 0.0
    if 380 <= w < 420: factor = 0.3 + 0.7 * (w - 380) / (420 - 380)
    elif 420 <= w < 645: factor = 1.0
    elif 645 <= w <= 750: factor = 0.3 + 0.7 * (750 - w) / (750 - 645)

    # Gamma 校正 (可选，模拟人眼感知)
    gamma = 0.8
    R = pow(R * factor, gamma) if R * factor > 0 else 0
    G = pow(G * factor, gamma) if G * factor > 0 else 0
    B = pow(B * factor, gamma) if B * factor > 0 else 0

    # 裁剪到 [0, 1] 范围
    return (np.clip(R, 0, 1), np.clip(G, 0, 1), np.clip(B, 0, 1))

def find_best_font(root: tk.Tk, preferred_fonts: list[str], fallback: str) -> str:
    """
    检查 Tkinter 环境中可用的字体，并返回最佳匹配。

    Args:
        root: Tkinter 根窗口 (用于查询字体族)。
        preferred_fonts: 优先尝试的字体列表。
        fallback: 如果所有首选字体都不可用，则返回此字体。

    Returns:
        找到的最佳字体名称。
    """
    available_fonts = set(tkFont.families(root))
    for font_name in preferred_fonts:
        if font_name in available_fonts:
            print(f"信息: Tkinter 将使用字体 '{font_name}'。")
            return font_name
    print(f"警告: 首选 Tkinter 字体 {preferred_fonts} 均不可用，将使用备用字体 '{fallback}'。")
    return fallback