from google.cloud import firestore
from trends.gTrends import getDailyTrends
from articles.mainScraper import scrape
from matcher import match
from trends.Trend import Trend
#from scraperURLs import urlDic


def main():
    db = firestore.Client()
    trendsAgg_doc_ref = db.collection(u'trendsAgg').document(u'recentTrends')
    doc_dict = trendsAgg_doc_ref.get().to_dict()
    print("\ndoc_dict:\n", doc_dict)
    if doc_dict:
        temp_dic = {}
        last500_list = doc_dict['last500']
        articles = scrape()
        if last500_list and articles:
            for trend in last500_list:
                prevTrend = Trend.from_dict(trend)
                print("prevTrend: ", prevTrend)
                temp_dic[prevTrend.name] = prevTrend
        else:
            return

        for google_trend in getDailyTrends():
            temp_dic.setdefault(google_trend)

        matchedTrends = match(articles, temp_dic.keys())
        print('matched trends: ', matchedTrends)
        for matched_trend in matchedTrends:
            if temp_dic[matched_trend.name] != matched_trend:
                try:
                    #old trend with new articles
                    popped_match = last500_list.pop(last500_list.index(temp_dic[matched_trend.name]))
                    for article in matched_trend.articles:
                        if article not in popped_match.articles:
                            popped_match.articles.insert(0, article)
                            if len(popped_match.articles) > 10:
                                popped_match.articles = popped_match.articles[:-1]
                    last500_list.insert(0, popped_match)
                except ValueError:
                    #new trend with new articles  
                    last500_list.insert(0, matched_trend)
                if len(last500_list) > 500:
                    last500_list = last500_list[:-1]
        trendsAgg_doc_ref.set({
            u'last500': last500_list
        })

if __name__ == "__main__":
    main()
