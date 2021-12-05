# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from platform import processor
import scrapy
from itemloaders.processors import TakeFirst, MapCompose

class LeroyparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(lambda x: float(x.replace(' ', ''))))
    url = scrapy.Field(output_processor=TakeFirst())
    images = scrapy.Field()
