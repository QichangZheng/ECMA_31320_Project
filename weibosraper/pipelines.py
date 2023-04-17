# -*- coding: utf-8 -*-
import datetime
import json
import os.path
import time
import sys

if len(sys.argv) > 1:
    start_date = sys.argv[1]
    passed = int(sys.argv[2])

curr = datetime.datetime.strptime(start_date, '%Y-%m-%d') + datetime.timedelta(days=passed)
filename = os.path.join('output', curr.strftime('%Y-%m-%d'))

# filename = './output/2022-04-26'

class JsonWriterPipeline(object):
    """
    Write pipline to json file
    """

    def __init__(self):
        self.file = None
        if not os.path.exists(filename):
            os.mkdir(filename)

    def process_item(self, item, spider):
        """
        Processing item
        """
        if not self.file:
            now = datetime.datetime.now()
            file_name = spider.keyword + '.jsonl'
            self.file = open(os.path.join(filename, file_name), 'wt', encoding='utf-8')
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        self.file.flush()
        return item
