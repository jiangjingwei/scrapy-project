# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import re
import scrapy
import datetime
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader


def add_toefl(value):
    return value + '-toefl'


def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, '%Y/%m/%d').date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date


def return_value(value):
    return value


def get_nums(value):
    match_re = re.search('.*?(\d+).*', value)
    if match_re:
        return int(match_re.group(1))
    else:
        return 0


def remove_comment_tags(value):
    if "评论" in value:
        return ""
    else:
        return value


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


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
    image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    image_path = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    vote_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(',')
    )
    content = scrapy.Field()

