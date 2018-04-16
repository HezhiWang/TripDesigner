# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from trip.models import Attraction, Hotel
import json

class ScrapyAppPipeline(object):
    def process_item(self, item, spider):
        return item

class ScrapyAttractionPipeline(object):
    def __init__(self, unique_id, *args, **kwargs):
        self.unique_id = unique_id
        # print("id2", self.unique_id)
        self.items = []

    @classmethod
    def from_crawler(cls, crawler):
    	# print("id3", crawler.settings.get('unique_id'))
        return cls(
            unique_id=crawler.settings.get('unique_id'), # this will be passed from django view
        )

    def close_spider(self, spider):
        # And here we are saving our crawled data with django models.
        item = Attraction()
        item.unique_id = self.unique_id
        print("id4", item.unique_id)
        item.data = json.dumps(self.items)
        # print(item.data)
        item.save()

    def process_item(self, item, spider):
        self.items.append(item)
        #print(item)
        return item
   