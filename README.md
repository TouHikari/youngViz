# 杨氏双缝干涉模拟器 (Young's Double Slit Simulator)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

这是一个使用 Python、Tkinter 和 Matplotlib 构建的图形用户界面 (GUI) 应用程序，用于模拟和可视化经典的杨氏双缝干涉实验。用户可以通过调整参数实时观察干涉现象。项目经过重构，具有更清晰的模块化结构。

This is a Graphical User Interface (GUI) application built with Python, Tkinter, and Matplotlib to simulate and visualize the classic Young's double-slit experiment. Users can adjust parameters and observe the interference phenomenon in real-time. The project has been refactored for a clearer, modular structure.

---

## 目录 (Table of Contents)

*   [中文说明](#中文说明)
    *   [✨ 特性](#-特性)
    *   [📂 项目结构](#-项目结构)
    *   [🔧 安装与运行](#-安装与运行)
    *   [🐍 依赖](#-依赖)
    *   [📜 协议](#-协议)
*   [English Description](#english-description)
    *   [✨ Features](#-features)
    *   [📂 Project Structure](#-project-structure)
    *   [🔧 Installation & Usage](#-installation--usage)
    *   [🐍 Dependencies](#-dependencies)
    *   [📜 License](#-license)

---

## 中文说明

### ✨ 特性

*   **可视化模拟:** 实时显示干涉条纹（颜色随波长变化）和相对光强分布曲线。
*   **实时交互:** 通过滑块交互式地调整光源波长 (λ)、双缝间距 (d) 和屏缝距离 (D)，**图像实时更新**。
*   **参数范围:**
    *   波长 λ: 380 nm - 750 nm
    *   缝间距 d: 0.01 mm - 1.0 mm
    *   屏缝距离 D: 0.1 m - 5.0 m
*   **装置示意图:** 提供实验装置的 3D 和 2D (俯视) 示意图，随参数 D 和 d 更新（注意：3D图中的缝间距通过动态缩放以保持可见性）。
*   **数据分析:**
    *   显示理论计算的条纹间距 (Δx)。
    *   如果安装了 `scipy` 库，程序会尝试从模拟的光强曲线上测量条纹间距。
    *   在干涉结果图上点击可以获取该点的屏幕位置 (x)、近似光程差 (δ) 和相位差 (ΔΦ) 信息。
*   **界面友好:** 使用 Tkinter 构建图形界面，Matplotlib 嵌入绘图。尝试支持中文字体显示（需要系统中安装 `SimHei` 或其他可用中文字体）。
*   **代码结构清晰:** 项目代码被组织到独立的模块中，易于理解和扩展。

### 📂 项目结构

```txt
youngViz/                       # 项目根目录
├── config.py                   # 配置文件 (常量, 默认值, 样式)
├── simulation.py               # 模拟计算模块 (核心物理计算)
├── plotting.py                 # 绘图模块 (Matplotlib 逻辑)
├── utils.py                    # 工具函数模块
├── gui/                        # GUI 相关代码目录
│   ├── __init__.py
│   ├── main_window.py          # 主窗口类
│   ├── control_panel.py        # 控制面板控件
│   └── matplotlib_widget.py    # Matplotlib 图形嵌入控件
├── main.py                     # 程序主入口文件
├── README.md                   # 本文档
└── requirements.txt            # (建议创建) 依赖文件
```

### 🔧 安装与运行

1.  **克隆仓库:**
    ```bash
    git clone https://github.com/TouHikari/youngViz.git
    cd youngViz
    ```

2.  **创建虚拟环境 (推荐):**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **安装依赖:**
    *   *(推荐)* 使用仓库包含的 `requirements.txt` 文件:
        ```bash
        pip install -r requirements.txt
        ```
    *   或者手动安装:
        ```bash
        pip install numpy matplotlib scipy
        ```
        *(注意: `scipy` 是可选的，仅用于自动测量条纹间距)*

4.  **运行程序:**
    *(建议作为模块运行，确保你在 `youngViz/` 的上一层目录):*
    ```bash
    python -m youngViz.main
    ```

5.  **退出虚拟环境 (如果使用了):**
    ```bash
    deactivate
    ```

### 🐍 依赖

*   Python 3.7+ (建议)
*   NumPy (`pip install numpy`)
*   Matplotlib (`pip install matplotlib`)
*   SciPy (`pip install scipy`) - **可选**, 用于条纹间距测量功能。
*   Tkinter (通常随 Python 标准库一起安装)

### 📜 协议

本项目采用 **MIT 许可证**。详情请见 [LICENSE](LICENSE) 文件。

---

## English Description

### ✨ Features

*   **Visual Simulation:** Real-time display of interference fringes (color changes with wavelength) and the relative intensity distribution curve.
*   **Real-time Interaction:** Interactively adjust the light source wavelength (λ), slit separation (d), and screen distance (D) using sliders, with **immediate visual updates**.
*   **Parameter Ranges:**
    *   Wavelength λ: 380 nm - 750 nm
    *   Slit Separation d: 0.01 mm - 1.0 mm
    *   Screen Distance D: 0.1 m - 5.0 m
*   **Setup Diagrams:** Provides 3D and 2D (top-down view) schematic diagrams of the experimental setup, updated with parameters D and d (Note: Slit separation in the 3D view is dynamically scaled for visibility).
*   **Data Analysis:**
    *   Displays the theoretically calculated fringe spacing (Δx).
    *   If the `scipy` library is installed, the program attempts to measure the fringe spacing from the simulated intensity curve.
    *   Clicking on the interference result plots displays information about the screen position (x), approximate optical path difference (δ), and phase difference (ΔΦ) at that point.
*   **User-Friendly Interface:** GUI built with Tkinter, embedding plots using Matplotlib. Attempts to support Chinese font display (requires `SimHei` or another available Chinese font installed on the system).
*   **Clean Code Structure:** Project code is organized into distinct modules for better understanding and extensibility.

### 📂 Project Structure

```txt
youngViz/                       # Project Root
├── config.py                   # Configuration (constants, defaults, styles)
├── simulation.py               # Simulation core (physics calculations)
├── plotting.py                 # Plotting module (Matplotlib logic)
├── utils.py                    # Utility functions
├── gui/                        # GUI related code
│   ├── __init__.py
│   ├── main_window.py          # Main window class
│   ├── control_panel.py        # Control panel widget
│   └── matplotlib_widget.py    # Matplotlib embedding widget
├── main.py                     # Main application entry point
├── README.md                   # This document
└── requirements.txt            # (Recommended) Dependencies file
```

### 🔧 Installation & Usage

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/TouHikari/youngViz.git
    cd youngViz
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    *   *(Recommended)* Use a `requirements.txt` file including in the repository:
        ```bash
        pip install -r requirements.txt
        ```
    *   Or install manually:
        ```bash
        pip install numpy matplotlib scipy
        ```
        *(Note: `scipy` is optional, only needed for automatic fringe spacing measurement)*

4.  **Run the Application:**
    *(Suggest running it as a module. Ensure that you are in the directory above 'youngViz/'):*
    ```bash
    python -m youngViz.main # Typically used after package installation
    ```

5.  **Deactivate Virtual Environment (if used):**
    ```bash
    deactivate
    ```

### 🐍 Dependencies

*   Python 3.7+ (Recommended)
*   NumPy (`pip install numpy`)
*   Matplotlib (`pip install matplotlib`)
*   SciPy (`pip install scipy`) - **Optional**, for fringe spacing measurement feature.
*   Tkinter (Usually included with Python standard library)

### 📜 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.