#TODO: convert to data class 
class Article(object):
    def __init__(self, title, date, description,
            url, imageURL, publisher, category):
        self.title = title
        self.date = date
        self.description = description
        self.url = url
        self.imageURL = imageURL
        self.publisher = publisher
        self.category = category

    @staticmethod
    def from_dict(source):
        article = Article(
            source[u'title'],
            source[u'date'],
            source[u'description'],
            source[u'url'],
            source[u'imageURL'],
            source[u'publisher'],
            source[u'category']
        )
        return article

    def to_dict(self):
        dest = {
            u'title' : self.title,
            u'date' : self.date,
            u'description' : self.description,
            u'url' : self.url,
            u'imageURL' : self.imageURL,
            u'publisher' : self.publisher,
            u'category' : self.category
        }
        return dest

    def __eq__(self, other):
        return self.url == other.url

    def __repr__(self):
        return(
            f'\n    Article(\n'
            f'\ttitle={self.title}\n'
            f'\tdate={self.date}\n'
            f'\tdescription={self.description}\n'
            f'\turl={self.url}\n'
            f'\timageURL={self.imageURL}\n'
            f'\tpublisher={self.publisher}\n'
            f'\tcategory={self.category}\n'
            f'    )'
        )
