from scrapers.scraper import Scraper


class scraper_fox(Scraper):
    def __init__(self):
        super().__init__('fox', 'http://www.foxnews.com')

    # TODO: missing time
    def getDate(self, article):
        # meta_data_dict = dict(article.meta_data) #unnecessary, meta_data is already a collections.defaultdict (does not return error when looking up key that doesn't exist)
        # if meta_data_dict['dc.date']:
        #    return meta_data_dict['dc.date']
        if article.meta_data['dc.date']:
            try:
                return self.extractDate(article.meta_data['dc.date'])
        # datetime_str = str(datetime.fromisoformat(article.meta_data['article']['published_time']))
        # return datetime_str
            except:
                pass
        return super().getDate(article)

    # getText needs a little work - effects keyword extraction
