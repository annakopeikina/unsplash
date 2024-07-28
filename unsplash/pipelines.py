# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter


# class UnsplashPipeline:
#     def process_item(self, item, spider):
#         return item

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import os

class CustomImagesPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None, *, item=None):
        image_guid = request.url.split('/')[-1]
        return f'full/{image_guid}'

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['local_path'] = image_paths[0]
        return item
import csv

class CsvPipeline:

    def open_spider(self, spider):
        self.file = open('images.csv', 'w', newline='', encoding='utf-8')
        self.exporter = csv.writer(self.file)
        self.exporter.writerow(['title', 'category', 'local_path'])

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.writerow([item.get('title'), item.get('category'), item.get('local_path')])
        return item
