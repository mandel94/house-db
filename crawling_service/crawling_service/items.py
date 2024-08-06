# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class House(scrapy.Item):
    # Define database id, id with autoincrement
    id = scrapy.Field()
    global_id = scrapy.Field()  # Polyseme ID
    title = scrapy.Field()
    address_id = scrapy.Field()
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
    state = scrapy.Field()
    construction_year = scrapy.Field()
    elevator = scrapy.Field()
    garage_parking_space = scrapy.Field()
    energy_class = scrapy.Field()
    energy_certification = scrapy.Field()
    air_conditioning = scrapy.Field()
    price = scrapy.Field()
    condo_fees = scrapy.Field()
    agency = scrapy.Field()
    immobiliare_id = scrapy.Field()  # Codice annuncio
    created_at = scrapy.Field()
    last_updated = scrapy.Field() # Last updated




class Address(scrapy.Item):
    address_id = scrapy.Field()
    street = scrapy.Field()
    city = scrapy.Field()
    country = scrapy.Field()
    postal_code = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()

