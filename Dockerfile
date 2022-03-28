FROM python:3.9
WORKDIR /usr/src/app

COPY src/requirements.txt .
RUN pip3 install -r requirements.txt

COPY src/main.py .
COPY src/db.py .
COPY src/crawl_news.py .
COPY src/update_news.py .

CMD [ "python3", "main.py" ]
