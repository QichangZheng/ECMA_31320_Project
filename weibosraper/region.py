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

keywords = ["省", "市", "自治区"]
filtered_locations = [location for location in all_regions if any(location.endswith(keyword) for keyword in keywords)]
regions = [re.sub(r'(省|市|自治区)', '', region) for region in filtered_locations]
with open('../regions.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(regions))

# with open('all_regions.txt', 'w', encoding='utf-8') as f:
#     for region in all_regions:
#         f.write(region + '\n')
        # simplified_region = re.sub(r'(省|市|自治区|街道|镇|地区|乡|开发区|自治县|团|核心区)', '', region)
        # f.write(simplified_region + '\n')
