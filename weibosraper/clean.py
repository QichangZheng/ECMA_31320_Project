import os
import json
from collections import OrderedDict
import pandas as pd
from transformers import pipeline
from tqdm import tqdm
import sys
from mpi4py import MPI
from datetime import datetime,timedelta


model_name = 'uer/roberta-base-finetuned-jd-binary-chinese'
nlp = pipeline('sentiment-analysis', model=model_name)

regions = set(open('regions.txt', 'r', encoding='utf-8').read().splitlines())

def contains_keyword(text, keywords_set):
    return any(keyword in text for keyword in keywords_set)

def find_keywords(text, keywords_set):
    return [keyword for keyword in keywords_set if keyword in text]

def get_negative_sentiment_score(text, nlp):
    try:
        result = nlp(text)
        negative_sentiment = result[0]['score'] if result[0]['label'] == 'negative (stars 1, 2 and 3)' else 1 - result[0]['score']
    except:
        negative_sentiment = 'NA'
    return negative_sentiment

def jsonl_to_csv(directory_path=None, folder_path=None):
    if directory_path is not None:
        # 遍历所有文件夹
        for folder_name in tqdm(os.listdir(directory_path), colour='blue'):
            folder_path = os.path.join(directory_path, folder_name)
            process_folder(folder_path)
    elif folder_path is not None:
        process_folder(folder_path)
    else:
        raise ValueError("Either directory_path or folder_path must be provided.")

def process_folder(folder_path, end='.jsonl'):
    if os.path.exists(folder_path):
        # 遍历文件夹中的所有jsonl文件
        for file_name in os.listdir(folder_path):
            if file_name.endswith(end):
                # 构建文件路径
                file_path = os.path.join(folder_path, file_name)

                filename = os.path.splitext(file_name)[0]
                # 检查csv文件是否已经存在
                csv_file_path = os.path.join(folder_path, filename + '.csv')
                if os.path.exists(csv_file_path):
                    print(f"{csv_file_path} already exists. Skipping...")
                    continue

                # 读取jsonl文件
                data = []
                # print(file_path)
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f.readlines():
                        record = json.loads(line, object_pairs_hook=OrderedDict)
                        record['content'] = record['content'].replace(f'#{filename}#', '')
                        data.append(record)

                # 将数据转换为pandas DataFrame格式
                df = pd.DataFrame(data).loc[:, ['ip_location', 'content']]
                df['contained_keywords'] = df['content'].apply(lambda x: find_keywords(x, regions))
                df['has_keyword'] = df['contained_keywords'].apply(lambda x: bool(len(x) > 0))
                negative_score = []
                for text in tqdm(df['content'], colour='green'):
                    negative_score.append(get_negative_sentiment_score(text, nlp))
                df['negative_sentiment_score'] = negative_score

                # 将DataFrame导出为csv文件
                df.to_csv(csv_file_path, index=False, encoding='utf-8')
    else:
        print(f"{folder_path} does not exist")
    print(f"Finished processing {folder_path}")

start_date = '2022-04-25'
if len(sys.argv) > 1:
    start_date = sys.argv[1]
rank = MPI.COMM_WORLD.Get_rank()
start_date = datetime.strptime(start_date, '%Y-%m-%d')
curr = start_date + timedelta(days=rank)
if __name__ == '__main__':
    # jsonl_to_csv(directory_path='output')
    # jsonl_to_csv(folder_path='output/2022-04-28')
    jsonl_to_csv(folder_path="output/" + curr.strftime('%Y-%m-%d'))
    # process_folder('output/2022-04-26', end='残疾爷爷跪地拾柴救病孙.jsonl')
    # jsonl_to_csv(file_name='output/2022-04-26/2022-04-26-0.jsonl')
