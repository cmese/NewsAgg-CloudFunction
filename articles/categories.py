'''
fox news will have multiple categories per article. When a trend is made and
the articles are added to it, compare all the categories. If there is a tie,
split the trend into two trends with the categorically appropriate articles
If a trend matches to only 1 article and that article has a tie in categories,
use the section path only
'''
fox_categories = {
    'world':'world',
    'weather':'world',
    'us':'us',
    'politics':'politics',
    'entertainment':'entertainment',
    'tech':'sci-tech',
    'science':'sci-tech',
    'lifestyle':'lifestyle',
    'travel':'lifestyle',
    'health':'lifestyle',
    'style-and-beauty':'lifestyle',
    'great-outdoors':'lifestyle',
    'food-drink':'lifestyle',
    'sports':'sports',
    'auto':'auto',
    'business':'business', #missing, foxbusiness
}

cnn_categories = {
    'sports':'sports', #missing, cnn has bleacher report 
    'travel':'lifestyle', #different index 
    'health':'lifestyle',
    'style':'lifestyle', #different index
    'politics':'politics',
    'us':'us',
    'world':'world',
    'europe':'world',
    'africa':'world',
    'americas':'world',
    'asia':'world',
    'australia':'world',
    'china':'world',
    'india':'world',
    'middleeast':'world',
    'uk':'world',
    'energy':'world',
    'opinions':'world',
    'weather':'world',
    'business':'business',
    'economy':'business',
    'investing':'business',
    'media':'world',
    'homes':'business',
    'success':'business',
    'perspectives':'business',
    'tech':'sci-tech',
    'entertainment':'entertainment',
    'cars':'auto',
}

