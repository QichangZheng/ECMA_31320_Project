import requests

url = "https://raw.githubusercontent.com/modood/Administrative-divisions-of-China/master/dist/pcas-code.json"
response = requests.get(url)
data = response.json()

def extract_regions(region_data, result):
    for item in region_data:
        result.append(item["name"])
        if "children" in item:
            extract_regions(item["children"], result)

all_regions = []
extract_regions(data, all_regions)

for region in all_regions:
    if "市" in region:
        simplified_region = region.replace("市", "")
    elif "自治区" in region:
        simplified_region = region.replace("自治区", "")
    elif "省" in region:
        simplified_region = region.replace("省", "")
    else:
        simplified_region = region
    all_regions.append(simplified_region)

# save to file
with open('all_regions.txt', 'w', encoding='utf-8') as f:
    for region in all_regions:
        f.write(region + '\n')

# pattern = r'\b(?:' + '|'.join(all_regions) + r')\b'  # 将地区名称列表转换为正则表达式模式
# contains_region = bool(re.search(pattern, text))