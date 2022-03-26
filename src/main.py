from dotenv import load_dotenv, find_dotenv
from update_news import UpdateNews
from crawl_news import CrawlNews
from time import sleep
import threading

load_dotenv(find_dotenv())

crawl_news = threading.Thread(target=CrawlNews)
crawl_news.daemon = False
crawl_news.start()

sleep(5)

update_news = threading.Thread(target=UpdateNews)
update_news.daemon = False
update_news.start()
