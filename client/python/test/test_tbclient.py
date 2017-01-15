import unittest
import time

from helper import Helper
from tensorboard_http_api.tbclient import TBClient


class TBClientTestSuite(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TBClientTestSuite, self).__init__(*args, **kwargs)

    def test_init(self):
        TBClient()

    def test_init_wrong_localhost(self):
        self.failUnlessRaises(ValueError, TBClient, "not_open", 8889)

    def test_init_wrong_port(self):
        self.failUnlessRaises(ValueError, TBClient, "localhost", 123412341234)

    def test_add_scalar(self):
        tbc = TBClient()
        data = [time.clock(), 1, 2]
        tbc.add_scalar("foo", "bar", data)

    def test_add_scalar_less_data(self):
        tbc = TBClient()
        data = []
        self.failUnlessRaises(AssertionError, tbc.add_scalar,
                              "foo", "bar", data)

    # TODO These should really be tested singularly...
    def test_add_scalar_wrong_data(self):
        tbc = TBClient()
        data = ["lol", "lulz", "lelz"]
        self.failUnlessRaises(ValueError, tbc.add_scalar,
                              "foo", "bar", data)

    def test_add_scalar_wrong_experiment(self):
        tbc = TBClient()
        data = [time.clock(), 1, 2]
        self.failUnlessRaises(ValueError, tbc.add_scalar,
                              "", "bar", data)

    def test_add_scalar_wrong_variable(self):
        tbc = TBClient()
        data = [time.clock(), 1, 2]
        self.failUnlessRaises(ValueError, tbc.add_scalar,
                              "foo", "", data)

    def setUp(self):
        self.h = Helper()

    def tearDown(self):
        self.h.kill_remove()
        self.h = None

if __name__ == '__main__':
    unittest.main()
