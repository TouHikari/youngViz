# youngViz/gui/matplotlib_widget.py
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

class MatplotlibWidget(ttk.Frame):
    """一个嵌入 Matplotlib FigureCanvas 和可选工具栏的 Tkinter 控件。"""

    def __init__(self, master, figure: Figure, show_toolbar: bool = True, **kwargs):
        """
        初始化控件。

        Args:
            master: 父 Tkinter 控件。
            figure (Figure): 要显示的 Matplotlib Figure 对象。
            show_toolbar (bool): 是否显示 Matplotlib 导航工具栏。
            **kwargs: 传递给 ttk.Frame 的其他关键字参数。
        """
        super().__init__(master, **kwargs)
        self.figure = figure

        # 创建 Matplotlib 画布
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # (可选) 创建导航工具栏
        if show_toolbar:
            # 将工具栏放在画布下方
            toolbar_frame = ttk.Frame(self)
            toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
            self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
            self.toolbar.update()
        else:
            self.toolbar = None

        # 使画布获得焦点能力，以便接收键盘事件 (如果需要)
        self.canvas_widget.focus_set()

    def connect_event(self, event_name: str, callback):
        """
        连接 Matplotlib 画布事件。

        Args:
            event_name (str): Matplotlib 事件名称 (例如 'button_press_event')。
            callback: 事件触发时调用的函数。
        """
        self.canvas.mpl_connect(event_name, callback)

    def disconnect_event(self, signal_id):
        """断开 Matplotlib 画布事件连接。"""
        self.canvas.mpl_disconnect(signal_id)

    def draw(self):
        """重绘画布。"""
        self.canvas.draw_idle() # 使用 draw_idle 避免卡顿