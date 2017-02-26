import unittest
import time
import os

from .helper import Helper
from pycrayon.crayon import CrayonClient


class CrayonClientTestSuite(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(CrayonClientTestSuite, self).__init__(*args, **kwargs)
        self.test_server_port = 8886
        self.test_tb_port = 8887
        self.container_name = "crayon_test_python"

    def setUp(self):
        self.h = Helper(
            start=True,
            tb_ip=self.test_tb_port,
            server_ip=self.test_server_port,
            name=self.container_name)

    def tearDown(self):
        self.h.kill_remove()
        self.h = None

    # INIT
    def test_init(self):
        CrayonClient(port=self.test_server_port)

    def test_init_wrong_localhost(self):
        self.assertRaises(ValueError, CrayonClient, "not_open",
                          self.test_server_port)

    def test_init_wrong_port(self):
        self.assertRaises(ValueError, CrayonClient, "localhost", 123412341234)

    def test_init_xp_empty(self):
        cc = CrayonClient(port=self.test_server_port)
        self.assertRaises(ValueError, cc.create_experiment, "")

    def test_open_experiment(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        foo.add_scalar_value("bar", 1, step=2, wall_time=0)
        foo = cc.open_experiment("foo")
        foo.add_scalar_value("bar", 3, wall_time=1)
        self.assertEqual(foo.get_scalar_values("bar"),
                         [[0.0, 2, 1.0], [1.0, 3, 3.0]])

    def test_remove_experiment(self):
        cc = CrayonClient(port=self.test_server_port)
        self.assertRaises(ValueError, cc.open_experiment, "foo")
        foo = cc.create_experiment("foo")
        foo.add_scalar_value("bar", 1, step=2, wall_time=0)
        self.assertRaises(ValueError, cc.create_experiment, "foo")
        cc.open_experiment("foo")
        cc.remove_experiment(foo.xp_name)
        self.assertRaises(ValueError, cc.remove_experiment, foo.xp_name)
        foo = cc.create_experiment("foo")

    # scalars
    def test_add_scalar_value(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        foo.add_scalar_value("bar", 2, wall_time=time.clock(), step=1)

    def test_add_scalar_less_data(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        foo.add_scalar_value("bar", 2)

    # TODO These should really be tested singularly...
    def test_add_scalar_wrong_data(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        self.assertRaises(ValueError, foo.add_scalar_value,
                          "bar", "lol")

    def test_add_scalar_wrong_variable(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        self.assertRaises(ValueError, foo.add_scalar_value,
                          "", 2)

    def test_add_scalar_dict(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        data = {"fizz": 3, "buzz": 5}
        foo.add_scalar_dict(data, wall_time=0, step=5)
        data = {"fizz": 6, "buzz": 10}
        foo.add_scalar_dict(data)

    def test_add_scalar_dict_wrong_data(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        data = {"fizz": "foo", "buzz": 5}
        self.assertRaises(ValueError, foo.add_scalar_dict, data)
        data = {3: 6, "buzz": 10}
        self.assertRaises(ValueError, foo.add_scalar_dict, data)

    def test_get_scalar_values_no_data(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        self.assertRaises(ValueError, foo.get_scalar_values, "bar")

    def test_get_scalar_values_one_datum(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        foo.add_scalar_value("bar", 0, wall_time=0, step=0)
        self.assertEqual(foo.get_scalar_values("bar"), [[0.0, 0, 0.0]])

    def test_get_scalar_values_two_data(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        foo.add_scalar_value("bar", 0, wall_time=0, step=0)
        foo.add_scalar_value("bar", 1, wall_time=1, step=1)
        self.assertEqual(foo.get_scalar_values("bar"),
                         [[0.0, 0, 0.0], [1.0, 1, 1.0]])

    def test_get_scalar_values_auto_step(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        foo.add_scalar_value("bar", 0, wall_time=0)
        foo.add_scalar_value("bar", 1, wall_time=1)
        foo.add_scalar_value("bar", 2, wall_time=2, step=10)
        foo.add_scalar_value("bar", 3, wall_time=3)
        self.assertEqual(foo.get_scalar_values("bar"),
                         [[0.0, 0, 0.0], [1.0, 1, 1.0],
                          [2.0, 10, 2.0], [3.0, 11, 3.0]])

    def test_get_scalar_values_wrong_variable(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        foo.add_scalar_value("bar", 0)
        self.assertRaises(ValueError, foo.get_scalar_values, "")

    def test_get_scalar_dict(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        data = {"fizz": 3, "buzz": 5}
        foo.add_scalar_dict(data, wall_time=0, step=5)
        data = {"fizz": 6, "buzz": 10}
        foo.add_scalar_dict(data, wall_time=1)
        self.assertEqual(foo.get_scalar_values("fizz"),
                         [[0.0, 5, 3.0], [1.0, 6, 6.0]])
        self.assertEqual(foo.get_scalar_values("buzz"),
                         [[0.0, 5, 5.0], [1.0, 6, 10.0]])

    def test_get_scalar_names(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        foo.add_scalar_value("fizz", 0, wall_time=0)
        foo.add_scalar_value("buzz", 0, wall_time=0)
        self.assertEqual(sorted(foo.get_scalar_names()),
                         sorted(["fizz", "buzz"]))

    # Histograms
    def test_add_histogram_value(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        foo.add_histogram_value("bar", data, wall_time=0, step=0)
        foo.add_histogram_value("bar", data)

    def test_add_histogram_value_with_sum(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25],
                "sum": 75}
        foo.add_histogram_value("bar", data)

    def test_add_histogram_value_with_sumsq(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25],
                "sum_squares": 5625}
        foo.add_histogram_value("bar", data)

    def test_add_histogram_value_with_sum_sumsq(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25],
                "sum": 75,
                "sum_squares": 2675}
        foo.add_histogram_value("bar", data)

    def test_add_histogram_value_to_build(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        data = [1,2,3,4,5]
        foo.add_histogram_value("bar", data, tobuild=True)

    def test_add_histogram_value_less_data(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        data = {"some data": 0}
        self.assertRaises(ValueError, foo.add_histogram_value,
                          "bar", data)

    # TODO These should really be tested singularly...
    def test_add_histogram_value_wrong_data(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        data = ["lolz", "lulz", "lelz"]
        self.assertRaises(ValueError, foo.add_histogram_value,
                          "bar", data, tobuild=True)

    def test_add_histogram_value_wrong_variable(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        self.assertRaises(ValueError, foo.add_histogram_value,
                          "", data)

    def test_get_histogram_values_no_data(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        self.assertRaises(ValueError, foo.get_histogram_values, "bar")

    def test_get_histogram_values_one_datum(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        foo.add_histogram_value("bar", data, wall_time=0, step=0)
        self.assertEqual(foo.get_histogram_values("bar"),
                         [[0.0, 0,
                           [0.0, 100.0, 3.0, 0.0, 0.0,
                            [10.0, 50.0, 30.0],
                            [5.0, 45.0, 25.0]]]])

    def test_get_histogram_values_two_data(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        foo.add_histogram_value("bar", data, wall_time=0, step=0)
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        foo.add_histogram_value("bar", data, wall_time=1, step=1)
        self.assertEqual(foo.get_histogram_values("bar"),
                         [[0.0, 0,
                           [0.0, 100.0, 3.0, 0.0, 0.0,
                            [10.0, 50.0, 30.0],
                            [5.0, 45.0, 25.0]]],
                          [1.0, 1,
                           [0.0, 100.0, 3.0, 0.0, 0.0,
                            [10.0, 50.0, 30.0],
                            [5.0, 45.0, 25.0]]]])

    def test_get_histogram_values_wrong_variable(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        foo.add_histogram_value("bar", data, wall_time=0, step=0)
        self.assertRaises(ValueError, foo.get_histogram_values, "")

    def test_get_histogram_names(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        data = {"min": 0,
                "max": 100,
                "num": 3,
                "bucket_limit": [10, 50, 30],
                "bucket": [5, 45, 25]}
        foo.add_histogram_value("fizz", data, wall_time=0, step=0)
        foo.add_histogram_value("buzz", data, wall_time=1, step=1)
        self.assertEqual(sorted(foo.get_histogram_names()),
                         sorted(["fizz", "buzz"]))

    # Only checks that we get a zip file.
    # TODO open and match data to recorded
    def test_to_zip(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        foo.add_scalar_value("bar", 2, wall_time=time.time(), step=1)
        filename = foo.to_zip()
        os.remove(filename)

    # Only checks that we set a zip file.
    def test_init_from_file(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        foo.add_scalar_value("bar", 2, wall_time=time.time(), step=1)
        filename = foo.to_zip()
        new = cc.create_experiment("new", filename)
        os.remove(filename)

    def test_set_data_wrong_file(self):
        cc = CrayonClient(port=self.test_server_port)
        self.assertRaises(IOError, cc.create_experiment, "foo",
                          "random_noise")

    def test_backup(self):
        cc = CrayonClient(port=self.test_server_port)
        foo = cc.create_experiment("foo")
        foo.add_scalar_value("bar", 2, wall_time=time.time(), step=1)
        foo.add_scalar_value("bar", 2, wall_time=time.time(), step=2)
        foo_data = foo.get_scalar_values("bar")
        filename = foo.to_zip()

        cc.remove_experiment("foo")

        foo = cc.create_experiment("foo", zip_file=filename)
        new_data = foo.get_scalar_values("bar")
        self.assertEqual(foo_data, new_data)

        new = cc.create_experiment("new", zip_file=filename)
        new_data = new.get_scalar_values("bar")
        self.assertEqual(foo_data, new_data)

        os.remove(filename)
