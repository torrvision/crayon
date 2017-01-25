# [`pycrayon`](https://pypi.python.org/pypi/pycrayon)

This is the python client for the crayon package.

## Install

* From pip:
```bash
$ pip install pycrayon
```

* From source:
```bash
$ python setup.py install
```

## Testing

Run:

```bash
$ python -m unittest discover
```

## Usage example

```python
from pycrayon import CrayonClient
import time

# Connect to the server
cc = CrayonClient(hostname="server_machine_address")

# Create a new experiment
foo = cc.create_experiment("foo")

# Send some scalar values to the server
foo.add_scalar_value("accuracy", 0, wall_time=11.3)
foo.add_scalar_value("accuracy", 4, wall_time=12.3)
# You can force the time and step values
foo.add_scalar_value("accuracy", 6, wall_time=13.3, step=4)

# Get the datas sent to the server
foo.get_scalar_values("accuracy")
#>> [[11.3, 0, 0.0], [12.3, 1, 4.0], [13.3, 4, 6.0]])

# backup this experiment as a zip file
filename = foo.to_zip()

# delete this experiment from the server
cc.remove_experiment("foo")
# using the `foo` object from now on will result in an error

# Create a new experiment based on foo's backup
bar = cc.create_experiment("bar", zip_file=filename)

# Get the data points for this experiment
bar.get_scalar_list()
#>> ["accuracy"]

# Get the datas for this experiment
foo.get_scalar_values("accuracy")
#>> [[11.3, 0, 0.0], [12.3, 1, 4.0], [13.3, 4, 6.0]])
```

## Complete API

### `CrayonClient`

* Creation: `CrayonClient(hostname="localhost", port=8889)`
  * Create a client object and connect it to the server at address `hostname` and port `port`.

* `get_experiment_list()`
  * Returns a list of string containing the name of all the experiments on the server.

* `create_experiment(xp_name, zip_file=None)`
  * Creates a new experiment with name `xp_name` and returns a `CrayonExperiment` object.
  * If `zip_file` is provided, this experiment is initialized with the content of the zip file (see `CrayonExperiment.to_zip` to get the zip file).

* `open_experiment(xp_name)`
  * Opens the experiment called `xp_name` that already exist on the server.

* `remove_experiment(xp_name)`
  * Removes the experiment `xp_name` from the server.
  * WARNING: all the elements in this experiment are definitively lost!


### `CrayonExperiment`

* Creation: can only be created by the `CrayonClient`

* `get_scalar_list()`
  * Returns a list of string containing the name of all the scalar values in this experiment.

* `add_scalar_value(name, value, wall_time=-1, step=-1`
  * Adds a new point with value `value` to the scalar plot named `name`.
  * If not specified, the `wall_time` will be set to the current time and the `step` to the step of the previous point with this name plus one (or `0` if its the first point with this name).

* `add_scalar_batch(data, wall_time=-1, step=-1`
  * Add multiple points at the same times where `data` is a dictionary where each key is a scalar name and the associated value the value to add for this scalar plot.
  * `wall_time` and `step` are handled the same as for `add_scalar_value` for each entry independently.

* `get_scalar_values(name)`
  * Return a list with one entry for each point added for this scalar plot.
  * Each entry is a list containing [wall_time, step, value]. 

* `get_histogram_list()`
  * Returns a list of string containing the name of all the histogram values in this experiment.

* `add_histogram_value(name, hist, tobuild=False, wall_time=-1, step=-1`
  * Adds a new point with value `hist` to the histogram plot named `name`.
  * If `tobuild` is `False`, `hist` should be a dictionary containing: `{"min": minimum value, "max": maximum value, "num": number of items in the histogram, "bucket_limit": a list with the right limit of each bucket, "bucker": a list with the number of element in each bucket, "sum": optional, the sum of items in the histogram, "sum_squares": optional, the sum of squares of items in the histogram}`.
  * If `tobuild` if `True`, `hist` should be a list of value from which an histogram is going to be built.
  * If not specified, the `wall_time` will be set to the current time and the `step` to the step of the previous point with this name plus one (or `0` if its the first point with this name).

* `get_histogram_values(name)`
  * Return a list with one entry for each point added for this histogram plot.
  * Each entry is a list containing [wall_time, step, hist].
  * Where each `hist` is a dictionary similar to the one specified above.

* `to_zip(filename=None)`
  * Retrieve all the datas from this experiment from the server and store it in `filename`. If `filename` is not specified, it is saved in the current folder.
  * Returns the name of the file where the datas have been saved.
  * This file can then be used to recreate a new experiment with the exact same content as this one.

