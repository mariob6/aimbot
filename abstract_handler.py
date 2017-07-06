import abc


class AbstracHandler(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def handle(self, *kwargs):
        pass

    @staticmethod
    def getMention(user):
        return '<@{0}>'.format(user)
