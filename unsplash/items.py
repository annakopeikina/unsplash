# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Compose

def process_name(value):
    '''
    Функция ничего не делает, оставил для примера, чтобы не забыть.

    :param value:
    :return:
    '''
    return value

class ImgparserItem(scrapy.Item):
    name = scrapy.Field(input_processor=Compose(process_name), output_processor=TakeFirst())
    path = scrapy.Field()
    category = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    _id = scrapy.Field()

class UnsplashItem(scrapy.Item):
    categories = scrapy.Field()
    name = scrapy.Field()
    local_path = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()

