# `crayon`

This is the lua client for the crayon package.

## Install

* From luarocks:
```bash
$ luarocks install crayon
```

* From source:
```bash
$ luarocks make
```

## Testing

Run:

```bash
# Start new test server
$ docker run -d -p 7998:8888 -p 7999:8889 --name crayon_lua_test alband/crayon

# Run test script
$ lua(jit) test.lua

# Remove test server
$ docker rm -f crayon_lua_test
```

## Usage example

```lua
local crayon = require("crayon")

--  Connect to the server
local cc = crayon.CrayonClient("server_machine_address")

--  Create a new experiment
local foo = cc:create_experiment("foo")

--  Send some scalar values to the server with their time
foo:add_scalar_value("accuracy", 0, 11.3)
foo:add_scalar_value("accuracy", 4, 12.3)
--  You can force the step value also
foo:add_scalar_value("accuracy", 6, 13.3, 4)

--  Get the datas sent to the server
foo:get_scalar_values("accuracy")
-- >> {
--   1 :
--     {
--       1 : 11.3
--       2 : 0
--       3 : 0
--     }
--   2 :
--     {
--       1 : 12.3
--       2 : 1
--       3 : 4
--     }
--   3 :
--     {
--       1 : 13.3
--       2 : 4
--       3 : 6
--     }
-- }

--  backup this experiment as a zip file
local filename = foo:to_zip()

--  delete this experiment from the server
cc:remove_experiment("foo")
--  using the `foo` object from now on will result in an error

--  Create a new experiment based on foo's backup
local bar = cc:create_experiment("bar", filename)

--  Get the name of all scalar plots in this experiment
bar:get_scalar_names()
-- >> {
--   1 : "accuracy"
-- }

--  Get the data for this experiment
bar:get_scalar_values("accuracy")
-- >> {
--   1 :
--     {
--       1 : 11.3
--       2 : 0
--       3 : 0
--     }
--   2 :
--     {
--       1 : 12.3
--       2 : 1
--       3 : 4
--     }
--   3 :
--     {
--       1 : 13.3
--       2 : 4
--       3 : 6
--     }
-- }

```

## Complete API

### `CrayonClient`

* Creation: `CrayonClient(hostname="localhost", port=8889)`
  * Create a client object and connect it to the server at address `hostname` and port `port`.

* `get_experiment_names()`
  * Returns a list of string containing the name of all the experiments on the server.

* `create_experiment(xp_name, zip_file=nil)`
  * Creates a new experiment with name `xp_name` and returns a `CrayonExperiment` object.
  * If `zip_file` is provided, this experiment is initialized with the content of the zip file (see `CrayonExperiment.to_zip` to get the zip file).

* `open_experiment(xp_name)`
  * Opens the experiment called `xp_name` that already exists on the server.

* `remove_experiment(xp_name)`
  * Removes the experiment `xp_name` from the server.
  * WARNING: all elements from this experiment are permanently lost!

* `remove_all_experiments()`
  * Removes all experiment from the server.
  * WARNING: all elements from all experiments are permanently lost!


### `CrayonExperiment`

* Creation: can only be created by the `CrayonClient`

* `get_scalar_names()`
  * Returns a list of string containing the name of all the scalar values in this experiment.

* `add_scalar_value(name, value, wall_time=-1, step=-1)`
  * Adds a new point with value `value` to the scalar plot named `name`.
  * If not specified, the `wall_time` will be set to the current time and the `step` to the step of the previous point with this name plus one (or `0` if its the first point with this name).

* `add_scalar_dict(data, wall_time=-1, step=-1)`
  * Add multiple points at the same times where `data` is a dictionary where each key is a scalar name and the associated value the value to add for this scalar plot.
  * `wall_time` and `step` are handled the same as for `add_scalar_value` for each entry independently.

* `get_scalar_values(name)`
  * Return a list with one entry for each point added for this scalar plot.
  * Each entry is a list containing [wall_time, step, value].

* `get_histogram_names()`
  * Returns a list of string containing the name of all the histogram values in this experiment.

* `add_histogram_value(name, hist, tobuild=false, wall_time=-1, step=-1)`
  * Adds a new point with value `hist` to the histogram plot named `name`.
  * If `tobuild` is `false`, `hist` should be a dictionary containing: `{"min": minimum value, "max": maximum value, "num": number of items in the histogram, "bucket_limit": a list with the right limit of each bucket, "bucker": a list with the number of element in each bucket, "sum": optional, the sum of items in the histogram, "sum_squares": optional, the sum of squares of items in the histogram}`.
  * If `tobuild` if `True`, `hist` should be a list of value from which an histogram is going to be built.
  * If not specified, the `wall_time` will be set to the current time and the `step` to the step of the previous point with this name plus one (or `0` if its the first point with this name).

* `get_histogram_values(name)`
  * Return a list with one entry for each point added for this histogram plot.
  * Each entry is a list containing [wall_time, step, hist].
  * Where each `hist` is a dictionary similar to the one specified above.

* `to_zip(filename=nil)`
  * Retrieve all the datas from this experiment from the server and store it in `filename`. If `filename` is not specified, it is saved in the current folder.
  * Returns the name of the file where the datas have been saved.
  * This file can then be used to recreate a new experiment with the exact same content as this one.

