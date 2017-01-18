import requests
import json
import time


class TBClient(object):

    def __init__(self, hostname="localhost", port=8889):
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
                             " does not appear to be up!")
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
        assert(len(data) == 3)
        query = "/data/scalars?xp={}&name={}".format(xp, name)
        r = requests.post(self.url + query, json=data)
        if not r.ok:
            raise ValueError("Something went wrong.")

    def get_scalars(self, xp, name):
        query = "/data/scalars?xp={}&name={}".format(xp, name)
        r = requests.get(self.url + query)
        if not r.ok:
            raise ValueError("Something went wrong.")
        return json.loads(r.text)

    def add_histogram(self, xp, name, data, tobuild=False):
        assert(len(data) == 3)

        if tobuild and (not isinstance(data[2], dict)
                        or not self.check_histogram_data(data[2], tobuild)):
            raise ValueError("Data was not provided in a valid format!")
        query = "/data/histograms?xp={}&name={}&tobuild={}".format(
            xp, name, tobuild)
        r = requests.post(self.url + query, json=data)
        if not r.ok:
            raise ValueError("Something went wrong.")

    def get_histograms(self, xp, name):
        query = "/data/histograms?xp={}&name={}".format(xp, name)
        r = requests.get(self.url + query)
        if not r.ok:
            raise ValueError("Something went wrong.")
        return json.loads(r.text)

    def set_data(self, xp, zip_file, force=False):
        query = "/backup?xp={}&force={}".format(
            xp, force)
        fileobj = open(zip_file, 'rb')
        r = requests.post(self.url + query, data={"mysubmit": "Go"},
                          files={"archive": ("backup.zip", fileobj)})
        if not r.ok:
            raise ValueError("Something went wrong.")

    def get_data(self, xp, filename=None):
        query = "/backup?xp={}".format(xp)
        r = requests.get(self.url + query)
        if not r.ok:
            raise ValueError("Something went wrong.")
        if not filename:
            filename = "backup_" + xp + "_" + str(time.time())
        out = open(filename + ".zip", "w")
        out.write(r.content)
        out.close()
        return filename + ".zip"

    def check_histogram_data(self, data, tobuild):
        # TODO should use a schema here
        # Note: all of these are sorted already

        expected = ["bucket", "bucket_limit", "max", "min", "num"]
        expected2 = ["bucket", "bucket_limit", "max", "min", "num",
                     "sum"]
        expected3 = ["bucket", "bucket_limit", "max", "min", "num",
                     "sum", "sum_squares"]
        expected4 = ["bucket", "bucket_limit", "max", "min", "num",
                     "sum_squares"]
        ks = tuple(data.keys())
        ks = sorted(ks)
        return (ks == expected or ks == expected2
                or ks == expected3 or ks == expected4)
