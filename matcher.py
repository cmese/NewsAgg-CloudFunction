from scrapers.scraper_cnn import scraper_cnn
from scrapers.scraper_fox import scraper_fox
from scrapers.scraper_cnbc import scraper_cnbc
from scrapers.scraper_nyt import scraper_nyt

from articles.Article import Article
from trends.Trend import Trend
from trends.gTrends import getDailyTrends
from filter import filterString
from sim_scorers import getJaccardScore

from newspaper import news_pool
# from google.cloud import firestore

import pprint


def update_articles_trends(trends_agg):
    trends_dic = {}
    fs_trends_list = getLatestTrendsList(trends_agg)
    for trend in fs_trends_list:
        trends_dic[trend.name] = [trend, filterString(trend.name)]
    for trend in getDailyTrends():
        trends_dic.setdefault(trend, [None, filterString(trend)])

    scraper_objs = [scraper_nyt]
                    #scraper_cnn,
                    #scraper_fox]
                    #scraper_cnbc]
    scraper_objs_built = [scraper() for scraper in scraper_objs]
    papers = [paper.built_site for paper in scraper_objs_built]
    print([paper.size() for paper in papers])
    news_pool.set(papers, threads_per_source=2) # 4 papers * 2 threads = 8 threads total
    news_pool.join()

    # at this point, every article has been downloaded
    for scraper in scraper_objs_built:
        article_gen = (scrape(scraper, article) for article in scraper.built_site.articles)
        for article_obj in article_gen:
            if article_obj:
                # try to match it
                matched_list = match_article_to_trends(article_obj, trends_dic)
                add_to_last500(matched_list, trends_dic, fs_trends_list)
    if len(fs_trends_list) > 500:
        fs_trends_list = fs_trends_list[:-1]
    return fs_trends_list


def add_to_last500(matched_list, trends_dic, fs_trends_list):
    for matched_trend in matched_list:
        if trends_dic[matched_trend.name][0] in fs_trends_list:
            fs_trends_list.pop(
                        fs_trends_list.index(trends_dic[matched_trend.name][0]))
        fs_trends_list.insert(0, matched_trend)
        update_trends_dic(trends_dic, matched_trend)


def match_article_to_trends(article_obj, trends_dic):
    matched_list = []
    article_tokens = filterString(article_obj.title)
    for key, value in trends_dic.items():
        jacScore = getJaccardScore(value[1], article_tokens)
        if jacScore > 0:
            # value[0].articles.append(article_obj)
            # value[0].categories = combineCategories(value[0].articles)
            new_articles = []
            old_categories = set()
            if value[0]: # if trend object exists
                # if value[0].articles: # if old trend
                new_articles = value[0].articles[:]
                old_categories = value[0].categories
            if article_obj not in new_articles:
                new_articles.insert(0, article_obj)
            new_trend = Trend(name=key, categories=article_obj.categories.union(old_categories), articles=new_articles)
            matched_list.append(new_trend)
    pprint.pprint(matched_list)
    return matched_list

def update_trends_dic(trends_dic, new_trend):
    trends_dic[new_trend.name] = [new_trend, trends_dic[new_trend.name][1]]

# gets a list of the latest trends stored on firestore
def getLatestTrendsList(trends_agg):
    last500_list = trends_agg.last500
    return last500_list


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
