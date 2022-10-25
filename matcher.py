# matches latest trends to latest articles

from filter import filterString
from trends.Trend import Trend
# similarity scorer (for now)
def getJaccardScore(str1_tokens, str2_tokens):
    a = set(str1_tokens)
    b = set(str2_tokens)
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))


# returns a list of matched Trend objects
def match(articles, trends):
    result_list = []
    for trend in trends:
        trend_tokens = filterString(trend)
        matched_articles = []
        for article in articles:
            article_tokens = filterString(article.title)
            jacScore = getJaccardScore(trend_tokens, article_tokens)
            if jacScore > 0:
                matched_articles.append(article)
        if matched_articles:
            category_set = combineCategories(matched_articles)
            matched_trend = Trend(name=trend, categories=category_set, articles=matched_articles)
            result_list.append(matched_trend)
    return result_list


# takes all article categories from article list
# and converts it to either sports, politics, business, health
# example: baseball -> sports, covid -> health, stocks -> business
def combineCategories(articles):
    categories = set()
    for article in articles:
        for category in article.categories:
            categories.add(category)
    return categories
