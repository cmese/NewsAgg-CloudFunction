from google.cloud import firestore
from matcher import update_articles_trends
from TrendsAgg import TrendsAgg
import pprint
# This os import solves weird DNS error:
'''
google.api_core.exceptions.RetryError: Deadline of 300.0s exceeded while calling target function, last exception: 503 DNS resolution failed for firestore.googleapis.com: C-ares status is not ARES_SUCCESS qtype=AAAA name=firestore.googleapis.com is_balancer=0: Could not contact DNS servers
'''
import os
os.environ['GRPC_DNS_RESOLVER'] = 'native'

def main():
    db = firestore.Client()
    trendsAgg_doc_ref = db.collection(u'trendsAgg').document(u'recentTrends')
    doc_dict = trendsAgg_doc_ref.get().to_dict()

    if doc_dict:
        print("scraping and matching......")
        trends_agg = TrendsAgg.from_dict(doc_dict)
        trends_agg.last500 = update_articles_trends(trends_agg)
        trends_agg = trends_agg.to_dict()
        # trendsAgg_doc_ref.set(trends_agg.to_dict())
        print('----------------------------------------')
        pprint.pprint(trends_agg)
        print(len(trends_agg['last500']))
    else:
        print("Error: doc_dict is blank")


if __name__ == "__main__":
    main()
