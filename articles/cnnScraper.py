import feedparser
from rssLinks import rssDic
from urllib.request import urlopen
from xml.etree.ElementTree import parse
import re
# from filter import filterString
# from pprint import pprint
# from .Article import Article
from Article import Article  # for testing seperately
# from .categories import cnn_categories
from categories import cnn_categories
URL = 'http://rss.cnn.com/rss/cnn_latest.rss'


def getArticles():
    articles = []
    for url in rssDic['cnn']:
        feed = feedparser.parse(url)
        print(feed.entries[0].keys())
        for item in feed.entries:
            article = {}
            try:
                article["publisher"] = "cnn"
                article["title"] = item.title
                article["date"] = item.published
                article["description"] = item.summary
                article["imageURL"] = item.media_content[0]['url']
                article["url"] = item.link
                categories = getCategories(item.link)
                if (categories is set()):  # if empty
                    continue
                article["categories"] = categories
            except (AttributeError, KeyError):
                continue
            articles.append(Article.from_dict(article))
    return [*set(articles)]  # removes duplicates

def getCategories(link):
    categories = set()
    category = processURL(link)
    if category:
        categories.add(category)
    return categories


# extracts the category from the article's url
# TODO: make this safer: could easily break if url's change, doesn't work for travel articles for example
def processURL(url):
    splitURL = url.split("/")
    category = ""
    if len(splitURL) == 9:
        category = splitURL[6]
    elif len(splitURL) == 7:
        category = splitURL[3]

    if category in cnn_categories:
        return cnn_categories[category]
    return category


# Scrapes a list of articles from an rss feed
def loadRSS():
    return urlopen(URL)


# Parses xml for articles that have a title, description, link, date, and url
def parseXML(respHTML):
    respXML = parse(respHTML)
    articles = []

    for item in respXML.iterfind('./channel/item'):
        article = {}
        article["publisher"] = "cnn"
        title = item.findtext('title')
        if title:
            article["title"] = str(title)
            #article["title_tokens"] = filterString(str(title))
        else:
            continue

        description = re.match(r'.+?(?=<)', str(item.findtext('description')))
        if description:
            article["description"] = str(description.group())
            #article["description_tokens"] = filterString(str(description.group()))
        else:
            continue

        category_set = set()
        link = item.findtext('link')
        if link:
            article["url"] = str(link)
            category = processURL(str(link))
            if category:
                category_set.add(category)
                article["categories"] = category_set
            else:
                continue
        else:
            continue

        pubDate = item.findtext('pubDate')
        if pubDate:
            article["date"] = str(pubDate)
        else:
            continue

        try:
            selectedimage = item[-1][0].attrib.get('url')
            article["imageURL"] = str(selectedimage)
        except:
            continue
        articles.append(Article.from_dict(article))
    return articles

# TODO: Sorensen-Dice to get torken scores for grouping
    # TODO: Tokenize Titles, Descriptions too?

# helper to print specific elements from parsed xmlTree to console
def printFullParsedTree(xmlTree):
    for item in xmlTree.iterfind('./channel/item'):
        print("Title: ", item.findtext('title'))
        description = re.match(r'.+?(?=<)', str(item.findtext('description')))
        if description:
            print("Description: ", description.group())
        else:
            print("Description: ")
        print("URL: ", item.findtext('link'))
        print("Date: ", item.findtext('pubDate'))
        try:
            print("Image: ", item[-1][0].attrib.get('url'))
        except:
            print("Image: ")
        print("\n")

# CHANGE to recursive 
# messy helper function for exploring element tree for tags and attributes
def printXMLtree(xmlTree):
    root = xmlTree.getroot()
    print(root.tag)
    for child in root:
        print("root child--")
        print(child.tag, child.attrib)
        for item in child:
            print(item.tag, item.attrib)
            for itemchild in item:
                print("\t", itemchild.tag, itemchild.attrib)
                for x in itemchild:
                    print("\t\t", x.tag, x.attrib)
            print("==========================================")
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")


def printParsedArticles(articles):
    for i in range (len(articles)):
        print(articles[i])
        print("\n")


def getArticlesOld():
    articles = parseXML(loadRSS())
    #printParsedArticles(articles)
    #return parseXML(loadRSS())
    return articles

#printXMLtree(parse(loadRSS()))
'''
articles = getArticles()
printParsedArticles(articles)
print("number of articles: ", len(articles))
print("bytes: ", sys.getsizeof(articles))
'''
#Title with a high ranking will get grouped under that keyword
#All unqualified articles will have their descriptions processed and appended to the title tokens 
    #run algorithm again to get new rankings and group under keywords accordingly 

#For each article, compare each keyword from keywordList to the title of the article and get a score for each
    #get the max score and see if its greater then a threshold
        #if its greater, store that article[i] under that keyword 
        #if its less, compare each keyword from keywordList to the description of the article and get a score for each comparison
    #get the max score and see if its greater then a threshold 
        #if its greater, store that article[i] under that keyword
        #if its less, store the article in the "other" keyword/category 

getArticles()






