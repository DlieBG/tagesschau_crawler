from datetime import datetime, timedelta
from db import TagesschauDB
from typing import Tuple
from time import sleep
import requests


class UpdateNews:

    def __init__(self):
        self.db = TagesschauDB()
        while True:
            self.update_articles(datetime.now() - timedelta(days=1))
            sleep(5 * 60)


    def update_articles(self, timestamp: datetime):
        try:
            self.upstream_articles = requests.get('https://www.tagesschau.de/api2').json()['news']

            for article in self.db.get_articles_to_update(timestamp):
                try:
                    index, upstream_article = self.find_article_in_upstream_articles(article['article']['sophoraId'])
                    update = requests.get(article['article']['updateCheckUrl']).json()

                    if index is not None:
                        if update or index is not article['article']['crawler']['index']:
                            self.db.update_article(upstream_article, index, article['article']['crawler']['insertTime'])
                        continue
                    
                    if update:
                        new_article = requests.get(article['article']['details']).json()
                        self.db.update_article(new_article, -1, article['article']['crawler']['insertTime'])
                except Exception as e:
                    print(f'Failed updating article "{article["article"]["sophoraId"]}", because of "{e}"')
                    self.db.delete_article(article['article'], article['article']['crawler']['insertTime'])
        except Exception as e:
            print(f'# Failed updating news, because of "{e}"')


    def find_article_in_upstream_articles(self, sophoraId: str) -> Tuple[int, dict]:
        for index, article in enumerate(self.upstream_articles):
            if article.get('sophoraId', None) == sophoraId:
                return index, article

        return None, None
