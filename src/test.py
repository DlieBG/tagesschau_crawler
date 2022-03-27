from db import TagesschauDB
from datetime import datetime, timedelta

db = TagesschauDB()

article = db.get_articles_to_update(datetime.now() - timedelta(days=1))

for a in article:
    print(a['article'].get('title', None))
    print("gibts")