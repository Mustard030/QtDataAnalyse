import pandas as pd
import matplotlib.pyplot as plt
import re

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

# 统计每个时间段的各有机物数量总和
df['Organic_Count'] = df[organic_columns].sum(axis=1)  # 有机物总数
df['Non_Organic_Count'] = df[non_organic_columns].sum(axis=1)  # 无机物总数
df['C1_C4_Count'] = df[C1_C4_columns].sum(axis=1)  # C1-C4总数
df['C5_C13_Count'] = df[C5_C13_columns].sum(axis=1)  # C5-C13总数
df['C14_C40_Count'] = df[C14_C40_columns].sum(axis=1)  # C14-C40总数
df['C40p_Count'] = df[C40p_columns].sum(axis=1)  # C40+总数

organic_counts = df['Organic_Count']
non_organic_counts = df['Non_Organic_Count']
C1_C4_counts = df['C1_C4_Count']
C5_C13_counts = df['C5_C13_Count']
C14_C40_counts = df['C14_C40_Count']
C40p_counts = df['C40p_Count']

for col in non_organic_columns:
    df[col+'_percentages'] = df[col] / non_organic_counts * 100
    df[col+'_percentages'] = df[col+'_percentages'].apply(lambda x: 0 if pd.isna(x) else x)

# ################################# 绘图 ################################

plt.figure(figsize=(12, 6))

# 各无机物分别渲染
for column in non_organic_columns:
    plt.plot(timestamps, df[column+'_percentages'], label=column)

# 所有无机物汇总渲染
# plt.plot(timestamps, non_organic_counts, label='Non-Organic')

# 各有机物分别渲染
# for column in organic_columns:
#     plt.plot(timestamps, df[column], label=column)

# 所有有机物汇总渲染
# plt.plot(timestamps, organic_counts, label='Organic')

# C1-C4, C5-C13, C14-C40, C40+的有机物渲染
# plt.plot(timestamps, C1_C4_counts, label='C1-C4')
# plt.plot(timestamps, C5_C13_counts, label='C5-C13')
# plt.plot(timestamps, C14_C40_counts, label='C14-C40')
# plt.plot(timestamps, C40p_counts, label='C40+')


# 绘制参数
plt.xlabel('Timestep')  # X轴标签
plt.ylabel('Percentage')    # Y轴标签
plt.title('Non-Organic Percentage Over Time')
plt.legend()
plt.grid(True)
plt.show()
