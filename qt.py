import sys
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, \
    QFileDialog, QComboBox, QSplitter, QLineEdit
from PyQt5.QtCore import Qt
import matplotlib.font_manager as font_manager

from data import TableData


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = plt.Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class TabPage(QWidget):
    def __init__(self, title):
        super().__init__()
        self.file_line_edit = QLineEdit()
        self.combo_box_count = QComboBox()
        self.combo_box_type = QComboBox()
        self.sc = None

        # 查找系统中的中文字体
        font_list = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
        chinese_fonts = [f for f in font_list if 'SimSun' in f or 'msyh.ttc' in f]

        # 使用找到的第一个中文字体
        if chinese_fonts:
            self.font = font_manager.FontProperties(fname=chinese_fonts[0], size=10)
            # 设置全局字体
            plt.rcParams['font.sans-serif'] = [self.font.get_name()]
        else:
            # 如果没有找到中文字体，则使用默认字体
            self.font = font_manager.FontProperties(size=10)

        if title == '等温热解':
            self.equal_heat_decompose()
        else:
            self.heating_pyrolysis()

    # 等温热解
    def equal_heat_decompose(self):
        layout = QVBoxLayout()
        left_layout = QVBoxLayout()  # 使用更紧凑的垂直布局
        left_layout.setSpacing(1)  # 减小控件之间的间距

        file_input_layout = QHBoxLayout()  # 使用HBox布局使按钮和文本框紧凑排列
        choose_file_button = QPushButton('选择文件')
        choose_file_button.clicked.connect(self.open_filename_dialog)
        file_input_layout.addWidget(choose_file_button)
        self.file_line_edit = QLineEdit()
        self.file_line_edit.setReadOnly(True)
        self.file_line_edit.setFixedHeight(24)  # 设置文本框的固定高度
        file_input_layout.addWidget(self.file_line_edit)
        left_layout.addLayout(file_input_layout)

        self.combo_box_type = QComboBox()
        self.combo_box_type.addItem("有机物")
        self.combo_box_type.addItem("无机物")
        self.combo_box_type.addItem("有机物分类")
        self.combo_box_type.addItem("最终有机产物")
        self.combo_box_type.addItem("最终有机产物分类")
        self.combo_box_type.currentIndexChanged.connect(self.update_plot)
        left_layout.addWidget(self.combo_box_type)

        self.combo_box_count = QComboBox()
        self.combo_box_count.addItem("含量")
        self.combo_box_count.addItem("数量")
        self.combo_box_count.currentIndexChanged.connect(self.update_plot)
        left_layout.addWidget(self.combo_box_count)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout()
        self.sc = MplCanvas(right_widget, width=5, height=4, dpi=100)
        toolbar = NavigationToolbar2QT(self.sc, right_widget)
        right_layout.addWidget(toolbar)
        right_layout.addWidget(self.sc)
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

    # 升温热解
    def heating_pyrolysis(self):
        layout = QVBoxLayout()
        button = QPushButton("升温热解")
        layout.addWidget(button)
        self.setLayout(layout)

    # 选择文件
    def open_filename_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "所有文件 (*);;文本文件 (*.txt)")
        if file_name:
            self.file_line_edit.setText(file_name)
            self.update_plot()  # 文件选择后立即更新图表

    # 更新图表
    def update_plot(self):
        # 获取当前选择的文件路径
        file_path = self.file_line_edit.text()
        # 获取当前选择的含量类型
        count_type = self.combo_box_count.currentText()
        # 获取当前选择的有机物类型
        organic_type = self.combo_box_type.currentText()

        print("文件路径:", file_path, "含量类型:", count_type, "有机物类型:", organic_type)

        self.sc.axes.clear()  # 清除旧的图表

        data = TableData(file_path)
        if organic_type == '有机物' and count_type == '含量':
            data.organic_content()
            for line in data.y:
                self.sc.axes.plot(data.x, line.data, label=line.label)  # 绘制新的图表

            # 设置图表标题和坐标轴标签
            self.sc.axes.set_title('各有机物含量', fontproperties=self.font)
            self.sc.axes.set_xlabel('皮秒(ps)', fontproperties=self.font)
            self.sc.axes.set_ylabel('含量', fontproperties=self.font)

        elif organic_type == '无机物' and count_type == '含量':
            data.inorganic_content()
            for line in data.y:
                self.sc.axes.plot(data.x, line.data, label=line.label)  # 绘制新的图表

            # 设置图表标题和坐标轴标签
            self.sc.axes.set_title('各无机物含量', fontproperties=self.font)
            self.sc.axes.set_xlabel('皮秒(ps)', fontproperties=self.font)
            self.sc.axes.set_ylabel('含量', fontproperties=self.font)

        elif organic_type == '有机物分类' and count_type == '含量':
            data.organic_classification_content()
            for line in data.y:
                self.sc.axes.plot(data.x, line.data, label=line.label)  # 绘制新的图表

            # 设置图表标题和坐标轴标签
            self.sc.axes.set_title('有机物分类含量', fontproperties=self.font)
            self.sc.axes.set_xlabel('皮秒(ps)', fontproperties=self.font)
            self.sc.axes.set_ylabel('含量', fontproperties=self.font)

        # 添加图例，并使其浮动在右上角
        legend = self.sc.axes.legend()
        # 为图例添加点击事件监听器
        legend.set_draggable(True)  # 允许拖动图例
        legend.figure.canvas.mpl_connect('pick_event', self.on_pick)  # 连接点击事件

        self.sc.draw()  # 更新图表

    # 定义点击事件处理函数
    def on_pick(self, event):
        # 获取点击的图例项
        legline = event.artist
        origline = legline.get_children()[0]  # 获取原始的线条对象
        legline.set_alpha(1)  # 设置图例线条的透明度为 1，确保始终可见

        # 切换原始线条的可见性
        if origline.get_visible():
            origline.set_visible(False)
            legline.set_alpha(0.2)  # 设置图例线条的透明度为 0.2，表示被隐藏
        else:
            origline.set_visible(True)
            legline.set_alpha(1)  # 设置图例线条的透明度为 1，表示可见

        # 更新图表
        legline.figure.canvas.draw()


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        tab_widget = QTabWidget()

        tab1 = TabPage('等温热解')
        tab_widget.addTab(tab1, '等温热解')

        tab2 = TabPage('升温热解')
        tab_widget.addTab(tab2, '升温热解')

        self.setCentralWidget(tab_widget)

        self.setWindowTitle('My App')
        self.resize(1300, 800)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
