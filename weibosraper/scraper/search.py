#!/usr/bin/env python
# encoding: utf-8

import json
import re
import sys
from scrapy import Spider, Request
from scraper.common import parse_tweet_info, parse_long_tweet
from process_keywords import extract_high_score_keywords
import os
from datetime import datetime,timedelta
import time
from mpi4py import MPI

pre = 0
if len(sys.argv) > 1:
    start_date = sys.argv[1]
    passed = int(sys.argv[2])
    try:
        pre = int(sys.argv[3])
    except:
        pass
    # pre = int(sys.argv[1])

curr = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=passed)
file = os.path.join('KWS', curr.strftime('%Y-%m-%d') + '.csv')

# file = 'KWS/2022-04-26.csv'

dt = file.split('/')[-1].split('.')[0] + '-0'
keywords = extract_high_score_keywords(file, 10)

# rank = 0

class SearchSpider(Spider):
    """
    Keyword search scraper
    """
    name = "search_spider"
    base_url = "https://s.weibo.com/"

    def start_requests(self):
        """
        start request for search
        Input: The class and its attributes
        Output: Request
        """
        with open("config.json",'r',encoding="utf-8") as f:
            config = json.load(f)

        rank = MPI.COMM_WORLD.Get_rank() + 2 * pre
        # with open('KWS/2022-03-28.json', 'r') as f:
        #     keywords = f.read().splitlines()

        self.keyword = keywords[rank]
        # self.start_time = datetime.strptime(config["start_time"],"%Y-%m-%d-%H")
        # self.end_time = datetime.strptime(config["end_time"],"%Y-%m-%d-%H")
        self.start_time = datetime.strptime(dt,"%Y-%m-%d-%H")
        self.end_time = self.start_time + timedelta(days=1)
        self.hour_interval = config["hour_interval"]
        search_with_time_scope = config["search_with_time_scope"]  
        sort_by_hot = config["sort_by_hot"]  
        self.cur_time = self.end_time

        while True:
            end_time = datetime.strftime(self.cur_time,"%Y-%m-%d-%H")

            start_time = datetime.strftime(self.cur_time + timedelta(hours = -self.hour_interval),"%Y-%m-%d-%H")
            if search_with_time_scope:
                url = f"https://s.weibo.com/weibo?q={self.keyword}&timescope=custom%3A{start_time}%3A{end_time}&page=1"
            else:
                url = f"https://s.weibo.com/weibo?q={self.keyword}&page=1"
            if sort_by_hot:
                url += "&xsort=hot"
            yield Request(url, callback=self.parse, meta={'keyword': self.keyword})
            self.cur_time = datetime.strptime(start_time,"%Y-%m-%d-%H")
            time.sleep(1)
            if datetime.strptime(end_time,"%Y-%m-%d-%H") <= self.start_time:
                break
            
    def parse(self, response, **kwargs):
        """
        parse search result
        Input: response,self, **kwargs
        Output: Request
        """
        html = response.text
        tweet_ids = re.findall(r'\d+/(.*?)\?refer_flag=1001030103_" ', html)
        for tweet_id in tweet_ids:
            url = f"https://weibo.com/ajax/statuses/show?id={tweet_id}"
            yield Request(url, callback=self.parse_tweet, meta=response.meta)
        next_page = re.search('<a href="(.*?)" class="next">下一页</a>', html)
        if next_page:
            url = "https://s.weibo.com" + next_page.group(1)
            yield Request(url, callback=self.parse, meta=response.meta)

    @staticmethod
    def parse_tweet(response):
        """
        parse tweet(here is weibo posy)
        Input: response
        Output: item
        """
        data = json.loads(response.text)
        # save the response to file
        # with open("response.txt",'w',encoding="utf-8") as f:
        #     f.write(response.text)
        item = parse_tweet_info(data)
        if item['isLongText']:
            url = "https://weibo.com/ajax/statuses/longtext?id=" + item['mblogid']
            yield Request(url, callback=parse_long_tweet, meta={'item': item})
        else:
            yield item
