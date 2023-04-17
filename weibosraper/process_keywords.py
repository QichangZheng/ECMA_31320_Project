import os
import json
import re
import csv
from datetime import datetime, timedelta
from transformers import pipeline
import pandas as pd


def process_json_files(start_date_str, end_date_str, input_folder, output_folder):
    # 创建情感分析 pipeline
    model_name = 'liam168/c2-roberta-base-finetuned-dianping-chinese'
    nlp = pipeline('sentiment-analysis', model=model_name)

    # 将日期字符串转换为 datetime 对象
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    # 计算日期范围
    date_range = (end_date - start_date).days + 1

    # 逐个处理给定日期范围内的 .json 文件
    for i in range(date_range):
        file_date = start_date + timedelta(days=i)
        file_date_str = file_date.strftime('%Y-%m-%d')
        file_name = f"{file_date_str}.json"

        try:
            with open(os.path.join(input_folder, file_name), encoding='utf-8') as f:
                data = json.load(f)
                keywords = [item['title'] for item in data]

            # 计算关键词的负面情感分数
            negative_sentiment_scores = []
            for keyword in keywords:
                result = nlp(keyword)
                negative_sentiment_score = result[0]['score'] \
                    if result[0]['label'] == 'negative' else 1 - result[0]['score']
                negative_sentiment_scores.append((keyword, negative_sentiment_score))

            # 将结果保存到相应的 .csv 文件
            output_file = os.path.join(output_folder, file_date_str + '.csv')
            with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['keywords', 'score'])
                csv_writer.writerows(negative_sentiment_scores)

        except FileNotFoundError:
            print(f"File {file_name} not found. Skipping.")
            continue

def extract_high_score_keywords(csv_file, k=10):
    df = pd.read_csv(csv_file)
    df = df.sort_values(by='score', ascending=False)
    high_score_keywords = df['keywords'][:k].tolist()

    return high_score_keywords

# 调用函数处理指定日期范围内的 .json 文件
if __name__ == '__main__':
    process_json_files('2022-03-28', '2022-05-28', 'Keywords/weibo-trending-hot-search/raw', 'KWS')
# process_json_files('2022-03-28', '2022-05-28', 'Keywords/weibo-trending-hot-search/raw', 'KWS')
