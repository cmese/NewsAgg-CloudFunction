from pytrends.request import TrendReq
# from filter import filterString


def getDailyTrends():
    pytrends = TrendReq(hl='en-US', tz=360)  # change to est?
    daily_trends = pytrends.trending_searches(pn='united_states')
    trendsSet = set(daily_trends[0].values)
    # print(trendsSet)
    return trendsSet


def getRealTimeTrends():
    return


# combines daily and realtime trends into one set
def getAllTrends():
    return
