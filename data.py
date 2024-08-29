import re
from typing import List

import numpy as np
import pandas as pd


def read_file(data_source: str) -> pd.DataFrame:
    def read_two_lines_at_a_time(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            # Ensure there's an even number of lines to pair up
            if len(lines) % 2 != 0:
                lines.append('')  # Add an empty string if needed
            paired_lines = [lines[i:i + 2] for i in range(0, len(lines), 2)]
            return paired_lines

    source_data = read_two_lines_at_a_time(data_source)
    df_data = list()
    for group in source_data:
        col = group[0].strip().split()[1:]
        data = group[1].strip().split()
        if len(data) == 0:
            continue
        aline = dict()
        for i in range(len(col)):
            aline[col[i]] = data[i]
        df_data.append(aline)

    # 构造DataFrame
    df = pd.DataFrame(df_data)
    df = df.apply(pd.to_numeric).fillna(0)
    df['Timestep'] = df['Timestep'] / 1000
    return df


class LineData:
    def __init__(self, data: List, label: str):
        self.data = data
        self.label = label


class TableData:
    def __init__(self, file_path):
        self.x: List[str | int] = list()
        self.y: List[LineData] = list()
        self.df = read_file(file_path)
        self.index_col = "Timestep"

        self.ignore_columns = ['Timestep', 'No_Moles', 'No_Specs']
        self.timestamps = self.df['Timestep']

        self.organic_columns = []
        self.C1_C4_columns = []
        self.C5_C13_columns = []
        self.C14_C40_columns = []
        self.C40p_columns = []
        self.non_organic_columns = []

        for col in self.df.columns:
            if col in self.ignore_columns:  # 排除忽略列
                continue

            if 'C' in col and 'H' in col:  # 同时含C和H判定为有机物
                self.organic_columns.append(col)
                continue

            res = re.search(r'C(\d+)', col)
            if res and int(res.group(1)) >= 2:  # C后有数字且大于2判定为有机物
                self.organic_columns.append(col)

            elif not res or int(res.group(1)) < 2:
                self.non_organic_columns.append(col)

        for col in self.organic_columns:  # 有机物细分判断
            res = re.search(r'C(\d+)', col)
            if not res or int(res.group(1)) < 5:  # C1-C4
                self.C1_C4_columns.append(col)
            elif int(res.group(1)) < 14:  # C5-C13
                self.C5_C13_columns.append(col)
            elif int(res.group(1)) < 41:  # C14-C40
                self.C14_C40_columns.append(col)
            else:  # C40+
                self.C40p_columns.append(col)

        # 统计每个时间段的各有机物数量总和
        self.df['Organic_Count'] = self.df[self.organic_columns].sum(axis=1)  # 有机物总数
        self.df['Non_Organic_Count'] = self.df[self.non_organic_columns].sum(axis=1)  # 无机物总数
        self.df['C1_C4_Count'] = self.df[self.C1_C4_columns].sum(axis=1)  # C1-C4总数
        self.df['C5_C13_Count'] = self.df[self.C5_C13_columns].sum(axis=1)  # C5-C13总数
        self.df['C14_C40_Count'] = self.df[self.C14_C40_columns].sum(axis=1)  # C14-C40总数
        self.df['C40p_Count'] = self.df[self.C40p_columns].sum(axis=1)  # C40+总数

    def set_x_temp(self, initial_temp, heating_rate):
        """
        设置x轴温度
        :param initial_temp: 初始温度
        :param heating_rate: 升温速率
        :return:
        """
        # 将初始温度转化为float类型
        initial_temp = float(initial_temp)
        heating_rate = float(heating_rate)
        self.x = initial_temp + heating_rate * self.timestamps
        self.df['Temperature'] = self.x
        self.index_col = 'Temperature'

    def organic_content(self):  # 有机物含量
        for col in self.organic_columns:
            self.df[col + '_percentages'] = self.df[col] / self.df['Organic_Count'] * 100
            self.df[col + '_percentages'] = self.df[col + '_percentages'].apply(lambda x: 0 if pd.isna(x) else x)

        self.x = self.timestamps

        return_col = [self.index_col]

        for column in self.organic_columns:
            col_name = column + '_percentages'
            self.y.append(LineData(self.df[col_name], column))
            return_col.append(col_name)

        return self.df[return_col]

    def inorganic_content(self):
        for col in self.non_organic_columns:
            self.df[col + '_percentages'] = self.df[col] / self.df['Non_Organic_Count'] * 100
            self.df[col + '_percentages'] = self.df[col + '_percentages'].apply(lambda x: 0 if pd.isna(x) else x)

        self.x = self.timestamps
        return_col = [self.index_col]

        for column in self.non_organic_columns:
            col_name = column + '_percentages'
            self.y.append(LineData(self.df[col_name], column))
            return_col.append(col_name)

        return self.df[return_col]

    def organic_classification_content(self):
        self.df['C1_C4_percentages'] = self.df['C1_C4_Count'] / self.df['Organic_Count'] * 100
        self.df['C5_C13_percentages'] = self.df['C5_C13_Count'] / self.df['Organic_Count'] * 100
        self.df['C14_C40_percentages'] = self.df['C14_C40_Count'] / self.df['Organic_Count'] * 100
        self.df['C40p_percentages'] = self.df['C40p_Count'] / self.df['Organic_Count'] * 100

        # 确保在C1_C4_Count为0的情况下避免除以零错误
        self.df['C1_C4_percentages'] = self.df['C1_C4_percentages'].apply(lambda x: 0 if pd.isna(x) else x)
        self.df['C5_C13_percentages'] = self.df['C5_C13_percentages'].apply(lambda x: 0 if pd.isna(x) else x)
        self.df['C14_C40_percentages'] = self.df['C14_C40_percentages'].apply(lambda x: 0 if pd.isna(x) else x)
        self.df['C40p_percentages'] = self.df['C40p_percentages'].apply(lambda x: 0 if pd.isna(x) else x)

        self.x = self.timestamps

        self.y.append(LineData(self.df["C1_C4_percentages"], "C1-C4"))
        self.y.append(LineData(self.df["C5_C13_percentages"], "C5-C13"))
        self.y.append(LineData(self.df["C14_C40_percentages"], "C14-C40"))
        self.y.append(LineData(self.df["C40p_percentages"], "C40+"))

        return self.df[
            [self.index_col, "C1_C4_percentages", "C5_C13_percentages", "C14_C40_percentages", "C40p_percentages"]]

    def organic_products(self):
        last_timestamp_index = self.df[self.index_col].idxmax()
        all_last = self.df.loc[last_timestamp_index, self.organic_columns].sum()
        values = []
        names = []
        for col in self.organic_columns:
            if self.df.loc[last_timestamp_index, col] > 0:
                names.append(col)
                values.append(self.df.loc[last_timestamp_index, col] / all_last * 100)

        ind = np.arange(len(names))
        self.x = ind
        self.y.append(LineData(values, "organic_products"))

        output_dict = dict()
        output_dict[self.index_col] = self.df.loc[last_timestamp_index, self.index_col]
        output_dict.update(dict(zip(names, values)))
        return names, pd.DataFrame(output_dict, index=[0])

    def organic_classification_products(self):
        last_timestamp_index = self.df[self.index_col].idxmax()
        C1_C4_last = self.df.loc[last_timestamp_index, self.C1_C4_columns].sum()
        C5_C13_last = self.df.loc[last_timestamp_index, self.C5_C13_columns].sum()
        C14_C40_last = self.df.loc[last_timestamp_index, self.C14_C40_columns].sum()
        C40p_last = self.df.loc[last_timestamp_index, self.C40p_columns].sum()
        all_last = self.df.loc[last_timestamp_index, self.organic_columns].sum()
        # 创建一个字典来存储数据，便于绘图
        data = {
            'C1-C4': C1_C4_last / all_last * 100,
            'C5-C13': C5_C13_last / all_last * 100,
            'C14-C40': C14_C40_last / all_last * 100,
            'C40+': C40p_last / all_last * 100
        }
        names = list(data.keys())
        values = list(data.values())
        ind = np.arange(len(names))
        self.x = ind
        self.y.append(LineData(values, "organic_classification_products"))
        output_dict = dict()
        output_dict[self.index_col] = self.df.loc[last_timestamp_index, self.index_col]
        output_dict.update(data)
        return names, pd.DataFrame(output_dict, index=[0])

    def organic_amount(self):
        self.x = self.timestamps
        for column in self.organic_columns:
            self.y.append(LineData(self.df[column], label=column))

        return self.df[[self.index_col] + self.organic_columns]

    def inorganic_amount(self):
        self.x = self.timestamps
        for column in self.non_organic_columns:
            self.y.append(LineData(self.df[column], label=column))
        return self.df[[self.index_col] + self.non_organic_columns]

    def organic_classification_amount(self):
        self.x = self.timestamps

        self.y.append(LineData(self.df['C1_C4_Count'], label='C1-C4'))
        self.y.append(LineData(self.df['C5_C13_Count'], label='C5-C13'))
        self.y.append(LineData(self.df['C14_C40_Count'], label='C14-C40'))
        self.y.append(LineData(self.df['C40p_Count'], label='C40+'))

        return self.df[[self.index_col, 'C1_C4_Count', 'C5_C13_Count', 'C14_C40_Count', 'C40p_Count']]

    def organic_products_amount(self):
        last_timestamp_index = self.df[self.index_col].idxmax()
        values = []
        names = []
        for col in self.organic_columns:
            if self.df.loc[last_timestamp_index, col] > 0:
                names.append(col)
                values.append(self.df.loc[last_timestamp_index, col])

        ind = np.arange(len(names))
        self.x = ind
        self.y.append(LineData(values, "organic_products_amount"))
        output_dict = dict()
        output_dict[self.index_col] = self.df.loc[last_timestamp_index, self.index_col]
        output_dict.update(dict(zip(names, values)))
        return names, pd.DataFrame(output_dict, index=[0])

    def organic_classification_products_amount(self):
        last_timestamp_index = self.df[self.index_col].idxmax()
        C1_C4_last = self.df.loc[last_timestamp_index, self.C1_C4_columns].sum()
        C5_C13_last = self.df.loc[last_timestamp_index, self.C5_C13_columns].sum()
        C14_C40_last = self.df.loc[last_timestamp_index, self.C14_C40_columns].sum()
        C40p_last = self.df.loc[last_timestamp_index, self.C40p_columns].sum()
        all_last = self.df.loc[last_timestamp_index, self.organic_columns].sum()

        # 创建一个字典来存储数据，便于绘图
        data = {'C1-C4': C1_C4_last,
                'C5-C13': C5_C13_last,
                'C14-C40': C14_C40_last,
                'C40+': C40p_last}
        names = list(data.keys())
        values = list(data.values())
        ind = np.arange(len(names))
        self.x = ind
        self.y.append(LineData(values, "organic_classification_products"))

        output_dict = dict()
        output_dict[self.index_col] = self.df.loc[last_timestamp_index, self.index_col]
        output_dict.update(data)
        return names, pd.DataFrame(output_dict, index=[0])
