from scrapers.scraper import Scraper


class scraper_fox(Scraper):
    def __init__(self):
        super().__init__('fox', 'http://www.foxnews.com')

    def getDate(self, article):
        meta_data_dict = dict(article.meta_data)
        if meta_data_dict['dc.date']:
            return meta_data_dict['dc.date']
        return super().getDate(article)

    # getText needs a little work - effects keyword extraction
