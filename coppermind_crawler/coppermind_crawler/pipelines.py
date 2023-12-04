# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import csv

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class CoppermindCrawlerPipeline:

    def __init__(self):
        self.file = None
        self.writer = None

    def open_spider(self, spider):
        self.file = open('../data/articles.csv', 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['title', 'url', 'article'])

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        self.writer.writerow([item['title'], item['url'], item['article']])
        return item
