import feedparser
from rssLinks import rssDic
from urllib.request import urlopen
from xml.etree.ElementTree import parse
import re
# from .Article import Article
from Article import Article #for testing seperately
# from .categories import fox_categories
from categories import fox_categories
URL = 'https://moxie.foxnews.com/feedburner/latest.xml'
# TODO: combine with cnnScraper
DOMAIN_1 = "foxnews.com/taxonomy"
DOMAIN_2 = "foxnews.com/section-path"


def loadRSS():
    return urlopen(URL)

#Parses xml for articles that have a title, description, link, date, and url
def parseXML(respHTML):
    respXML = parse(respHTML)
    articles = []

    for item in respXML.iterfind('./channel/item'):
        article = {}
        article["publisher"] = "fox"
        title = item.findtext('title')
        if title:
            article["title"] = str(title)
            #article["title_tokens"] = filterString(str(title))
        else:
            continue

        description = item.findtext('description')
        if description:
            article["description"] = str(description)
            #article["description_tokens"] = filterString(str(description.group()))
        else:
            continue

        category_set = set()
        for categoryTag in item.findall('category'):
            domain = categoryTag.get('domain')
            if (domain == DOMAIN_1) or (domain == DOMAIN_2):
                category = processCategory(categoryTag.text)
                if category:
                    category_set.add(category)
        article["categories"] = category_set

        link = item.findtext('link')
        if link:
            article["url"] = str(link)
        else:
            continue

        pubDate = item.findtext('pubDate')
        if pubDate:
            article["date"] = str(pubDate)
        else:
            continue

        imgURL_group = item.find('{http://search.yahoo.com/mrss/}group')
        if imgURL_group is not None:
            imgURL = imgURL_group.find('{http://search.yahoo.com/mrss/}content')
            if imgURL is not None:
                article["imageURL"] = imgURL.attrib.get('url')
            else:
                continue
        else:
            continue

        articles.append(Article.from_dict(article))
    return articles

# TODO: Sorensen-Dice to get torken scores for grouping
    # TODO: Tokenize Titles, Descriptions too?

# extracts the category from the article's url
# TODO: make this safer: could easily break if url's change,
# check category against list of valid category names to make
# sure a proper category was recorded.
def processURL(url):
    splitURL = url.split("/")
    if len(splitURL) == 5:
        category = splitURL[3]
        return category
    return


def processCategoryOld(category):
    # print(category)
    split_category = category.split("/")
    if split_category[1] in fox_categories:
        return fox_categories[split_category[1]]
    return

def processCategory(category):
    split_category = category.split("/")
    if split_category[0] == "fox-news":
        if split_category[1] in fox_categories:
            return fox_categories[split_category[1]]
    return

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

#CHANGE to recursive print 
def betterPrint(xmlTree):
    root = xmlTree.getroot()
    print(f'root: {root.tag}')
    for child in root:
        print(f'\t{child.tag}')
        for grandChild in child:
            print(f'\t\t{grandChild.tag}')
            for greatGrandChild in grandChild:
                print(f'\t\t\t{greatGrandChild.tag}')
                for greatGreatGrandChild in greatGrandChild:
                    print(f'\t\t\t\t{greatGreatGrandChild.tag}')

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
    articles = []
    for url in rssDic['fox']:
        articles.append(parseXML(loadRSS()))
    #printXMLtree(parse(loadRSS()))
    #betterPrint(parse(loadRSS()))
    #printParsedArticles(articles)
    #return parseXML(loadRSS())
    return articles

def processURL(url):
    splitURL = url.split("/")
    if len(splitURL) == 5:
        category = splitURL[3]
        return category
    return

def getArticles():
    articles = []
    for url in rssDic['fox']:
        feed = feedparser.parse(url)
        #print(feed.entries[0].tags)
        for item in feed.entries:
            article = {}
            try:
                article["publisher"] = "cnn"
                article["title"] = item.title
                article["date"] = item.published
                article["description"] = item.summary
                article["imageURL"] = item.media_content[0]['url']
                article["url"] = item.link
                category_set = set()
                for category in item.tags:
                    category = processCategory(category.term)
                    if category:
                        category_set.add(category)
                if (category_set is set()):
                    continue
                article["categories"] = category_set
            except (AttributeError, KeyError):
                continue
            articles.append(Article.from_dict(article))
    return [*set(articles)]  # removes duplicates


print(getArticles())
#print(getArticles())
'''
printParsedArticles(articles)
print("number of articles: ", len(articles))
print("bytes: ", sys.getsizeof(articles))
'''

#getArticles()
