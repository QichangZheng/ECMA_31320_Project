# encoding: utf-8


class IPProxyMiddleware(object):
    """
    Proxy IP Middleware
    """

    @staticmethod
    def fetch_proxy():
        """
        Get a proxy IP
        """
        return None

    def process_request(self, request, spider):
        """
        Add the proxy IP to the request
        """
        proxy_data = self.fetch_proxy()
        if proxy_data:
            current_proxy = f'http://{proxy_data}'
            spider.logger.debug(f"current proxy:{current_proxy}")
            request.meta['proxy'] = current_proxy
