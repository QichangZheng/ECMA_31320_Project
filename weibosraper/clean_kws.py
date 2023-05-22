import os
import csv
from transformers import pipeline
from glob import glob
from pypinyin import pinyin, Style

model_name = 'uer/roberta-base-finetuned-jd-binary-chinese'
nlp = pipeline('sentiment-analysis', model=model_name)


def get_negative_sentiment_score(text):
    result = nlp(text)
    return result[0]['score'] if result[0]['label'] == 'negative (stars 1, 2 and 3)' else 1 - \
                                                                                          result[0][
                                                                                              'score']


def find_keywords(text, keywords_set):
    return [keyword for keyword in keywords_set if keyword in text]


def convert_to_pinyin(city_list):
    translated_cities = []
    for city in city_list:
        city_pinyin = pinyin(city, style=Style.NORMAL, heteronym=False)
        city_pinyin = [''.join(word.capitalize() for word in words) for words in city_pinyin]
        translated_cities.append(''.join(city_pinyin))
    return translated_cities


regions = set(open('regions.txt', 'r', encoding='utf-8').read().splitlines())
output_dir = 'output'
kws_dir = 'KWS'
results = []

for date_folder in os.listdir(output_dir):
    date_path = os.path.join(output_dir, date_folder)
    if os.path.isdir(date_path):
        kws_csv = os.path.join(kws_dir, f"{date_folder}.csv")
        kws_data = {}
        if os.path.exists(kws_csv):
            with open(kws_csv, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for index, row in enumerate(reader):
                    kws_data[row[0]] = index + 1

        for keyword_csv in glob(os.path.join(date_path, '*.csv')):
            keyword = os.path.splitext(os.path.basename(keyword_csv))[0]
            negative_sentiment = get_negative_sentiment_score(keyword)
            rank = kws_data.get(keyword, 'NA')

            # Check for regional info
            found_regions = find_keywords(keyword, regions)
            has_regional_info = bool(found_regions)
            found_regions_pinyin = convert_to_pinyin(found_regions)

            results.append([date_folder, keyword, rank, negative_sentiment, has_regional_info,
                            ','.join(found_regions_pinyin)])

with open('summary.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(
        ['date', 'keyword', 'rank', 'negative sentiment score', 'regional info', 'regions'])
    for row in results:
        writer.writerow(row)
