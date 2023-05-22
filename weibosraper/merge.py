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

def extract_location(ip_location):
    if pd.isnull(ip_location):
        return ""
    location = ip_location.split(' ')[-1]
    return convert_to_pinyin([location])[0]

def merge_csv_files(root_folder, output_file):
    merged_data = pd.DataFrame(columns=["date", "keyword", "contains_keyword", "ip_loc", "region", "region_info", "score"])

    for folder in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder)

        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)

                if file_path.endswith(".csv"):
                    data = pd.read_csv(file_path)

                    extracted_data = data.iloc[:, [0, 2, 3, 4]].copy()

                    extracted_data.columns = ["ip_loc", "region", "region_info", "score"]

                    extracted_data['region'] = extracted_data['region'].apply(process_region)

                    # 在这里处理 'ip_loc' 列，将其转化为拼音
                    extracted_data['ip_loc'] = extracted_data['ip_loc'].apply(extract_location)

                    extracted_data.insert(0, "date", folder)

                    # 修改此处，将文件名去掉后缀并插入到第二列
                    extracted_data.insert(1, "keyword", file[:-4])

                    file_contains_keyword = contains_keyword(file, regions)
                    extracted_data.insert(2, "contains_keyword", file_contains_keyword)

                    merged_data = pd.concat([merged_data, extracted_data], ignore_index=True)

    merged_data.to_csv(output_file, index=False)

if __name__ == "__main__":
    root_folder = "output"
    output_file = "merged_data.csv"
    merge_csv_files(root_folder, output_file)
