from crawling_service.spiders.spiders import IdealistaSpider


class SpiderFactory:
    @staticmethod
    def create_spider(spider_name):
        if spider_name == "idealista":
            return IdealistaSpider
        else:
            raise ValueError(f"Spider {spider_name} not found")
        


