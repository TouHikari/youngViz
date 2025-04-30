# youngViz/gui/main_window.py
import tkinter as tk
from tkinter import ttk
import numpy as np

# 尝试导入 SciPy 用于峰值查找
try:
    from scipy.signal import find_peaks
    SCIPY_AVAILABLE = True
    print("信息: SciPy 库已找到，将启用条纹间距自动测量。")
except ImportError:
    print("提示：未找到 SciPy 库。条纹间距自动测量功能将不可用。")
    print("     如需此功能，请运行 'pip install scipy'")
    find_peaks = None # 定义为 None 以便后续检查
    SCIPY_AVAILABLE = False

# 导入项目内的模块
from .. import config
from .. import simulation
from ..plotting import PlotManager # 导入绘图管理器
from .control_panel import ControlPanel # 导入控制面板
from .matplotlib_widget import MatplotlibWidget # 导入 Matplotlib 控件

class MainWindow:
    """应用程序的主窗口类，负责整合 UI 和逻辑。"""

    def __init__(self, master: tk.Tk):
        """
        初始化主窗口。

        Args:
            master (tk.Tk): Tkinter 的根窗口。
        """
        self.master = master
        master.title("杨氏双缝干涉模拟器")
        master.geometry("1150x850") # 初始窗口大小

        # --- 数据模型和状态 ---
        self._last_params_mks = {}          # 缓存上次计算使用的 MKS 参数，用于优化
        self._last_x_coords_mm = None       # 缓存上次计算的 X 坐标 (mm)
        self._last_intensity = None         # 缓存上次计算的光强

        # --- 创建核心组件 ---
        self.plot_manager = PlotManager() # 创建绘图管理器实例

        # --- 创建 GUI 布局 ---
        main_frame = ttk.Frame(master, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧：控制面板
        self.control_panel = ControlPanel(main_frame, update_callback=self.update_simulation)
        self.control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=5, anchor='nw')

        # 右侧：显示区域 (包含两个绘图控件)
        right_display_frame = ttk.Frame(main_frame)
        right_display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=5)
        right_display_frame.rowconfigure(0, weight=1) # 让示意图区域可扩展
        right_display_frame.rowconfigure(1, weight=1) # 让干涉图区域可扩展
        right_display_frame.columnconfigure(0, weight=1)

        # 右上：实验装置示意图
        setup_frame = ttk.LabelFrame(right_display_frame, text="实验装置示意图", padding=10)
        setup_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        self.setup_plot_widget = MatplotlibWidget(setup_frame, self.plot_manager.fig_setup, show_toolbar=False)
        self.setup_plot_widget.pack(fill=tk.BOTH, expand=True)

        # 右下：干涉结果图 (自带工具栏)
        fringe_frame = ttk.LabelFrame(right_display_frame, text="干涉结果", padding=10)
        fringe_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        self.fringe_plot_widget = MatplotlibWidget(fringe_frame, self.plot_manager.fig_fringe, show_toolbar=True)
        self.fringe_plot_widget.pack(fill=tk.BOTH, expand=True)

        # --- 绑定事件 ---
        # 连接干涉结果图区域的点击事件
        self.fringe_plot_widget.connect_event('button_press_event', self.on_plot_click)

        # --- 初始化显示 ---
        # 控制面板的标签已在内部初始化
        self.update_simulation(force_redraw=True) # 执行第一次模拟计算和绘图，强制绘制所有图表

    def update_simulation(self, force_redraw=False):
        """
        核心更新函数：获取参数、执行模拟计算、更新所有图表和分析信息。

        Args:
            force_redraw (bool): 是否强制重绘所有图表，即使参数未改变。
                                  (例如，初始化时或窗口大小改变需要重绘时)
        """
        # 1. 从控制面板获取当前参数 (MKS 单位)
        current_params_mks = self.control_panel.get_parameters_mks()
        lambda_m = current_params_mks['lambda_m']
        d_m = current_params_mks['d_m']
        cap_d_m = current_params_mks['cap_d_m']

        # 2. 优化：检查参数是否改变
        params_changed = current_params_mks != self._last_params_mks
        # 示意图参数 (d, D) 是否改变
        setup_params_changed = (self._last_params_mks.get('d_m') != d_m or
                                self._last_params_mks.get('cap_d_m') != cap_d_m)

        # 如果没有强制重绘，且参数未改变，则跳过大部分更新
        if not force_redraw and not params_changed:
            # print("调试: 参数未改变，跳过模拟计算和主要绘图。") # 调试信息
            return

        # 3. 执行干涉计算
        # print(f"调试: 参数改变或强制刷新，执行模拟 lambda={lambda_m}, d={d_m}, D={cap_d_m}") # 调试信息
        result = simulation.calculate_intensity(lambda_m, d_m, cap_d_m)

        calculation_ok = False
        if result:
            self._last_x_coords_mm, self._last_intensity = result
            calculation_ok = True
        else:
            # 计算失败，清除缓存数据
            self._last_x_coords_mm = None
            self._last_intensity = None
            calculation_ok = False
            # 重置分析标签
            self.control_panel.update_analysis_labels("计算错误", "N/A")
            self.control_panel.reset_point_info_label() # 清除旧的点击信息

        # 4. 更新干涉图样和光强曲线图
        # 需要获取 GUI 单位用于颜色
        lambda_nm_val = self.control_panel.lambda_nm.get()
        self.plot_manager.update_fringe_display(self._last_x_coords_mm, self._last_intensity, lambda_nm_val)
        self.plot_manager.update_intensity_plot(self._last_x_coords_mm, self._last_intensity, lambda_nm_val)
        self.plot_manager.redraw_canvas_fringe() # 触发干涉结果画布重绘

        # 5. 计算和更新条纹间距 (仅当计算成功时)
        if calculation_ok:
            theoretical_spacing_mm = simulation.calculate_fringe_spacing(lambda_m, d_m, cap_d_m)
            measured_spacing_str = self._measure_fringe_spacing() # 尝试测量

            # 格式化理论间距字符串
            if theoretical_spacing_mm is None:
                 theoretical_spacing_str = "计算错误"
            elif np.isinf(theoretical_spacing_mm):
                 theoretical_spacing_str = "∞ mm"
            else:
                  theoretical_spacing_str = f"{theoretical_spacing_mm:.3f} mm"

            # 更新控制面板上的分析标签
            self.control_panel.update_analysis_labels(theoretical_spacing_str, measured_spacing_str)
        # else: # calculation_ok is False, labels already reset

        # 6. 更新装置示意图 (仅当相关参数改变或强制刷新时)
        if setup_params_changed or force_redraw:
             # 获取 GUI 单位传入绘图函数
             d_mm_val = self.control_panel.d_mm.get()
             cap_d_m_val = self.control_panel.D_m.get()
             self.plot_manager.update_setup_plots(d_mm_val, cap_d_m_val)
             self.plot_manager.redraw_canvas_setup() # 触发装置示意图画布重绘

        # 7. 缓存当前 MKS 参数
        self._last_params_mks = current_params_mks

    def _measure_fringe_spacing(self) -> str:
        """
        尝试使用 SciPy 测量光强峰值间距。

        Returns:
            str: 测量结果的文本描述 (例如 "0.531 mm", "峰值不足", "需要 SciPy")。
        """
        if not SCIPY_AVAILABLE:
            return "需要 SciPy"
        if self._last_intensity is None or self._last_x_coords_mm is None or self._last_intensity.size < 2:
             return "无有效数据"

        try:
            # 使用 find_peaks 寻找强度峰值
            # prominence 参数有助于过滤掉噪声引起的小峰值
            peaks_indices, _ = find_peaks(self._last_intensity, prominence=config.PEAK_FINDING_PROMINENCE)

            if len(peaks_indices) >= 2:
                # 计算峰值位置 (mm)
                peak_positions_mm = self._last_x_coords_mm[peaks_indices]
                # 计算相邻峰值之间的间距
                spacings = np.diff(peak_positions_mm)
                # 计算平均间距
                measured_spacing = np.mean(spacings)
                return f"{measured_spacing:.3f} mm"
            elif len(peaks_indices) < 2:
                return "峰值不足"
            else: # Should not happen if find_peaks ran
                 return "测量失败"

        except Exception as e:
            print(f"错误: 测量条纹间距时发生异常: {e}")
            return "测量错误"

    def on_plot_click(self, event):
        """
        处理在干涉结果图区域（条纹或曲线）的点击事件。
        """
        # 1. 检查点击是否在有效的 Axes 内
        if event.inaxes not in [self.plot_manager.ax_fringe, self.plot_manager.ax_plot] or event.xdata is None:
            # print("调试: 点击在绘图区域之外。")
            return # 点击无效

        # print(f"调试: 点击事件发生在 {event.inaxes} at x={event.xdata}") # 调试信息

        # 2. 在图上绘制指示点，并获取点击的 x 坐标 (mm)
        x_click_mm = self.plot_manager.draw_click_indicator(event, self._last_x_coords_mm, self._last_intensity)
        self.plot_manager.redraw_canvas_fringe() # 重绘以显示指示点

        if x_click_mm is None: # 如果 draw_click_indicator 未返回有效坐标
             self.control_panel.reset_point_info_label() # 重置信息
             return

        # 3. 获取当前计算所需的参数 (MKS)
        params_mks = self.control_panel.get_parameters_mks()
        lambda_m = params_mks['lambda_m']
        d_m = params_mks['d_m']
        cap_d_m = params_mks['cap_d_m']

        # 4. 计算光程差和相位差
        path_diff_m, phase_diff_rad = simulation.calculate_path_phase_diff(
            x_click_mm, d_m, cap_d_m, lambda_m
        )

        # 5. 格式化输出字符串
        x_str = f"{x_click_mm:.3f} mm"
        if path_diff_m is not None:
            delta_str = f"{path_diff_m:.3e} m" #科学计数法
        else:
            delta_str = "计算错误"

        if phase_diff_rad is not None:
            delta_phi_str = f"{phase_diff_rad:.2f} rad ({phase_diff_rad / np.pi:.2f}π)" # 弧度和π倍数
        else:
            delta_phi_str = "计算错误"

        # 6. 更新控制面板上的信息标签
        self.control_panel.update_point_info_label(x_str, delta_str, delta_phi_str)