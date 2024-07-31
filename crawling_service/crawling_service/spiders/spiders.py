import scrapy
from abc import ABC, abstractmethod
import logging
from scrapy.spiders import SitemapSpider
import re
from ..loaders import TestLoader, HouseLoader
from ..items import House
from ..exceptions import FeatureTranslationError
import sys, traceback


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        "features": {
            "Tipologia": "type",
            "Piano": "floor",
            "Piani edificio": "number_of_floors",
            "Superficie": "living_space_mq",
            "Locali": "rooms",
            "Camere da letto": "bedrooms",
            "Cucina": "kitchen",
            "Bagni": "bathrooms",
            "Arredato": "furnished",
            "Balcone": "balcony",
            "Terrazzo": "terrace",
            "Box, posti auto": "garage_parking_space",
            "Riscaldamento": "heating",
            "Climatizzazione": "air_conditioning",
            "Ascensore": "elevator",
        },
    }

    def __init__(self, where, publication_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info(
            f"Creating ImmobiliareSitemapSpider with where: {where} and publication_type: {publication_type}"
        )
        self.where = where.lower().replace(" ", "-").strip("-")
        self.publication_type = publication_type.lower().replace(" ", "-").strip("-")

    def parse(self, response):
        try:
            links = response.xpath(
                "//sitemap:loc/text()", namespaces=self.namespaces
            ).extract()
            for link in links:
                if self.is_target_link(link):
                    yield scrapy.Request(url=link, callback=self.parse_item)
        except Exception as e:
            logger.error(f"Error parsing sitemap: {e}", exc_info=True)

    def parse_item(self, response):
        try:
            for house_card in self.xpath_match_house_card(response):
                loader = HouseLoader()
                immobiliare_house_id = self.get_id_from_card(house_card)
                loader.add_value("immobiliare_id", immobiliare_house_id)
                link_to_house = self.get_link_from_card(house_card)
                yield scrapy.Request(
                    url=link_to_house,
                    callback=self.parse_house,
                    meta={"loader": loader},
                )
        except Exception as e:
            logger.error(f"Error parsing item: {e}", exc_info=True)

    def parse_house(self, response):
        try:
            loader = response.meta["loader"]
            title = response.xpath(
                "//h1[@class='re-title__title']/text()"
            ).extract_first()
            loader.add_value("title", title)
            characteristics = response.xpath(
                "//dl[contains(@class, 're-featuresGrid__list')]"
            )
            features = self.scrape_characteristics(characteristics)
            for translation, value in features:
                if translation:
                    loader.add_value(translation, value)
            description = response.xpath(
                "//div[@data-tracking-key='description']/text()"
            ).extract_first()
            loader.add_value("description", description)
            yield loader.load_item()
        except Exception as e:
            logger.error(f"Error parsing house: {e}", exc_info=True)

    def scrape_characteristics(self, characteristics):
        try:
            features_titles = characteristics.xpath(
                "div[@class='re-featuresItem']//dt[@class='re-featuresItem__title']/text()"
            ).getall()
            features_values = characteristics.xpath(
                "div[@class='re-featuresItem']//dd[@class='re-featuresItem__description']/text()"
            ).getall()
            features = []
            for feature_name, feature_value in zip(features_titles, features_values):
                feature_name = feature_name.strip()
                feature_value = feature_value.strip()
                features.append(
                    (self.translate(feature_name, raise_error=False), feature_value)
                )
            return features
        except Exception as e:
            logger.error(f"Error scraping characteristics: {e}", exc_info=True)

    def is_target_link(self, link):
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

    def translate(self, feature_name, raise_error=True):
        try:
            if raise_error:
                return self.TRANSLATIONS["features"][feature_name]
            else:
                return self.TRANSLATIONS["features"].get(feature_name, None)
        except KeyError as e:
            err_ctx = f"Error from spider {self.__class__.__name__} when translating feature {feature_name}. Check the TRANSLATIONS dictionary of the spider."
            logger.error(f"{err_ctx}: {e}", exc_info=True)
            if raise_error:
                raise FeatureTranslationError(feature_name, context=err_ctx, message=str(e))


class IdealistaSpider(MyBaseSpider):
    name = "idealista"
    allowed_domains = ["idealista.it"]

    def __init__(self, where, publication_type, *args, **kwargs):
        super(IdealistaSpider, self).__init__(where, publication_type, *args, **kwargs)
        logger.info(
            f"Creating IdealistaSpider with where: {where} and publication_type: {publication_type}"
        )

    def create_url(self, where, publication_type):
        return MyBaseSpider.url_from_template(
            MyBaseSpider.TEMPLATE_URLS["idealista"], where, publication_type
        )

    def start_requests(self):
        logger.debug(f"Starting request with URL: {self.entry_point}")
        yield scrapy.Request(url=self.entry_point, callback=self.parse)

    def parse(self, response):
        try:
            links = response.xpath(
                "//div[@class='item-info-container']/a/@href"
            ).extract()
            for link in links:
                test_loader = TestLoader(response=response)
                test_loader.add_value("link", link)
                yield test_loader.load_item()
        except Exception as e:
            logger.error(f"Error parsing Idealista listings: {e}", exc_info=True)
