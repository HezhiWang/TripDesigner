# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from trip.models import Attraction, Hotel
import json
import psycopg2
from scrapy.contrib.exporter import CsvItemExporter

HOSTNAME = 'localhost'
username = 'postgres' # the username when you create the database
password = '***' #change to your password
database = 'quotes'

class ScrapyAppPipeline(object):
    def process_item(self, item, spider):
        return item

class ScrapyAttractionPipeline(object):
    def __init__(self, unique_id, *args, **kwargs):
        self.unique_id = unique_id
        self.items = []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            unique_id=crawler.settings.get('unique_id'), # this will be passed from django view
        )

    def open_spider(self, spider):
        self.file = open(str(self.unique_id)+'.csv', 'w+b')
        self.exporter = CsvItemExporter(self.file)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        # And here we are saving our crawled data with django models.
        item = Attraction()
        item.unique_id = self.unique_id
        item.data = json.dumps(self.items)
        item.save()
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.items.append(item)
        self.exporter.export_item(item)
        return item
   