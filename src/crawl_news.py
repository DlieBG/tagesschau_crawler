from db import TagesschauDB
from datetime import datetime
from time import sleep
import requests
import os

class CrawlNews:

    db = TagesschauDB()

    def __init__(self):
        while True:
            self.crawl_articles()
            sleep(5 * 60)


    def crawl_articles(self):
        current_articles = requests.get('https://www.tagesschau.de/api2').json()['news']

        for index, article in enumerate(current_articles):
            if article.get('sophoraId', None):
                if not self.db.get_article(article['sophoraId']):
                    self.db.insert_article(article, index)
