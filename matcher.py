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
import gc


def update_articles_trends(trends_agg):
    trends_dic = {}
    fs_trends_list = getLatestTrendsList(trends_agg)
    for trend in fs_trends_list:
        trends_dic[trend.name] = [trend, filterString(trend.name)]
    for trend in getDailyTrends():
        trends_dic.setdefault(trend, [None, filterString(trend)])

    # scraper_objs = [scraper_nyt]
    scraper_objs = [scraper_nyt,
                    scraper_cnn,
                    scraper_fox,
                    scraper_cnbc]
    scraper_objs_built = (scraper() for scraper in scraper_objs)
    # papers = [paper.built_site for paper in scraper_objs_built]
    # print([scraper.built_site.size() for scraper in scraper_objs_built])
    # print([paper.size() for paper in papers])
    # news_pool.set(papers, threads_per_source=2) # 4 papers * 2 threads = 8 threads total
    # news_pool.join()

    # at this point, every article has been downloaded
    counter = 0
    for scraper in scraper_objs_built:
        article_gen = (scrape(scraper, article) for article in scraper.built_site.articles)
        for article_obj in article_gen:
            if article_obj:
                # try to match it
                counter = counter + 1
                match_article_to_trends(article_obj, trends_dic, fs_trends_list, counter)
                # add_to_last500(matched_list, trends_dic, fs_trends_list)
            #--del article_obj
        #--del scraper
        #--gc.collect()
    print("Done matching articles")
    if len(fs_trends_list) > 500:
        fs_trends_list = fs_trends_list[:-1]
    return fs_trends_list


def add_to_last500(matched_trend, trends_dic, fs_trends_list):
    if trends_dic[matched_trend.name][0] in fs_trends_list:
        i = fs_trends_list.index(trends_dic[matched_trend.name][0])
        fs_trends_list.pop(i)
    fs_trends_list.insert(0, matched_trend)
    update_trends_dic(trends_dic, matched_trend)
    print(f"updated last500_list with trend: {matched_trend.name}")
    #--return


def match_article_to_trends(article_obj, trends_dic, fs_trends_list, counter):
    print(f"articles checked: {counter}")
    trends_dic_copy = trends_dic.copy()
    match_gen = (get_updated_match(article_obj, trends_dic_copy, key) for key in trends_dic_copy.keys())
    for match in match_gen:
        if match:
            add_to_last500(match, trends_dic, fs_trends_list)
    #--del trends_dic_copy
    #--return


# matches article to trend and returns updated trend if matched
def get_updated_match(article_obj, trend_dic_copy, key):
    article_tokens = filterString(article_obj.title)
    trend_tokens = trend_dic_copy[key][1]
    jacScore = getJaccardScore(article_tokens, trend_tokens)
    if jacScore > 0:
        # value[0].articles.append(article_obj)
        # value[0].categories = combineCategories(value[0].articles)
        new_articles = []
        old_categories = set()
        if trend_dic_copy[key][0]:  # if trend object exists
            # if value[0].articles: # if old trend
            new_articles = trend_dic_copy[key][0].articles[:]
            old_categories = trend_dic_copy[key][0].categories
        if article_obj not in new_articles:
            new_articles.insert(0, article_obj)
        new_trend = Trend(name=key, categories=article_obj.categories.union(old_categories), articles=new_articles)
        # pprint.pprint(new_trend)
        return new_trend
    #--return

def update_trends_dic(trends_dic, new_trend):
    trend_filtered_string = trends_dic[new_trend.name][1]
    trends_dic[new_trend.name] = [new_trend, trend_filtered_string]
    #--return

# gets a list of the latest trends stored on firestore
def getLatestTrendsList(trends_agg):
    last500_list = trends_agg.last500
    return last500_list


def scrape(scraper, article_extract):
    article = {}
    try:
        article_extract.download()
        article_extract.parse()

        article["publisher"] = scraper.getPublisher()
        article["url"] = scraper.getArticleURL(article_extract)
        article["title"] = scraper.getTitle(article_extract)
        article["date"] = scraper.getDate(article_extract)
        article["description"] = scraper.getDescription(article_extract)
        article["imageURL"] = scraper.getImageURL(article_extract)
        article["categories"] = scraper.getCategories(article_extract)
        #--del article_extract
        return Article.from_dict(article)  # to article object
    except:
        pass
