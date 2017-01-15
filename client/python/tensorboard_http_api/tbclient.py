import requests
import json


class TBClient(object):

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.url = self.hostname + ":" + str(self.port)
        # TODO use urlparse
        if not (self.url.startswith("http://") or
                self.url.startswith("https://")):
            self.url = "http://" + self.url

        # check server is working (not only up).
        try:
            assert(requests.get(self.url).ok)
        except requests.ConnectionError:
            raise ValueError("The server at {}:{}".format(self.hostname,
                                                          self.port) +
                             "does not appear to be up!")
        except AssertionError:
            raise RuntimeError("Something went wrong!" +
                               " Tensorboard may be the problem.")

    def get_experiments(self, xp=None):
        query = "/data"
        r = requests.get(self.url + query)
        if not r.ok:
            experiments = []
        else:
            experiments = json.loads(r.text)
        return experiments

    def add_scalar(self, xp, name, data):
        query = "/data/scalars?xp={}&name={}".format(xp, name)
        r = requests.post(self.url + query, json=data)
        if not r.ok:
            raise ValueError("SOMETHING HORRIBLY WRONG HAS HAPPENED")

    def get_scalars(self, xp, name):
        query = "/data/scalars?xp={}&name={}".format(xp, name)
        r = requests.get(self.url + query)
        if not r.ok:
            raise ValueError("SOMETHING HORRIBLY WRONG HAS HAPPENED")
        return r.text

    def add_histogram(self, xp, name, tobuild, data):
        query = "/data/histograms?xp={}&name={}&tobuild={}".format(
            xp, name, tobuild)
        r = requests.post(self.url + query, json=data)
        if not r.ok:
            raise ValueError("SOMETHING HORRIBLY WRONG HAS HAPPENED")

    def get_histograms(self, xp, name):
        query = "/data/histograms?xp={}&name={}".format(xp, name)
        r = requests.get(self.url + query)
        if not r.ok:
            raise ValueError("SOMETHING HORRIBLY WRONG HAS HAPPENED")
        return r.text

    def set_data(self, xp, force, data):
        query = "/data/backup?xp={}&force={}".format(
            xp, force)
        r = requests.post(self.url + query, json=data)
        if not r.ok:
            raise ValueError("SOMETHING HORRIBLY WRONG HAS HAPPENED")

    def get_data(self, xp):
        query = "/data/backup?xp={}".format(
            xp, force)
        r = requests.get(self.url + query)
        if not r.ok:
            raise ValueError("SOMETHING HORRIBLY WRONG HAS HAPPENED")
        return r.text
