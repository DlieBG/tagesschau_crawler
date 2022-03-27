from datetime import datetime, timedelta
from typing import Tuple
from pymongo import MongoClient
from time import sleep
import requests
import os

from db import TagesschauDB

class UpdateNews:

    db = TagesschauDB()

    def __init__(self):
        while True:
            self.update_articles(datetime.now() - timedelta(days=1))
            sleep(5 * 60)


    def update_articles(self, timestamp: datetime):
        self.upstream_articles = requests.get('https://www.tagesschau.de/api2').json()['news']

        for article in self.db.get_articles_to_update(timestamp):
            try:
                index, upstream_article = self.find_article_in_upstream_articles(article['article']['sophoraId'])
                update = requests.get(article['article']['updateCheckUrl']).json()

                if index:
                    if update or index is not article['article']['crawler']['index']:
                        self.db.update_article(upstream_article, index, article['article']['crawler']['insertTime'])
                else:
                    if update:
                        new_article = requests.get(upstream_article['details']).json()
                        self.db.update_article(new_article, -1, article['article']['crawler']['insertTime'])
            except Exception as e:
                print(e)
                self.db.delete_article(article['article'], article['article']['crawler']['insertTime'])


    def find_article_in_upstream_articles(self, sophoraId: str) -> Tuple[int, dict]:
        for index, article in enumerate(self.upstream_articles):
            if article.get('sophoraId', None) == sophoraId:
                return index, article

        return None, None


    def update_article(self, article: dict):
        try:
            if requests.get(article['updateCheckUrl']).json():
                new_article = requests.get(article['details']).json()

                new_article['crawlTimeInsert'] = article['crawlTimeInsert']
                new_article['crawlTime'] = datetime.now()
                new_article['crawlType'] = 'update'
                new_article['crawlIndex'] = article['index']
                new_article['date'] = datetime.fromisoformat(new_article['date'])

                self.db.news.insert_one(new_article)
                print('Updated article: ', new_article['title'])

        except Exception as e:
            print('Error', e)

            del(article['_id'])
            article['crawlTime'] = datetime.now()
            article['crawlType'] = 'delete'

            self.db.news.insert_one(article)
            print('Deleted article: ',  article['title'])
