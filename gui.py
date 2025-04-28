import tkinter as tk
from tkinter import ttk, font as tkFont # 导入 tkFont
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.colors as mcolors
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
try:
    from scipy.signal import find_peaks
except ImportError:
    print("错误：需要安装 SciPy 库才能使用条纹间距测量功能。请运行 'pip install scipy'")
    find_peaks = None

import calculation as calc

# --- Font Configuration ---
# 定义一些常用的字体大小 (保持不变)
TITLE_FONT_SIZE = 14
AXIS_LABEL_FONT_SIZE = 12
TICK_LABEL_FONT_SIZE = 10
ANNOTATION_FONT_SIZE = 10
BUTTON_FONT_SIZE = 11
LABEL_FONT_SIZE = 12
FRAME_TITLE_FONT_SIZE = 13

# --- 配置 Matplotlib 字体 ---
# 直接尝试设置 SimHei，如果失败则打印警告
# 这个设置应该在创建 Figure 之前生效
try:
    plt.rcParams['font.family'] = 'SimHei'
    # 如果 SimHei 设置成功，下面的设置确保负号也能正确显示
    plt.rcParams['axes.unicode_minus'] = False
    print("Matplotlib 字体尝试设置为 SimHei。")
except Exception as e:
    print(f"警告：设置 Matplotlib 字体为 'SimHei' 失败: {e}")
    print("Matplotlib 图中的中文可能无法显示。请确保已安装 SimHei 字体，或尝试安装其他中文字体（如 Microsoft YaHei）并修改代码。")
    # 在 SimHei 失败时，仍然设置 unicode_minus
    plt.rcParams['axes.unicode_minus'] = False

# --- 其他函数 (wavelength_to_rgb 不变) ---
def wavelength_to_rgb(wavelength_nm):
    # ... (代码不变) ...
    w = float(wavelength_nm)
    R, G, B = 0.0, 0.0, 0.0
    if 380 <= w < 440: R = -(w - 440) / (440 - 380); G = 0.0; B = 1.0
    elif 440 <= w < 490: R = 0.0; G = (w - 440) / (490 - 440); B = 1.0
    elif 490 <= w < 510: R = 0.0; G = 1.0; B = -(w - 510) / (510 - 490)
    elif 510 <= w < 580: R = (w - 510) / (580 - 510); G = 1.0; B = 0.0
    elif 580 <= w < 645: R = 1.0; G = -(w - 645) / (645 - 580); B = 0.0
    elif 645 <= w <= 750: R = 1.0; G = 0.0; B = 0.0
    factor = 0.0
    if 380 <= w < 420: factor = 0.3 + 0.7 * (w - 380) / (420 - 380)
    elif 420 <= w < 645: factor = 1.0
    elif 645 <= w <= 750: factor = 0.3 + 0.7 * (750 - w) / (750 - 645)
    gamma = 0.8
    R = pow(R * factor, gamma) if R > 0 else 0
    G = pow(G * factor, gamma) if G > 0 else 0
    B = pow(B * factor, gamma) if B > 0 else 0
    return (np.clip(R, 0, 1), np.clip(G, 0, 1), np.clip(B, 0, 1))

