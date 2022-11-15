from trends.Trend import Trend

class TrendsAgg(object):
    def __init__(self, last500):
        self.last500 = last500

    @staticmethod
    def from_dict(source):
        last500_object_list = []
        if source:
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
