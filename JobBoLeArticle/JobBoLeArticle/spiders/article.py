# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from JobBoLeArticle.utils.common import get_md5
import re
import datetime
from scrapy.loader import ItemLoader

from JobBoLeArticle.items import JobbolearticleItem, ArticleItemLoader


class ArticleSpider(scrapy.Spider):
    name = 'article'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):

        # 获取文章url和图片url
        nodes = response.css("#archive .post-thumb")
        for node in nodes:
            article_url = node.css('a::attr(href)').extract()[0]
            image_url = node.css('a img::attr(src)').extract()[0]
            # print(article_url, image_url)
            yield Request(article_url, meta={'image_url': image_url}, callback=self.parse_detail)

        # 获取下一页url
        # next_page_url = response.css(".navigation a.next::attr(href)").extract_first("")
        # if next_page_url:
        #     print(next_page_url)
        #     yield Request(next_page_url, callback=self.parse)

    def parse_detail(self, response):

        # item = JobbolearticleItem()
        #
        # # 文章标题
        # item['title'] = response.css(".entry-header h1::text").extract_first("")
        #
        # # 文章url
        # item['url'] = response.url
        #
        # item['image_url'] = [response.meta.get('image_url', '')]
        #
        # # url进行md5加密
        # item['url_object_id'] = get_md5(response.url)
        #
        # # 文章创建时间
        # create_date = response.css(".entry-meta p::text").extract_first().strip()[:-2]
        # try:
        #     create_date = datetime.datetime.strptime(create_date, '%Y/%m/%d').date()
        #
        # except Exception as e:
        #     create_date = datetime.datetime.now().date()
        #
        # item['create_date'] = create_date
        #
        # # 文章标签
        # tags_list = response.css(".entry-meta a::text").extract()
        # tags_list = [tag for tag in tags_list if not tag.strip().endswith("评论")]
        # item['tags'] = ",".join(tags_list)
        #
        # # 点赞数
        # item['vote_nums'] = response.css("vote_nums").extract_first("")
        #
        # # 收藏数
        # fav_nums = response.css(".post-adds .bookmark-btn::text").extract_first("")
        # item['fav_nums'] = self.match_re(fav_nums)
        #
        # # 评论数
        # comments = response.css(".post-adds a[href='#article-comment'] span::text").extract_first("")
        # item['comment_nums'] = self.match_re(comments)
        #
        # # 文章内容
        # item['content'] = response.css(".entry").extract_first("")

        # 通过itemloader加载item  item_loader.add_xpath()  item_loader.add_value()
        item_loader = ArticleItemLoader(item=JobbolearticleItem(), response=response)
        item_loader.add_css('title', '.entry-header h1::text')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_css('create_date', '.entry-meta p::text')
        item_loader.add_value('image_url', [response.meta.get('image_url', '')])
        item_loader.add_css('vote_nums', '.vote-post-up h10::text')
        item_loader.add_css('fav_nums', '.post-adds .bookmark-btn::text')
        item_loader.add_css('comment_nums', ".post-adds a[href='#article-comment'] span::text")
        item_loader.add_css('tags', '.entry-meta a::text')
        item_loader.add_css('content', '.entry')

        article_item = item_loader.load_item()



        # yield item
        yield article_item

    def match_re(self, string):
        match_re = re.search('.*?(\d+).*', string)
        if match_re:
            return int(match_re.group(1))
        else:
            return 0