from scrapers.scraper import Scraper


class scraper_nyt(Scraper):

    def __init__(self):
        super().__init__('nyt', 'http://nytimes.com')
