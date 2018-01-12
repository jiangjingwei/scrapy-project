# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose


def add_toefl(value):
    return value + '-toefl'


class JobbolearticleItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    title = scrapy.Field(
        # input_processor=MapCompose(add_jobbole)
        # 可以设置多个函数，从左向右执行
        input_processor=MapCompose(lambda x: x + '-jobbole', add_toefl)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    image_url = scrapy.Field()
    image_path = scrapy.Field()
    create_date = scrapy.Field()
    vote_nums = scrapy.Field()
    fav_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()

