import tkinter as tk
from tkinter import ttk, font as tkFont
import sys # 用于检查平台

import matplotlib
# 尝试设置 Agg 后端，有时可以解决 Tkinter 和 Matplotlib 的冲突
# matplotlib.use('Agg') # 如果遇到渲染问题可以取消注释这一行试试
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.colors as mcolors
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

# 尝试导入 SciPy 用于峰值查找
try:
    from scipy.signal import find_peaks
except ImportError:
    print("提示：未找到 SciPy 库。条纹间距自动测量功能将不可用。")
    print("     如需此功能，请运行 'pip install scipy'")
    find_peaks = None # 定义为 None 以便后续检查

# 导入本地计算模块
import calculation as calc

# --- 全局样式配置 ---
TITLE_FONT_SIZE = 14
AXIS_LABEL_FONT_SIZE = 12
TICK_LABEL_FONT_SIZE = 10
ANNOTATION_FONT_SIZE = 10
BUTTON_FONT_SIZE = 11
LABEL_FONT_SIZE = 12
FRAME_TITLE_FONT_SIZE = 13

# --- Matplotlib 字体配置 ---
# 尝试设置中文字体 'SimHei'，如果失败则打印警告并回退
# 此设置影响 Matplotlib 图表的显示
try:
    plt.rcParams['font.family'] = 'SimHei'
    plt.rcParams['axes.unicode_minus'] = False # 解决负号显示问题
    print("Matplotlib 字体尝试设置为 SimHei。")
except Exception as e:
    print(f"警告：设置 Matplotlib 字体为 'SimHei' 失败: {e}")
    print("     Matplotlib 图中的中文可能无法正常显示。")
    print("     请确保已安装 SimHei 字体，或尝试安装其他中文字体（如 Microsoft YaHei, Source Han Sans CN）并修改此处代码。")
    # 即使 SimHei 失败，也要尝试设置 unicode_minus
    plt.rcParams['axes.unicode_minus'] = False

# --- 辅助函数 ---
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

    # 强度因子调整
    factor = 0.0
    if 380 <= w < 420: factor = 0.3 + 0.7 * (w - 380) / (420 - 380)
    elif 420 <= w < 645: factor = 1.0
    elif 645 <= w <= 750: factor = 0.3 + 0.7 * (750 - w) / (750 - 645)

    # Gamma 校正
    gamma = 0.8
    R = pow(R * factor, gamma) if R > 0 else 0
    G = pow(G * factor, gamma) if G > 0 else 0
    B = pow(B * factor, gamma) if B > 0 else 0

    # 裁剪到 [0, 1] 范围
    return (np.clip(R, 0, 1), np.clip(G, 0, 1), np.clip(B, 0, 1))

