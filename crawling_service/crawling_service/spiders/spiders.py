import scrapy
from abc import ABC, abstractmethod
import logging
from scrapy.spiders import SitemapSpider
import re
from ..loaders import HouseLoader
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


class ImmobiliareSpider(scrapy.Spider):
    name = "immobiliare"

    TEMPLATE_URL = "https://www.immobiliare.it/{publication_type}/{where}/"

    start_urls = ["https://www.immobiliare.it/sitemaps/residenziale.xml"]

    sitemap_namespaces = {
        "sitemap": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "xhtml": "http://www.w3.org/1999/xhtml",
    }

    ENDPOINT_TRANSLATIONS = (
        {  # Translations for the endpoint to immobiliare.it semantics
            "onsale": "vendita-case",
        }
    )

    FEATURE_TRANSLATIONS = {
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
        "prezzo": "price",
        "spese condominio": "condo_fees",
        "Stato": "state",
        "Certificazione energetic": "energy_certification",
    }

    def __init__(self, where, publication_type, version="v1", *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not version in ["v0", "v1"]:
            raise ValueError("Version must be either 'v0' or 'v1'")
        self.version = version
        self.where = where.lower().replace(" ", "-").strip("-")
        self.publication_type = self.ENDPOINT_TRANSLATIONS[publication_type] 
        # Example of publication_type: "onsale"

    def parse(self, response):
        try:
            if self.version == "v0":
                links = response.xpath(
                    "//sitemap:loc/text()", namespaces=self.sitemap_namespaces
                ).extract()
                for link in links:
                    if self.is_target_link(link):
                        yield scrapy.Request(url=link, callback=self.parse_item)
            elif self.version == "v1":
                link = self.TEMPLATE_URL.format(
                    where=self.where,
                    publication_type=self.publication_type,
                )
                logger.debug(f"Link: {link}")
                yield scrapy.Request(url=link, callback=self.parse_item)
        except Exception as e:
            logger.error(f"Error parsing sitemap: {e}", exc_info=True)

    def parse_item(self, response):
        try:
            logger.debug(f"Processing response from {response.url}")
            for house_card in self.xpath_match_house_card(response):
                loader = HouseLoader()
                immobiliare_house_id = self.get_id_from_card(house_card)
                loader.add_value("immobiliare_id", immobiliare_house_id)
                link_to_house = self.get_link_from_card(house_card)
                logger.debug(f"Link to house: {link_to_house}")
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
            characteristics_section = response.xpath(
                "//dl[contains(@class, 're-featuresGrid__list')]"
            )
            chars = self.scrape_characteristics(characteristics_section)
            self.load_multiple(loader, chars)
            description = response.xpath(
                "//div[@data-tracking-key='description']/text()"
            )
            costs_section = response.xpath("//div[@data-tracking-key='costs']")
            cost_info = self.scrape_costs(costs_section)
            self.load_multiple(loader, cost_info)
            energy_consumptions_section = response.xpath(
                "//div[@data-tracking-key='energy-consumptions']"
            )
            energy_consumptions_info = self.scrape_energy_consumptions(
                energy_consumptions_section
            )
            agency_section = response.xpath("//div[@data-cy='agency-data']")
            agency_info = self.scrape_agency_info(agency_section)
            loader.add_value("agency", agency_info["agency_value"])
            self.load_multiple(loader, energy_consumptions_info)
            loader.add_value("description", description)
            yield loader.load_item()
        except Exception as e:
            logger.error(f"Error parsing house: {e}", exc_info=True)

    def scrape_characteristics(self, characteristics):
        try:
            characteristics_props = self.scrape_child_properties(
                characteristics,
                title_xpath="div[@class='re-featuresItem']//dt[@class='re-featuresItem__title']/text()",
                value_xpath="div[@class='re-featuresItem']//dd[@class='re-featuresItem__description']/text()",
            )
            return characteristics_props
        except Exception as e:
            logger.error(f"Error scraping characteristics: {e}", exc_info=True)

    def scrape_costs(self, costs):
        try:
            cost_props = self.scrape_child_properties(
                costs,
                title_xpath="dl[@class='re-realEstateFeatures__list']//dt/text()",
                value_xpath="dl[@class='re-realEstateFeatures__list']//dd/text()",
            )
            return cost_props
        except Exception as e:
            logger.error(f"Error scraping costs: {e}", exc_info=True)

    def scrape_energy_consumptions(self, energy_consumptions):
        try:
            energy_consumptions_props = self.scrape_child_properties(
                energy_consumptions,
                title_xpath="ul[@class='re-energy__featuresWrapper']//p/text()",
                value_xpath="ul[@class='re-energy__featuresWrapper']//span/text()",
            )
            return energy_consumptions_props
        except Exception as e:
            logger.error(f"Error scraping energy consumptions: {e}", exc_info=True)

    def scrape_agency_info(self, agency_section):
        try:
            agency_value = agency_section.xpath(".//p/text()").extract()
            if not agency_value:
                agency_value = agency_section.xpath(".//a/text()").extract()
            logger.debug(f"Agency section: {agency_section}")
            return {"agency_value": agency_value}
        except Exception as e:
            logger.error(f"Error scraping agency info: {e}", exc_info=True)

    def scrape_child_properties(self, parent_selector, title_xpath, value_xpath):
        energy_consumptions_features = parent_selector.xpath(f"{title_xpath}").getall()
        features_values = parent_selector.xpath(f"{value_xpath}").getall()
        features = []
        for feature_name, feature_value in zip(
            energy_consumptions_features, features_values
        ):
            feature_name = feature_name.strip()
            feature_value = feature_value.strip()
            features.append(
                (self.translate_feature(feature_name, raise_error=False), feature_value)
            )
        return features

    def is_target_link(self, link):
        pub_type = self.TRANSLATIONS.get(self.publication_type)
        where = self.where
        pattern = re.compile(f".*{pub_type}/.*{where}")
        logger.debug(f"Pub type: {pub_type}, where: {where}, link: {link}, pattern: {pattern}, match: {pattern.match(link)}")
        return pattern.match(link)

    def xpath_match_house_card(self, response):
        cards = response.xpath("//div[@class='in-listingCard']")
        return cards

    def get_link_from_card(self, card):
        house_id = self.get_id_from_card(card)
        return f"https://www.immobiliare.it/annunci/{house_id}/"

    def get_id_from_card(self, card):
        return card.xpath(".//@id").extract_first()

    def translate_feature(self, feature_name, raise_error=True):
        try:
            if raise_error:
                return self.FEATURE_TRANSLATIONS[feature_name]
            else:
                return self.FEATURE_TRANSLATIONS.get(feature_name, None)
        except KeyError as e:
            err_ctx = f"Error from spider {self.__class__.__name__} when translating feature {feature_name}. Check the TRANSLATIONS dictionary of the spider."
            logger.error(f"{err_ctx}: {e}", exc_info=True)
            if raise_error:
                raise FeatureTranslationError(
                    feature_name, context=err_ctx, message=str(e)
                )

    def load_multiple(self, loader, props):
        """Load multiple properties into the loader"""
        try:
            for prop_name, prop_value in props:
                if prop_name:
                    loader.add_value(prop_name, prop_value)
        except Exception as e:
            logger.error(f"Error loading multiple properties: {e}", exc_info=True)


class IdealistaSpider(MyBaseSpider):
    name = "idealista"
    allowed_domains = ["idealista.it"]

    def __init__(self, where, publication_type, *args, **kwargs):
        super(IdealistaSpider, self).__init__(where, publication_type, *args, **kwargs)

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
