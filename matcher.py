from scrapers.scraper_cnn import scraper_cnn
from scrapers.scraper_fox import scraper_fox
from scrapers.scraper_cnbc import scraper_cnbc
from scrapers.scraper_nyt import scraper_nyt

from articles.Article import Article
from trends.Trend import Trend
from trends.gTrends import getDailyTrends
from filter import filterString
from sim_scorers import getJaccardScore


# fetches latest trends cached in cloud firestore and google
# builds and fetches articles from all news sites and matches
# them to trends one by one. Returns the updated agg list
def update_articles_trends(trends_agg):
    # combine latest trends from firestore and google into trends dictionary
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
    # initialize a news site's scraper object
    # this also builds the site with newspaper3k
    scraper_objs_built = (scraper() for scraper in scraper_objs)

    # for each built site's scraper object, scrape each article and try to
    # match it
    counter = 0
    for scraper in scraper_objs_built:
        article_gen = (scrape(scraper, article) for article in scraper.built_site.articles)
        for article_obj in article_gen:
            if article_obj:
                # try to match it
                counter = counter + 1
                match_article_to_trends(article_obj, trends_dic, fs_trends_list, counter)
    print("Done matching articles")

    # trim updated agg list if trend objects > 500
    fs_trends_list = fs_trends_list[:500]
    return fs_trends_list


# tries to match an article to each of the trends in the current trends_dic one by one
# for each match found, update the aggregated trends list with the new trend found
def match_article_to_trends(article_obj, trends_dic, fs_trends_list, counter):
    print(f"Trying to match article {counter}: PUBLISHER={article_obj.publisher}...TITLE={article_obj.title}")
    trends_dic_copy = trends_dic.copy()
    match_gen = (get_updated_match(article_obj, trends_dic_copy, key) for key in trends_dic_copy.keys())
    for match in match_gen:
        if match:
            print(f"MATCHED article {counter}: PUBLISHER={article_obj.publisher}...TITLE={article_obj.title}...TREND={match.name}")
            add_to_last500(match, trends_dic, fs_trends_list)


# if the matched trend already exists in the aggregated trends list, pop it and
# insert the updated trend object at the front. Updates trends dic before the next
# article / trend match check
def add_to_last500(matched_trend, trends_dic, fs_trends_list):
    if trends_dic[matched_trend.name][0] in fs_trends_list:
        i = fs_trends_list.index(trends_dic[matched_trend.name][0])
        fs_trends_list.pop(i)
    fs_trends_list.insert(0, matched_trend)
    update_trends_dic(trends_dic, matched_trend)
    print(f"updated last500_list with trend: {matched_trend.name}")


# matches article to trend and returns new trend object with article if matched
def get_updated_match(article_obj, trend_dic_copy, key):
    # compare article tokens and trend tokens
    article_tokens = filterString(article_obj.title)
    trend_tokens = trend_dic_copy[key][1]
    jacScore = getJaccardScore(article_tokens, trend_tokens)
    if jacScore > 0: # if match
        new_articles = []
        old_categories = set()
        # if trend object exists, copy old articles list and categories set
        if trend_dic_copy[key][0]:  # if trend object exists
            new_articles = trend_dic_copy[key][0].articles[:]
            old_categories = trend_dic_copy[key][0].categories
        # append new article to old articles list in the front
        if article_obj not in new_articles: # prevents duplicate articles in trend object
            new_articles.insert(0, article_obj)
            new_articles = new_articles[:10]
        # combine categories sets and create new trend with new categories set and new articles list
        new_trend = Trend(name=key, categories=article_obj.categories.union(old_categories), articles=new_articles)
        return new_trend


# updates trends dict with the updated trend
def update_trends_dic(trends_dic, new_trend):
    trend_filtered_string = trends_dic[new_trend.name][1]
    trends_dic[new_trend.name] = [new_trend, trend_filtered_string]


# gets a list of the latest trends stored on firestore
def getLatestTrendsList(trends_agg):
    last500_list = trends_agg.last500
    return last500_list


# downloads and parses an article extract
# scrapes the required attributes into an article dictionary
# if all attributes are found, an article object is created and returned
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
        return Article.from_dict(article)  # to article object
    except:
        pass
