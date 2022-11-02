from scrapers.scraper_cnn import scraper_cnn
from scrapers.scraper_fox import scraper_fox
from scrapers.scraper_cnbc import scraper_cnbc

from articles.Article import Article
from trends.Trend import Trend
from trends.gTrends import getDailyTrends
from filter import filterString

from newspaper import news_pool
from google.cloud import firestore


class TrendsAgg(object):
    def __init__(self, last500=[]):
        self.last500 = last500

    @staticmethod
    def from_dict(source):
        last500_object_list = [Trend.from_dict(
            trend) for trend in source[u'last500']]
        return TrendsAgg(last500_object_list)

    def to_dict(self):
        last500_dict_list = [trend.to_dict() for trend in self.last500]
        dest = {
            u'last500': last500_dict_list
        }
        return dest

    def __repr__(self):
        return(
            f'\nLAST500(\n'
            f' {self.last500}\n'
            f')'
        )


def genScraper():
    trends_dic = {}
    fs_trends_list = getLatestTrendsList()
    for trend in fs_trends_list:
        trends_dic[trend.name] = [trend, filterString(trend.name)]
    for trend in getDailyTrends():
        trends_dic.setdefault(trend, [None, filterString(trend.name)])

    scraper_objs = [scraper_cnn]
                    #scraper_fox,
                    #scraper_cnbc]
    scraper_objs_built = [scraper() for scraper in scraper_objs]
    papers = [paper.built_site for paper in scraper_objs_built]
    print([paper.size() for paper in papers])
    news_pool.set(papers, threads_per_source=2) # 4 papers * 2 threads = 8 threads total
    news_pool.join()

    # at this point, every article has been downloaded
    for scraper in scraper_objs_built:
        article_gen = (scrape(scraper, article) for article in scraper.built_site.articles)
        for article in article_gen:
            article_obj = Article.from_dict(article)
            if article_obj:
                # try to match it
                matched_list = match_article_to_trends(article, trends_dic)
                add_to_last500(matched_list, trends_dic, fs_trends_list)



def add_to_last500(matched_list, trends_dic, fs_trends_list):
    for matched_trend in matched_list:
        if trends_dic[matched_trend.name][0] is None: # brand new trend
            fs_trends_list.insert(0, matched_trend)
        elif trends_dic[matched_trend.name][0] != matched_trend: #previous trend with new articles
            fs_trends_list.pop(
                    fs_trends_list.index(trends_dic[matched_trend.name]))
            fs_trends_list.insert(0, matched_trend)
        if len(fs_trends_list) > 500:
            fs_trends_list = fs_trends_list[:-1]
    return fs_trends_list


def match_article_to_trends(article_obj, trends_dic):
    matched_list = []
    article_tokens = filterString(article_obj.title)
    for key, value in trends_dic.items():
        jacScore = getJaccardScore(value[1], article_tokens)
        if jacScore > 0:
            # value[0].articles.append(article_obj)
            # value[0].categories = combineCategories(value[0].articles)
            old_articles = []
            if value[0]: # old trend match
                old_articles = value[0].articles[:]
                new_trend = Trend(name=key, categories=article_obj.categories.Union(value[0].categories), articles=old_articles.insert(0, article_obj))
                matched_list.append(new_trend)
            else: # new google trend match
                new_trend = Trend(name=key, categories=article_obj.categories, articles=article_obj)
                matched_list.append(new_trend)
    return matched_list


# gets a list of the latest trends stored on firestore
def getLatestTrendsList():
    db = firestore.Client()
    trendsAgg_doc_ref = db.collection(u'trendsAgg').document(u'recentTrends')
    doc_dict = trendsAgg_doc_ref.get().to_dict()
    last500_list = []
    if doc_dict:
        trends_agg = TrendsAgg.from_dict(doc_dict)
        last500_list = trends_agg.last500
    return last500_list


def getJaccardScore(str1_tokens, str2_tokens):
    a = set(str1_tokens)
    b = set(str2_tokens)
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))
def scrape(scraper, article_extract):
    article_extract.parse()
    try:
        article = {}
        article["publisher"] = scraper.getPublisher()
        article["url"] = scraper.getArticleURL(article_extract)
        article["title"] = scraper.getTitle(article_extract)
        article["date"] = scraper.getDate(article_extract)
        article["description"] = scraper.getDescription(article_extract)
        article["imageURL"] = scraper.getImageURL(article_extract)
        article["categories"] = scraper.getCategories(article_extract)
    except:
        pass
    return Article.from_dict(article)
