import feedparser
# from .Article import Article
from Article import Article  # for testing seperately
from rssLinks import rssDic


def getArticles():
    articles = []
    for url in rssDic['nyt']:
        feed = feedparser.parse(url)
        for item in feed.entries:
            article = {}
            try:
                article["publisher"] = "nyt"
                article["title"] = item.title
                article["date"] = item.published
                article["description"] = item.summary
                article["url"] = item.link
                article["imageURL"] = item.media_content[0]['url']
                category = processURL(item.link)
                if category:
                    category_set = set()
                    category_set.add(category)
                    article["categories"] = category_set
                else:
                    continue
                '''
                category_set = set()
                for category in item.tags:
                    category_set.add(category.term)
                if (category_set is set()):
                    continue
                article["categories"] = category_set
                '''
            except (AttributeError, KeyError):
                continue
            articles.append(Article.from_dict(article))
    return [*set(articles)]  # removes duplicates

def processURL(url):
    splitURL = url.split("/")
    if len(splitURL) >= 6:
        category = splitURL[6]
        return category
    return

def processCategory(category):
    split_category = category.split("/")
    if split_category[0] == "fox-news":
        if split_category[1] in fox_categories:
            return fox_categories[split_category[1]]
    return

print(getArticles())
