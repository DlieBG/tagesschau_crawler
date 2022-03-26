from datetime import datetime, timedelta
from pymongo import MongoClient
from time import sleep
import requests
import os

class UpdateNews:

    db = MongoClient(os.getenv('MONGO_URI')).tagesschau

    def __init__(self):
        while True:
            self.update_news(datetime.now() - timedelta(days=1))
            sleep(30 * 60)


    def update_news(self, timestamp: datetime):
        for article in self.load_news(timestamp):
            self.update_article(article['article'])


    def load_news(self, timestamp: datetime):
        return self.db.news.aggregate([
            { 
                '$match': { 
                    'crawlTime': { 
                        '$gte': timestamp
                    },
                    'crawlType': {
                        '$not': {
                            '$regex': "delete"
                        }
                    }
                } 
            },
            {
                '$group': {
                    '_id': '$sophoraId', 
                    'article': {
                        '$last': '$$ROOT'
                    }
                }
            }
        ])


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
