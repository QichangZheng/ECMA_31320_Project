import os
import json
import csv
import pandas as pd
from collections import OrderedDict

# 指定jsonl文件所在的文件夹路径
folder_path = 'output'

# 遍历文件夹中的所有jsonl文件
for file_name in os.listdir(folder_path):
    if file_name.endswith('.jsonl'):
        # 构建文件路径
        file_path = os.path.join(folder_path, file_name)

        # 读取jsonl文件
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                record = json.loads(line, object_pairs_hook=OrderedDict)
                data.append(record)

        # 将数据转换为pandas DataFrame格式
        df = pd.DataFrame(data)

        # 将DataFrame导出为csv文件
        csv_file_path = os.path.splitext(file_path)[0] + '.csv'
        df.to_csv(csv_file_path, index=False, encoding='utf-8')
