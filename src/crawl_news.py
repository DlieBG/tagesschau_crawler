from datetime import datetime, timedelta
from db import TagesschauDB
from time import sleep
import requests

class CrawlNews:

    db = TagesschauDB()

    def __init__(self):
        while True:
            self.crawl_articles()
            sleep(5 * 60)


    def crawl_articles(self):
        articles = requests.get('https://www.tagesschau.de/api2').json()['news']

        for index, article in enumerate(articles):
            if article.get('sophoraId', None):
                existing_article = self.db.get_article(article['sophoraId'])
                
                if not existing_article:
                    self.db.insert_article(article, index)
                else:
                    if existing_article['article']['crawler']['crawlTime'] < (datetime.now() - timedelta(days=1)):
                        self.db.update_article(article, index, existing_article['article']['crawler']['insertTime'])
