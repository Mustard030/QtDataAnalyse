import matplotlib.pyplot as plt
import re
import data

# data_source = input("数据文件路径：")
data_source = r"C:\Users\Administrator\Downloads\species.out.txt"
if data_source.startswith('"') and data_source.endswith('"'):
    data_source = data_source[1:-1]

df = data.read_file(data_source)


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
df['Organic_Count'] = df[organic_columns].sum(axis=1)
df['Non_Organic_Count'] = df[non_organic_columns].sum(axis=1)
df['C1_C4_Count'] = df[C1_C4_columns].sum(axis=1)
df['C5_C13_Count'] = df[C5_C13_columns].sum(axis=1)
df['C14_C40_Count'] = df[C14_C40_columns].sum(axis=1)
df['C40p_Count'] = df[C40p_columns].sum(axis=1)

organic_counts = df['Organic_Count']
non_organic_counts = df['Non_Organic_Count']
C1_C4_counts = df['C1_C4_Count']
C5_C13_counts = df['C5_C13_Count']
C14_C40_counts = df['C14_C40_Count']
C40p_counts = df['C40p_Count']

# ################################# 绘图 ################################

plt.figure(figsize=(12, 6))

# 各无机物分别渲染
# for column in non_organic_columns:
#     plt.plot(timestamps, df[column], label=column)

# 所有无机物汇总渲染
# plt.plot(timestamps, non_organic_counts, label='Non-Organic')

# 各有机物分别渲染
# for column in organic_columns:
#     plt.plot(timestamps, df[column], label=column)

# 所有有机物汇总渲染
plt.plot(timestamps, organic_counts, label='Organic')

# C1-C4, C5-C13, C14-C40, C40+的有机物渲染
plt.plot(timestamps, C1_C4_counts, label='C1-C4')
plt.plot(timestamps, C5_C13_counts, label='C5-C13')
plt.plot(timestamps, C14_C40_counts, label='C14-C40')
plt.plot(timestamps, C40p_counts, label='C40+')


# 绘制参数
plt.xlabel('皮秒(ps)')  # X轴标签
plt.ylabel('Counts')    # Y轴标签
plt.title('Non-Organic Counts Over Time')
plt.legend()
plt.grid(True)
plt.show()
