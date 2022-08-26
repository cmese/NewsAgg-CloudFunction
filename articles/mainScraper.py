'''
The 'master' scraper
'''
# from .cnnScraper import getCNNArticles
from . import cnnScraper, foxScraper, nytScraper


def scrape():
    cnnArticles = cnnScraper.getArticles()
    foxArticles = foxScraper.getArticles()
    nytArticles = nytScraper.getArticles()
    return [cnnArticles + nytArticles + foxArticles]
