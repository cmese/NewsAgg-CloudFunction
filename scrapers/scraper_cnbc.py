from scrapers.scraper import Scraper
from dateutil import parser

class scraper_cnbc(Scraper):
    def __init__(self):
        super().__init__('cnbc', 'http://www.cnbc.com')

    def getDate(self, article):
        if article.meta_data['article']['published_time']:
            return self.extractDate(article.meta_data['article']['published_time'])
                # datetime_str = str(datetime.fromisoformat(article.meta_data['article']['published_time']))
                # return datetime_str
        return super().getDate(article)