class InterferenceSimulatorApp:
    def __init__(self, master):
        self.master = master
        master.title("杨氏双缝干涉模拟器 V4")
        master.geometry("1150x850")

        # --- 配置 TTK 样式 ---
        style = ttk.Style()

        # 尝试获取 Tkinter 默认字体或备用字体
        # 这个需要在 root 窗口创建后进行，所以放在 __init__ 里
        try:
            # 检查 SimHei 是否真的可用于 Tkinter
            root_fonts = tkFont.families(master) # 使用 master (即 root)
            if 'SimHei' in root_fonts:
                DEFAULT_TK_FONT = 'SimHei'
                print("Tkinter 控件将尝试使用 SimHei 字体。")
            else:
                print("警告：在 Tkinter 中未找到 SimHei，控件将使用默认字体或 Arial。")
                DEFAULT_TK_FONT = 'Arial' # 回退到 Arial 或其他安全字体
        except Exception as e:
             print(f"检查 Tkinter 字体时出错: {e}. 控件将使用默认字体或 Arial。")
             DEFAULT_TK_FONT = 'Arial' # 最终回退

        # 配置控件字体大小 (使用刚刚确定的 DEFAULT_TK_FONT)
        style.configure('TLabel', font=(DEFAULT_TK_FONT, LABEL_FONT_SIZE))
        style.configure('TButton', font=(DEFAULT_TK_FONT, BUTTON_FONT_SIZE))
        style.configure('TLabelframe.Label', font=(DEFAULT_TK_FONT, FRAME_TITLE_FONT_SIZE, 'bold'))

        # --- 数据模型 (保持不变) ---
        self.lambda_nm = tk.DoubleVar(value=calc.DEFAULT_LAMBDA_NM / 1e-9)
        self.d_mm = tk.DoubleVar(value=calc.DEFAULT_D_MM / 1e-3)
        self.D_m = tk.DoubleVar(value=calc.DEFAULT_CAP_D_M)
        self._last_intensity_data = None
        self._last_x_coords_mm = None
        self._last_params = {}
        # --- 点击指示器对象 ---
        self._click_indicator_fringe = None
        self._click_indicator_plot = None

        # --- 创建主框架 (保持不变) ---
        main_frame = ttk.Frame(master, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 左侧：控制面板 (布局不变) ---
        control_frame = ttk.LabelFrame(main_frame, text="参数设置与分析", padding="15")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        # ... (控件布局代码保持之前版本不变) ...
        current_row = 0
        pady_val = 4
        ttk.Label(control_frame, text="波长 λ (nm):").grid(row=current_row, column=0, sticky="w", pady=pady_val)
        self.lambda_label = ttk.Label(control_frame, text=f"{self.lambda_nm.get():.0f} nm", anchor='e')
        self.lambda_label.grid(row=current_row, column=1, sticky="ew", pady=pady_val)
        current_row += 1
        self.lambda_scale = ttk.Scale(control_frame, from_=380, to=750, orient=tk.HORIZONTAL, variable=self.lambda_nm, command=self.update_simulation)
        self.lambda_scale.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=(pady_val, pady_val+5))
        if not (380 <= self.lambda_nm.get() <= 750): self.lambda_nm.set(550.0)
        current_row += 1
        preset_button_frame = ttk.Frame(control_frame)
        preset_button_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=(0, pady_val+10))
        preset_button_frame.columnconfigure((0,1,2), weight=1)
        red_button = ttk.Button(preset_button_frame, text="红(650)", command=lambda: self.set_wavelength(650.0))
        green_button = ttk.Button(preset_button_frame, text="绿(550)", command=lambda: self.set_wavelength(550.0))
        blue_button = ttk.Button(preset_button_frame, text="蓝(450)", command=lambda: self.set_wavelength(450.0))
        red_button.grid(row=0, column=0, sticky='ew', padx=2)
        green_button.grid(row=0, column=1, sticky='ew', padx=2)
        blue_button.grid(row=0, column=2, sticky='ew', padx=2)
        current_row += 1
        ttk.Label(control_frame, text="缝间距 d (mm):").grid(row=current_row, column=0, sticky="w", pady=pady_val)
        self.d_label = ttk.Label(control_frame, text=f"{self.d_mm.get():.2f} mm", anchor='e')
        self.d_label.grid(row=current_row, column=1, sticky="ew", pady=pady_val)
        current_row += 1
        self.d_scale = ttk.Scale(control_frame, from_=0.01, to=1.0, orient=tk.HORIZONTAL, variable=self.d_mm, command=self.update_simulation)
        self.d_scale.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=pady_val)
        current_row += 1
        ttk.Label(control_frame, text="屏缝距离 D (m):").grid(row=current_row, column=0, sticky="w", pady=pady_val)
        self.D_label = ttk.Label(control_frame, text=f"{self.D_m.get():.1f} m", anchor='e')
        self.D_label.grid(row=current_row, column=1, sticky="ew", pady=pady_val)
        current_row += 1
        self.D_scale = ttk.Scale(control_frame, from_=0.1, to=5.0, orient=tk.HORIZONTAL, variable=self.D_m, command=self.update_simulation)
        self.D_scale.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=pady_val)
        current_row += 1
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).grid(row=current_row, column=0, columnspan=2, sticky='ew', pady=pady_val+10)
        current_row += 1
        self.spacing_comparison_label = ttk.Label(control_frame, text="理论间距 Δx:\n测量间距 Δx_m:", justify=tk.LEFT)
        self.spacing_comparison_label.grid(row=current_row, column=0, columnspan=2, sticky="w", pady=pady_val)
        current_row += 1
        self.point_info_label = ttk.Label(control_frame, text="点击下方图形获取点信息:\nx=\nδ=\nΔΦ=", justify=tk.LEFT)
        self.point_info_label.grid(row=current_row, column=0, columnspan=2, sticky="w", pady=pady_val)
        current_row += 1

        # --- 右侧：显示区域 (保持不变) ---
        right_display_frame = ttk.Frame(main_frame)
        right_display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # --- 右上：实验装置示意图区域 (保持不变) ---
        setup_frame = ttk.LabelFrame(right_display_frame, text="实验装置示意图", padding=10)
        setup_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.fig_setup = Figure(figsize=(6, 4), dpi=100)
        self.ax_setup_3d = self.fig_setup.add_subplot(1, 2, 1, projection='3d')
        self.ax_setup_2d = self.fig_setup.add_subplot(1, 2, 2)
        self.fig_setup.subplots_adjust(left=0.05, right=0.95, bottom=0.1, top=0.9, wspace=0.4, hspace=0.3)
        self.canvas_setup = FigureCanvasTkAgg(self.fig_setup, master=setup_frame)
        self.canvas_setup_widget = self.canvas_setup.get_tk_widget()
        self.canvas_setup_widget.pack(fill=tk.BOTH, expand=True)

        # --- 右下：干涉图样和光强曲线区域 (保持不变) ---
        fringe_frame = ttk.LabelFrame(right_display_frame, text="干涉结果", padding=10)
        fringe_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        self.fig_fringe = Figure(figsize=(6, 4), dpi=100)
        self.ax_fringe = self.fig_fringe.add_subplot(2, 1, 1)
        self.ax_plot = self.fig_fringe.add_subplot(2, 1, 2)
        self.fig_fringe.tight_layout(pad=3.0, h_pad=2.0)
        self.canvas_fringe = FigureCanvasTkAgg(self.fig_fringe, master=fringe_frame)
        self.canvas_fringe_widget = self.canvas_fringe.get_tk_widget()
        self.canvas_fringe_widget.pack(fill=tk.BOTH, expand=True)
        toolbar_frame = ttk.Frame(fringe_frame)
        toolbar_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.toolbar = NavigationToolbar2Tk(self.canvas_fringe, toolbar_frame)
        self.toolbar.update()

        # --- 绑定和初始化 (保持不变) ---
        self.lambda_nm.trace_add("write", self.update_labels_and_trigger_sim)
        self.d_mm.trace_add("write", self.update_labels_and_trigger_sim)
        self.D_m.trace_add("write", self.update_labels_and_trigger_sim)

        self.canvas_fringe.mpl_connect('button_press_event', self.on_plot_click)

        self.update_labels()
        self.update_simulation()

    # --- 事件处理与更新逻辑 ---
    def update_labels_and_trigger_sim(self, *args):
        self.update_labels()
        self.update_simulation()

    def set_wavelength(self, wavelength_nm):
        current_lambda = self.lambda_nm.get()
        if abs(current_lambda - wavelength_nm) > 1e-6:
            self.lambda_nm.set(wavelength_nm)
            # trace 会自动触发 update_labels_and_trigger_sim

    def update_labels(self, *args):
        # ... (代码不变, 字体大小由Style控制) ...
         try:
            lambda_val = self.lambda_nm.get()
            d_val = self.d_mm.get()
            D_val = self.D_m.get()

            self.lambda_label.config(text=f"{lambda_val:.0f} nm")
            self.d_label.config(text=f"{d_val:.2f} mm")
            self.D_label.config(text=f"{D_val:.1f} m")
         except tk.TclError: pass
         except Exception as e: print(f"更新标签时出错: {e}")

    def update_simulation(self, *args):
        """核心函数：重新计算并更新所有显示"""
        # --- 移除旧的点击指示器 ---
        if self._click_indicator_fringe:
            self._click_indicator_fringe.remove()
            self._click_indicator_fringe = None
        if self._click_indicator_plot:
            self._click_indicator_plot.remove()
            self._click_indicator_plot = None

        try:
            lambda_nm_val = self.lambda_nm.get()
            d_mm_val = self.d_mm.get()
            D_m_val = self.D_m.get()
        except tk.TclError: return
        except Exception as e: print(f"获取参数值时出错: {e}"); return

        current_params = {'lambda': lambda_nm_val, 'd': d_mm_val, 'D': D_m_val}
        # 优化：检查参数是否实际变化，如果仅lambda变化，则无需重绘示意图
        params_changed = current_params != self._last_params
        setup_params_changed = (self._last_params.get('d') != d_mm_val or
                                self._last_params.get('D') != D_m_val)

        # 如果没有任何参数变化（包括点击触发的重算），则返回
        if not params_changed and 'click' not in args: #  允许点击强制重绘
             return

        # --- 计算干涉 ---
        try:
            x_coords_mm, intensity = calc.calculate_intensity(lambda_nm_val, d_mm_val, D_m_val)
            self._last_x_coords_mm = x_coords_mm
            self._last_intensity_data = intensity
            calculation_ok = True
        except Exception as e:
            print(f"计算过程中出错: {e}")
            x_coords_mm = calc.x_coords_mm # 保留坐标轴范围
            intensity = np.zeros_like(x_coords_mm)
            self._last_x_coords_mm = None
            self._last_intensity_data = None
            calculation_ok = False

        # --- 更新理论/测量间距 (放在这里确保使用最新的计算结果) ---
        measured_spacing_str = "N/A mm"
        theoretical_spacing_str = "N/A mm"
        try:
            delta_x_theory = calc.calculate_fringe_spacing(lambda_nm_val, d_mm_val, D_m_val)
            if delta_x_theory == float('inf'): theoretical_spacing_str = "∞ mm"
            else: theoretical_spacing_str = f"{delta_x_theory:.3f} mm"

            if calculation_ok and self._last_intensity_data is not None and find_peaks:
                 peaks_indices, _ = find_peaks(self._last_intensity_data, prominence=0.1)
                 if len(peaks_indices) >= 2:
                     peak_positions_mm = self._last_x_coords_mm[peaks_indices]
                     spacings = np.diff(peak_positions_mm)
                     measured_spacing = np.mean(spacings)
                     measured_spacing_str = f"{measured_spacing:.3f} mm"
                 elif len(peaks_indices) < 2 and len(self._last_intensity_data) > 0:
                     measured_spacing_str = "峰值不足"
                 else:
                      measured_spacing_str = "无数据"

        except Exception as e:
            print(f"计算间距时出错: {e}")
            measured_spacing_str = "错误"
            theoretical_spacing_str = "错误"
        self.spacing_comparison_label.config(text=f"理论间距 Δx: {theoretical_spacing_str}\n测量间距 Δx_m: {measured_spacing_str}")

        # --- 更新示意图 (仅当 d 或 D 变化时) ---
        if setup_params_changed or not self._last_params:
            self.update_setup_plots(d_mm_val, D_m_val)

        # --- 更新干涉图 (如果计算成功或参数改变) ---
        # 强制更新以清除旧的指示器
        self.update_fringe_display(x_coords_mm, intensity, lambda_nm_val, calculation_ok)
        self.update_intensity_plot(x_coords_mm, intensity, lambda_nm_val, calculation_ok)
        # if calculation_ok or params_changed: # 原逻辑
        #      self.update_fringe_display(x_coords_mm, intensity, lambda_nm_val, calculation_ok)
        #      self.update_intensity_plot(x_coords_mm, intensity, lambda_nm_val, calculation_ok)
        # elif not calculation_ok:
        #      self.clear_fringe_plots_on_error() # 清除错误现在包含在update函数内部

        # 保存当前参数
        self._last_params = current_params

    def on_plot_click(self, event):
        """处理在干涉图区域的点击事件，并显示红点指示"""
        # --- 移除旧的指示器 ---
        if self._click_indicator_fringe:
            try: self._click_indicator_fringe.remove()
            except ValueError: pass # 可能已被移除
            self._click_indicator_fringe = None
        if self._click_indicator_plot:
            try: self._click_indicator_plot.remove()
            except ValueError: pass
            self._click_indicator_plot = None

        x_click_mm = event.xdata
        y_click = event.ydata # ydata 对 fringe 图有用

        # 检查点击是否在指定的 Axes 内且坐标有效
        target_ax = None
        if event.inaxes == self.ax_fringe and x_click_mm is not None and y_click is not None:
            target_ax = self.ax_fringe
        elif event.inaxes == self.ax_plot and x_click_mm is not None:
            target_ax = self.ax_plot
        else:
            return # 点击无效或在 Axes 之外

        # --- 计算点信息 ---
        try:
            lambda_nm = self.lambda_nm.get()
            d_mm = self.d_mm.get()
            D_m = self.D_m.get()
        except tk.TclError: return

        x_m = x_click_mm * 1e-3
        lambda_ = lambda_nm * 1e-9
        d = d_mm * 1e-3
        D = D_m

        delta_str = "N/A m"
        delta_phi_str = "N/A rad"
        try:
            if D == 0: raise ZeroDivisionError("屏缝距离 D 不能为零")
            delta = (d * x_m) / D
            delta_str = f"{delta:.3e} m"
            if lambda_ == 0: raise ZeroDivisionError("波长 λ 不能为零")
            delta_phi = (2 * np.pi * delta) / lambda_
            delta_phi_str = f"{delta_phi:.2f} rad ({delta_phi/np.pi:.2f}π)" # 同时显示 pi 的倍数
        except ZeroDivisionError as zde: print(f"计算光程/相位差时出错: {zde}")
        except Exception as e: print(f"计算光程/相位差时发生未知错误: {e}")

        # --- 更新信息标签 ---
        info_text = (
            f"点击位置:\n"
            f"  x = {x_click_mm:.3f} mm\n"
            f"光程差:\n"
            f"  δ = {delta_str}\n"
            f"相位差:\n"
            f"  ΔΦ = {delta_phi_str}"
        )
        self.point_info_label.config(text=info_text)

        # --- 绘制红点指示器 ---
        dot_size = 6 # 红点大小
        if target_ax == self.ax_fringe:
            # 直接在点击位置绘图
            self._click_indicator_fringe = self.ax_fringe.plot(x_click_mm, y_click, 'ro', markersize=dot_size)[0]
        elif target_ax == self.ax_plot:
            # 插值计算曲线上的 Y 值
            if self._last_x_coords_mm is not None and self._last_intensity_data is not None:
                try:
                    # 限制 x_click_mm 在数据范围内
                    x_clamped = np.clip(x_click_mm, self._last_x_coords_mm.min(), self._last_x_coords_mm.max())
                    y_intensity = np.interp(x_clamped, self._last_x_coords_mm, self._last_intensity_data)
                    self._click_indicator_plot = self.ax_plot.plot(x_clamped, y_intensity, 'ro', markersize=dot_size)[0]
                except Exception as e:
                    print(f"插值或绘制曲线红点时出错: {e}")

        # --- 重绘画布以显示红点 ---
        self.canvas_fringe.draw_idle()

    # --- 更新绘图函数（增加字体大小） ---

    def update_setup_plots(self, d_mm, D_m):
        """更新 3D 和 2D 实验装置示意图，并调整字体大小"""
        d = d_mm * 1e-3; D = D_m
        self.ax_setup_3d.cla(); self.ax_setup_2d.cla()
        # ... (范围和尺寸计算保持不变) ...
        z_range = (-0.2 * D, 1.1 * D)
        y_scale_factor = 50
        y_display_half_d = d / 2 * y_scale_factor
        y_range = (-max(0.01 * D, y_display_half_d * 2), max(0.01 * D, y_display_half_d * 2))
        x_range = y_range
        plate_width = y_range[1] * 1.8
        slit_length = max(plate_width * 0.1, d * 0.001)

        # 3D
        source_z = -0.1 * D
        self.ax_setup_3d.scatter([0], [0], [source_z], color='yellow', s=100, label='光源 S')
        plate_z = 0
        plate_y = [-plate_width / 2, plate_width / 2]
        plate_x = [-plate_width / 20, plate_width / 20]
        self.ax_setup_3d.plot([plate_x[0]]*2, plate_y, [plate_z]*2, color='gray')
        self.ax_setup_3d.plot([plate_x[1]]*2, plate_y, [plate_z]*2, color='gray')
        # ... (其他 plot) ...
        slit_y1 = y_display_half_d; slit_y2 = -y_display_half_d
        self.ax_setup_3d.plot([0]*2, [slit_y1 - slit_length/2, slit_y1 + slit_length/2], [plate_z]*2, color='cyan', linewidth=3)
        self.ax_setup_3d.plot([0]*2, [slit_y2 - slit_length/2, slit_y2 + slit_length/2], [plate_z]*2, color='cyan', linewidth=3)
        screen_z = D
        self.ax_setup_3d.plot([plate_x[0]]*2, plate_y, [screen_z]*2, color='black')
        self.ax_setup_3d.plot([plate_x[1]]*2, plate_y, [screen_z]*2, color='black')
        self.ax_setup_3d.plot([plate_x[0], plate_x[1]], [plate_y[0]]*2, [screen_z]*2, color='black')
        self.ax_setup_3d.plot([plate_x[0], plate_x[1]], [plate_y[1]]*2, [screen_z]*2, color='black')
        self.ax_setup_3d.plot([0, 0], [0, 0], [source_z, screen_z], 'r--', linewidth=0.8) # 稍粗光轴
        #--- 增大字体 ---
        self.ax_setup_3d.set_xlim(x_range); self.ax_setup_3d.set_ylim(y_range); self.ax_setup_3d.set_zlim(z_range)
        self.ax_setup_3d.set_xlabel("X", fontsize=AXIS_LABEL_FONT_SIZE)
        self.ax_setup_3d.set_ylabel("Y", fontsize=AXIS_LABEL_FONT_SIZE)
        self.ax_setup_3d.set_zlabel("Z (光传播)", fontsize=AXIS_LABEL_FONT_SIZE)
        self.ax_setup_3d.tick_params(axis='both', which='major', labelsize=TICK_LABEL_FONT_SIZE)
        self.ax_setup_3d.set_title("3D 示意图", fontsize=TITLE_FONT_SIZE)
        self.ax_setup_3d.view_init(elev=20., azim=-50)

        # 2D
        plate_y_range_2d = [-plate_width / 2, plate_width / 2] # 调整范围以显示完整标注
        self.ax_setup_2d.plot(source_z, 0, 'yo', markersize=8)
        self.ax_setup_2d.plot([plate_z]*2, plate_y_range_2d, color='gray', linewidth=2)
        self.ax_setup_2d.plot(plate_z, 0, 'cs', markersize=6)
        # --- 增大字体 ---
        self.ax_setup_2d.text(plate_z - 0.015*D, 0 , f'd={d_mm:.2f}mm', ha='right', va='center', fontsize=ANNOTATION_FONT_SIZE, rotation=90) # 调整位置和大小
        self.ax_setup_2d.plot([screen_z]*2, plate_y_range_2d, color='black', linewidth=2)
        self.ax_setup_2d.annotate("", xy=(plate_z, plate_y_range_2d[0]*1.1), xytext=(screen_z, plate_y_range_2d[0]*1.1),
                                   arrowprops=dict(arrowstyle='<->', color='blue', lw=1))
        self.ax_setup_2d.text((plate_z + screen_z)/2, plate_y_range_2d[0]*1.15, f'D={D_m:.1f}m',
                               ha='center', va='bottom', color='blue', fontsize=ANNOTATION_FONT_SIZE) # 增大标注字体
        # ... (光线 plot 不变) ...
        self.ax_setup_2d.plot([source_z, plate_z], [0, 0], 'y--', linewidth=0.8)
        self.ax_setup_2d.plot([plate_z, screen_z], [0, 0], 'c--', linewidth=0.8)
        self.ax_setup_2d.plot([plate_z, screen_z], [0, plate_y_range_2d[1]], 'c--', linewidth=0.8)
        self.ax_setup_2d.plot([plate_z, screen_z], [0, plate_y_range_2d[0]], 'c--', linewidth=0.8)
        #--- 增大字体 ---
        self.ax_setup_2d.set_xlabel("Z (m)", fontsize=AXIS_LABEL_FONT_SIZE)
        self.ax_setup_2d.set_ylabel("Y (m)", fontsize=AXIS_LABEL_FONT_SIZE)
        self.ax_setup_2d.set_ylim(plate_y_range_2d[0] * 1.4, plate_y_range_2d[1] * 1.4) # 增大 Y 范围适应标注
        self.ax_setup_2d.set_xlim(z_range[0], z_range[1]*1.05) # 稍微扩大 Z 范围
        self.ax_setup_2d.set_aspect('auto')
        self.ax_setup_2d.set_title("2D 俯视图 (Z-Y 平面)", fontsize=TITLE_FONT_SIZE)
        self.ax_setup_2d.grid(True, linestyle=':', alpha=0.5)
        self.ax_setup_2d.tick_params(axis='both', which='major', labelsize=TICK_LABEL_FONT_SIZE)

        self.canvas_setup.draw_idle()

    def update_fringe_display(self, x_coords_mm, intensity, lambda_nm, calculation_ok):
        """更新干涉条纹图像，调整字体，移除旧指示点"""
        # 移除旧指示点
        if self._click_indicator_fringe:
            try: self._click_indicator_fringe.remove()
            except ValueError: pass
            self._click_indicator_fringe = None

        self.ax_fringe.clear()
        if not calculation_ok:
             self.ax_fringe.text(0.5, 0.5, '计算错误', ha='center', va='center', fontsize=TITLE_FONT_SIZE, color='red', transform=self.ax_fringe.transAxes)
        else:
            fringe_height = 50
            if intensity.ndim > 1: intensity = intensity.flatten()
            img_data = np.tile(intensity, (fringe_height, 1))
            cmap = self.get_wavelength_colormap(lambda_nm)
            extent = [x_coords_mm.min(), x_coords_mm.max(), 0, fringe_height]
            self.ax_fringe.imshow(img_data, cmap=cmap, aspect='auto', extent=extent, interpolation='bilinear', vmin=0, vmax=1)
            self.ax_fringe.set_yticks([])

        # --- 增大字体 ---
        self.ax_fringe.set_title("干涉条纹 (模拟)", fontsize=TITLE_FONT_SIZE)
        self.ax_fringe.set_xlabel("屏幕位置 x (mm)", fontsize=AXIS_LABEL_FONT_SIZE)
        self.ax_fringe.tick_params(axis='x', which='major', labelsize=TICK_LABEL_FONT_SIZE)
        if calculation_ok: # 有效数据时才设置 x 范围
             self.ax_fringe.set_xlim(extent[0], extent[1])
        else:
             self.ax_fringe.set_xticks([]) # 错误时不显示刻度

    def update_intensity_plot(self, x_coords_mm, intensity, lambda_nm, calculation_ok):
        """更新光强分布曲线，调整字体，移除旧指示点"""
         # 移除旧指示点
        if self._click_indicator_plot:
            try: self._click_indicator_plot.remove()
            except ValueError: pass # 可能已被移除
            self._click_indicator_plot = None

        self.ax_plot.clear() # 清除之前的曲线和指示点
        if not calculation_ok:
            # 显示错误信息
            self.ax_plot.text(0.5, 0.5, '计算错误', ha='center', va='center', fontsize=TITLE_FONT_SIZE, color='red', transform=self.ax_plot.transAxes)
            # 设置轴标签和标题（即使没有数据）
            self.ax_plot.set_xlabel("屏幕位置 x (mm)", fontsize=AXIS_LABEL_FONT_SIZE)
            self.ax_plot.set_ylabel("相对光强 I/Imax", fontsize=AXIS_LABEL_FONT_SIZE)
            self.ax_plot.set_title("相对光强分布", fontsize=TITLE_FONT_SIZE)
            self.ax_plot.set_xticks([]) # 错误时不显示刻度
            self.ax_plot.set_yticks([])
        else:
            # 绘制光强曲线
            plot_color = wavelength_to_rgb(lambda_nm)
            self.ax_plot.plot(x_coords_mm, intensity, color=plot_color, lw=2.0) # 增加线宽
            # --- 增大字体和调整样式 ---
            self.ax_plot.set_ylim(0, 1.1)
            self.ax_plot.grid(True, linestyle='--', alpha=0.6) # 使用更清晰的网格线
            self.ax_plot.set_xlabel("屏幕位置 x (mm)", fontsize=AXIS_LABEL_FONT_SIZE)
            self.ax_plot.set_ylabel("相对光强 I/Imax", fontsize=AXIS_LABEL_FONT_SIZE)
            self.ax_plot.set_title("相对光强分布", fontsize=TITLE_FONT_SIZE)
            self.ax_plot.tick_params(axis='both', which='major', labelsize=TICK_LABEL_FONT_SIZE)
            self.ax_plot.set_xlim(x_coords_mm.min(), x_coords_mm.max()) # 确保X轴范围正确

        # 统一在最后调用 draw_idle，确保更新
        self.canvas_fringe.draw_idle()

    def clear_fringe_plots_on_error(self):
        """计算出错时清空干涉图区域并显示错误信息"""
        # 移除指示点
        if self._click_indicator_fringe:
            try: self._click_indicator_fringe.remove()
            except ValueError: pass
            self._click_indicator_fringe = None
        if self._click_indicator_plot:
            try: self._click_indicator_plot.remove()
            except ValueError: pass
            self._click_indicator_plot = None

        # 清空并显示错误信息
        self.ax_fringe.clear()
        self.ax_plot.clear()
        self.ax_fringe.text(0.5, 0.5, '计算错误', ha='center', va='center', fontsize=TITLE_FONT_SIZE, color='red', transform=self.ax_fringe.transAxes)
        self.ax_plot.text(0.5, 0.5, '计算错误', ha='center', va='center', fontsize=TITLE_FONT_SIZE, color='red', transform=self.ax_plot.transAxes)

        # 设置标题和标签（使用大字体）
        self.ax_fringe.set_title("干涉条纹 (模拟)", fontsize=TITLE_FONT_SIZE)
        self.ax_plot.set_title("相对光强分布", fontsize=TITLE_FONT_SIZE)
        self.ax_fringe.set_xlabel("屏幕位置 x (mm)", fontsize=AXIS_LABEL_FONT_SIZE)
        self.ax_plot.set_xlabel("屏幕位置 x (mm)", fontsize=AXIS_LABEL_FONT_SIZE)
        self.ax_plot.set_ylabel("相对光强 I/Imax", fontsize=AXIS_LABEL_FONT_SIZE)

        # 隐藏刻度
        self.ax_fringe.set_xticks([]); self.ax_fringe.set_yticks([])
        self.ax_plot.set_xticks([]); self.ax_plot.set_yticks([])

        self.canvas_fringe.draw_idle()

    def get_wavelength_colormap(self, lambda_nm):
        """根据波长返回一个从黑到对应颜色的 matplotlib Colormap 对象。"""
        target_rgb = wavelength_to_rgb(lambda_nm)
        # 如果计算出的目标色非常暗（例如超出可见光范围），使用标准灰度图
        if sum(target_rgb) < 0.05: # 设置一个阈值
            return plt.get_cmap('gray')
        # 否则创建从黑到目标色的渐变
        custom_cmap = mcolors.LinearSegmentedColormap.from_list(
            "custom_wavelength_cmap", [(0, 0, 0), target_rgb] # 从黑色 (0,0,0) 到 target_rgb
        )
        return custom_cmap

# --- 主程序入口 ---
if __name__ == "__main__":
    root = tk.Tk()
    # Set application icon (optional, requires a .ico file)
    # try:
    #     # 在 Windows 上设置图标
    #     # 需要将 'your_icon.ico' 替换为你的图标文件路径
    #     # 如果使用 PyInstaller 打包，确保图标文件被包含
    #     import sys
    #     if sys.platform == 'win32':
    #         root.iconbitmap('your_icon.ico')
    # except Exception as e:
    #     print(f"设置图标失败: {e}")

    app = InterferenceSimulatorApp(root)
    root.mainloop()
