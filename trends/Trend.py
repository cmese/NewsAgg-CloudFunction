#TODO:convert to data class 
#Trend class
from articles.Article import Article

class Trend(object):
    def __init__(self, name, category, articles=[]):
        self.name = name
        self.category = category
        self.articles = articles

    @staticmethod
    def from_dict(source):
        article_object_list = [Article.from_dict(article) for article in source[u'articles']]
        return Trend(source[u'name'], source[u'category'], article_object_list)

    def to_dict(self):
        article_dict_list = [article.to_dict() for article in self.articles]
        dest = {
            u'name': self.name,
            u'category': self.category,
            u'articles': article_dict_list
        }
        return dest

    def __eq__(self, other):
        return self.name == other.name and self.articles == other.articles

    def __repr__(self):
        return(
            f'\nTREND(\n'
                f'  name={self.name}\n'
                f'  category={self.category}\n'
                f'  articles={self.articles}\n'
            f')'
        )

