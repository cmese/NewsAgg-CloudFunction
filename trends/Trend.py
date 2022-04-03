#TODO:convert to data class 
#Trend class 
class Trend(object):
    def __init__(self, name, category, articles=[]):
        self.name = name
        self.category = category
        self.articles = articles

    @staticmethod
    def from_dict(source):
       trend = Trend(source[u'name'], source[u'category'], source[u'articles'])
       return trend

    def to_dict(self):
        dest = {
            u'name': self.name,
            u'category': self.category,
            u'articles': self.articles
        }
        return dest

    def __eq__(self, other):
        return self.name == other.name and set(self.articles) == set(other.articles)

    def __repr__(self):
        return(
            f'\nTREND(\n'
                f'  name={self.name}\n'
                f'  category={self.category}\n'
                f'  articles={self.articles}\n'
            f')'
        )

