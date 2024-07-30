import scrapy
from abc import ABC, abstractmethod
import logging
from scrapy.spiders import SitemapSpider
import re

from ..loaders import TestLoader, HouseLoader


# Create Base Spider
class MyBaseSpider(scrapy.Spider, ABC):

    TEMPLATE_URLS = {
        "idealista": "https://www.idealista.it/{publication_type}/{where}/"
    }

    @staticmethod
    def url_from_template(template, where, publication_type):
        """Get the URL from the template"""
        return template.format(
            where=where.lower(), publication_type=publication_type.lower()
        )

    def __init__(self, where, publication_type, *args, **kwargs):
        super(MyBaseSpider, self).__init__(*args, **kwargs)
        self.entry_point = self.create_url(where, publication_type)

    @abstractmethod
    def create_url(self, where, publication_type):
        raise NotImplementedError("Method create_url not implemented")


class ImmobiliareSitemapSpider(scrapy.Spider):
    name = "immobiliare_sitemap"

    start_urls = ["https://www.immobiliare.it/sitemaps/residenziale.xml"]

    namespaces = {
        "sitemap": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "xhtml": "http://www.w3.org/1999/xhtml",
    }

    TRANSLATIONS = {
        "onsale": "vendita-case",
    }

    def __init__(self, where, publication_type, *args, **kwargs):
        logging.info(
            f"Creating ImmobiliareSitemapSpider with where: {where} and publication_type: {publication_type}"
        )
        self.where = where.lower().replace(" ", "-").strip("-")
        self.publication_type = publication_type.lower().replace(" ", "-").strip("-")

    def parse(self, response):
        # Get all links from sitemap
        links = response.xpath(
            "//sitemap:loc/text()", namespaces=self.namespaces
        ).extract()
        logging.debug(f"Links: {links}")
        for link in links:
            if self.is_target_link(link):
                yield scrapy.Request(url=link, callback=self.parse_item)

    def parse_item(self, response):
        # Get item card
        for house_card in self.xpath_match_house_card(response):
            house_id = self.get_id_from_card(house_card)
            logging.debug(f"House ID: {house_id}")
            link_to_house = self.get_link_from_card(house_card)
            logging.debug(f"Link to house: {link_to_house}")
            yield scrapy.Request(url=link_to_house, callback=self.parse_house)

    def parse_house(self, response):
        house_loader = HouseLoader(response=response)

    def is_target_link(self, link):
        """Check if the link is a target link"""
        pub_type = self.TRANSLATIONS.get(self.publication_type)
        where = self.where
        pattern = re.compile(f".*{pub_type}/.*{where}")
        return pattern.match(link)

    def xpath_match_house_card(self, response):
        cards = response.xpath("//div[@class='in-listingCard']")
        return cards

    def get_link_from_card(self, card):
        house_id = self.get_id_from_card(card)
        return f"https://www.immobiliare.it/annunci/{house_id}/"

    def get_id_from_card(self, card):
        return card.xpath(".//@id").extract_first()


class IdealistaSpider(MyBaseSpider):
    name = "idealista"
    allowed_domains = ["idealista.it"]

    def __init__(self, where, publication_type, *args, **kwargs):
        logging.info(
            f"Creating IdealistaSpider with where: {where} and publication_type: {publication_type}"
        )
        super(IdealistaSpider, self).__init__(
            where=where, publication_type=publication_type, *args, **kwargs
        )

    def create_url(self, where, publication_type):
        return MyBaseSpider.url_from_template(
            MyBaseSpider.TEMPLATE_URLS["idealista"], where, publication_type
        )

    def start_requests(self):
        logging.debug(f"Starting request with URL: {self.entry_point}")
        yield scrapy.Request(url=self.entry_point, callback=self.parse)

    def parse(self, response):
        links = response.xpath(
            "//div[@class='item-info-container']/a/@href"
        ).extract()  # Extract all the links
        for link in links:
            test_loader = TestLoader(response=response)
            test_loader.add_value("link", link)
            return test_loader.load_item()
            # yield scrapy.Request(url=link, callback=self.parse_item)
