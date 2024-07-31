# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlingServiceItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class House(scrapy.Item):
    # Define database id, id with autoincrement
    id = scrapy.Field()
    global_id = scrapy.Field() # Polyseme ID
    title = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    district = scrapy.Field()
    description = scrapy.Field()
    type = scrapy.Field()
    floor = scrapy.Field()
    rooms = scrapy.Field()
    bedrooms = scrapy.Field()
    kitchen = scrapy.Field()
    number_of_floors = scrapy.Field()
    furnished = scrapy.Field()
    balcony = scrapy.Field()
    terrace = scrapy.Field()
    heating = scrapy.Field()
    url = scrapy.Field()
    living_space_mq = scrapy.Field()
    rooms = scrapy.Field()
    bathrooms = scrapy.Field()
    construction_year = scrapy.Field()
    elevator = scrapy.Field()
    garage_parking_space = scrapy.Field()
    energy_class = scrapy.Field()
    air_conditioning = scrapy.Field()
    price = scrapy.Field()
    condo_fees = scrapy.Field()
    agency = scrapy.Field()
    agency_url = scrapy.Field()
    immobiliare_id = scrapy.Field() # Codice annuncio
    last_updated = scrapy.Field()



class TestItem(scrapy.Item):
    link = scrapy.Field()


