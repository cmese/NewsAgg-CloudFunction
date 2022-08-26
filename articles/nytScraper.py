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
                category_set = set()
                for category in item.tags:
                    category_set.add(category)
                if (category_set is set()):
                    continue
                article["categories"] = category_set
            except (AttributeError, KeyError):
                continue
            articles.append(Article.from_dict(article))
    return [*set(articles)]  # removes duplicates

print(getArticles())
