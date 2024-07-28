import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst
from unsplash.items import UnsplashItem
import logging
import json
import csv
import os
import requests


class UnsplashImgsSpider(CrawlSpider):
    name = "unsplash_imgs"
    allowed_domains = ["unsplash.com"]
    start_urls = ["https://unsplash.com"]
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    rules = (
        Rule(LinkExtractor(restrict_xpaths='//a[contains(@href, "/t/")]'), follow=True),
        Rule(LinkExtractor(restrict_xpaths='//a[contains(@href, "/photos/")]'), callback="parse_item", follow=True)
    )

    def parse_item(self, response):
        logging.info(f"Parsing image page: {response.url}")
        
        loader = ItemLoader(item=UnsplashItem(), response=response)
        loader.default_input_processor = MapCompose(str.strip)
        loader.default_output_processor = TakeFirst()

        # Извлечение категорий
        categories = response.xpath('//a[contains(@class, "IQzj8")]/text()').getall()
        if categories:
            logging.info(f"Found categories: {categories}")
            loader.add_value('categories', categories)

        # Извлечение названия изображения
        name = response.url.split('/')[-1]
        name = name.split('-')
        name = name[:-1]
        name = ' '.join(name)
        if name:
            logging.info(f"Image name: {name}")
            loader.add_value('name', name)
            loader.add_value('local_path', f'images/{name}.jpg')

        # Извлечение URL изображения
        image_url = response.xpath('//img[contains(@class, "_2UpQX")]/@src').get()
        if image_url:
            logging.info(f"Image URL: {image_url}")
            loader.add_value('image_urls', image_url)

        item = loader.load_item()

        # Сохранение данных в JSON и CSV
        self.save_to_json(item)
        self.save_to_csv(item)

        # Загрузка изображения
        self.download_image(item)

        return item

    def save_to_json(self, item):
        with open('images.json', 'a') as f:
            json.dump(dict(item), f, ensure_ascii=False, indent=4)

    def save_to_csv(self, item):
        file_exists = os.path.isfile('images.csv')
        with open('images.csv', 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=item.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(item)

    def download_image(self, item):
        image_url = item.get('image_urls')
        if image_url:
            image_name = item.get('local_path')
            if not os.path.exists('images'):
                os.makedirs('images')
            with open(image_name, 'wb') as f:
                f.write(requests.get(image_url).content)
