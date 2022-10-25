import newspaper
import nltk
from nltk.tokenize import word_tokenize
from news_urls import url_dic
# from .Article import Article
from Article import Article  # for testing seperately
# from newspaper import Config, Article, Source
from categories import cnn_categories, fox_categories

# for running seperately
import sys
sys.path.append('..')
from filter import filterString

#date for fox = article_extract.meta_data["dcterms.created"]
#date for nyt, cnn, cnbc - article_extract.publish_date
def scraper():
    articles = []
    for site in url_dic:
        paper = newspaper.build(url_dic[site], language='en', memoize_articles=False)
        print(site)
        print(paper.size())
        article_extract = paper.articles[100]
        # for article_extract in paper.articles:
        try:
            article_extract.download()
            article_extract.parse()
            #print(article_extract.meta_data["dcterms.created"]) #DATE FOR FOX
            print(article_extract.meta_data)
            print("--------------------------------")
            for thing in vars(article_extract):
                print(thing)
            print("--------------------------------")
            article = {}
            article["publisher"] = site
            article["title"] = str(article_extract.title)
            article["date"] = article_extract.publish_date
            article["description"] = article_extract.meta_description
            article["imageURL"] = article_extract.top_image
            article["url"] = article_extract.url
            # article["categories"] = article_extract.tags
            article["categories"] = getCategories(article_extract)
        except:
            continue
        article_obj = Article.from_dict(article)
        if article_obj:
            articles.append(article_obj)
    return [*set(articles)]

#TODO: add article_extract.tags
def getCategories(article):
    article.nlp()
    categories = set()
    if article.keywords:
        for keyword in article.keywords:
            keyword = keyword.lower()
            if keyword in cnn_categories:
                print("keyword found")
                categories.add(cnn_categories[keyword])
            if keyword in fox_categories:
                categories.add(fox_categories[keyword])
                print("keyword found")

    title = word_tokenize(article.title.lower())
    #title = nlp.expunge_punctuations(article.title).lower()
    #description = nlp.expunge_punctuatoins(article.meta_description).lower()
    description = []
    if article.meta_description:
        print("----description before: " + article.meta_description)
        description = filterString(article.meta_description)
        print("----description after: ", description)
    #article_text = article.text.replace('\n', '')
    most_common_words = []
    if article.text:
        print("----article_text before: " + article.text)
        article_text = filterString(article.text)
        print("----article_text after: ", article_text)
        article_text_Dist = nltk.FreqDist(word for word in article_text)
        most_common_words = article_text_Dist.most_common(20)
        print("----most common words: ", most_common_words)
        '''
        for pair in most_common_words:
            (word, freq) = pair
            print(word)
        '''
    # remove_stopwords = nlp.expunge_stopwords(article_text)
    # normalize_text = nlp.expunge_punctuations(remove_stopwords)
    # most_common_words = nlp.get_most_common_words(normalize_text, 10)
    for word in title:
        print("Checking title")
        if word in cnn_categories:
            print("title word found.")
            categories.add(cnn_categories[word])
        if word in fox_categories:
            print("title word found.")
            categories.add(fox_categories[word])
    for word in description:
        print("Checking description")
        if word in cnn_categories:
            categories.add(cnn_categories[word])
        if word in fox_categories:
            categories.add(fox_categories[word])
    for pair in most_common_words:
        (word, freq) = pair
        if word in cnn_categories:
            print("found word in cnn categories")
            categories.add(cnn_categories[word])
        if word in fox_categories:
            print("found word in fox categories")
            categories.add(fox_categories[word])
    #print(len(categories))
    #if len(categories) == 0:
    if not categories:
        categories.add("other")
    print("-----categories:")
    print(categories)
    return list(categories) # TODO: change list / set

articles = scraper()
print(articles)
#for url in newspaper.popular_urls():
#    print(url)
    #paper = newspaper.build(url)
    #print(paper.size())

#print(newspaper.hot())
#print(newspaper.popular_urls())
#from newspaper import Article
