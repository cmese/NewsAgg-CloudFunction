from scrapers.scraper import Scraper
from datetime import datetime
from dateutil import parser


class scraper_cnn(Scraper):

    def __init__(self):
        super().__init__('cnn', 'http://cnn.com')

    # meta_data.section
    def getCategories(self, article):
        top_keywords = super().getCategories(article)
        if article.meta_data['section']:
            top_keywords.append(article.meta_data['section'])
        # print(top_keywords)
        return [*set(self.filterCategories(top_keywords))]

    # where to get date from article changes
    # meta_data.pubdate if regular date is empty
    #TODO: convert to dateutil
    def getDate(self, article):
        if article.meta_data['pubdate']:
            try:
                return self.extractDate(article.meta_data['pubdate'])
                # datetime_str = str(datetime.strptime(article.meta_data['pubdate'], '%Y-%m-%dT%H:%M:%SZ'))
                # return datetime_str
            except:
                pass
        return super().getDate(article) # returns '' if found nothing

#scraper = scraper_cnn()
#article = scraper.buildArticleNum(10)

# scraper.printVars(article)
# print("----------------------------------------------------------")
# scraper.printVars(scraper.scrapeArticle(article))
# pprint.pprint(scraper.scrapeArticle(article))
