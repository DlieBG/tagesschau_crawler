from pymongo import MongoClient
from datetime import datetime
from sqlite3 import Cursor
import os

class TagesschauDB:

    def __init__(self):
        self.db = MongoClient(os.getenv('MONGO_URI')).tagesschau

    def __insert_article(self, article: dict, insert_time: datetime, index: int = -1, crawl_type: str = 'new'):
        try:
            try:
                del(article['_id'])
            except:
                pass

            article['date'] = datetime.fromisoformat(str(article['date']))
            
            article['crawler'] = {
                'index': index,
                'insertTime': insert_time,
                'crawlTime': datetime.now(),
                'crawlType': crawl_type
            }

            self.db.news.insert_one(article)
        except Exception as e:
            self.db.error.insert_one({
                'function': 'insert_article',
                'type': crawl_type,
                'exception': str(e)
            })

    def insert_article(self, article: dict, index: int):
        self.__insert_article(article, datetime.now(), index)
        print('Inserted article: ', article['sophoraId'])

    def update_article(self, article: dict, index: int, insert_time: datetime):
        self.__insert_article(article, insert_time, index, crawl_type='update')
        print('Updated article: ', article['sophoraId'])

    def delete_article(self, article: dict, insert_time: datetime):
        self.__insert_article(article, insert_time, crawl_type='delete')
        print('Deleted article: ', article['sophoraId'])

    def get_articles(self, sophoraId: str) -> Cursor:
        return self.db.news.find({ 'sophoraId': sophoraId })

    def get_articles_to_update(self, timestamp: datetime) -> Cursor:
        return self.db.news.aggregate([
            { 
                '$match': { 
                    'crawler.crawlTime': { 
                        '$gte': timestamp
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
            },
            {
                '$match': {
                    'article.crawler.crawlType': {
                        '$not': {
                            '$regex': "delete"
                        }
                    }
                }
            }
        ])

    def get_article(self, sophoraId: str):
        try:
            return self.db.news.aggregate([
                { 
                    '$match': { 
                        'sophoraId': sophoraId
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
            ]).next()
        except:
            return None
