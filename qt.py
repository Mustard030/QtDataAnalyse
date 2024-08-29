import os
import subprocess
import sys
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QTabWidget, QWidget, QVBoxLayout, \
    QHBoxLayout, \
    QPushButton, \
    QFileDialog, QComboBox, QSplitter, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt
import matplotlib.font_manager as font_manager

from data import TableData

# pyinstaller -F -n 数据分析 --noconsole qt.py

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = plt.Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class TabPage(QWidget):
    def __init__(self, title):
        super().__init__()
        self.initial_temp_line_edit = None
        self.heating_rate_line_edit = None
        self.file_line_edit = QLineEdit()
        self.combo_box_count = QComboBox()
        self.combo_box_type = QComboBox()
        self.sc = None
        self.file_path = None  # 当前选择的文件路径
        self.count_type = None  # 当前选择的含量类型
        self.organic_type = None  # 当前选择的有机物类型
        self.data = None    # 当前选择的类型计算出的数据
        self.export_df = None    # 限定data.df中数据列

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
        elif title == '升温热解':
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
        self.combo_box_type.currentIndexChanged.connect(self.update_plot_equal_heat)
        left_layout.addWidget(self.combo_box_type)

        self.combo_box_count = QComboBox()
        self.combo_box_count.addItem("含量")
        self.combo_box_count.addItem("数量")
        self.combo_box_count.currentIndexChanged.connect(self.update_plot_equal_heat)
        left_layout.addWidget(self.combo_box_count)

        # 添加导出按钮
        export_button = QPushButton('导出Excel')
        export_button.clicked.connect(self.export_data)
        left_layout.addWidget(export_button)

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
        left_layout = QVBoxLayout()  # 使用更紧凑的垂直布局
        left_layout.setSpacing(1)  # 减小控件之间的间距

        file_input_layout = QHBoxLayout()  # 使用HBox布局使按钮和文本框紧凑排列
        choose_file_button = QPushButton('选择文件')
        choose_file_button.clicked.connect(self.open_filename_dialog_heating)
        file_input_layout.addWidget(choose_file_button)
        self.file_line_edit = QLineEdit()
        self.file_line_edit.setReadOnly(True)
        self.file_line_edit.setFixedHeight(24)  # 设置文本框的固定高度
        file_input_layout.addWidget(self.file_line_edit)
        left_layout.addLayout(file_input_layout)

        # 添加初始温度输入框
        initial_temp_layout = QHBoxLayout()
        initial_temp_label = QLabel("初始温度 (℃):")
        self.initial_temp_line_edit = QLineEdit()
        self.initial_temp_line_edit.setValidator(QDoubleValidator())  # 验证输入为数字
        initial_temp_layout.addWidget(initial_temp_label)
        initial_temp_layout.addWidget(self.initial_temp_line_edit)
        left_layout.addLayout(initial_temp_layout)

        # 添加升温速率输入框
        heating_rate_layout = QHBoxLayout()
        heating_rate_label = QLabel("升温速率 (℃/ps):")
        self.heating_rate_line_edit = QLineEdit()
        self.heating_rate_line_edit.setValidator(QDoubleValidator())  # 验证输入为数字
        heating_rate_layout.addWidget(heating_rate_label)
        heating_rate_layout.addWidget(self.heating_rate_line_edit)
        left_layout.addLayout(heating_rate_layout)

        self.combo_box_type = QComboBox()
        self.combo_box_type.addItem("有机物")
        self.combo_box_type.addItem("无机物")
        self.combo_box_type.addItem("有机物分类")
        self.combo_box_type.addItem("最终有机产物")
        self.combo_box_type.addItem("最终有机产物分类")
        self.combo_box_type.currentIndexChanged.connect(self.update_plot_heating)
        left_layout.addWidget(self.combo_box_type)

        self.combo_box_count = QComboBox()
        self.combo_box_count.addItem("含量")
        self.combo_box_count.addItem("数量")
        self.combo_box_count.currentIndexChanged.connect(self.update_plot_heating)
        left_layout.addWidget(self.combo_box_count)

        # 添加导出按钮
        export_button = QPushButton('导出Excel')
        export_button.clicked.connect(self.export_data)
        left_layout.addWidget(export_button)

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

    # 选择文件
    def open_filename_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "所有文件 (*);;文本文件 (*.txt)")
        if file_name:
            self.file_line_edit.setText(file_name)
            self.update_plot_equal_heat()  # 文件选择后立即更新图表

        # 选择文件
    def open_filename_dialog_heating(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "所有文件 (*);;文本文件 (*.txt)")
        if file_name:
            self.file_line_edit.setText(file_name)
            self.update_plot_heating()  # 文件选择后立即更新图表

    # 更新数据
    def refresh_data(self):
        # 获取当前选择的文件路径
        self.file_path = self.file_line_edit.text()
        # 获取当前选择的含量类型
        self.count_type = self.combo_box_count.currentText()
        # 获取当前选择的有机物类型
        self.organic_type = self.combo_box_type.currentText()

        print("文件路径:", self.file_path, "含量类型:", self.count_type, "有机物类型:", self.organic_type)

        self.sc.axes.clear()  # 清除旧的图表

        self.data = TableData(self.file_path)

    # 更新图表
    def update_plot_equal_heat(self):
        self.refresh_data()

        self.sc.axes.clear()  # 清除旧的图表

        if self.count_type == '含量':
            self.sc.axes.set_xlabel('时间', fontproperties=self.font)
            self.sc.axes.set_ylabel('含量(%)', fontproperties=self.font)

            if self.organic_type == '有机物':
                self.export_df = self.data.organic_content()
                for line in self.data.y:
                    self.sc.axes.plot(self.data.x, line.data, label=line.label)  # 绘制新的图表
                self.sc.axes.set_title('各有机物含量', fontproperties=self.font)

            elif self.organic_type == '无机物':
                self.export_df = self.data.inorganic_content()
                for line in self.data.y:
                    self.sc.axes.plot(self.data.x, line.data, label=line.label)  # 绘制新的图表
                self.sc.axes.set_title('各无机物含量', fontproperties=self.font)

            elif self.organic_type == '有机物分类':
                self.export_df = self.data.organic_classification_content()
                for line in self.data.y:
                    self.sc.axes.plot(self.data.x, line.data, label=line.label)  # 绘制新的图表
                self.sc.axes.set_title('有机物分类含量', fontproperties=self.font)

            elif self.organic_type == '最终有机产物':
                names, self.export_df = self.data.organic_products()
                for line in self.data.y:
                    self.sc.axes.bar(self.data.x, line.data, 0.35)  # 绘制新的图表
                    self.sc.axes.set_xticks(self.data.x)
                    self.sc.axes.set_xticklabels(names, rotation=45, fontproperties=self.font)
                    for i, v in enumerate(line.data):
                        self.sc.axes.text(i, v, f"{v:.1f}%", ha='center', va='bottom', fontproperties=self.font)
                self.sc.axes.set_title('最终有机产物含量', fontproperties=self.font)
                self.sc.axes.set_xlabel('最终有机产物', fontproperties=self.font)

            elif self.organic_type == '最终有机产物分类':
                names, self.export_df = self.data.organic_classification_products()
                for line in self.data.y:
                    self.sc.axes.bar(self.data.x, line.data, 0.35)  # 绘制新的图表
                    self.sc.axes.set_xticks(self.data.x)
                    self.sc.axes.set_xticklabels(names, rotation=45, fontproperties=self.font)
                    for i, v in enumerate(line.data):
                        self.sc.axes.text(i, v, f"{v:.1f}%", ha='center', va='bottom', fontproperties=self.font)
                self.sc.axes.set_title('最终有机产物分类含量', fontproperties=self.font)
                self.sc.axes.set_xlabel('最终有机产物分类', fontproperties=self.font)

        elif self.count_type == '数量':
            self.sc.axes.set_xlabel('皮秒(ps)', fontproperties=self.font)
            self.sc.axes.set_ylabel('数量', fontproperties=self.font)

            if self.organic_type == '有机物':
                self.export_df = self.data.organic_amount()
                for line in self.data.y:
                    self.sc.axes.plot(self.data.x, line.data, label=line.label)  # 绘制新的图表
                self.sc.axes.set_title('各有机物数量', fontproperties=self.font)

            elif self.organic_type == '无机物':
                self.export_df = self.data.inorganic_amount()
                for line in self.data.y:
                    self.sc.axes.plot(self.data.x, line.data, label=line.label)  # 绘制新的图表
                self.sc.axes.set_title('各无机物数量', fontproperties=self.font)

            elif self.organic_type == '有机物分类':
                self.export_df = self.data.organic_classification_amount()
                for line in self.data.y:
                    self.sc.axes.plot(self.data.x, line.data, label=line.label)  # 绘制新的图表
                self.sc.axes.set_title('有机物分类数量', fontproperties=self.font)

            elif self.organic_type == '最终有机产物':
                names, self.export_df = self.data.organic_products_amount()
                for line in self.data.y:
                    self.sc.axes.bar(self.data.x, line.data, 0.35)  # 绘制新的图表
                    self.sc.axes.set_xticks(self.data.x)
                    self.sc.axes.set_xticklabels(names, rotation=45, fontproperties=self.font)
                    for i, v in enumerate(line.data):
                        self.sc.axes.text(i, v, f"{v:.1f}", ha='center', va='bottom', fontproperties=self.font)
                self.sc.axes.set_title('最终有机产物数量', fontproperties=self.font)
                self.sc.axes.set_xlabel('最终有机产物', fontproperties=self.font)

            elif self.organic_type == '最终有机产物分类':
                names, self.export_df = self.data.organic_classification_products_amount()
                for line in self.data.y:
                    self.sc.axes.bar(self.data.x, line.data, 0.35)  # 绘制新的图表
                    self.sc.axes.set_xticks(self.data.x)
                    self.sc.axes.set_xticklabels(names, rotation=45, fontproperties=self.font)
                    for i, v in enumerate(line.data):
                        self.sc.axes.text(i, v, f"{v:.1f}", ha='center', va='bottom', fontproperties=self.font)
                self.sc.axes.set_title('最终有机产物分类数量', fontproperties=self.font)
                self.sc.axes.set_xlabel('最终有机产物分类', fontproperties=self.font)

        # 添加图例，并使其浮动在右上角
        legend = self.sc.axes.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        # 为图例添加点击事件监听器
        legend.set_draggable(True)  # 允许拖动图例
        legend.figure.canvas.mpl_connect('pick_event', self.on_pick)  # 连接点击事件

        self.sc.draw()  # 更新图表

    # 更新图表
    def update_plot_heating(self):
        self.refresh_data()

        if not (bool(self.initial_temp_line_edit.text()) and bool(self.heating_rate_line_edit.text())):
            return

        print("文件路径:", self.file_path, "含量类型:", self.count_type, "有机物类型:", self.organic_type, "初始温度:", self.initial_temp_line_edit.text(), "加热速率:", self.heating_rate_line_edit.text())

        self.sc.axes.clear()  # 清除旧的图表

        self.data.set_x_temp(self.initial_temp_line_edit.text(), self.heating_rate_line_edit.text())

        if self.count_type == '含量':
            self.sc.axes.set_xlabel('温度(℃)', fontproperties=self.font)
            self.sc.axes.set_ylabel('含量(%)', fontproperties=self.font)

            if self.organic_type == '有机物':
                self.export_df = self.data.organic_content()
                for line in self.data.y:
                    self.sc.axes.plot(self.data.x, line.data, label=line.label)  # 绘制新的图表
                self.sc.axes.set_title('各有机物含量', fontproperties=self.font)

            elif self.organic_type == '无机物':
                self.export_df = self.data.inorganic_content()
                for line in self.data.y:
                    self.sc.axes.plot(self.data.x, line.data, label=line.label)  # 绘制新的图表
                self.sc.axes.set_title('各无机物含量', fontproperties=self.font)

            elif self.organic_type == '有机物分类':
                self.export_df = self.data.organic_classification_content()
                for line in self.data.y:
                    self.sc.axes.plot(self.data.x, line.data, label=line.label)  # 绘制新的图表
                self.sc.axes.set_title('有机物分类含量', fontproperties=self.font)

            elif self.organic_type == '最终有机产物':
                names, self.export_df = self.data.organic_products()
                for line in self.data.y:
                    self.sc.axes.bar(self.data.x, line.data, 0.35)  # 绘制新的图表
                    self.sc.axes.set_xticks(self.data.x)
                    self.sc.axes.set_xticklabels(names, rotation=45, fontproperties=self.font)
                    for i, v in enumerate(line.data):
                        self.sc.axes.text(i, v, f"{v:.1f}%", ha='center', va='bottom', fontproperties=self.font)
                self.sc.axes.set_title('最终有机产物含量', fontproperties=self.font)
                self.sc.axes.set_xlabel('最终有机产物', fontproperties=self.font)

            elif self.organic_type == '最终有机产物分类':
                names, self.export_df = self.data.organic_classification_products()
                for line in self.data.y:
                    self.sc.axes.bar(self.data.x, line.data, 0.35)  # 绘制新的图表
                    self.sc.axes.set_xticks(self.data.x)
                    self.sc.axes.set_xticklabels(names, rotation=45, fontproperties=self.font)
                    for i, v in enumerate(line.data):
                        self.sc.axes.text(i, v, f"{v:.1f}%", ha='center', va='bottom', fontproperties=self.font)
                self.sc.axes.set_title('最终有机产物分类含量', fontproperties=self.font)
                self.sc.axes.set_xlabel('最终有机产物分类', fontproperties=self.font)

        elif self.count_type == '数量':
            self.sc.axes.set_xlabel('温度(℃)', fontproperties=self.font)
            self.sc.axes.set_ylabel('数量', fontproperties=self.font)

            if self.organic_type == '有机物':
                self.export_df = self.data.organic_amount()
                for line in self.data.y:
                    self.sc.axes.plot(self.data.x, line.data, label=line.label)  # 绘制新的图表
                self.sc.axes.set_title('各有机物数量', fontproperties=self.font)

            elif self.organic_type == '无机物':
                self.export_df = self.data.inorganic_amount()
                for line in self.data.y:
                    self.sc.axes.plot(self.data.x, line.data, label=line.label)  # 绘制新的图表
                self.sc.axes.set_title('各无机物数量', fontproperties=self.font)

            elif self.organic_type == '有机物分类':
                self.export_df = self.data.organic_classification_amount()
                for line in self.data.y:
                    self.sc.axes.plot(self.data.x, line.data, label=line.label)  # 绘制新的图表
                self.sc.axes.set_title('有机物分类数量', fontproperties=self.font)

            elif self.organic_type == '最终有机产物':
                names, self.export_df = self.data.organic_products_amount()
                for line in self.data.y:
                    self.sc.axes.bar(self.data.x, line.data, 0.35)  # 绘制新的图表
                    self.sc.axes.set_xticks(self.data.x)
                    self.sc.axes.set_xticklabels(names, rotation=45, fontproperties=self.font)
                    for i, v in enumerate(line.data):
                        self.sc.axes.text(i, v, f"{v:.1f}", ha='center', va='bottom', fontproperties=self.font)
                self.sc.axes.set_title('最终有机产物数量', fontproperties=self.font)
                self.sc.axes.set_xlabel('最终有机产物', fontproperties=self.font)

            elif self.organic_type == '最终有机产物分类':
                names, self.export_df = self.data.organic_classification_products_amount()
                for line in self.data.y:
                    self.sc.axes.bar(self.data.x, line.data, 0.35)  # 绘制新的图表
                    self.sc.axes.set_xticks(self.data.x)
                    self.sc.axes.set_xticklabels(names, rotation=45, fontproperties=self.font)
                    for i, v in enumerate(line.data):
                        self.sc.axes.text(i, v, f"{v:.1f}", ha='center', va='bottom', fontproperties=self.font)
                self.sc.axes.set_title('最终有机产物分类数量', fontproperties=self.font)
                self.sc.axes.set_xlabel('最终有机产物分类', fontproperties=self.font)

        # 添加图例，并使其浮动在右上角
        legend = self.sc.axes.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        # 为图例添加点击事件监听器
        legend.set_draggable(True)  # 允许拖动图例
        legend.figure.canvas.mpl_connect('pick_event', self.on_pick)  # 连接点击事件

        self.sc.draw()  # 更新图表

    # 添加导出方法用于等温热解
    def export_data(self):
        # 打开对话框让用户选择目录并输入文件名
        file_name, _ = QFileDialog.getSaveFileName(self, "保存Excel文件", "", "Excel Files (*.xlsx)")
        if file_name:
            # 将数据写入 Excel 文件
            with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
                # 写入数据到 Excel 文件
                # 示例: df.to_excel(writer, sheet_name='Sheet1')
                self.export_df.to_excel(writer, sheet_name='Sheet1')

            # 弹出对话框提示导出成功
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("导出成功")
            msg_box.setText("文件已成功导出！")
            msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Open)
            msg_box.setDefaultButton(QMessageBox.Ok)

            # 连接按钮点击事件
            msg_box.button(QMessageBox.Open).clicked.connect(lambda: self.open_file(file_name))
            msg_box.exec_()

    def open_file(self, file_name):
        # 打开文件
        if os.name == 'nt':  # Windows
            os.startfile(file_name)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, file_name])

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
        self.resize(1400, 800)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
