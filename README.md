# 杨氏双缝干涉模拟器 (Young's Double Slit Simulator)

这是一个使用 Python、Tkinter 和 Matplotlib 构建的图形用户界面 (GUI) 应用程序，用于模拟和可视化经典的杨氏双缝干涉实验。用户可以通过调整参数实时观察干涉现象。

This is a Graphical User Interface (GUI) application built with Python, Tkinter, and Matplotlib to simulate and visualize the classic Young's double-slit experiment. Users can adjust parameters and observe the interference phenomenon in real-time.

---

## 目录 (Table of Contents)

*   [中文说明](#中文说明)
    *   [✨ 特性](#-特性)
    *   [🔧 安装与运行](#-安装与运行)
    *   [🐍 依赖](#-依赖)
    *   [📜 协议](#-协议)
*   [English Description](#english-description)
    *   [✨ Features](#-features)
    *   [🔧 Installation & Usage](#-installation--usage)
    *   [🐍 Dependencies](#-dependencies)
    *   [📜 License](#-license)

---

## 中文说明

### ✨ 特性

*   **可视化模拟:** 实时显示干涉条纹（颜色随波长变化）和相对光强分布曲线。
*   **参数可调:** 通过滑块交互式地调整光源波长 (λ, 380nm-750nm)、双缝间距 (d, 0.01mm-1.0mm) 和屏缝距离 (D, 0.1m-5.0m)。
*   **装置示意图:** 提供实验装置的 3D 和 2D (俯视) 示意图，随参数 D 和 d 更新。
*   **数据分析:**
    *   显示理论计算的条纹间距 (Δx)。
    *   如果安装了 `scipy` 库，程序会尝试从模拟的光强曲线上测量条纹间距。
    *   在图形上点击可以获取该点的屏幕位置 (x)、近似光程差 (δ) 和相位差 (ΔΦ) 信息。
*   **界面友好:** 使用 Tkinter 构建图形界面，Matplotlib 嵌入绘图。尝试支持中文字体显示（需要系统中安装 `SimHei` 或其他可用中文字体）。

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
    *   使用 `requirements.txt` 文件:
        ```bash
        pip install -r requirements.txt
        ```
    *   或者手动安装:
        ```bash
        pip install numpy matplotlib scipy
        ```
        *(注意: `scipy` 是可选的，仅用于自动测量条纹间距)*

4.  **运行程序:**
    ```bash
    python gui.py
    ```

5.  **退出虚拟环境 (如果使用了):**
    ```bash
    deactivate
    ```

### 🐍 依赖

*   Python 3.x
*   NumPy (`pip install numpy`)
*   Matplotlib (`pip install matplotlib`)
*   SciPy (`pip install scipy`) - 可选，用于条纹间距测量功能。
*   Tkinter (通常随 Python 一起安装)

### 📜 协议

本项目未采用任何协议。

---

## English Description

### ✨ Features

*   **Visual Simulation:** Real-time display of interference fringes (color changes with wavelength) and the relative intensity distribution curve.
*   **Adjustable Parameters:** Interactively adjust the light source wavelength (λ, 380nm-750nm), slit separation (d, 0.01mm-1.0mm), and screen distance (D, 0.1m-5.0m) using sliders.
*   **Setup Diagrams:** Provides 3D and 2D (top-down view) schematic diagrams of the experimental setup, updated with parameters D and d.
*   **Data Analysis:**
    *   Displays the theoretically calculated fringe spacing (Δx).
    *   If the `scipy` library is installed, the program attempts to measure the fringe spacing from the simulated intensity curve.
    *   Clicking on the plots displays information about the screen position (x), approximate optical path difference (δ), and phase difference (ΔΦ) at that point.
*   **User-Friendly Interface:** GUI built with Tkinter, embedding plots using Matplotlib. Attempts to support Chinese font display (requires `SimHei` or another available Chinese font installed on the system).

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
    *   Use a `requirements.txt` file:
        ```bash
        pip install -r requirements.txt
        ```
    *   Or install manually:
        ```bash
        pip install numpy matplotlib scipy
        ```
        *(Note: `scipy` is optional, only needed for automatic fringe spacing measurement)*

4.  **Run the Application:**
    ```bash
    python gui.py
    ```

5.  **Deactivate Virtual Environment (if used):**
    ```bash
    deactivate
    ```

 ### 🐍 Dependencies

*   Python 3.x
*   NumPy (`pip install numpy`)
*   Matplotlib (`pip install matplotlib`)
*   SciPy (`pip install scipy`) - Optional, for fringe spacing measurement feature.
*   Tkinter (Usually included with Python standard library)

### 📜 License

This project did not adopt any license.