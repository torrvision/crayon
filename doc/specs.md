API specification
============

## API version
  * GET `/`
    * Check that the server runs properly and return running version
    * return: a string containing the running version of the server

## Experience management
  * GET `/data`
    * Get the list of running experiments
    * return: a json list of name of all the running experiments

  * GET `/data?xp=foo`
    * Get the informations about the experiment `foo`
    * return: a json dictionnary with the following entries:
      * `scalars`: the name of all the scalar data entries
      * `histograms`: the name of all the histogram data entries

  * POST `/data`
    * Add a new experiment
    * post content: a string with the name of the new experiment

  * DELETE '/data?xp=foo'
    * Delete the experiment named `foo`. Impossible to cancel!

## Scalar data
  * POST `/data/scalars?xp=foo&name=bar`
    * Adds a new scalar point in the experience `foo` for the scalar named `bar`
    * param:
      * `xp`: the considered experience
      * `name`: the name of the scalar metric we want to add a value to
    * post content: a json with a single list containing 3 values:
      * wall_time of the measure
      * step of the measure
      * value

  * GET `/data/scalars?xp=foo&name=bar`
    * Get the values for the scalar named `bar` in the experience `foo`
    * return: a json with a list with one entry per value logged.Each entry is a list containing 3 values:
      * wall_time of the measure
      * step of the measure
      * value

## Histogram data
  * POST `/data/histograms?xp=foo&name=bar&tobuild=True`
    * Adds a new histogram in the experience `foo` for the scalar named `bar`
    * param:
      * `xp`: the considered experience
      * `name`: the name of the scalar metric we want to add a value to
      * `tobuild`: if true, the post content should be a list, otherwise the histogram
    * post content: a json containing a list of 3 elements:
      * wall time of the measure
      * step of the measure
      * the histogram:
        * if `tobuild`=true: a single list containing all the values that will be converted to an histogram
        * if `tobuild`=false: json containing a dictionary with the following keys:
          * `min`: the minimum value
          * `max`: the maximum value
          * `num`: the number of entries
          * `bucket_limit`: a list of `len` elements containing the (right) limit for each bucket
          * `bucket`: a list of `len` elements containing the count for each bucket
          * `sum` (optionnal): the sum of all the values
          * `sum_squares` (optionnal): the squared sum of all the values

  * GET `/data/histograms?xp=foo&name=bar`
    * Get the values for the histogram named `bar` in the experience `foo`
    * return: a json containing:
```
      [
        [
          1443871386.185149, # wall_time
          235166,            # step
          [
            -0.66,           # minimum value
            0.44,            # maximum value
            8.0,             # number of items in the histogram
            -0.80,           # sum of items in the histogram
            0.73,            # sum of squares of items in the histogram
            [-0.68, -0.62, -0.292, -0.26, -0.11, -0.10, -0.08, -0.07, -0.05,
            -0.0525, -0.0434, -0.039, -0.029, -0.026, 0.42, 0.47, 1.8e+308],
                            # the right edge of each bucket
          [0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0,
            1.0, 0.0]        # the number of elements within each bucket
          ]
        ]
      ]
```

## Backup data
  * GET `/backup?xp=foo`
    * Return a zip file containing all the datas for the experiment `foo`
    * param:
      * `xp`: the experiment to backup

  * POST `/backup?xp=foo&force=True`
    * Drop all current datas for the experiment `foo` and replace them with the state contained in the zip
    * param:
      * `xp`: the experiment to replace
      * `force`: has to be set to 1 to be able to delete the old experiment
    * post content: a zip file coming from the backup GET request
