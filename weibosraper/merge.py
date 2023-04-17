import os
import pandas as pd
from pypinyin import pinyin, Style

regions = set(open('regions.txt', 'r', encoding='utf-8').read().splitlines())

def contains_keyword(text, keywords_set):
    return any(keyword in text for keyword in keywords_set)

def convert_to_pinyin(city_list):
    translated_cities = []
    for city in city_list:
        city_pinyin = pinyin(city, style=Style.NORMAL, heteronym=False)
        city_pinyin = [''.join(word.capitalize() for word in words) for words in city_pinyin]
        translated_cities.append(''.join(city_pinyin))
    return translated_cities

def process_region(region):
    region_list = eval(region)
    return convert_to_pinyin(region_list)

import os
import pandas as pd
from pypinyin import pinyin, Style

# ...

def merge_csv_files(root_folder, output_file):
    # 初始化一个空的DataFrame，用于存储合并后的数据
    merged_data = pd.DataFrame(columns=["date", "file_name", "contains_keyword", "region", "region_info", "score"])

    # 遍历文件夹中的所有子文件夹
    for folder in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder)

        # 检查是否为文件夹
        if os.path.isdir(folder_path):
            # 遍历文件夹中的所有文件
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)

                # 检查是否为csv文件
                if file_path.endswith(".csv"):
                    # 读取csv文件
                    data = pd.read_csv(file_path)

                    # 提取csv文件中的第3、4、5列（使用索引2、3、4）
                    extracted_data = data.iloc[:, [2, 3, 4]].copy()

                    # 修改提取出的数据的列名以匹配最终的合并数据的列名
                    extracted_data.columns = ["region", "region_info", "score"]

                    # 对地区名进行转换
                    extracted_data['region'] = extracted_data['region'].apply(process_region)

                    # 将文件夹名称添加为新的一列，并将其放在第一列的位置
                    extracted_data.insert(0, "date", folder)

                    # 插入包含文件名的新列到第二列
                    extracted_data.insert(1, "file_name", file)

                    # 检查文件名是否包含关键词
                    file_contains_keyword = contains_keyword(file, regions)
                    extracted_data.insert(2, "contains_keyword", file_contains_keyword)

                    # 将提取到的数据追加到合并后的数据中
                    merged_data = pd.concat([merged_data, extracted_data], ignore_index=True)

    # 保存合并后的数据到csv文件中
    merged_data.to_csv(output_file, index=False)

if __name__ == "__main__":
    root_folder = "output"
    output_file = "merged_data.csv"
    merge_csv_files(root_folder, output_file)


