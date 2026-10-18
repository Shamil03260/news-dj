from celery import shared_task
from .scraper import fetch_news


@shared_task
def fetch_news_task():
    return fetch_news()