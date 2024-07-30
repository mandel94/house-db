# Import item loaders
from scrapy.loader import ItemLoader 
from itemloaders.processors import TakeFirst

# Import item classes

from crawling_service.items import House, TestItem


# Define the class HouseLoader


class HouseLoader(ItemLoader):
    default_item_class = House
    default_input_processor = TakeFirst()

class TestLoader(ItemLoader):
    default_item_class = TestItem
    default_input_processor = TakeFirst()


