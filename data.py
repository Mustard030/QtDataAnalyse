from typing import List

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


class PointData:
    pass


class LineData:
    def __init__(self):
        self.x: List[str | int] = list()
        self.y: List[PointData] = list()