# --- 主应用类 ---
class InterferenceSimulatorApp:
    """
    杨氏双缝干涉模拟器的 Tkinter 图形用户界面主类。
    """
    def __init__(self, master: tk.Tk):
        """
        初始化应用程序。

        Args:
            master (tk.Tk): Tkinter 的根窗口。
        """
        self.master = master
        master.title("杨氏双缝干涉模拟器") # 更简洁的标题
        master.geometry("1150x850") # 初始窗口大小

        # --- Tkinter 控件样式和字体配置 ---
        style = ttk.Style()
        DEFAULT_TK_FONT = 'Arial' # 默认或备用字体
        try:
            # 检查系统是否支持 SimHei 字体用于 Tkinter 控件
            root_fonts = tkFont.families(master)
            if 'SimHei' in root_fonts:
                DEFAULT_TK_FONT = 'SimHei'
                print("Tkinter 控件将尝试使用 SimHei 字体。")
            elif 'Microsoft YaHei' in root_fonts: # 备选中文
                DEFAULT_TK_FONT = 'Microsoft YaHei'
                print("Tkinter 控件将尝试使用 Microsoft YaHei 字体。")
            else:
                # 在 Windows 上可以尝试 'Microsoft YaHei UI' 或 'DengXian'
                # 在 macOS 上可以尝试 'PingFang SC'
                # 在 Linux 上可能需要安装 'Noto Sans CJK SC' 等
                print(f"警告：在 Tkinter 中未找到 SimHei 或 Microsoft YaHei，控件将使用默认西文字体 ({DEFAULT_TK_FONT})。")
        except Exception as e:
             print(f"检查 Tkinter 字体时出错: {e}. 控件将使用默认字体 ({DEFAULT_TK_FONT})。")

        # 应用字体到 ttk 控件
        style.configure('TLabel', font=(DEFAULT_TK_FONT, LABEL_FONT_SIZE))
        style.configure('TButton', font=(DEFAULT_TK_FONT, BUTTON_FONT_SIZE))
        style.configure('TLabelframe.Label', font=(DEFAULT_TK_FONT, FRAME_TITLE_FONT_SIZE, 'bold'))
        style.configure('TScale', troughcolor='#d3d3d3') # 给 Scale 加点样式

        # --- 数据模型变量 ---
        # 使用 calc 中的默认值，注意单位转换
        self.lambda_nm = tk.DoubleVar(value=calc.DEFAULT_LAMBDA_M * 1e9) # m -> nm
        self.d_mm = tk.DoubleVar(value=calc.DEFAULT_D_M * 1e3)         # m -> mm
        self.D_m = tk.DoubleVar(value=calc.DEFAULT_CAP_D_M)            # m -> m

        self._last_intensity_data = None    # 缓存上次计算的光强数据
        self._last_x_coords_mm = None       # 缓存上次计算的位置坐标
        self._last_params = {}              # 缓存上次使用的参数，用于优化重绘
        self._click_indicator_fringe = None # 干涉条纹图上的点击指示器
        self._click_indicator_plot = None   # 光强曲线图上的点击指示器

        # --- 创建 GUI 布局 ---
        self._create_widgets()

        # --- 绑定事件 ---
        self._bind_events()

        # --- 初始化显示 ---
        self.update_labels()       # 更新标签显示初始值
        self.update_simulation()   # 执行第一次模拟计算和绘图

    def _create_widgets(self):
        """创建所有的 GUI 控件。"""
        main_frame = ttk.Frame(self.master, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 左侧：控制面板 ---
        control_frame = ttk.LabelFrame(main_frame, text="参数设置与分析", padding="15")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=5, anchor='nw') # 靠左上
        control_frame.columnconfigure(1, weight=1) # 让标签值右对齐

        current_row = 0
        pady_val = 4
        pady_section = (pady_val, pady_val + 5)

        # 波长控件
        ttk.Label(control_frame, text="波长 λ (nm):").grid(row=current_row, column=0, sticky="w", pady=pady_val)
        self.lambda_label = ttk.Label(control_frame, text="", width=8, anchor='e') # 预设宽度，右对齐
        self.lambda_label.grid(row=current_row, column=1, sticky="ew", pady=pady_val)
        current_row += 1
        self.lambda_scale = ttk.Scale(control_frame, from_=380, to=750, orient=tk.HORIZONTAL, variable=self.lambda_nm)
        self.lambda_scale.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=pady_section)
        # 确保初始值在范围内
        if not (380 <= self.lambda_nm.get() <= 750): self.lambda_nm.set(550.0)
        current_row += 1

        # 波长预设按钮
        preset_button_frame = ttk.Frame(control_frame)
        preset_button_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=(0, pady_val + 10))
        preset_button_frame.columnconfigure((0, 1, 2), weight=1) # 按钮均分布局
        ttk.Button(preset_button_frame, text="红(650)", command=lambda: self.set_wavelength(650.0)).grid(row=0, column=0, sticky='ew', padx=2)
        ttk.Button(preset_button_frame, text="绿(550)", command=lambda: self.set_wavelength(550.0)).grid(row=0, column=1, sticky='ew', padx=2)
        ttk.Button(preset_button_frame, text="蓝(450)", command=lambda: self.set_wavelength(450.0)).grid(row=0, column=2, sticky='ew', padx=2)
        current_row += 1

        # 缝间距控件
        ttk.Label(control_frame, text="缝间距 d (mm):").grid(row=current_row, column=0, sticky="w", pady=pady_val)
        self.d_label = ttk.Label(control_frame, text="", width=8, anchor='e')
        self.d_label.grid(row=current_row, column=1, sticky="ew", pady=pady_val)
        current_row += 1
        self.d_scale = ttk.Scale(control_frame, from_=0.01, to=1.0, orient=tk.HORIZONTAL, variable=self.d_mm)
        self.d_scale.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=pady_section)
        current_row += 1

        # 屏缝距离控件
        ttk.Label(control_frame, text="屏缝距离 D (m):").grid(row=current_row, column=0, sticky="w", pady=pady_val)
        self.D_label = ttk.Label(control_frame, text="", width=8, anchor='e')
        self.D_label.grid(row=current_row, column=1, sticky="ew", pady=pady_val)
        current_row += 1
        self.D_scale = ttk.Scale(control_frame, from_=0.1, to=5.0, orient=tk.HORIZONTAL, variable=self.D_m)
        self.D_scale.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=pady_section)
        current_row += 1

        # 分隔线
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).grid(row=current_row, column=0, columnspan=2, sticky='ew', pady=pady_val + 10)
        current_row += 1

        # 分析结果标签
        self.spacing_comparison_label = ttk.Label(control_frame, text="理论间距 Δx:\n测量间距 Δx_m:", justify=tk.LEFT)
        self.spacing_comparison_label.grid(row=current_row, column=0, columnspan=2, sticky="w", pady=pady_val)
        current_row += 1

        self.point_info_label = ttk.Label(control_frame, text="点击下方图形获取点信息:\nx=\nδ=\nΔΦ=", justify=tk.LEFT)
        self.point_info_label.grid(row=current_row, column=0, columnspan=2, sticky="w", pady=(pady_val, 0)) # Pady bottom 0
        current_row += 1

        # --- 右侧：显示区域 ---
        right_display_frame = ttk.Frame(main_frame)
        right_display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=5) # padx left 10

        # 右上：实验装置示意图
        setup_frame = ttk.LabelFrame(right_display_frame, text="实验装置示意图", padding=10)
        setup_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5)) # pady bottom 5

        self.fig_setup = Figure(figsize=(6, 4), dpi=100)
        self.ax_setup_3d = self.fig_setup.add_subplot(1, 2, 1, projection='3d')
        self.ax_setup_2d = self.fig_setup.add_subplot(1, 2, 2)
        self.fig_setup.subplots_adjust(left=0.08, right=0.95, bottom=0.15, top=0.9, wspace=0.4, hspace=0.3) # 微调布局
        self.canvas_setup = FigureCanvasTkAgg(self.fig_setup, master=setup_frame)
        self.canvas_setup_widget = self.canvas_setup.get_tk_widget()
        self.canvas_setup_widget.pack(fill=tk.BOTH, expand=True)

        # 右下：干涉结果图
        fringe_frame = ttk.LabelFrame(right_display_frame, text="干涉结果", padding=10)
        fringe_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0)) # pady top 5

        self.fig_fringe = Figure(figsize=(6, 4), dpi=100)
        self.ax_fringe = self.fig_fringe.add_subplot(2, 1, 1) # 干涉条纹
        self.ax_plot = self.fig_fringe.add_subplot(2, 1, 2)   # 光强曲线
        self.fig_fringe.tight_layout(pad=3.0, h_pad=2.5) # 调整子图间距
        self.canvas_fringe = FigureCanvasTkAgg(self.fig_fringe, master=fringe_frame)
        self.canvas_fringe_widget = self.canvas_fringe.get_tk_widget()
        self.canvas_fringe_widget.pack(fill=tk.BOTH, expand=True)

        # Matplotlib 工具栏
        toolbar_frame = ttk.Frame(fringe_frame)
        toolbar_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        self.toolbar = NavigationToolbar2Tk(self.canvas_fringe, toolbar_frame)
        self.toolbar.update()

    def _bind_events(self):
        """绑定变量变化和用户交互事件。"""
        # 当 Scale/变量 变化时，更新标签并触发模拟更新
        self.lambda_nm.trace_add("write", self.update_labels_and_trigger_sim)
        self.d_mm.trace_add("write", self.update_labels_and_trigger_sim)
        self.D_m.trace_add("write", self.update_labels_and_trigger_sim)
        # Use lambda for scale command to avoid passing the value automatically
        self.lambda_scale.config(command=lambda val: self.update_labels_and_trigger_sim())
        self.d_scale.config(command=lambda val: self.update_labels_and_trigger_sim())
        self.D_scale.config(command=lambda val: self.update_labels_and_trigger_sim())

        # 连接干涉结果图的点击事件
        self.canvas_fringe.mpl_connect('button_press_event', self.on_plot_click)

    # --- 事件处理与更新逻辑 ---

    def update_labels_and_trigger_sim(self, *args):
        """回调函数：先更新参数标签，然后触发模拟计算和绘图更新。"""
        self.update_labels()
        self.update_simulation() # 可以考虑加一个小的延迟 debounce，防止拖动时过于频繁计算

    def set_wavelength(self, wavelength_nm: float):
        """通过按钮设置特定的波长值。"""
        # 检查值是否有实际变化，避免不必要的触发
        if abs(self.lambda_nm.get() - wavelength_nm) > 1e-6:
            self.lambda_nm.set(wavelength_nm)
            # value.set() 会自动触发 trace_add("write", ...)绑定的回调

    def update_labels(self, *args):
        """更新控制面板中显示参数值的标签。"""
        try:
            lambda_val = self.lambda_nm.get()
            d_val = self.d_mm.get()
            D_val = self.D_m.get()

            self.lambda_label.config(text=f"{lambda_val:.0f} nm")
            self.d_label.config(text=f"{d_val:.2f} mm")
            self.D_label.config(text=f"{D_val:.1f} m")
        except tk.TclError:
            # 在程序关闭过程中，获取变量值可能失败，忽略此错误
            pass
        except Exception as e:
            print(f"错误：更新标签时发生异常: {e}")

    def update_simulation(self, *args):
        """核心函数：获取参数、执行计算、更新所有相关的图表和信息。"""
        # 1. 清除旧的点击指示器（如果存在）
        self._remove_click_indicators()

        # 2. 获取当前参数值 (GUI单位)
        try:
            lambda_nm_val = self.lambda_nm.get()
            d_mm_val = self.d_mm.get()
            D_m_val = self.D_m.get()
        except tk.TclError:
            return # 关闭时可能出错
        except Exception as e:
            print(f"错误：获取参数值时发生异常: {e}")
            return

        # 3. 单位转换 (GUI单位 -> 计算所需MKS单位)
        lambda_m_val = lambda_nm_val * 1e-9
        d_m_val = d_mm_val * 1e-3
        # D_m_val 已经是 m

        # 4. 优化：检查参数是否实际改变
        current_params = {'lambda': lambda_m_val, 'd': d_m_val, 'D': D_m_val}
        params_changed = current_params != self._last_params
        # 装置图参数 (d, D) 是否改变
        setup_params_changed = (self._last_params.get('d') != d_m_val or
                                self._last_params.get('D') != D_m_val)

        # 如果参数未变，且不是由点击事件强制触发的重绘 ('click' 标记)，则跳过计算
        # 'click' argument is not used in this version, optimization relies solely on param change comparison
        if not params_changed and self._last_params: # Only skip if params haven't changed AND we have previous params
             return

        # 5. 执行干涉计算
        calculation_ok = False # 标记计算是否成功
        try:
            # 使用 MKS 单位进行计算
            x_coords_mm, intensity = calc.calculate_intensity(lambda_m_val, d_m_val, D_m_val)
            # 缓存结果
            self._last_x_coords_mm = x_coords_mm
            self._last_intensity_data = intensity
            calculation_ok = True
        except Exception as e:
            print(f"错误：计算光强分布时发生异常: {e}")
            # 保留 x 轴坐标用于显示错误，强度设为零
            x_coords_mm = calc.x_coords_mm # 使用预计算的坐标轴
            intensity = np.zeros_like(x_coords_mm)
            self._last_x_coords_mm = None
            self._last_intensity_data = None
            calculation_ok = False

        # 6. 计算和更新理论/测量条纹间距
        measured_spacing_str = "N/A"
        theoretical_spacing_str = "N/A"
        try:
            # 计算理论间距 (使用 MKS 单位)
            delta_x_theory_mm = calc.calculate_fringe_spacing(lambda_m_val, d_m_val, D_m_val)
            if np.isinf(delta_x_theory_mm):
                theoretical_spacing_str = "∞ mm"
            elif delta_x_theory_mm is not None:
                 theoretical_spacing_str = f"{delta_x_theory_mm:.3f} mm"
            else: # Should not happen with current calc logic, but handle defensively
                 theoretical_spacing_str = "计算错误"

            # 如果计算成功且 SciPy 可用，尝试测量间距
            if calculation_ok and find_peaks and self._last_intensity_data is not None:
                 # 使用 find_peaks 寻找强度峰值
                 # prominence 参数有助于过滤掉噪声引起的小峰值
                 peaks_indices, _ = find_peaks(self._last_intensity_data, prominence=0.1)
                 if len(peaks_indices) >= 2:
                     # 计算峰值之间的平均距离
                     peak_positions_mm = self._last_x_coords_mm[peaks_indices]
                     spacings = np.diff(peak_positions_mm)
                     measured_spacing = np.mean(spacings)
                     measured_spacing_str = f"{measured_spacing:.3f} mm"
                 elif len(peaks_indices) < 2:
                     measured_spacing_str = "峰值不足"
                 else: # Should not happen if calculation_ok is True
                     measured_spacing_str = "无数据"
            elif find_peaks is None:
                 measured_spacing_str = "需要 SciPy" # 提示用户缺少库

        except Exception as e:
            print(f"错误：计算或测量条纹间距时发生异常: {e}")
            measured_spacing_str = "错误"
            # 理论值可能已计算，保留

        # 更新间距显示标签
        self.spacing_comparison_label.config(text=f"理论间距 Δx: {theoretical_spacing_str}\n测量间距 Δx_m: {measured_spacing_str}")

        # 7. 更新示意图 (仅当 d 或 D 变化，或首次加载时)
        # 使用 GUI 单位 (mm, m) 传入绘图函数，它们内部会处理
        if setup_params_changed or not self._last_params:
            self.update_setup_plots(d_mm_val, D_m_val)

        # 8. 更新干涉图样和光强曲线图
        # 无论参数是否变化，都需要调用以清除旧指示器或显示 Calculation Error
        # GUI 单位用于颜色，MKS单位的计算结果用于绘图
        self.update_fringe_display(x_coords_mm, intensity, lambda_nm_val, calculation_ok)
        self.update_intensity_plot(x_coords_mm, intensity, lambda_nm_val, calculation_ok)

        # 9. 保存当前参数 (MKS 单位) 作为下次比较的基准
        self._last_params = current_params

    def on_plot_click(self, event):
        """处理在干涉图区域（条纹或曲线）的点击事件。"""
        # 1. 移除旧的指示器
        self._remove_click_indicators()

        x_click_mm = event.xdata # 点击的 x 坐标 (mm)
        y_click = event.ydata    # 点击的 y 坐标 (用于条纹图)

        # 2. 检查点击是否落在有效的绘图区域 (Axes) 内
        target_ax = None
        if event.inaxes == self.ax_fringe and x_click_mm is not None and y_click is not None:
            target_ax = self.ax_fringe
        elif event.inaxes == self.ax_plot and x_click_mm is not None:
            target_ax = self.ax_plot
        else:
            return # 点击无效或在 Axes 之外

        # 3. 获取当前参数 (需要用于计算光程差/相位差)
        try:
            lambda_nm = self.lambda_nm.get()
            d_mm = self.d_mm.get()
            D_m = self.D_m.get()
        except tk.TclError:
            return # 关闭时可能出错

        # 4. 单位转换以进行物理计算
        x_m = x_click_mm * 1e-3 # mm to m
        lambda_m = lambda_nm * 1e-9 # nm to m
        d_m = d_mm * 1e-3       # mm to m

        # 5. 计算光程差 (delta) 和相位差 (delta_phi)
        delta_str = "计算错误"
        delta_phi_str = "计算错误"
        try:
            # 检查分母是否为零
            if D_m <= 0:
                delta_str = "D 不能为零"
                delta_phi_str = "D 不能为零"
                raise ZeroDivisionError("屏缝距离 D 不能为零")

            # 光程差 delta = d * sin(theta) approx d * x / D
            delta = (d_m * x_m) / D_m
            delta_str = f"{delta:.3e} m" # 使用科学计数法显示

            # 相位差 delta_phi = (2 * pi / lambda) * delta
            if lambda_m <= 0:
                delta_phi_str = "λ 不能为零"
                raise ZeroDivisionError("波长 λ 不能为零")

            delta_phi = (2 * np.pi * delta) / lambda_m
            # 显示弧度和 pi 的倍数
            delta_phi_str = f"{delta_phi:.2f} rad ({delta_phi/np.pi:.2f}π)"

        except ZeroDivisionError as zde:
             print(f"提示：{zde}") # 用户已知问题，用提示级别
             # delta_str 和 delta_phi_str 已被设置为错误信息
        except Exception as e:
            print(f"错误：计算光程/相位差时发生未知异常: {e}")
            # 保持 "计算错误"

        # 6. 更新信息显示标签
        info_text = (
            f"点击位置:\n"
            f"  x = {x_click_mm:.3f} mm\n"
            f"光程差(近似):\n"
            f"  δ ≈ {delta_str}\n"
            f"相位差:\n"
            f"  ΔΦ = {delta_phi_str}"
        )
        self.point_info_label.config(text=info_text)

        # 7. 在对应的图上绘制红色指示点
        dot_size = 5 # 指示点大小

        if target_ax == self.ax_fringe:
            # 在条纹图上，直接在点击位置绘制
            self._click_indicator_fringe = self.ax_fringe.plot(x_click_mm, y_click, 'ro', markersize=dot_size)[0]
            # Make indicator visible even if fringe data is black
            self._click_indicator_fringe.set_markeredgecolor('red')
            self._click_indicator_fringe.set_markerfacecolor('red')

        elif target_ax == self.ax_plot:
            # 在曲线图上，需要找到对应 x 坐标的曲线上的 y 值
            if self._last_x_coords_mm is not None and self._last_intensity_data is not None:
                try:
                    # 确保点击的 x 在数据范围内，然后插值计算 y
                    x_clamped = np.clip(x_click_mm, self._last_x_coords_mm.min(), self._last_x_coords_mm.max())
                    y_intensity = np.interp(x_clamped, self._last_x_coords_mm, self._last_intensity_data)
                    self._click_indicator_plot = self.ax_plot.plot(x_clamped, y_intensity, 'ro', markersize=dot_size)[0]
                except Exception as e:
                    print(f"错误：插值或绘制曲线指示点时发生异常: {e}")
            else:
                 print("提示：无强度数据，无法在曲线上绘制指示点。")

        # 8. 重绘包含指示器的画布
        self.canvas_fringe.draw_idle()

    def _remove_click_indicators(self):
        """安全地移除画布上的点击指示器。"""
        if self._click_indicator_fringe:
            try:
                self._click_indicator_fringe.remove()
            except (ValueError, AttributeError): # 可能已被移除或未正确创建
                pass
            finally: # 确保变量被重置
                 self._click_indicator_fringe = None
        if self._click_indicator_plot:
            try:
                self._click_indicator_plot.remove()
            except (ValueError, AttributeError):
                pass
            finally:
                 self._click_indicator_plot = None

    # --- 更新绘图函数 ---

    def update_setup_plots(self, d_mm: float, D_m: float):
        """更新 3D 和 2D 实验装置示意图。"""
        d_m = d_mm * 1e-3 # mm to m
        self.ax_setup_3d.cla() # Clear previous 3D plot
        self.ax_setup_2d.cla() # Clear previous 2D plot

        # --- 几何参数计算 ---
        z_range = (-0.2 * D_m, 1.1 * D_m)
        # Y 轴显示，适当放大缝间距 (保持或微调此逻辑以确保可见性)
        y_scale_factor = max(50, 0.02 * D_m / (d_m + 1e-9))
        y_display_half_d = d_m / 2 * y_scale_factor
        y_range_abs = max(0.02 * D_m, y_display_half_d * 2.5)
        y_range = (-y_range_abs, y_range_abs)
        # X 轴范围 (3D视图)
        x_range = y_range # Keep X and Y ranges similar for a balanced view

        # 板和缝的尺寸 (使用原始的简化比例)
        plate_width = y_range[1] * 1.8 # Based on original rough proportion
        # Represent plate as thin lines in x-direction for simplicity like original
        plate_x_thin = [-plate_width / 40, plate_width / 40] # Very thin plate representation
        slit_length = max(plate_width * 0.1, d_m * 0.5 * y_scale_factor)

        # --- 绘制 3D 图 (恢复原始视觉风格) ---
        source_z = -0.1 * D_m # 光源位置
        # 恢复原始 scatter 样式
        self.ax_setup_3d.scatter([0], [0], [source_z], color='yellow', s=100, label='光源 S')

        plate_z = 0 # 双缝板位置
        plate_y_coords = [-plate_width / 2, plate_width / 2]

        # 绘制双缝板框架 (灰色) - 使用细板条X坐标
        self.ax_setup_3d.plot([plate_x_thin[0]]*2, plate_y_coords, [plate_z]*2, color='gray')
        self.ax_setup_3d.plot([plate_x_thin[1]]*2, plate_y_coords, [plate_z]*2, color='gray')
        # Add top and bottom edges for completeness if desired, using thin x coordinates
        self.ax_setup_3d.plot(plate_x_thin, [plate_y_coords[0]]*2, [plate_z]*2, color='gray')
        self.ax_setup_3d.plot(plate_x_thin, [plate_y_coords[1]]*2, [plate_z]*2, color='gray')

        # 绘制双缝 (亮蓝色) - 恢复线宽
        slit_y1_disp = y_display_half_d
        slit_y2_disp = -y_display_half_d
        self.ax_setup_3d.plot([0]*2, [slit_y1_disp - slit_length/2, slit_y1_disp + slit_length/2], [plate_z]*2, color='cyan', linewidth=3) # Original linewidth
        self.ax_setup_3d.plot([0]*2, [slit_y2_disp - slit_length/2, slit_y2_disp + slit_length/2], [plate_z]*2, color='cyan', linewidth=3) # Original linewidth

        # 绘制屏幕 (黑色框架) - 使用细板条X坐标
        screen_z = D_m
        self.ax_setup_3d.plot([plate_x_thin[0]]*2, plate_y_coords, [screen_z]*2, color='black')
        self.ax_setup_3d.plot([plate_x_thin[1]]*2, plate_y_coords, [screen_z]*2, color='black')
        self.ax_setup_3d.plot(plate_x_thin, [plate_y_coords[0]]*2, [screen_z]*2, color='black')
        self.ax_setup_3d.plot(plate_x_thin, [plate_y_coords[1]]*2, [screen_z]*2, color='black')

        # 绘制光轴 (红色虚线) - 恢复线宽
        self.ax_setup_3d.plot([0, 0], [0, 0], [source_z, screen_z], 'r--', linewidth=0.8) # Original linewidth

        # 3D 图设置 (保留字体常量，恢复原始视角，移除网格/面板修改)
        self.ax_setup_3d.set_xlim(x_range)
        self.ax_setup_3d.set_ylim(y_range)
        self.ax_setup_3d.set_zlim(z_range)
        self.ax_setup_3d.set_xlabel("X", fontsize=AXIS_LABEL_FONT_SIZE)
        self.ax_setup_3d.set_ylabel("Y (放大显示)", fontsize=AXIS_LABEL_FONT_SIZE) # Indicate scaling
        self.ax_setup_3d.set_zlabel("Z (光传播方向)", fontsize=AXIS_LABEL_FONT_SIZE)
        self.ax_setup_3d.tick_params(axis='both', which='major', labelsize=TICK_LABEL_FONT_SIZE)
        self.ax_setup_3d.set_title("3D 示意图", fontsize=TITLE_FONT_SIZE)
        # 恢复原始视角
        self.ax_setup_3d.view_init(elev=20., azim=-50) # Original view angle
        # 移除 grid(False) 和 pane 相关修改，恢复默认外观

        # --- 绘制 2D 俯视图 (Z-Y 平面) ---
        # ... (这部分代码保持不变，除非你需要也调整它) ...
        # (确保 2D 图的 y_range_2d 和 plate_z, screen_z 与 3D 匹配)
        y_range_2d = y_range # Use the same calculated Y range for consistency

        # 光源 (黄色圆点)
        self.ax_setup_2d.plot([source_z], [0], 'yo', markersize=8, label='光源 S', markeredgecolor='orange')
        # 双缝板 (灰色线，中心用青色点标示缝位置)
        self.ax_setup_2d.plot([plate_z]*2, y_range_2d, color='gray', linewidth=2, label='双缝板')
        # Plot slits using scaled y, but label with actual d
        self.ax_setup_2d.plot([plate_z]*2, [slit_y1_disp, slit_y2_disp], 'cs', markersize=5, linestyle='') # Cyan squares for slits

        # 标注缝间距 'd' (实际值)
        text_d_y = max(abs(slit_y1_disp), abs(slit_y2_disp)) * 0.5
        self.ax_setup_2d.text(plate_z - 0.02*abs(z_range[1]-z_range[0]), text_d_y, f'd={d_mm:.2f}mm',
                              ha='right', va='center', fontsize=ANNOTATION_FONT_SIZE, rotation=90, color='cyan')

        # 屏幕 (黑色线)
        self.ax_setup_2d.plot([screen_z]*2, y_range_2d, color='black', linewidth=2, label='屏')
        # 标注屏缝距离 'D'
        self.ax_setup_2d.annotate("", xy=(plate_z, y_range_2d[0]*0.9), xytext=(screen_z, y_range_2d[0]*0.9),
                                   arrowprops=dict(arrowstyle='<->', color='blue', lw=1.5))
        self.ax_setup_2d.text((plate_z + screen_z)/2, y_range_2d[0]*0.85, f'D={D_m:.1f}m',
                               ha='center', va='top', color='blue', fontsize=ANNOTATION_FONT_SIZE)

        # 绘制示例光路 (虚线)
        self.ax_setup_2d.plot([source_z, plate_z], [0, slit_y1_disp], 'y--', linewidth=0.8)
        self.ax_setup_2d.plot([source_z, plate_z], [0, slit_y2_disp], 'y--', linewidth=0.8)
        self.ax_setup_2d.plot([plate_z, screen_z], [slit_y1_disp, 0], 'c--', linewidth=0.8)
        self.ax_setup_2d.plot([plate_z, screen_z], [slit_y2_disp, 0], 'c--', linewidth=0.8)
        self.ax_setup_2d.plot([source_z, screen_z], [0, 0], 'r--', linewidth=1, label='光轴')

        # 2D 图设置
        self.ax_setup_2d.set_xlabel("Z (m)", fontsize=AXIS_LABEL_FONT_SIZE)
        self.ax_setup_2d.set_ylabel("Y (m, 放大显示)", fontsize=AXIS_LABEL_FONT_SIZE)
        self.ax_setup_2d.set_ylim(y_range_2d)
        self.ax_setup_2d.set_xlim(z_range)
        self.ax_setup_2d.set_aspect('auto')
        self.ax_setup_2d.set_title("2D 俯视图 (Z-Y 平面)", fontsize=TITLE_FONT_SIZE)
        self.ax_setup_2d.grid(True, linestyle=':', alpha=0.6) # 保持网格
        self.ax_setup_2d.tick_params(axis='both', which='major', labelsize=TICK_LABEL_FONT_SIZE)

        # 强制画布重绘
        self.canvas_setup.draw_idle()

    def update_fringe_display(self, x_coords_mm: np.ndarray, intensity: np.ndarray, lambda_nm: float, calculation_ok: bool):
        """更新干涉条纹图像显示。"""
        # 移除旧指示点 (防御性)
        if self._click_indicator_fringe:
            try: self._click_indicator_fringe.remove()
            except (ValueError, AttributeError): pass
            self._click_indicator_fringe = None

        self.ax_fringe.clear() # 清除旧图像

        if not calculation_ok:
             # 在图像中心显示错误信息
             self.ax_fringe.text(0.5, 0.5, '计算错误', ha='center', va='center',
                                 fontsize=TITLE_FONT_SIZE, color='red', transform=self.ax_fringe.transAxes)
             self.ax_fringe.set_xticks([]) # 隐藏刻度
             self.ax_fringe.set_yticks([])
        else:
            # 创建条纹图像数据 (将一维强度复制多行)
            fringe_height_pixels = 50 # 图像的高度（像素）
            # 确保 intensity 是 1D array
            if intensity.ndim > 1: intensity = intensity.flatten()
            # 处理 intensity 可能为空的情况
            if intensity.size == 0:
                 self.ax_fringe.text(0.5, 0.5, '无数据', ha='center', va='center', fontsize=ANNOTATION_FONT_SIZE, transform=self.ax_fringe.transAxes)
                 self.ax_fringe.set_xticks([])
                 self.ax_fringe.set_yticks([])
            else:
                 img_data = np.tile(intensity, (fringe_height_pixels, 1))
                 # 获取对应波长的颜色映射 (黑 -> R,G,B)
                 cmap = self.get_wavelength_colormap(lambda_nm)
                 # 确定图像范围
                 extent = [x_coords_mm.min(), x_coords_mm.max(), 0, fringe_height_pixels]
                 # 显示图像
                 self.ax_fringe.imshow(img_data, cmap=cmap, aspect='auto', extent=extent,
                                     interpolation='bilinear', vmin=0, vmax=1) # 双线性插值使边缘平滑
                 self.ax_fringe.set_yticks([]) # 隐藏 Y 轴刻度
                 self.ax_fringe.set_xlim(extent[0], extent[1]) # 设置 X 轴范围
                 self.ax_fringe.tick_params(axis='x', which='major', labelsize=TICK_LABEL_FONT_SIZE)

        # --- 设置标题和标签 ---
        self.ax_fringe.set_title("干涉条纹 (模拟)", fontsize=TITLE_FONT_SIZE)
        # Conditionally set xlabel only if calculation was ok and we have ticks
        if calculation_ok and intensity.size > 0 :
            self.ax_fringe.set_xlabel("屏幕位置 x (mm)", fontsize=AXIS_LABEL_FONT_SIZE)
        else:
            self.ax_fringe.set_xlabel("") # No label if no ticks

    def update_intensity_plot(self, x_coords_mm: np.ndarray, intensity: np.ndarray, lambda_nm: float, calculation_ok: bool):
        """更新光强分布曲线图。"""
        # 移除旧指示点 (防御性)
        if self._click_indicator_plot:
            try: self._click_indicator_plot.remove()
            except (ValueError, AttributeError): pass
            self._click_indicator_plot = None

        self.ax_plot.clear() # 清除旧曲线

        if not calculation_ok:
            # 显示错误信息
            self.ax_plot.text(0.5, 0.5, '计算错误', ha='center', va='center',
                              fontsize=TITLE_FONT_SIZE, color='red', transform=self.ax_plot.transAxes)
            self.ax_plot.set_xticks([]) # 隐藏刻度
            self.ax_plot.set_yticks([])
        else:
             # 检查是否有数据
             if intensity.size == 0 or x_coords_mm.size == 0:
                  self.ax_plot.text(0.5, 0.5, '无数据', ha='center', va='center', fontsize=ANNOTATION_FONT_SIZE, transform=self.ax_plot.transAxes)
                  self.ax_plot.set_xticks([])
                  self.ax_plot.set_yticks([])
             else:
                 # 获取对应波长的颜色
                 plot_color = wavelength_to_rgb(lambda_nm)
                 # 绘制光强曲线
                 self.ax_plot.plot(x_coords_mm, intensity, color=plot_color, lw=1.5) # 线宽适中

                 # --- 设置坐标轴、网格和标签 ---
                 self.ax_plot.set_ylim(-0.05, 1.1) # Y 轴留一点边距
                 self.ax_plot.grid(True, linestyle=':', alpha=0.7) # 更淡的网格线
                 self.ax_plot.tick_params(axis='both', which='major', labelsize=TICK_LABEL_FONT_SIZE)
                 # Ensure X axis range matches the data
                 self.ax_plot.set_xlim(x_coords_mm.min(), x_coords_mm.max())

        # 统一设置标题和轴标签 (无论成功与否)
        self.ax_plot.set_title("相对光强分布", fontsize=TITLE_FONT_SIZE)
        # Conditionally set labels only if calculation was ok and we have ticks
        if calculation_ok and intensity.size > 0:
             self.ax_plot.set_xlabel("屏幕位置 x (mm)", fontsize=AXIS_LABEL_FONT_SIZE)
             self.ax_plot.set_ylabel("相对光强 I/Imax", fontsize=AXIS_LABEL_FONT_SIZE)
        else:
             self.ax_plot.set_xlabel("")
             self.ax_plot.set_ylabel("")

        # 在所有绘图更新后，统一调用 draw_idle
        # (update_simulation 最后已经调用了，这里重复调用是为了确保独立更新也能生效)
        self.canvas_fringe.draw_idle()

    def get_wavelength_colormap(self, lambda_nm: float):
        """
        根据波长返回一个从黑色到对应可见光颜色的 Matplotlib Colormap 对象。
        如果颜色太暗或无效，则返回灰度图。
        """
        target_rgb = wavelength_to_rgb(lambda_nm)
        # 如果计算出的颜色非常接近黑色 (例如波长超出可见光范围很多)
        # 或亮度很低，使用灰度图代替，避免全黑图像
        brightness_threshold = 0.05
        if sum(target_rgb) < brightness_threshold:
            # print(f"波长 {lambda_nm}nm 颜色过暗，使用灰度图。") # Debugging info
            return plt.get_cmap('gray')

        # 创建从黑色 (0,0,0) 到目标颜色 (R,G,B) 的线性渐变 Colormap
        try:
            custom_cmap = mcolors.LinearSegmentedColormap.from_list(
                f"custom_wavelength_{lambda_nm}", [(0, 0, 0), target_rgb]
            )
            return custom_cmap
        except Exception as e:
             print(f"创建颜色映射时出错 for {lambda_nm}nm: {e}. 返回灰度图。")
             return plt.get_cmap('gray')

