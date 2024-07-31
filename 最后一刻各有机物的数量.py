import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用黑体显示中文
plt.rcParams['axes.unicode_minus'] = False   # 正常显示负号

data_source = input("数据文件路径：")
# data_source = r"C:\Users\Administrator\Downloads\species.out.txt"
if data_source.startswith('"') and data_source.endswith('"'):
    data_source = data_source[1:-1]


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

print(df)

# ################################ df数据构造完成 ################################

ignore_columns = ['Timestep', 'No_Moles', 'No_Specs']
timestamps = df['Timestep']

organic_columns = []
C1_C4_columns = []
C5_C13_columns = []
C14_C40_columns = []
C40p_columns = []
non_organic_columns = []

print(df.columns)

for col in df.columns:
    if col in ignore_columns:   # 排除忽略列
        continue

    if 'C' in col and 'H' in col:   # 同时含C和H判定为有机物
        organic_columns.append(col)
        continue

    res = re.search(r'C(\d+)', col)
    if res and int(res.group(1)) >= 2:  # C后有数字且大于2判定为有机物
        organic_columns.append(col)

    elif not res or int(res.group(1)) < 2:
        non_organic_columns.append(col)

for col in organic_columns:     # 有机物细分判断
    res = re.search(r'C(\d+)', col)
    if not res or int(res.group(1)) < 5:  # C1-C4
        C1_C4_columns.append(col)
    elif int(res.group(1)) < 14:  # C5-C13
        C5_C13_columns.append(col)
    elif int(res.group(1)) < 41:  # C14-C40
        C14_C40_columns.append(col)
    else:   # C40+
        C40p_columns.append(col)

# ##############检查判定结果是否正确###############
print("organic_columns:", organic_columns)
print("C1_C4_columns:", C1_C4_columns)
print("C5_C13_columns:", C5_C13_columns)
print("C14_C40_columns:", C14_C40_columns)
print("C40+_columns:", C40p_columns)
print("non_organic_columns:", non_organic_columns)


last_timestamp_index = df['Timestep'].idxmax()

# 创建一个字典来存储数据，便于绘图

values = []
names = []
for col in organic_columns:
    if df.loc[last_timestamp_index, col] > 0:
        names.append(col)
        values.append(df.loc[last_timestamp_index, col])

ind = np.arange(len(names))
# ################################# 绘图 ################################
plt.figure(figsize=(12, 6))
plt.bar(ind, values)
# 设置横坐标的标签位置和文本


# 绘制参数
plt.xlabel('各有机物')
plt.ylabel('数量')
plt.title('最后一时刻有机物数量')
plt.xticks(ind, names, rotation=45)
ax = plt.gca()
for i, v in enumerate(values):
    ax.text(i, v, f"{v}", ha='center', va='bottom')
plt.tight_layout()
plt.show()
