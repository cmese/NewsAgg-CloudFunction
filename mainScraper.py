'''
The 'master' scraper
'''
from newspaper import news_pool
from newspaper import Config
from scrapers.scraper_cnn import scraper_cnn
from scrapers.scraper_fox import scraper_fox
from scrapers.scraper_cnbc import scraper_cnbc
#from scraper_nyt import scraper_nyt

import asyncio
import pprint
# from .Article import Article
from articles.Article import Article  # for testing seperately

# from .cnnScraper import getCNNArticles
# from . import cnnScraper, foxScraper, nytScraper

async def getNewArticles():
    articles = []
    scraper_objs = [scraper_cnn,
                    scraper_fox,
                    scraper_cnbc]
                    # scraper_nyt]
    scraper_objs_built = [scraper() for scraper in scraper_objs]
    papers = [paper.built_site for paper in scraper_objs_built]
    print([paper.size() for paper in papers])
    news_pool.set(papers, threads_per_source=2) # 4 papers * 2 threads = 8 threads total
    news_pool.join()
    tasks = []
    for built_scraper in scraper_objs_built:
        tasks.append(scrape(built_scraper))
    results = await asyncio.gather(*tasks)
    for result in results:
        articles = articles + result
    pprint.pprint(articles)
    return articles
    #return scrape(scraper_objs_built)

async def scrape(scraper):
    articles = []
    # at this point, every article has been downloaded
    for article_extract in scraper.built_site.articles:
        article_extract.parse()
        # print(article_extract)
        try:
            article = {}
            # print(scraper.printVars(article_extract))
            article["publisher"] = scraper.getPublisher()
            article["url"] = scraper.getArticleURL(article_extract)
            article["title"] = scraper.getTitle(article_extract)
            article["date"] = scraper.getDate(article_extract)
            article["description"] = scraper.getDescription(article_extract)
            article["imageURL"] = scraper.getImageURL(article_extract)
            article["categories"] = scraper.getCategories(article_extract)
            # print(article)
            article_obj = Article.from_dict(article)
            if article_obj:
                articles.append(article_obj)
            # articles.append(article_obj)
        except:
            pass
    # return [*set(articles)]
    print(len(articles))
    return articles

#final = scrape()
#pprint.pprint(final)
#print(len(final))
