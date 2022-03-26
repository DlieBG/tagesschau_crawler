from pymongo import MongoClient
from datetime import datetime
from time import sleep
import requests
import os

class CrawlNews:

    db = MongoClient(os.getenv('MONGO_URI')).tagesschau

    def __init__(self):
        while True:
            self.crawl_news()
            sleep(15 * 60)


    def crawl_news(self):
        api_request = requests.get('https://www.tagesschau.de/api2')

        for index, article in enumerate(api_request.json()['news']):
            if article.get('sophoraId', None):
                if not self.news_in_db(article['sophoraId']):
                    self.insert_news(index, article)
                    print('Inserted new article: ', article['title'])


    def news_in_db(self, sophoraId: str) -> bool:
        article = self.db.news.find_one({ 'sophoraId': sophoraId }, sort=[ ('crawlTime', -1) ])
        
        return article is not None


    def insert_news(self, index: int, article: dict):
        article['crawlTimeInsert'] = datetime.now()
        article['crawlTime'] = datetime.now()
        article['crawlType'] = 'new'
        article['crawlIndex'] = index
        article['date'] = datetime.fromisoformat(article['date'])
        
        self.db.news.insert_one(article)
