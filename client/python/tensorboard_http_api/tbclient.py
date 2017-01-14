import requests


class TBClient(object):

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        pass

    def get_experiments(self, xp=None):
        pass

    def add_scalar(self, xp, name, data):
        pass

    def get_scalars(self, xp, name):
        pass

    def add_histogram(self, xp, name, tobuild, data):
        pass

    def get_histograms(self, xp, name):
        pass

    def get_data(self, xp):
        pass

    def set_data(self, xp, force, data):
        pass
