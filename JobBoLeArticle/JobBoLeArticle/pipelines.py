# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
import codecs
import json
from scrapy.exporters import JsonItemExporter
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi


class JobbolearticlePipeline(object):

    def process_item(self, item, spider):

        return item


class ArticleImagePipeline(ImagesPipeline):

    def item_completed(self, results, item, info):
        for ok, value in results:
            image_file_path = value['path']
        item['image_path'] = image_file_path

        return item


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        data = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(data)
        return item

    def spider_closed(self, spider):
        self.file.close()


class JsonExporterPipeline(object):
    def __init__(self):
        self.file = open('articleexporter.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class MysqlClientPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('localhost', 'root', 'root', 'scrapy_spider', charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):

        # 数据同步插入数据库
        insert_sql = """
            insert into jobbole_article(title, url, url_object_id, image_url, image_path, create_date, 
            vote_nums, fav_nums, comment_nums, tags, content)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
        """
        self.cursor.execute(insert_sql, (item['title'], item['url'], item['url_object_id'], item['image_url'],
                                         item['image_path'], item['create_date'], item['vote_nums'], item['fav_nums'],
                                         item['comment_nums'], item['tags'], item['content']))
        self.conn.commit()

        return item


class MysqlTwistedPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings['MYSQL_HOSE'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,

        )

        # 创建连接池
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)

        # 处理异常
        query.addErrback(self.handle_error)

    def do_insert(self, cursor, item):

        # 数据插入数据库
        insert_sql = """
            insert into jobbole_article(title, url, url_object_id, image_url, image_path, create_date, vote_nums,
            fav_nums, comment_nums, tags, content)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (item['title'], item['url'], item['url_object_id'], item['image_url'],
                                    item['image_path'], item['create_date'], item['vote_nums'], item['fav_nums'],
                                    item['comment_nums'], item['tags'], item['content']))

    def handle_error(self, failure):
        # 处理异步处理的异常
        print(failure)
