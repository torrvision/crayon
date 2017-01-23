import requests
import json
import time
import collections


class CrayonClient(object):

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

    def new_experiment(self, xp, zip_file=None):
        assert(isinstance(xp, str))
        return CrayonExperiment(xp, self, zip_file)


class CrayonExperiment(object):

    def __init__(self, xp, client, zip_file=None):
        self.client = client
        self.xp = xp
        self.scalar_steps = collections.defaultdict(int)
        self.hist_steps = collections.defaultdict(int)

        if zip_file:
            self.init_from_file(zip_file, True)
        else:
            self.init_empty()

    def init_empty(self):
        query = "/data"
        r = requests.post(self.client.url + query, json=self.xp)
        if not r.ok:
            raise ValueError("Something went wrong. Server sent: {}.".format(r.text))

    def init_from_file(self, zip_file, force=False):
        query = "/backup?xp={}&force={}".format(
            self.xp, force)
        fileobj = open(zip_file, 'rb')
        r = requests.post(self.client.url + query, data={"mysubmit": "Go"},
                          files={"archive": ("backup.zip", fileobj)})
        if not r.ok:
            raise ValueError("Something went wrong. Server sent: {}.".format(r.text))

    def add_scalar_value(self, name, value, wall_time=-1, step=-1):
        if wall_time == -1:
            wall_time = time.time()
        if step == -1:
            step = self.scalar_steps[name]
            self.scalar_steps[name] += 1
        else:
            self.scalar_steps[name] = step + 1
        query = "/data/scalars?xp={}&name={}".format(self.xp, name)
        data = [wall_time, step, value]
        r = requests.post(self.client.url + query, json=data)
        if not r.ok:
            raise ValueError("Something went wrong. Server sent: {}.".format(r.text))

    def add_scalars_values(self, data, wall_time=-1, step=-1):
        for name, value in data.iteritems():
            if not isinstance(name, str):
                msg = "Scalar name should be a string, got: {}.".format(name)
                raise ValueError(msg)
            self.add_scalar_value(name, value, wall_time, step)

    def get_scalars(self, name):
        query = "/data/scalars?xp={}&name={}".format(self.xp, name)
        r = requests.get(self.client.url + query)
        if not r.ok:
            raise ValueError("Something went wrong. Server sent: {}.".format(r.text))
        return json.loads(r.text)

    def add_histogram(self, name, hist, tobuild=False, wall_time=-1, step=-1):
        if wall_time == -1:
            wall_time = time.time()
        if step == -1:
            step = self.scalar_steps[name]
            self.scalar_steps[name] += 1
        else:
            self.scalar_steps[name] = step
        if not tobuild and (not isinstance(hist, dict)
                        or not self.check_histogram_data(hist, tobuild)):
            raise ValueError("Data was not provided in a valid format!")
        if tobuild and (not isinstance(hist, list)):
            raise ValueError("Data was not provided in a valid format!")
        query = "/data/histograms?xp={}&name={}&tobuild={}".format(
            self.xp, name, tobuild)
        data = [wall_time, step, hist]
        r = requests.post(self.client.url + query, json=data)
        if not r.ok:
            raise ValueError("Something went wrong. Server sent: {}.".format(r.text))

    def get_histograms(self, name):
        query = "/data/histograms?xp={}&name={}".format(self.xp, name)
        r = requests.get(self.client.url + query)
        if not r.ok:
            raise ValueError("Something went wrong. Server sent: {}.".format(r.text))
        return json.loads(r.text)

    def get_data(self, filename=None):
        query = "/backup?xp={}".format(self.xp)
        r = requests.get(self.client.url + query)
        if not r.ok:
            raise ValueError("Something went wrong. Server sent: {}.".format(r.text))
        if not filename:
            filename = "backup_" + self.xp + "_" + str(time.time())
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
