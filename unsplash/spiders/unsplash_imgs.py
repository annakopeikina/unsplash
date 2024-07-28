import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst
from unsplash.items import UnsplashItem
import logging

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
        categories = response.xpath('//a[@class="IQzj8 eziW_"]/text()').getall()
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
        url = response.xpath('//div[@class="MorZF"]/img/@src').get()
        if url:
            logging.info(f"Image URL: {url}")
            loader.add_value('image_urls', [url])

        # Извлечение заголовка и описания
        title = response.xpath('//h1/text()').get()
        description = response.xpath('//meta[@name="description"]/@content').get()
        if title:
            logging.info(f"Image title: {title}")
            loader.add_value('title', title)
        if description:
            logging.info(f"Image description: {description}")
            loader.add_value('description', description)

        yield loader.load_item()
