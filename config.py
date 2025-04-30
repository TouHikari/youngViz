# youngViz/config.py
import numpy as np

# --- 物理常数与默认参数 (使用 MKS 单位) ---
DEFAULT_LAMBDA_M = 550e-9   # 默认波长 (m), 550 nm
DEFAULT_D_M = 0.1e-3      # 默认缝间距 (m), 0.1 mm
DEFAULT_CAP_D_M = 1.0     # 默认屏缝距离 (m), 1.0 m
SCREEN_WIDTH_M = 20e-3    # 模拟屏幕的总宽度 (m), 20 mm
NUM_PIXELS = 1000         # 屏幕分辨率 (像素点数)

# --- 预计算屏幕坐标 ---
# (如果认为这更属于模拟的核心，也可以放在 simulation.py 中)
X_COORDS_M = np.linspace(-SCREEN_WIDTH_M / 2, SCREEN_WIDTH_M / 2, NUM_PIXELS)
X_COORDS_MM = X_COORDS_M * 1000 # 转换为毫米，方便绘图

# --- GUI 样式配置 ---
TITLE_FONT_SIZE = 14
AXIS_LABEL_FONT_SIZE = 12
TICK_LABEL_FONT_SIZE = 10
ANNOTATION_FONT_SIZE = 10
BUTTON_FONT_SIZE = 11
LABEL_FONT_SIZE = 12
FRAME_TITLE_FONT_SIZE = 13

# 默认 Tkinter 字体 (尝试常见的跨平台选项)
DEFAULT_TK_FONT_FALLBACK = 'Arial' # 如果首选字体找不到，则使用此字体
PREFERRED_TK_FONTS = ['SimHei', 'Microsoft YaHei', 'Arial'] # 字体优先级

# --- Matplotlib 配置 ---
# 首选 Matplotlib 字体 (尝试在 main.py 或 gui/main_window.py 中设置)
PREFERRED_MPL_FONT = 'SimHei'

# --- GUI 参数范围和单位 ---
LAMBDA_RANGE_NM = (380, 750) # 波长范围 (nm)
D_RANGE_MM = (0.01, 1.0)    # 缝间距范围 (mm)
CAP_D_RANGE_M = (0.1, 5.0)   # 屏缝距离范围 (m)

# --- 绘图相关常量 ---
FRINGE_IMG_HEIGHT_PIXELS = 50 # 干涉条纹图像高度 (像素)
CLICK_INDICATOR_SIZE = 5      # 图形上点击指示点的大小
CLICK_INDICATOR_COLOR = 'red' # 指示点颜色
PLOT_LINEWIDTH = 1.5          # 光强曲线线宽

# 装置示意图绘图参数
SETUP_PLOT_YLIM_FACTOR = 2.5       # 根据缩放后的缝间距确定示意图Y轴范围的因子
SETUP_PLOT_Y_SCALE_FACTOR_BASE = 50 # 确保缝可见的基础缩放因子
SETUP_PLOT_PLATE_THICKNESS_FACTOR = 0.025 # 3D图中挡板视觉厚度的因子

# --- 分析相关常量 ---
PEAK_FINDING_PROMINENCE = 0.1 # 用于 scipy.signal.find_peaks 的显著性参数