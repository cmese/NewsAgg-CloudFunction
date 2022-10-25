import newspaper
import os
import tempfile
import pprint
import nltk
from datetime import datetime
from articles.categories import categories
from dateutil import parser

# for running seperately
import sys
sys.path.append('..')
from filter import filterString
# MAJOR TODO: newspaper3k newspool


# generic scraper class for newspaper3k
class Scraper:
    # publisher = key, url = value in url_dict
    def __init__(self, publisher, url):
        self.publisher = publisher
        self.base_url = url
        self.built_site = newspaper.build(url, language='en', memoize_articles=False)  # make setter here for validation

    def buildArticle(self, article):
        # article = built_site.articles[article_num]
        article.download()
        article.parse()


    # download all new articles from site locally - used when memoized = true
    def buildArticles(self):
        for article in self.built_site.articles:
            self.buildArticle(article)

    def buildArticleNum(self, num):
        article = self.built_site.articles[num]
        article.download()
        article.parse()
        return article

    # get all cached article urls - unnecessary
    def getCachedArticles(self):
        DATA_DIRECTORY = '.newspaper_scraper'
        DATA_PATH = os.path.join(tempfile.gettempdir(), DATA_DIRECTORY)

        MEMO_DIRECTORY = 'memoized'
        MEMO_PATH = os.path.join(DATA_PATH, MEMO_DIRECTORY)  # /tmp/.newspaper_scraper/memoized
        lines = []
        for file in os.listdir(MEMO_PATH):
            FULL_PATH = os.path.join(MEMO_PATH, file)
            with open(FULL_PATH) as site_file:
                for line in site_file:
                    lines.append(line)
        return lines

    def getPublisher(self):
        return self.publisher

    def getSiteURL(self):
        return self.url

    def getArticleURL(self, article):
        return article.url

    def getTitle(self, article):
        return article.title

    def getText(self, article):
        return article.text.replace('\n', '')

    def getDate(self, article):
        if article.publish_date:
            # return article.publish_date
            return str(article.publish_date)
        return ''

    def extractDate(self, date_string):
        article_date = parser.parse(date_string)
        return str(article_date)

    def getDescription(self, article):
        return article.meta_description

    def getImageURL(self, article):
        return article.top_image

    def getTags(self, article):
        article_tags = []
        if article.tags:
            article_tags = [x.lower() for x in list(article.tags)]
            #article_tags = list(article.tags)
        return article_tags

    def getCategories(self, article):
        return [*set(self.filterCategories(self.getTags(article) + self.getKeywords(article)))]

    def filterCategories(self, keyword_list):
        cats_from_keys = [categories[x] for x in keyword_list if x in categories]
        #cats_from_vals takes care of multiple filterCategories calls
        cats_from_vals = [x for x in keyword_list if x in categories.values()]
        return [*set(cats_from_keys + cats_from_vals)]

    # https://github.com/johnbumgarner/newspaper3_usage_overview
    # nltk example usage: https://github.com/johnbumgarner/newspaper3_usage_overview
    def getKeywords(self, article):
        article_text = self.getText(article)
        article_description = self.getDescription(article)
        article_title = self.getTitle(article)

        article_text = filterString(article_text)
        article_description = filterString(article_description)
        article_title = filterString(article_title)

        article_tokens = article_text + article_description + article_title + self.getTags(article)
        article_text_Dist = nltk.FreqDist(word for word in article_tokens)
        most_common_words = article_text_Dist.most_common(20)
        top_keywords = []
        for word, freq in most_common_words:
            top_keywords.append(word)
        final_keywords = top_keywords + article_title
        return final_keywords

    # print attribute values for object
    def printVars(self, obj):
        pprint.pprint(vars(obj))
        return
