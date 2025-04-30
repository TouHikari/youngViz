# youngViz/gui/control_panel.py
import tkinter as tk
from tkinter import ttk
from .. import config # 使用相对导入访问 config

class ControlPanel(ttk.LabelFrame):
    """包含参数控制滑块、标签和信息显示的控件。"""

    def __init__(self, master, update_callback, **kwargs):
        """
        初始化控制面板。

        Args:
            master: 父 Tkinter 控件。
            update_callback: 当参数发生交互式更改时调用的函数 (例如拖动滑块完成)。
            **kwargs: 传递给 ttk.LabelFrame 的其他关键字参数。
        """
        super().__init__(master, text="参数设置与分析", padding="15", **kwargs)
        self.update_callback = update_callback # 保存回调函数

        # --- Tkinter 变量 ---
        # 从 config 加载默认值，注意单位转换
        self.lambda_nm = tk.DoubleVar(value=config.DEFAULT_LAMBDA_M * 1e9) # m -> nm
        self.d_mm = tk.DoubleVar(value=config.DEFAULT_D_M * 1e3)         # m -> mm
        self.D_m = tk.DoubleVar(value=config.DEFAULT_CAP_D_M)            # m -> m

        # --- 布局配置 ---
        self.columnconfigure(1, weight=1) # 让第 1 列 (标签值) 扩展
        current_row = 0
        pady_val = 4 # 控件垂直间距
        pady_section = (pady_val, pady_val + 5) # 控件组之间的额外间距

        # --- 波长控件 ---
        ttk.Label(self, text="波长 λ (nm):").grid(row=current_row, column=0, sticky="w", pady=pady_val)
        self.lambda_label = ttk.Label(self, text="", width=8, anchor='e') # 右对齐显示值
        self.lambda_label.grid(row=current_row, column=1, sticky="ew", pady=pady_val)
        current_row += 1
        self.lambda_scale = ttk.Scale(self, from_=config.LAMBDA_RANGE_NM[0], to=config.LAMBDA_RANGE_NM[1],
                                      orient=tk.HORIZONTAL, variable=self.lambda_nm,
                                      command=self._on_scale_change) # command 现在会触发更新
        self.lambda_scale.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=pady_section)
        current_row += 1

        # 波长预设按钮
        preset_button_frame = ttk.Frame(self)
        preset_button_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=(0, pady_val + 10))
        preset_button_frame.columnconfigure((0, 1, 2), weight=1) # 均分布局
        ttk.Button(preset_button_frame, text="红(650)", command=lambda: self.set_wavelength(650.0)).grid(row=0, column=0, sticky='ew', padx=2)
        ttk.Button(preset_button_frame, text="绿(550)", command=lambda: self.set_wavelength(550.0)).grid(row=0, column=1, sticky='ew', padx=2)
        ttk.Button(preset_button_frame, text="蓝(450)", command=lambda: self.set_wavelength(450.0)).grid(row=0, column=2, sticky='ew', padx=2)
        current_row += 1

        # --- 缝间距控件 ---
        ttk.Label(self, text="缝间距 d (mm):").grid(row=current_row, column=0, sticky="w", pady=pady_val)
        self.d_label = ttk.Label(self, text="", width=8, anchor='e')
        self.d_label.grid(row=current_row, column=1, sticky="ew", pady=pady_val)
        current_row += 1
        self.d_scale = ttk.Scale(self, from_=config.D_RANGE_MM[0], to=config.D_RANGE_MM[1],
                                 orient=tk.HORIZONTAL, variable=self.d_mm,
                                 command=self._on_scale_change)
        self.d_scale.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=pady_section)
        current_row += 1

        # --- 屏缝距离控件 ---
        ttk.Label(self, text="屏缝距离 D (m):").grid(row=current_row, column=0, sticky="w", pady=pady_val)
        self.D_label = ttk.Label(self, text="", width=8, anchor='e')
        self.D_label.grid(row=current_row, column=1, sticky="ew", pady=pady_val)
        current_row += 1
        self.D_scale = ttk.Scale(self, from_=config.CAP_D_RANGE_M[0], to=config.CAP_D_RANGE_M[1],
                                 orient=tk.HORIZONTAL, variable=self.D_m,
                                 command=self._on_scale_change)
        self.D_scale.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=pady_section)
        current_row += 1

        # --- 分隔线 ---
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=current_row, column=0, columnspan=2, sticky='ew', pady=pady_val + 10)
        current_row += 1

        # --- 分析结果标签 ---
        self.spacing_comparison_label = ttk.Label(self, text="理论间距 Δx:\n测量间距 Δx_m:", justify=tk.LEFT)
        self.spacing_comparison_label.grid(row=current_row, column=0, columnspan=2, sticky="w", pady=pady_val)
        current_row += 1

        self.point_info_label = ttk.Label(self, text="点击下方图形获取点信息:\nx=\nδ=\nΔΦ=", justify=tk.LEFT)
        self.point_info_label.grid(row=current_row, column=0, columnspan=2, sticky="w", pady=(pady_val, 0))
        current_row += 1

        # --- 初始化标签显示 ---
        self.update_parameter_labels()

    def _on_scale_change(self, value):
        """当滑块被拖动时，更新标签并触发模拟更新。"""
        # value 参数是必需的，即使不用它
        self.update_parameter_labels()
        if self.update_callback:
            # print(f"Debug: Scale changed, triggering update...") # Optional debug print
            self.update_callback()

    def set_wavelength(self, wavelength_nm: float):
        """通过按钮设置波长值，并触发更新。"""
        current_val = self.lambda_nm.get()
        if abs(current_val - wavelength_nm) > 1e-6: # 避免不必要的更新
            self.lambda_nm.set(wavelength_nm)
            self.update_parameter_labels()
            if self.update_callback:
                self.update_callback() # 按钮点击后立即更新

    def get_parameters_mks(self) -> dict:
        """
        获取当前参数值，并转换为 MKS (国际标准) 单位。

        Returns:
            dict: 包含 'lambda_m', 'd_m', 'cap_d_m' 的字典。
        """
        try:
            lambda_nm = self.lambda_nm.get()
            d_mm = self.d_mm.get()
            D_m = self.D_m.get()

            return {
                'lambda_m': lambda_nm * 1e-9, # nm -> m
                'd_m': d_mm * 1e-3,         # mm -> m
                'cap_d_m': D_m              # m -> m
            }
        except tk.TclError:
            # 应用程序关闭时可能发生此错误
            print("信息: 获取参数时窗口可能已关闭。")
            return { # 返回默认值或 None 可能更好
                'lambda_m': config.DEFAULT_LAMBDA_M,
                'd_m': config.DEFAULT_D_M,
                'cap_d_m': config.DEFAULT_CAP_D_M
            }

    def update_parameter_labels(self):
        """更新显示参数当前值的标签。"""
        try:
            lambda_val = self.lambda_nm.get()
            d_val = self.d_mm.get()
            D_val = self.D_m.get()

            self.lambda_label.config(text=f"{lambda_val:.0f} nm")
            self.d_label.config(text=f"{d_val:.3f} mm") # 增加精度
            self.D_label.config(text=f"{D_val:.2f} m") # 增加精度
        except tk.TclError:
             pass # 忽略关闭时的错误
        except Exception as e:
            print(f"警告: 更新参数标签时出错: {e}")

    def update_analysis_labels(self, theoretical_spacing_str: str, measured_spacing_str: str):
        """
        更新显示条纹间距信息的标签。

        Args:
            theoretical_spacing_str: 理论间距的文本描述。
            measured_spacing_str: 测量间距的文本描述。
        """
        text = f"理论间距 Δx: {theoretical_spacing_str}\n测量间距 Δx_m: {measured_spacing_str}"
        self.spacing_comparison_label.config(text=text)

    def update_point_info_label(self, x_mm_str: str, delta_str: str, delta_phi_str: str):
        """
        更新显示点击点信息的标签。

        Args:
            x_mm_str: 点击位置 x 坐标的文本描述。
            delta_str: 光程差的文本描述。
            delta_phi_str: 相位差的文本描述。
        """
        info_text = (
            f"点击位置信息:\n"
            f"  x = {x_mm_str}\n"
            f"光程差 (近似):\n"
            f"  δ ≈ {delta_str}\n"
            f"相位差:\n"
            f"  ΔΦ = {delta_phi_str}"
        )
        self.point_info_label.config(text=info_text)

    def reset_point_info_label(self):
        """重置点击点信息标签到默认状态。"""
        self.point_info_label.config(text="点击下方图形获取点信息:\nx=\nδ=\nΔΦ=")