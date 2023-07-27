from google.cloud import firestore
from matcher import update_articles_trends_2
from TrendsAgg import TrendsAgg
import pprint
import pandas as pd
import gc

# This os import solves weird DNS error:
'''
google.api_core.exceptions.RetryError: Deadline of 300.0s exceeded while calling target function, last exception: 503 DNS resolution failed for firestore.googleapis.com: C-ares status is not ARES_SUCCESS qtype=AAAA name=firestore.googleapis.com is_balancer=0: Could not contact DNS servers
'''
import os
os.environ['GRPC_DNS_RESOLVER'] = 'native'


def main():
    # fetch current agg from cloud firestore document
    db = firestore.Client()
    trendsAgg_doc_ref = db.collection(u'trendsAgg').document(u'recentTrends')
    doc_dict = trendsAgg_doc_ref.get().to_dict()

    # doc_dict = 
    #   { last500 : [] }

    if not doc_dict:
        print("doc_dict is blank")
        doc_dict = {}

    print("Starting scraper and matcher......")

    last500_list = doc_dict['last500']

    #trends_agg = TrendsAgg.from_dict(doc_dict)
    #print(f"Total trends in current aggregator: {len(trends_agg.last500)}")

    # update trends_agg last500 list
    ### trends_agg.last500 = update_articles_trends(trends_agg)
    
    new_trends_agg = { 'last500' : update_articles_trends_2(last500_list) }


    #print("Updated Trends Agg: ")
    #pprint.pprint(new_trends_agg)
    #print(f"Total trends in updated aggregator: {len(new_trends_agg['last500'])}")

    # update cloud firestore document with new agg list
    # trendsAgg_doc_ref.set(new_trends_agg)


if __name__ == "__main__":
    main()
