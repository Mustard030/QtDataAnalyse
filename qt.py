import sys
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, \
    QFileDialog, QComboBox, QSplitter, QLineEdit
from PyQt5.QtCore import Qt


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = plt.Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class TabPage(QWidget):
    def __init__(self, title):
        super().__init__()
        layout = QVBoxLayout()
        if title == '等温热解':
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

            self.combo_box_count = QComboBox()
            self.combo_box_count.addItem("含量")
            self.combo_box_count.addItem("数量")
            self.combo_box_count.currentIndexChanged.connect(self.update_plot)
            left_layout.addWidget(self.combo_box_count)

            self.combo_box_type = QComboBox()
            self.combo_box_type.addItem("有机物")
            self.combo_box_type.addItem("无机物")
            self.combo_box_type.addItem("有机物分类")
            self.combo_box_type.addItem("最终有机产物")
            self.combo_box_type.addItem("最终有机产物分类")
            self.combo_box_type.currentIndexChanged.connect(self.update_plot)
            left_layout.addWidget(self.combo_box_type)

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
        else:
            button = QPushButton(title)
            layout.addWidget(button)
        self.setLayout(layout)

    def open_filename_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "所有文件 (*);;文本文件 (*.txt)")
        if file_name:
            self.file_line_edit.setText(file_name)
            self.update_plot()  # 文件选择后立即更新图表

    def update_plot(self):
        # 获取当前选择的文件路径
        file_path = self.file_line_edit.text()
        # 获取当前选择的含量类型
        count_type = self.combo_box_count.currentText()
        # 获取当前选择的有机物类型
        organic_type = self.combo_box_type.currentText()

        print("文件路径:", file_path, "含量类型:", count_type, "有机物类型:", organic_type)

        # 假设我们已经有了x和y的数据
        x = np.linspace(0, 10, 100)
        y = np.sin(x)

        self.sc.axes.clear()  # 清除旧的图表
        self.sc.axes.plot(x, y)  # 绘制新的图表
        self.sc.draw()  # 更新图表


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
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
