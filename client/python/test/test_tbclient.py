import unittest
from requests import ConnectionError

from helper import Helper
from tensorboard_http_api.tbclient import TBClient


class TBClientTestSuite(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TBClientTestSuite, self).__init__(*args, **kwargs)

    def test_init(self):
        h = Helper()
        TBClient("localhost", 8889)
        h.kill_remove()

    def test_init_connect_to_wrong(self):
        self.failUnlessRaises(ConnectionError, TBClient, "not_open", 8889)

    def test_add_scalar(self):
        self.

if __name__ == '__main__':
    unittest.main()
