# youngViz/main.py
import tkinter as tk
from tkinter import ttk, font as tkFont
import matplotlib.pyplot as plt
import sys
import os # 用于检查图标文件

# 导入项目模块
from youngViz import config
from youngViz import utils
from youngViz.gui.main_window import MainWindow

def setup_matplotlib_font():
    """尝试设置 Matplotlib 的字体，优先使用 config 中的配置。"""
    try:
        plt.rcParams['font.family'] = config.PREFERRED_MPL_FONT
        plt.rcParams['axes.unicode_minus'] = False # 解决负号显示问题
        print(f"信息: Matplotlib 尝试使用字体 '{config.PREFERRED_MPL_FONT}'。")
    except Exception as e:
        print(f"警告: 设置 Matplotlib 首选字体 '{config.PREFERRED_MPL_FONT}' 失败: {e}")
        print("     请确保该字体已安装，或修改 config.py 中的 PREFERRED_MPL_FONT。")
        print("     Matplotlib 图中的中文可能无法正常显示。")
        # 即便字体设置失败，依然尝试设置 unicode_minus
        plt.rcParams['axes.unicode_minus'] = False

def set_app_icon(root: tk.Tk):
    """尝试为应用程序窗口设置图标。"""
    # 图标文件应放在项目根目录或指定路径
    # 在 Windows 上通常用 .ico，其他系统倾向于 .png 或 .gif
    icon_paths = ['app_icon.ico', 'app_icon.png', 'icon.ico', 'icon.png'] # 尝试不同名称/格式

    found_icon_path = None
    for path in icon_paths:
         # 尝试在脚本所在目录或上一级目录查找
         possible_paths = [path, os.path.join(os.path.dirname(__file__), path)]
         if getattr(sys, 'frozen', False): # 如果是打包后的程序 (PyInstaller)
              possible_paths.append(os.path.join(sys._MEIPASS, path))

         for p in possible_paths:
             if os.path.exists(p):
                 found_icon_path = p
                 break
         if found_icon_path:
             break

    if not found_icon_path:
        print("提示: 未在常见路径找到应用程序图标文件 (如 app_icon.ico 或 app_icon.png)。")
        return

    try:
        if sys.platform.startswith('win'):
            root.iconbitmap(found_icon_path)
            print(f"信息: 成功设置窗口图标: {found_icon_path}")
        else:
            # Tkinter 在 Linux/macOS 上设置图标比较复杂，通常需要 PhotoImage
            # 但并非所有窗口管理器都支持通过这种方式设置窗口本身的图标
            # 这里尝试一种通用方法，可能不生效
            img = tk.PhotoImage(file=found_icon_path)
            # root.iconphoto(True, img) # Tk 8.6+ 的推荐方式
            root.tk.call('wm', 'iconphoto', root._w, img) # 兼容旧版本的方式
            print(f"信息: 尝试为非 Windows 系统设置图标: {found_icon_path} (效果取决于系统/窗口管理器)")
    except tk.TclError as e:
         if "format" in str(e) or "bitmap" in str(e):
             print(f"警告: 图标文件 '{found_icon_path}' 格式不受支持或损坏。 ({e})")
         else:
             print(f"警告: 设置应用程序图标时发生 TclError: {e}")
    except Exception as e:
        print(f"警告: 设置应用程序图标时发生意外错误: {e}")

if __name__ == "__main__":
    # 1. 创建 Tkinter 根窗口
    root = tk.Tk()

    # 2. 设置应用程序图标 (可选)
    set_app_icon(root)

    # 3. 查找并设置 Tkinter 控件的最佳字体
    best_tk_font = utils.find_best_font(root, config.PREFERRED_TK_FONTS, config.DEFAULT_TK_FONT_FALLBACK)

    # 4. 配置 ttk 样式
    style = ttk.Style()
    # 配置主要控件的字体
    style.configure('TLabel', font=(best_tk_font, config.LABEL_FONT_SIZE))
    style.configure('TButton', font=(best_tk_font, config.BUTTON_FONT_SIZE))
    style.configure('TLabelframe.Label', font=(best_tk_font, config.FRAME_TITLE_FONT_SIZE, 'bold'))
    # 可选: 给 Scale 添加些样式
    style.configure('TScale', troughcolor='#e0e0e0')

    # 5. 配置 Matplotlib 字体 (应在创建 Figure 之前)
    setup_matplotlib_font()

    # 6. 创建主应用程序窗口实例
    app = MainWindow(root)

    # 7. 启动 Tkinter 事件循环
    root.mainloop()