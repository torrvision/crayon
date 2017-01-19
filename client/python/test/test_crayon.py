import unittest
import time
import os

from helper import Helper
from crayon.crayon import CrayonClient

class CrayonClientTestSuite(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(CrayonClientTestSuite, self).__init__(*args, **kwargs)

    def setUp(self):
        self.h = Helper()

    def tearDown(self):
        self.h.kill_remove()
        self.h = None

    # INIT
    def test_init(self):
        CrayonClient()

    def test_init_wrong_localhost(self):
        self.assertRaises(ValueError, CrayonClient, "not_open", 8889)

    def test_init_wrong_port(self):
        self.assertRaises(ValueError, CrayonClient, "localhost", 123412341234)

    # scalars
    def test_add_scalar(self):
        cc = CrayonClient()
        data = [time.clock(), 1, 2]
        cc.new_experiment("foo")
        cc.add_scalar("foo", "bar", data)

    def test_add_scalar_less_data(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        data = []
        self.assertRaises(AssertionError, cc.add_scalar,
                          "foo", "bar", data)

    # TODO These should really be tested singularly...
    def test_add_scalar_wrong_data(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        data = ["lol", "lulz", "lelz"]
        self.assertRaises(ValueError, cc.add_scalar,
                          "foo", "bar", data)

    def test_add_scalar_wrong_experiment(self):
        cc = CrayonClient()
        data = [time.clock(), 1, 2]
        self.assertRaises(ValueError, cc.add_scalar,
                          "", "bar", data)

    def test_add_scalar_wrong_variable(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        data = [time.clock(), 1, 2]
        self.assertRaises(ValueError, cc.add_scalar,
                          "foo", "", data)

    def test_get_scalars_no_data(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        self.assertRaises(ValueError, cc.get_scalars, "foo", "bar")

    def test_get_scalars_one_datum(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        cc.add_scalar("foo", "bar", [0, 0, 0])
        time.sleep(1)
        self.assertEqual(cc.get_scalars("foo", "bar"), [[0.0, 0, 0.0]])

    def test_get_scalars_two_data(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        cc.add_scalar("foo", "bar", [0, 0, 0])
        cc.add_scalar("foo", "bar", [1, 1, 1])
        time.sleep(1)
        self.assertEqual(cc.get_scalars("foo", "bar"),
                         [[0.0, 0, 0.0], [1.0, 1, 1.0]])

    def test_get_scalars_wrong_experiment(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        cc.add_scalar("foo", "bar", [0, 0, 0])
        time.sleep(1)
        self.assertRaises(ValueError, cc.get_scalars, "", "bar")

    def test_get_scalars_wrong_variable(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        cc.add_scalar("foo", "bar", [0, 0, 0])
        time.sleep(1)
        self.assertRaises(ValueError, cc.get_scalars, "foo", "")

    # Histograms
    def test_add_histogram(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        data = [time.clock(), 1, 2]
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        cc.add_histogram("foo", "bar", [0, 1, data])

    def test_add_histogram_with_sum(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        data = [time.clock(), 1, 2]
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25],
                "sum": 75}
        cc.add_histogram("foo", "bar", [0, 1, data])

    def test_add_histogram_with_sumsq(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        data = [time.clock(), 1, 2]
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25],
                "sum_squares": 5625}
        cc.add_histogram("foo", "bar", [0, 1, data])

    def test_add_histogram_with_sum_sumsq(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        data = [time.clock(), 1, 2]
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25],
                "sum": 75,
                "sum_squares": 2675}
        cc.add_histogram("foo", "bar", [0, 1, data])

    def test_add_histogram_less_data(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        data = {"some data": 0}
        self.assertRaises(AssertionError, cc.add_histogram,
                          "foo", "bar", [data])

    # TODO These should really be tested singularly...
    def test_add_histogram_wrong_data(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        data = ["lolz", "lulz", "lelz"]
        self.assertRaises(ValueError, cc.add_histogram,
                          "foo", "bar", [0, 1, data], True)

    def test_add_histogram_wrong_experiment(self):
        cc = CrayonClient()
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        self.assertRaises(ValueError, cc.add_histogram,
                          "", "bar", [0, 1, data])

    def test_add_histogram_wrong_variable(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        self.assertRaises(ValueError, cc.add_histogram,
                          "foo", "", [0, 1, data])

    def test_get_histograms_no_data(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        self.assertRaises(ValueError, cc.get_histograms, "foo", "bar")

    def test_get_histograms_one_datum(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        cc.add_histogram("foo", "bar", [0, 0, data])
        time.sleep(1)
        self.assertEqual(cc.get_histograms("foo", "bar"),
                         [[0.0, 0,
                           [0.0, 100.0, 3.0, 0.0, 0.0,
                            [10.0, 50.0, 30.0],
                            [5.0, 45.0, 25.0]]]])

    def test_get_histograms_two_data(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        cc.add_histogram("foo", "bar", [0, 0, data])
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        cc.add_histogram("foo", "bar", [1, 1, data])
        time.sleep(1)
        self.assertEqual(cc.get_histograms("foo", "bar"),
                         [[0.0, 0,
                           [0.0, 100.0, 3.0, 0.0, 0.0,
                            [10.0, 50.0, 30.0],
                            [5.0, 45.0, 25.0]]],
                          [1.0, 1,
                           [0.0, 100.0, 3.0, 0.0, 0.0,
                            [10.0, 50.0, 30.0],
                            [5.0, 45.0, 25.0]]]])

    def test_get_histograms_wrong_experiment(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        cc.add_histogram("foo", "bar", [0, 0, data])
        time.sleep(1)
        self.assertRaises(ValueError, cc.get_histograms, "", "bar")

    def test_get_histograms_wrong_variable(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        cc.add_histogram("foo", "bar", [0, 0, data])
        time.sleep(1)
        self.assertRaises(ValueError, cc.get_histograms, "foo", "")

    # Only checks that we get a zip file.
    # TODO open and match data to recorded
    def test_get_data(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        data = [time.clock(), 1, 2]
        cc.add_scalar("foo", "bar", data)
        time.sleep(1)
        filename = cc.get_data("foo")
        os.remove(filename)

    def test_get_data_empty(self):
        cc = CrayonClient()
        self.assertRaises(ValueError, cc.get_data, "foo")

    def test_get_data_wrong_experiment(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        data = [time.clock(), 1, 2]
        cc.add_scalar("foo", "bar", data)
        time.sleep(1)
        self.assertRaises(ValueError, cc.get_data, "not_there")

    # Only checks that we set a zip file.
    def test_set_data(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        data = [time.clock(), 1, 2]
        cc.add_scalar("foo", "bar", data)
        time.sleep(1)
        filename = cc.get_data("foo")
        time.sleep(1)
        cc.set_data("foo", filename, True)
        os.remove(filename)

    def test_set_data_force(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        data = [time.clock(), 1, 2]
        cc.add_scalar("foo", "bar", data)
        time.sleep(1)
        filename = cc.get_data("foo")
        time.sleep(1)
        cc.set_data("foo", filename, True)
        os.remove(filename)

    def test_set_data_wrong_file(self):
        cc = CrayonClient()
        cc.new_experiment("foo")
        self.assertRaises(IOError, cc.set_data, "foo",
                          "random_noise")
