# -*- coding: utf-8 -*-
import mpi4py
rank = mpi4py.MPI.COMM_WORLD.Get_rank()
# rank = MPI.COMM_WORLD.Get_rank()
rank = 0
BOT_NAME = 'spider'

SPIDER_MODULES = ['spider']
NEWSPIDER_MODULE = 'spider'

ROBOTSTXT_OBEY = False



with open('./cookies.txt', 'rt', encoding='utf-8') as f:
    # cookie = f.read().strip()
    cookie = f.readlines()[rank].strip()
with open('./agents.txt', 'rt', encoding='utf-8') as f:
    user_agent = f.readlines()[rank].strip()
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': user_agent,
    'Cookie': cookie
}

CONCURRENT_REQUESTS = 10

DOWNLOAD_DELAY = 1

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    'middlewares.IPProxyMiddleware': 100,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 101,
}

ITEM_PIPELINES = {
    'pipelines.JsonWriterPipeline': 300,
}
