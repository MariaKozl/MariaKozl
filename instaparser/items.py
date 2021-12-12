# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    user_id = scrapy.Field()
    username = scrapy.Field()
    friend_type = scrapy.Field()
    following_id = scrapy.Field()
    following_name = scrapy.Field()
    following_login = scrapy.Field()
    following_photo_link = scrapy.Field()
    _id = scrapy.Field()
