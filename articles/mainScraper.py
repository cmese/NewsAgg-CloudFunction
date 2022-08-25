'''
The main scraper that calls all of the
other different types of RSS scrapers from
the different news organizations in one function
'''
# from .cnnScraper import getCNNArticles
from . import cnnScraper, foxScraper


def scrape():
    cnnArticles = cnnScraper.getArticles()
    foxArticles = foxScraper.getArticles()
    return cnnArticles + foxArticles
