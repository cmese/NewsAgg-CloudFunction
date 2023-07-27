from scrapers.scraper_cnn import scraper_cnn
from scrapers.scraper_fox import scraper_fox
from scrapers.scraper_cnbc import scraper_cnbc
from scrapers.scraper_nyt import scraper_nyt

from articles.Article import Article
from trends.Trend import Trend
from trends.gTrends import getDailyTrends
from filter import filterString2, filter_string3, process_text
from sim_scorers import getJaccardScore
from collections import OrderedDict, deque

import yake
from articles.categories import categories

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import pprint
import pandas as pd

kw_extractor = yake.KeywordExtractor()
omit_columns = ['text', 'processed_text']

def update_articles_trends_2(prev_trends_array):

    ###################################################################################
    #deq_trends = deque(prev_trends_array) # for popping / pushing newest stuff back to the front of the list
    print(len(prev_trends_array))
    for i in range(5):
        pprint.pprint(prev_trends_array[i])

    trends_feed_ordered_dict = OrderedDict([(trend['name'], trend) for trend in prev_trends_array])
    #pprint.pprint(trends_feed_ordered_dict)

    current_trends_keywords = list(OrderedDict.fromkeys([trend['name'] for trend in prev_trends_array] + [trend_string for trend_string in getDailyTrends()])) # need to maintain order for keyword_indices array below
    processed_keywords_list = [filterString2(keyword) for keyword in current_trends_keywords]

    #scraper_objs = [scraper_fox]
    scraper_objs = [scraper_nyt,
                    scraper_cnn,
                    scraper_fox,
                    scraper_cnbc]
    # initialize a news site's scraper object
    # this also builds the site with newspaper3k
    scraper_objs_built = [scraper() for scraper in scraper_objs]
    for scraper in scraper_objs_built:
        print("ARTICLES #: ", scraper.built_site.size())

    # for each built site's scraper object, scrape each article
    for scraper in scraper_objs_built:
        scraped_articles_list = []
        #df_articles = pd.DataFrame(columns=['publisher', 'url', 'title', 'date', 'description', 'text', 'imageURL', 'categories'])
        for article in scraper.built_site.articles:
            scrape2(scraper, article, scraped_articles_list)
        
        if len(scraped_articles_list) == 0:
            print("ZERO scraped articles from ", scraper.publisher)
            break

        #scraped articles list should be populated now, convert to dataframe
        df_articles = pd.DataFrame(scraped_articles_list)
        print(df_articles)

        # process articles, remove stopwords, punc, etc
        df_articles['processed_text'] = df_articles.apply(process_text, axis=1)

        # vectorize the articles with TF-IDF
        vectorizer = TfidfVectorizer(stop_words=None, max_df=0.5, min_df=2, max_features=1000)
        X = vectorizer.fit_transform(df_articles['processed_text'])


        # cosine similarity between each processed article vector and the trend keyword vector
        keyword_vector = vectorizer.transform(processed_keywords_list)
        similarities = cosine_similarity(X, keyword_vector)

        # similarity threshold, any article above this gets added to that trend's article list
        threshold = 0.25
        print("******************************SIMS MATRIX********************************")
        #pprint.pprint(similarities)
        # loop through keywords and group nonduplicate articles with similarities above the threshold
        for keyword_index, keyword in enumerate(processed_keywords_list):
            full_trend_keyword = current_trends_keywords[keyword_index]
            keyword_sims = similarities[:, keyword_index]
            sim_article_indices = [index for index, similarity in enumerate(keyword_sims) if similarity > threshold]
            for article_index in sim_article_indices:
                new_article_row = df_articles.iloc[article_index]
                most_important_keywords = kw_extractor.extract_keywords(new_article_row['text'] + new_article_row['description'] + new_article_row['title'])
                most_important_keywords_list = [filter_string3(keyword[0]) for keyword in most_important_keywords] 
                article_categories = [categories[x] for x in most_important_keywords_list if x in categories] 
                
                new_article = new_article_row.loc[~new_article_row.index.isin(omit_columns)].to_dict()
                new_article['categories'] = article_categories
                # if existing trend, push article to the front of the articles list
                if full_trend_keyword in trends_feed_ordered_dict:
                    current_articles_list = trends_feed_ordered_dict[full_trend_keyword]['articles']
                    if not is_duplicate_article(current_articles_list, new_article):
                        trends_feed_ordered_dict[full_trend_keyword]['articles'].insert(0, new_article)
                        trends_feed_ordered_dict[full_trend_keyword]['articles'][:10]
                        trends_feed_ordered_dict.move_to_end(full_trend_keyword, last=False)
                else:
                    trends_feed_ordered_dict[full_trend_keyword] = {'name': full_trend_keyword, 'categories': [], 'articles': [new_article]}
                    trends_feed_ordered_dict.move_to_end(full_trend_keyword, last=False)
                current_categories = trends_feed_ordered_dict[full_trend_keyword]['categories']
                trends_feed_ordered_dict[full_trend_keyword]['categories'] = [*set(article_categories + current_categories)]
                pprint.pprint(trends_feed_ordered_dict[full_trend_keyword]['name'])
    print("\n------------------------------------------------------------------------\n")
    print("\n------------------------------------------------------------------------\n")
    print("\n------------------------------------------------------------------------\n")
    print("\n------------------------------------------------------------------------\n")
    print("\n------------------------------------------------------------------------\n")
    #pprint.pprint(trends_feed_ordered_dict)
    new_list = list(trends_feed_ordered_dict.values())

    for i in range(5):
        pprint.pprint(new_list[i])
    print(len(new_list))
    return new_list[:500]


        # group articles to keywords
        # for i, row_article in df_articles.iterrows():
        #     keyword_indices = [index for index, similarity in enumerate(similarities[i]) if similarity > threshold]
        #     for keyword_index in keyword_indices:
        #         update_main_list(deq_trends, keyword_index, row_article.to_dict())
                #trends_dic[keywords_list[keyword_index]].append(article)


    #####################################################################################

def is_duplicate_article(articles, new_article):
    for article in articles:
        if article['url'] == new_article['url']:
            return True
    return False
        


def update_lists(deq_trends, keyword_index, article_dict):
    updated_trend = deq_trends.pop(keyword_index)
    updated_trend['articles'].insert(0, article_dict)
    updated_trend['articles'] = updated_trend['articles'][:10]
    deq_trends.appendleft(updated_trend)
    #problem: need to maintain order of deq_trends AND keyword_indices AND similarities columns


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


def scrape2(scraper, article_extract, scraped_articles_list):
    article_dic = {}
    try:
        article_extract.download()
        article_extract.parse()

        article_dic["publisher"] = scraper.getPublisher()
        article_dic["url"] = scraper.getArticleURL(article_extract)
        article_dic["title"] = scraper.getTitle(article_extract)
        article_dic["date"] = scraper.getDate(article_extract)
        article_dic["description"] = scraper.getDescription(article_extract)
        article_dic["text"] = scraper.getText(article_extract)
        article_dic["imageURL"] = scraper.getImageURL(article_extract)
        #article_dic["categories"] = scraper.getCategories(article_extract)
        scraped_articles_list.append(article_dic)
    except:
        pass


