#!/usr/bin/env python
# encoding: utf-8
import os
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper.search import SearchSpider

if __name__ == '__main__':
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'scrapy_settings'
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(SearchSpider)
    # the script will block here until the crawling is finished
    process.start()
