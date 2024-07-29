import scrapy


def create_url(search_params):
    # Destructure parameters
    where = search_params["where"]
    # Extract Other parameters



class IdealistaSpider(scrapy.Spider):
    name = "idealista"
    allowed_domains = ["idealista.it"]

    def __init__(self, search_params, *args, **kwargs):
        super(IdealistaSpider, self).__init__(*args, **kwargs)
        self.entry_point = create_url(search_params)

    def start_requests(self):
        yield scrapy.Request(url=self.entry_point, callback=self.parse)

    def parse(self, response):
        pass

    