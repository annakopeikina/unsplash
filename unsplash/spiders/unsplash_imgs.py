import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst, Compose
from unsplash.items import UnsplashItem

class UnsplashImgsSpider(CrawlSpider):
    name = "unsplash_imgs"
    allowed_domains = ["unsplash.com"]
    start_urls = ["https://unsplash.com"]

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//a[contains(@href, "/t/")]'), follow=True),
        Rule(LinkExtractor(restrict_xpaths='//a[contains(@href, "/photos/")]'), callback="parse_item", follow=True)
    )

    def parse_item(self, response):
        loader = ItemLoader(item=UnsplashItem(), response=response)
        loader.default_input_processor = MapCompose(str.strip)
        loader.default_output_processor = TakeFirst()

        categories = response.xpath('//a[@class="IQzj8 eziW_"]/text()').getall()
        if categories:
            loader.add_value('categories', categories)

        name = response.url.split('/')[-1]
        name = name.split('-')
        name = name[:-1]
        name = ' '.join(name)
        if name:
            loader.add_value('name', name)
            loader.add_value('local_path', f'images/{name}.jpg')

        url = response.xpath('//div[@class="MorZF"]/img/@src').get()
        if url:
            loader.add_value('image_urls', [url])

        yield loader.load_item()