# --- 主程序入口 ---
if __name__ == "__main__":
    root = tk.Tk()

    # 可选：设置应用程序图标
    # 需要一个 .ico 文件 (Windows) 或 .png/.gif (某些Linux/macOS环境)
    # 确保图标文件与脚本在同一目录或提供完整路径
    # 如果使用 PyInstaller 打包，需要将图标文件包含在内
    # ICON_PATH = 'app_icon.ico' # 或者 'app_icon.png'
    # try:
    #     if sys.platform.startswith('win'):
    #          if os.path.exists(ICON_PATH): root.iconbitmap(ICON_PATH)
    #     else:
    #          # 对于 Linux/macOS, Tkinter 支持 PhotoImage
    #          # 但设置窗口图标可能需要特定平台的库或方法
    #          if os.path.exists(ICON_PATH):
    #              img = tk.PhotoImage(file=ICON_PATH)
    #              # The following line might work on some systems/window managers
    #              # root.tk.call('wm', 'iconphoto', root._w, img)
    #              # On others, you might need external libraries like PIL/Pillow
    #              print(f"尝试设置图标 ({ICON_PATH})，但在非 Windows 平台上可能不生效。")
    # except Exception as e:
    #     print(f"设置应用程序图标失败: {e}")

    app = InterferenceSimulatorApp(root)
    root.mainloop()