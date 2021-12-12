# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.insta
        self.mongo_base['followers'].create_index('follower_id', unique=True)
        self.mongo_base['following'].create_index('following_id', unique=True)

    def process_item(self, item, spider):
        collection_followers = self.mongo_base['followers']
        collection_following = self.mongo_base['following']
        try:
            collection.insert_one(item)
        except DuplicateKeyError:
            pass

        return item


