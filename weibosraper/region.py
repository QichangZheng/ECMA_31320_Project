import requests
import re
import gc

url = "https://raw.githubusercontent.com/modood/Administrative-divisions-of-China/master/dist/pcas-code.json"
response = requests.get(url)
data = response.json()

def extract_regions(region_data):
    for item in region_data:
        yield item["name"]
        if "children" in item:
            yield from extract_regions(item["children"])

all_regions = extract_regions(data)
del data
gc.collect()

with open('all_regions.txt', 'w', encoding='utf-8') as f:
    for region in all_regions:
        simplified_region = re.sub(r'(省|市|自治区)', '', region)
        f.write(simplified_region + '\n')
