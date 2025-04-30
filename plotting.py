# youngViz/plotting.py
import matplotlib.pyplot as plt
import matplotlib # 用于访问 colormaps
from matplotlib.figure import Figure
import matplotlib.colors as mcolors
import numpy as np
from mpl_toolkits.mplot3d import Axes3D # 导入 3D 绘图工具

from . import config
from . import utils # 导入包含 wavelength_to_rgb 的工具模块

plt.rcParams['axes.unicode_minus'] = False # 全局解决负号显示问题

class PlotManager:
    """管理应用程序中的所有 Matplotlib 图表。"""

    def __init__(self):
        """初始化 Figure 和 Axes 对象。"""
        self.fig_setup = Figure(figsize=(6, 4), dpi=100)
        # 添加 3D 和 2D 子图
        self.ax_setup_3d = self.fig_setup.add_subplot(1, 2, 1, projection='3d')
        self.ax_setup_2d = self.fig_setup.add_subplot(1, 2, 2)
        # 调整子图布局，防止标签重叠
        self.fig_setup.subplots_adjust(left=0.08, right=0.95, bottom=0.15, top=0.9, wspace=0.4, hspace=0.3)

        self.fig_fringe = Figure(figsize=(6, 4), dpi=100)
        # 添加干涉条纹和光强曲线子图
        self.ax_fringe = self.fig_fringe.add_subplot(2, 1, 1)
        self.ax_plot = self.fig_fringe.add_subplot(2, 1, 2)
        # 自动调整布局
        self.fig_fringe.tight_layout(pad=3.0, h_pad=2.5)

        self._click_indicator_fringe = None # 干涉条纹图上的点击指示器 artist
        self._click_indicator_plot = None   # 光强曲线图上的点击指示器 artist

    def update_setup_plots(self, d_mm: float, D_m: float):
        """
        更新 3D 和 2D 实验装置示意图。

        Args:
            d_mm (float): 缝间距 (单位: mm)。
            D_m (float): 屏缝距离 (单位: m)。
        """
        self.ax_setup_3d.cla() # 清除旧的 3D 图
        self.ax_setup_2d.cla() # 清除旧的 2D 图

        d_m = d_mm * 1e-3 # 转换为米用于计算

        # --- 几何参数计算 ---
        # Z 轴范围 (涵盖光源、板、屏)
        z_range = (-0.2 * D_m, 1.1 * D_m)

        # Y 轴显示范围：适当放大缝间距以提高可见性
        # 动态调整缩放因子，确保距离变化时缝仍然可见
        y_scale_factor = max(config.SETUP_PLOT_Y_SCALE_FACTOR_BASE, 0.02 * D_m / (d_m + 1e-9)) # 避免 d_m 为 0
        y_display_half_d = (d_m / 2) * y_scale_factor # 缩放后的半缝间距
        # Y 轴范围需要足够大以容纳缩放后的缝和一些边距
        y_range_abs = max(0.02 * D_m, y_display_half_d * config.SETUP_PLOT_YLIM_FACTOR)
        y_range = (-y_range_abs, y_range_abs)

        # X 轴范围 (3D视图)，保持与 Y 轴相似的比例
        x_range = y_range

        # 挡板和缝的尺寸（视觉表示）
        plate_width_y = abs(y_range[0]) + abs(y_range[1]) # Y 方向宽度覆盖大部分范围
        # 3D图中表示挡板的细微 X 宽度
        plate_x_thin = [-plate_width_y * config.SETUP_PLOT_PLATE_THICKNESS_FACTOR,
                        plate_width_y * config.SETUP_PLOT_PLATE_THICKNESS_FACTOR]
        # 缝的视觉长度
        slit_visual_length = max(plate_width_y * 0.1, y_display_half_d * 0.5)

        # --- 绘制 3D 图 ---
        source_z = -0.1 * D_m # 光源 Z 坐标
        self.ax_setup_3d.scatter([0], [0], [source_z], color='yellow', s=100, label='光源 S', depthshade=False) # 使用 scatter 绘制光源

        plate_z = 0 # 双缝板 Z 坐标
        plate_y_coords = [-plate_width_y / 2, plate_width_y / 2] # 挡板 Y 坐标范围

        # 绘制双缝板框架 (灰色) - 使用细微的 X 坐标
        self.ax_setup_3d.plot(plate_x_thin, plate_y_coords, [plate_z]*2, color='gray') # 垂直线
        self.ax_setup_3d.plot([plate_x_thin[0]]*2, plate_y_coords, [plate_z]*2, color='gray') # 侧边
        self.ax_setup_3d.plot([plate_x_thin[1]]*2, plate_y_coords, [plate_z]*2, color='gray') # 另一侧边
        self.ax_setup_3d.plot(plate_x_thin, [plate_y_coords[0]]*2, [plate_z]*2, color='gray') # 底部
        self.ax_setup_3d.plot(plate_x_thin, [plate_y_coords[1]]*2, [plate_z]*2, color='gray') # 顶部

        # 绘制双缝 (亮蓝色) - 使用缩放后的坐标
        slit_y1_disp = y_display_half_d
        slit_y2_disp = -y_display_half_d
        # 在 Z=0 平面上，X=0 处绘制两条线段代表缝
        self.ax_setup_3d.plot([0]*2, [slit_y1_disp - slit_visual_length/2, slit_y1_disp + slit_visual_length/2],
                              [plate_z]*2, color='cyan', linewidth=3)
        self.ax_setup_3d.plot([0]*2, [slit_y2_disp - slit_visual_length/2, slit_y2_disp + slit_visual_length/2],
                              [plate_z]*2, color='cyan', linewidth=3)

        # 绘制屏幕 (黑色框架) - 使用细微 X 坐标
        screen_z = D_m # 屏幕 Z 坐标
        self.ax_setup_3d.plot(plate_x_thin, plate_y_coords, [screen_z]*2, color='black')
        self.ax_setup_3d.plot([plate_x_thin[0]]*2, plate_y_coords, [screen_z]*2, color='black')
        self.ax_setup_3d.plot([plate_x_thin[1]]*2, plate_y_coords, [screen_z]*2, color='black')
        self.ax_setup_3d.plot(plate_x_thin, [plate_y_coords[0]]*2, [screen_z]*2, color='black')
        self.ax_setup_3d.plot(plate_x_thin, [plate_y_coords[1]]*2, [screen_z]*2, color='black')

        # 绘制光轴 (红色虚线)
        self.ax_setup_3d.plot([0, 0], [0, 0], [source_z, screen_z], 'r--', linewidth=1)

        # 3D 图设置
        self.ax_setup_3d.set_xlim(x_range)
        self.ax_setup_3d.set_ylim(y_range)
        self.ax_setup_3d.set_zlim(z_range)
        self.ax_setup_3d.set_xlabel("X (m)", fontsize=config.AXIS_LABEL_FONT_SIZE)
        self.ax_setup_3d.set_ylabel("Y (m, 放大显示)", fontsize=config.AXIS_LABEL_FONT_SIZE)
        self.ax_setup_3d.set_zlabel("Z (m, 光传播方向)", fontsize=config.AXIS_LABEL_FONT_SIZE)
        self.ax_setup_3d.tick_params(axis='both', which='major', labelsize=config.TICK_LABEL_FONT_SIZE)
        self.ax_setup_3d.set_title("3D 示意图", fontsize=config.TITLE_FONT_SIZE)
        self.ax_setup_3d.view_init(elev=20., azim=-50) # 设置观察角度
        # 可以选择性地关闭网格和背景板以简化视图
        # self.ax_setup_3d.grid(False)
        # self.ax_setup_3d.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0)) # 透明背景板
        # self.ax_setup_3d.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        # self.ax_setup_3d.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))

        # --- 绘制 2D 俯视图 (Z-Y 平面) ---
        y_range_2d = y_range # 使用与 3D 图一致的 Y 范围

        # 光源 (黄色圆点)
        self.ax_setup_2d.plot([source_z], [0], 'yo', markersize=8, label='光源 S', markeredgecolor='orange')
        # 双缝板 (灰色线)
        self.ax_setup_2d.plot([plate_z]*2, y_range_2d, color='gray', linewidth=2, label='双缝板')
        # 用青色方块标示缝的位置 (使用缩放坐标)
        self.ax_setup_2d.plot([plate_z]*2, [slit_y1_disp, slit_y2_disp], 'cs', markersize=5, linestyle='')

        # 标注缝间距 'd' (显示实际值 mm)
        # 调整文本位置避免遮挡
        text_d_y = 0 # 放在中心附近
        self.ax_setup_2d.text(plate_z - 0.02 * abs(z_range[1] - z_range[0]), text_d_y, f'd={d_mm:.2f} mm',
                              ha='right', va='center', fontsize=config.ANNOTATION_FONT_SIZE - 1, rotation=90, color='cyan')
        # 添加指示线指向缝
        self.ax_setup_2d.plot([plate_z - 0.01 * abs(z_range[1] - z_range[0])] * 2, [slit_y1_disp, slit_y2_disp], 'c:', lw=0.8)

        # 屏幕 (黑色线)
        self.ax_setup_2d.plot([screen_z]*2, y_range_2d, color='black', linewidth=2, label='屏')
        # 标注屏缝距离 'D'
        self.ax_setup_2d.annotate("", xy=(plate_z, y_range_2d[0]*0.9), xytext=(screen_z, y_range_2d[0]*0.9),
                                   arrowprops=dict(arrowstyle='<->', color='blue', lw=1.5))
        self.ax_setup_2d.text((plate_z + screen_z)/2, y_range_2d[0]*0.85, f'D={D_m:.1f} m',
                               ha='center', va='top', color='blue', fontsize=config.ANNOTATION_FONT_SIZE)

        # 绘制示例光路 (虚线) - 从光源到缝，从缝到屏幕中心点 (示意)
        self.ax_setup_2d.plot([source_z, plate_z], [0, slit_y1_disp], 'y--', linewidth=0.8)
        self.ax_setup_2d.plot([source_z, plate_z], [0, slit_y2_disp], 'y--', linewidth=0.8)
        self.ax_setup_2d.plot([plate_z, screen_z], [slit_y1_disp, 0], 'c--', linewidth=0.8) # 指向屏幕中心
        self.ax_setup_2d.plot([plate_z, screen_z], [slit_y2_disp, 0], 'c--', linewidth=0.8) # 指向屏幕中心
        # 可以绘制光轴
        # self.ax_setup_2d.plot([source_z, screen_z], [0, 0], 'r--', linewidth=1, label='光轴')

        # 2D 图设置
        self.ax_setup_2d.set_xlabel("Z (m)", fontsize=config.AXIS_LABEL_FONT_SIZE)
        self.ax_setup_2d.set_ylabel("Y (m, 放大显示)", fontsize=config.AXIS_LABEL_FONT_SIZE)
        self.ax_setup_2d.set_ylim(y_range_2d)
        self.ax_setup_2d.set_xlim(z_range)
        self.ax_setup_2d.set_aspect('auto') # 自动调整宽高比
        self.ax_setup_2d.set_title("2D 俯视图 (Z-Y 平面)", fontsize=config.TITLE_FONT_SIZE)
        self.ax_setup_2d.grid(True, linestyle=':', alpha=0.6)
        self.ax_setup_2d.tick_params(axis='both', which='major', labelsize=config.TICK_LABEL_FONT_SIZE)

    def update_fringe_display(self, x_coords_mm: np.ndarray | None, intensity: np.ndarray | None, lambda_nm: float):
        """
        更新干涉条纹图像显示。

        Args:
            x_coords_mm (np.ndarray | None): 屏幕位置坐标数组 (mm)。None 表示计算失败。
            intensity (np.ndarray | None): 对应的相对光强数组。None 表示计算失败。
            lambda_nm (float): 当前波长 (nm), 用于颜色映射。
        """
        self._remove_click_indicator(self.ax_fringe) # 清除旧指示点
        self.ax_fringe.clear()

        if x_coords_mm is None or intensity is None or x_coords_mm.size == 0 or intensity.size == 0:
            self.ax_fringe.text(0.5, 0.5, '计算错误或无数据', ha='center', va='center',
                                fontsize=config.TITLE_FONT_SIZE, color='red', transform=self.ax_fringe.transAxes)
            self.ax_fringe.set_xticks([])
            self.ax_fringe.set_yticks([])
            self.ax_fringe.set_xlabel("")
        else:
            # 创建条纹图像数据 (将一维强度复制多行)
            img_data = np.tile(intensity, (config.FRINGE_IMG_HEIGHT_PIXELS, 1))
            # 获取对应波长的颜色映射 (黑 -> R,G,B)
            cmap = self._get_wavelength_colormap(lambda_nm)
            # 确定图像范围
            extent = [x_coords_mm.min(), x_coords_mm.max(), 0, config.FRINGE_IMG_HEIGHT_PIXELS]
            # 显示图像
            self.ax_fringe.imshow(img_data, cmap=cmap, aspect='auto', extent=extent,
                                  interpolation='bilinear', vmin=0, vmax=1) # 双线性插值使边缘平滑
            self.ax_fringe.set_yticks([]) # 隐藏 Y 轴刻度
            self.ax_fringe.set_xlim(extent[0], extent[1]) # 设置 X 轴范围
            self.ax_fringe.tick_params(axis='x', which='major', labelsize=config.TICK_LABEL_FONT_SIZE)
            self.ax_fringe.set_xlabel("屏幕位置 x (mm)", fontsize=config.AXIS_LABEL_FONT_SIZE)

        self.ax_fringe.set_title("干涉条纹 (模拟)", fontsize=config.TITLE_FONT_SIZE)

    def update_intensity_plot(self, x_coords_mm: np.ndarray | None, intensity: np.ndarray | None, lambda_nm: float):
        """
        更新光强分布曲线图。

        Args:
            x_coords_mm (np.ndarray | None): 屏幕位置坐标数组 (mm)。None 表示计算失败。
            intensity (np.ndarray | None): 对应的相对光强数组。None 表示计算失败。
            lambda_nm (float): 当前波长 (nm), 用于曲线颜色。
        """
        self._remove_click_indicator(self.ax_plot) # 清除旧指示点
        self.ax_plot.clear()

        if x_coords_mm is None or intensity is None or x_coords_mm.size == 0 or intensity.size == 0:
            self.ax_plot.text(0.5, 0.5, '计算错误或无数据', ha='center', va='center',
                              fontsize=config.TITLE_FONT_SIZE, color='red', transform=self.ax_plot.transAxes)
            self.ax_plot.set_xticks([])
            self.ax_plot.set_yticks([])
            self.ax_plot.set_xlabel("")
            self.ax_plot.set_ylabel("")
        else:
            # 获取对应波长的颜色
            plot_color = utils.wavelength_to_rgb(lambda_nm)
            # 绘制光强曲线
            self.ax_plot.plot(x_coords_mm, intensity, color=plot_color, lw=config.PLOT_LINEWIDTH)

            # 设置坐标轴、网格和标签
            self.ax_plot.set_ylim(-0.05, 1.1) # Y 轴留一点边距
            self.ax_plot.grid(True, linestyle=':', alpha=0.7)
            self.ax_plot.tick_params(axis='both', which='major', labelsize=config.TICK_LABEL_FONT_SIZE)
            # 确保 X 轴范围与数据匹配
            self.ax_plot.set_xlim(x_coords_mm.min(), x_coords_mm.max())
            self.ax_plot.set_xlabel("屏幕位置 x (mm)", fontsize=config.AXIS_LABEL_FONT_SIZE)
            self.ax_plot.set_ylabel("相对光强 I/Imax", fontsize=config.AXIS_LABEL_FONT_SIZE)

        self.ax_plot.set_title("相对光强分布", fontsize=config.TITLE_FONT_SIZE)

    def draw_click_indicator(self, event, x_coords_mm, intensity):
        """在点击的图上绘制指示点，并返回点击的坐标 (mm)。"""
        x_click_mm = event.xdata
        y_click = event.ydata # 可能在 ax_fringe 或 ax_plot 上

        # 清除之前的指示点
        self._remove_click_indicator(self.ax_fringe)
        self._remove_click_indicator(self.ax_plot)

        target_ax = event.inaxes
        indicator = None

        if target_ax == self.ax_fringe and x_click_mm is not None and y_click is not None:
            # 在条纹图上绘制
            indicator = self.ax_fringe.plot(x_click_mm, y_click, 'o',
                                            markersize=config.CLICK_INDICATOR_SIZE,
                                            markerfacecolor=config.CLICK_INDICATOR_COLOR,
                                            markeredgecolor=config.CLICK_INDICATOR_COLOR)[0]
            self._click_indicator_fringe = indicator

        elif target_ax == self.ax_plot and x_click_mm is not None:
            # 在曲线图上绘制，需要插值找到曲线上的 y 值
            if x_coords_mm is not None and intensity is not None and x_coords_mm.size > 0:
                try:
                    # 确保点击的 x 在数据范围内，然后插值计算 y
                    x_clamped = np.clip(x_click_mm, x_coords_mm.min(), x_coords_mm.max())
                    y_intensity = np.interp(x_clamped, x_coords_mm, intensity)
                    indicator = self.ax_plot.plot(x_clamped, y_intensity, 'o',
                                                  markersize=config.CLICK_INDICATOR_SIZE,
                                                  markerfacecolor=config.CLICK_INDICATOR_COLOR,
                                                  markeredgecolor=config.CLICK_INDICATOR_COLOR)[0]
                    self._click_indicator_plot = indicator
                except Exception as e:
                    print(f"错误: 插值或绘制曲线指示点时出错: {e}")
            else:
                print("提示: 无有效光强数据，无法在曲线上绘制指示点。")

        return x_click_mm # 返回点击的 x 坐标，供主窗口计算用

    def _remove_click_indicator(self, ax):
        """安全地移除指定 Axes 上的点击指示器。"""
        indicator = None
        if ax == self.ax_fringe:
            indicator = self._click_indicator_fringe
            self._click_indicator_fringe = None
        elif ax == self.ax_plot:
            indicator = self._click_indicator_plot
            self._click_indicator_plot = None

        if indicator:
            try:
                indicator.remove()
            except (ValueError, AttributeError):
                pass # 可能已被移除或未正确创建

    def _get_wavelength_colormap(self, lambda_nm: float):
        """
        根据波长返回一个从黑色到对应可见光颜色的 Matplotlib Colormap 对象。
        如果颜色太暗或无效，则返回灰度图。
        """
        target_rgb = utils.wavelength_to_rgb(lambda_nm)
        brightness_threshold = 0.05
        if sum(target_rgb) < brightness_threshold:
            # print(f"调试: 波长 {lambda_nm}nm 颜色过暗，使用灰度图。")
            try:
                return matplotlib.colormaps['gray']
            except AttributeError: # 兼容旧版本 Matplotlib
                 return matplotlib.cm.get_cmap('gray')

        try:
            cmap_name = f"custom_wavelength_{lambda_nm}_{target_rgb}"
            if cmap_name not in matplotlib.colormaps:
                 custom_cmap = mcolors.LinearSegmentedColormap.from_list(
                     cmap_name, [(0, 0, 0), target_rgb]
                 )
                 # 使用 matplotlib.colormaps.register 注册
                 matplotlib.colormaps.register(custom_cmap, name=cmap_name)
                 # print(f"调试: 注册了新的 Colormap: {cmap_name}") # 调试信息
                 return custom_cmap
            else:
                 # 使用 matplotlib.colormaps[cmap_name] 获取
                 # print(f"调试: 使用了已注册的 Colormap: {cmap_name}") # 调试信息
                 return matplotlib.colormaps[cmap_name]

        except Exception as e:
             print(f"警告: 为波长 {lambda_nm}nm 创建/获取颜色映射时出错: {e}. 返回灰度图。")
             try:
                return matplotlib.colormaps['gray']
             except AttributeError:
                 return matplotlib.cm.get_cmap('gray')

    def redraw_canvas_fringe(self):
        """重绘干涉图和曲线图所在的画布。"""
        try:
            self.fig_fringe.canvas.draw_idle()
        except AttributeError:
            print("调试: fig_fringe 画布尚未完全初始化。") # 可能在初始设置时发生

    def redraw_canvas_setup(self):
        """重绘装置示意图所在的画布。"""
        try:
            self.fig_setup.canvas.draw_idle()
        except AttributeError:
             print("调试: fig_setup 画布尚未完全初始化。")