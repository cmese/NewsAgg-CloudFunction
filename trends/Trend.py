#TODO:convert to data class
#Trend class
from articles.Article import Article

class Trend(object):
    def __init__(self, name, categories, articles=[]): #TODO: default empty list can cause weird errors, change this
        self.name = name
        self.categories = categories
        self.articles = articles

    @staticmethod
    def from_dict(source):
        article_object_list = [Article.from_dict(article) for article in source[u'articles']]
        return Trend(source[u'name'], set(source[u'categories']), article_object_list)

    def to_dict(self):
        article_dict_list = [article.to_dict() for article in self.articles]
        dest = {
            u'name': self.name,
            u'categories': list(self.categories),
            u'articles': article_dict_list
        }
        return dest

    def __eq__(self, other):
        return self.name == other.name and self.articles == other.articles

    def __repr__(self):
        return(
            f'\nTREND(\n'
            f'  name={self.name}\n'
            f'  categories={self.categories}\n'
            f'  articles={self.articles}\n'
            f')'
        )
