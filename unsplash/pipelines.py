# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter


# class UnsplashPipeline:
#     def process_item(self, item, spider):
#         return item
import csv
import logging
import os
import scrapy
import signal
import sys
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import json

class CustomImagesPipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        image_guid = request.url.split('/')[-1]
        extension = image_guid.split('.')[-1]  # Получаем расширение файла
        logging.info(f"Saving image with guid: {image_guid}")
        return f'full/{image_guid}.{extension}'

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['local_path'] = image_paths[0]
        logging.info(f"Item completed with local path: {item['local_path']}")
        return item

class CsvPipeline:
    def open_spider(self, spider):
        self.file = open('images.csv', 'w', newline='', encoding='utf-8', buffering=1)
        self.exporter = csv.writer(self.file)
        self.exporter.writerow(['name', 'categories', 'local_path', 'title', 'description'])
        logging.info("CSV file opened and header written")

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def close_spider(self, spider):
        self.file.close()
        logging.info("CSV file closed")

    def process_item(self, item, spider):
        self.exporter.writerow([item.get('name'), item.get('categories'), item.get('local_path'), item.get('title'), item.get('description')])
        logging.info(f"Item written to CSV: {item}")
        return item

    def signal_handler(self, signum, frame):
        self.file.close()
        logging.info('Process interrupted and CSV file closed properly')
        sys.exit(0)

class JsonPipeline:
    def open_spider(self, spider):
        self.file = open('images.json', 'w', encoding='utf-8')
        self.file.write('[\n')
        logging.info("JSON file opened")

    def close_spider(self, spider):
        self.file.write('\n]')
        self.file.close()
        logging.info("JSON file closed")

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + ",\n"
        self.file.write(line)
        logging.info(f"Item written to JSON: {item}")
        return item
