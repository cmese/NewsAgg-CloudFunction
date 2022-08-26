# TODO: convert to data class
class Article(object):
    def __init__(self, title, date, description,
                 url, imageURL, publisher, categories):
        self.title = title
        self.date = date
        self.description = description
        self.url = url
        self.imageURL = imageURL
        self.publisher = publisher
        self.categories = categories

    @staticmethod
    def from_dict(source):
        article = Article(
            source[u'title'],
            source[u'date'],
            source[u'description'],
            source[u'url'],
            source[u'imageURL'],
            source[u'publisher'],
            set(source[u'categories'])
        )
        return article

    def to_dict(self):
        dest = {
            u'title': self.title,
            u'date': self.date,
            u'description': self.description,
            u'url': self.url,
            u'imageURL': self.imageURL,
            u'publisher': self.publisher,
            u'categories': list(self.categories)
        }
        return dest

    def __eq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return(
            f'\n    Article(\n'
            f'\t\ttitle={self.title}\n'
            # f'\t\tdate={self.date}\n'
            # f'\t\tdescription={self.description}\n'
            # f'\t\turl={self.url}\n'
            # f'\t\timageURL={self.imageURL}\n'
            f'\t\tpublisher={self.publisher}\n'
            f'\t\tcategories={self.categories}\n'
            f'    )'
        )
