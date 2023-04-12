# -*- coding: utf-8 -*-
import datetime
import json
import os.path
import time


class JsonWriterPipeline(object):
    """
    Write pipline to json file
    """

    def __init__(self):
        self.file = None
        if not os.path.exists('./output'):
            os.mkdir('./output')

    def process_item(self, item, spider):
        """
        Processing item
        """
        if not self.file:
            now = datetime.datetime.now()
            file_name = spider.keyword + '.jsonl'
            self.file = open(f'./output/{file_name}', 'wt', encoding='utf-8')
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        self.file.flush()
        return item
