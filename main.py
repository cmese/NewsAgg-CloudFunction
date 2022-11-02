from google.cloud import firestore
from trends.gTrends import getDailyTrends
from mainScraper import scrape
from matcher import match
from trends.Trend import Trend
from genScraper import genScraper
# from scraperURLs import urlDic

# This os import solves weird DNS error:
'''
google.api_core.exceptions.RetryError: Deadline of 300.0s exceeded while calling target function, last exception: 503 DNS resolution failed for firestore.googleapis.com: C-ares status is not ARES_SUCCESS qtype=AAAA name=firestore.googleapis.com is_balancer=0: Could not contact DNS servers
'''
import os
os.environ['GRPC_DNS_RESOLVER'] = 'native'


class TrendsAgg(object):
    def __init__(self, last500=[]):
        self.last500 = last500

    @staticmethod
    def from_dict(source):
        last500_object_list = [Trend.from_dict(
            trend) for trend in source[u'last500']]
        return TrendsAgg(last500_object_list)

    def to_dict(self):
        last500_dict_list = [trend.to_dict() for trend in self.last500]
        dest = {
            u'last500': last500_dict_list
        }
        return dest

    def __repr__(self):
        return(
            f'\nLAST500(\n'
            f' {self.last500}\n'
            f')'
        )


def main():
    db = firestore.Client()
    trendsAgg_doc_ref = db.collection(u'trendsAgg').document(u'recentTrends')
    doc_dict = trendsAgg_doc_ref.get().to_dict()
    # doc_dict = trendsAgg_doc_ref.get()
    # print("\ndoc_dict:\n", doc_dict)
    if doc_dict:
        temp_dic = {}
        trends_agg = TrendsAgg.from_dict(doc_dict)
        last500_list = trends_agg.last500
        # last500_list = doc_dict['last500']
        # ----------------------------------------
        genScraper()
        # ----------------------------------------
        articles = scrape()
        if last500_list and articles:
            # print("Last500_list before anything happens:\n", last500_list)
            for trend in last500_list:
                # prevTrend = Trend.from_dict(trend)
                # temp_dic[prevTrend.name] = prevTrend
                temp_dic[trend.name] = trend
        else:
            return

        for google_trend in getDailyTrends():
            temp_dic.setdefault(google_trend)

        # print("Scraped articles:\n", articles)
        # print("Temp_dic (previous trends + current google trends before matching): \n", temp_dic)

        matchedTrends = match(articles, temp_dic.keys())  # change this to trends, not just keys. otherwise you can lose old articles when matching very old previous trends. which could move the popped trend bit to the matcher function....or do we actually wanna do this? An old trend might have the same trend name but not necessarily be about the same thing so the articles might be different......hmmmmm maybe we shouuld just keep this like so
        #print('matched trends:\n', matchedTrends)
        for matched_trend in matchedTrends:
            if temp_dic[matched_trend.name] is None:  # new trend with new articles
                last500_list.insert(0, matched_trend)
            # previous trend with new articles
            elif temp_dic[matched_trend.name] != matched_trend:
                popped_trend = last500_list.pop(
                    last500_list.index(temp_dic[matched_trend.name]))
                for article in matched_trend.articles:
                    if article not in popped_trend.articles:
                        popped_trend.articles.insert(0, article)
                        if len(popped_trend.articles) > 10:
                            popped_trend.articles = popped_trend.articles[:-1]
                last500_list.insert(0, popped_trend)
            '''
            else: #matched trend but its a previous trend with the same articles
                #should this get popped to the front anyway? current answer: nahhhhhhh
            '''
            if len(last500_list) > 500:
                last500_list = last500_list[:-1]
            '''
            if temp_dic[matched_trend.name] is None or temp_dic[matched_trend.name] != matched_trend:
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
            '''
        #print("Last500_list after matching:\n", last500_list)
        trends_agg.last500 = last500_list
        print(
            "Last500_list BEFORE repacking for firestore:\n",
            trends_agg,
            "\n\n"
        )
        #print("Last500_list AFTER repacking for firestore:\n", trends_agg.to_dict())
        '''
        trendsAgg_doc_ref.set({
            u'last500': last500_list
        })
        '''
        #trendsAgg_doc_ref.set(trends_agg.to_dict())


if __name__ == "__main__":
    main()
