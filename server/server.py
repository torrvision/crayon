# Flask app server
from flask import Flask, request, json
app = Flask("crayonserver")

# HTTP client to use the tensorboard api
import urllib2

# Server version
__version__ = "0.5"

# Not-supported logging types
not_supported_types = [
  "audio",
  "compressedHistograms",
  "graph",
  "images",
  "meta_graph",
  "run_metadata",
  "firstEventTimestamp"]

# Supported logging types
supported_types = [
  "scalars",
  "histograms"]

# Tensorboard includes
import tensorflow as tf
import bisect
import time

# Backup includes
from os import path
from subprocess import Popen, PIPE
from flask import send_file
import shutil

# Command line arguments
import argparse
parser = argparse.ArgumentParser(description="Backend server for crayon")
parser.add_argument("port", type=int, default=8889,
          help="Port where to listen for incoming datas")
parser.add_argument("backend_reload", type=float, default=1,
          help="How fast is tensorboard reloading its backend")
cli_args = parser.parse_args()

# Delay timer
# We add 1s to make sure all files are loaded from disk
request_delay = cli_args.backend_reload + 1

def to_unicode(experiment):

  assert experiment and isinstance(experiment, basestring)

  return unicode(experiment)

### Tensorboard utility functions
tensorboard_folder = "/tmp/tensorboard/{}"
# Make sure we do not access data too fast
xp_modified = {}
def tb_modified_xp(experiment, modified_type=None, wall_time=None):
  assert(modified_type is None or modified_type in supported_types)
  xp_modified[experiment] = (time.time(), modified_type, wall_time)

def last_timestamp_loaded(experiment, modified_type, last_timestamp):
  req_res = tb_request("runs", safe=False)
  tb_data = json.loads(req_res)
  if experiment in tb_data:
    if modified_type in tb_data[experiment]:
      names = tb_data[experiment][modified_type]
      for name in names:
        req_res = tb_request(modified_type, experiment, name, safe=False)
        req_res = json.loads(req_res)
        for value in req_res:
          if value[0] == last_timestamp:
            return True
  return False

def tb_access_xp(experiment):
  if experiment not in xp_modified:
    return
  last_modified, modified_type, last_timestamp = xp_modified[experiment]

  while time.time() < last_modified + request_delay:
    # If we know the last timestamp, try to exit early
    if modified_type is not None:
      if last_timestamp_loaded(experiment, modified_type, last_timestamp):
        break
    else:
      time.sleep(0.01)
  del xp_modified[experiment]

def tb_access_all():
  for experiment in xp_modified.keys():
    tb_access_xp(experiment)

# Make sure we have writers for all experiments
xp_writers = {}
def tb_get_xp_writer(experiment):
  if experiment in xp_writers:
    return xp_writers[experiment]

  tb_access_xp(experiment)
  xp_folder = tensorboard_folder.format(experiment)
  writer = tf.summary.FileWriter(xp_folder, flush_secs=1)
  xp_writers[experiment] = writer
  tb_modified_xp(experiment)
  return writer

def tb_remove_xp_writer(experiment):
  # If the experiment does not exist, does nothing silently
  if experiment in xp_writers:
    del xp_writers[experiment]
    # Prevent recreating it too quickly
    tb_modified_xp(experiment)

def tb_xp_writer_exists(experiment):
  return experiment in xp_writers

# Use writers
def tb_add_scalar(experiment, name, wall_time, step, value):
  writer = tb_get_xp_writer(experiment)
  summary = tf.Summary(value=[
      tf.Summary.Value(tag=name, simple_value=value),
  ])
  event = tf.Event(wall_time=wall_time, step=step, summary=summary)
  writer.add_event(event)
  writer.flush()
  tb_modified_xp(experiment, modified_type="scalars", wall_time=wall_time)

def tb_add_histogram(experiment, name, wall_time, step, histo):
  # Tensorflow does not support key being unicode
  histo_string = {}
  for k,v in histo.items():
    histo_string[str(k)] = v
  histo = histo_string

  writer = tb_get_xp_writer(experiment)
  summary = tf.Summary(value=[
      tf.Summary.Value(tag=name, histo=histo),
  ])
  event = tf.Event(wall_time=wall_time, step=step, summary=summary)
  writer.add_event(event)
  writer.flush()
  tb_modified_xp(experiment, modified_type="histograms", wall_time=wall_time)

# Perform requests to tensorboard http api
def tb_request(query_type, run=None, tag=None, safe=True):
  request_url = "http://localhost:8888/data/{}"
  if run and tag:
    request_url += "?run={}&tag={}"

  if safe:
    if run:
      tb_access_xp(run)
    else:
      tb_access_all()

  request_url = request_url.format(query_type, run, tag)
  try:
    return urllib2.urlopen(request_url, timeout=1).read()
  except:
    raise ValueError

# Borrowed from tensorflow/tensorboard/scripts/generate_testdata.py
# Create a histogram from a list of values
def _MakeHistogramBuckets():
  v = 1E-12
  buckets = []
  neg_buckets = []
  while v < 1E20:
    buckets.append(v)
    neg_buckets.append(-v)
    v *= 1.1
  # Should include DBL_MAX, but won't bother for test data.
  return neg_buckets[::-1] + [0] + buckets


def tb_make_histogram(values):
  """Convert values into a histogram proto using logic from histogram.cc."""
  limits = _MakeHistogramBuckets()
  counts = [0] * len(limits)
  for v in values:
    idx = bisect.bisect_left(limits, v)
    counts[idx] += 1

  limit_counts = [(limits[i], counts[i]) for i in xrange(len(limits))
                  if counts[i]]
  bucket_limit = [lc[0] for lc in limit_counts]
  bucket = [lc[1] for lc in limit_counts]
  sum_sq = sum(v * v for v in values)
  return {
      "min": min(values),
      "max": max(values),
      "num": len(values),
      "sum": sum(values),
      "sum_squares": sum_sq,
      "bucket_limit": bucket_limit,
      "bucket": bucket}
## END of borrowed


### Error handler
@app.errorhandler(404)
def not_found(error):
  return "This is not the web page you are looking for."

def wrong_argument(message):
  print("wrong_argument: ", message)
  return message, 400

### Running and version check
@app.route('/', methods=["GET"])
def get_version():
  # Verify that tensorboard is running
  try:
    req_res = tb_request("logdir")
  except:
    return wrong_argument("Server: TensorBoard failed to answer request 'logdir'")

  if not json.loads(req_res)["logdir"] == tensorboard_folder[:-3]:
    return wrong_argument("Tensorboard is not running in the correct folder.")

  return __version__


### Experience management
@app.route('/data', methods=["GET"])
def get_all_experiments():
  experiment = request.args.get('xp')

  result = ""
  try:
    req_res = tb_request("runs")
  except:
    return wrong_argument("Server: TensorBoard failed to answer request 'runs'")

  tb_data = json.loads(req_res)
  if experiment:
    try:
      experiment = to_unicode(experiment)
    except:
      return wrong_argument("Experiment name should be a non-empty string or unicode instead of '{}'".format(type(experiment)))
    if not tb_xp_writer_exists(experiment):
      return wrong_argument("Unknown experiment name '{}'".format(experiment))
    if experiment in tb_data:
      result = tb_data[experiment]
      # Remove the not supported types from the answer
      for not_supported_type in not_supported_types:
        if not_supported_type in result:
          del result[not_supported_type]
    else:
      # Experience with no data on tensorboard,
      # return empty list for all types
      result = {}
      for t in supported_types:
        result[t] = []
  else:
    result = tb_data.keys()
  return json.dumps(result)

@app.route('/data', methods=["POST"])
def post_experiment():
  experiment = request.get_json()
  try:
    experiment = to_unicode(experiment)
  except:
    return wrong_argument("Experiment name should be a non-empty string or unicode instead of '{}'".format(type(experiment)))

  if tb_xp_writer_exists(experiment):
    return wrong_argument("'{}' experiment already exists".format(experiment))

  tb_get_xp_writer(experiment)
  return "ok"

@app.route('/data', methods=["DELETE"])
def delete_experiment():
  experiment = request.args.get('xp')
  try:
    experiment = to_unicode(experiment)
  except:
    return wrong_argument("Experiment name should be a non-empty string or unicode instead of '{}'".format(type(experiment)))

  if not tb_xp_writer_exists(experiment):
    return wrong_argument("'{}' experiment does not already exist".format(experiment))

  # Delete folder on disk
  folder_path = tensorboard_folder.format(experiment)
  shutil.rmtree(folder_path)

  # Delete experience writer
  tb_remove_xp_writer(experiment)

  return "ok"

### Scalar data
@app.route('/data/scalars', methods=["GET"])
def get_scalars():
  experiment = request.args.get('xp')
  try:
    experiment = to_unicode(experiment)
  except:
    return wrong_argument("Experiment name should be a non-empty string or unicode instead of '{}'".format(type(experiment)))
  name = request.args.get('name')
  if (not experiment) or (not name):
    return wrong_argument("xp and name arguments are required")
  if not tb_xp_writer_exists(experiment):
    return wrong_argument("Unknown experiment name '{}'".format(experiment))

  try:
    req_res = tb_request("scalars", experiment, name)
    return req_res
  except:
    message = "Combination of experiment '{}' and name '{}' does not exist".format(experiment, name)
    return wrong_argument(message)



@app.route('/data/scalars', methods=['POST'])
def post_scalars():
  experiment = request.args.get('xp')
  try:
    experiment = to_unicode(experiment)
  except:
    return wrong_argument("Experiment name should be a non-empty string or unicode instead of '{}'".format(type(experiment)))
  name = request.args.get('name')
  if (not experiment) or (not name):
    return wrong_argument("xp and name arguments are required")
  if not tb_xp_writer_exists(experiment):
    return wrong_argument("Unknown experiment name '{}'".format(experiment))

  data = request.get_json()
  if not data:
    return wrong_argument("POST content is not a proper json")
  if not isinstance(data, list):
    return wrong_argument("POST content is not a list: '{}'".format(request.form.keys()))
  if not len(data)==3:
    return wrong_argument("POST does not contain a list of 3 elements but '{}'".format(data))
  if not (isinstance(data[2], int) or isinstance(data[2], float)):
    return wrong_argument("POST value is not a number but '{}'".format(data[2]))

  tb_add_scalar(experiment, name, data[0], data[1], data[2])

  return "ok"


### Histogram data
@app.route('/data/histograms', methods=["GET"])
def get_histograms():
  experiment = request.args.get('xp')
  try:
    experiment = to_unicode(experiment)
  except:
    return wrong_argument("Experiment name should be a non-empty string or unicode instead of '{}'".format(type(experiment)))
  name = request.args.get('name')
  if (not experiment) or (not name):
    return wrong_argument("xp and name arguments are required")
  if not tb_xp_writer_exists(experiment):
    return wrong_argument("Unknown experiment name '{}'".format(experiment))

  try:
    req_res = tb_request("histograms", experiment, name)
    return req_res
  except:
    message = "Combination of experiment '{}' and name '{}' does not exist".format(experiment, name)
    return wrong_argument(message)



@app.route('/data/histograms', methods=['POST'])
def post_histograms():
  experiment = request.args.get('xp')
  try:
    experiment = to_unicode(experiment)
  except:
    return wrong_argument("Experiment name should be a non-empty string or unicode instead of '{}'".format(type(experiment)))
  name = request.args.get('name')
  to_build = request.args.get('tobuild')
  if (not experiment) or (not name) or (not to_build):
    return wrong_argument("xp, name and tobuild arguments are required")
  if not tb_xp_writer_exists(experiment):
    return wrong_argument("Unknown experiment name '{}'".format(experiment))
  to_build = to_build.lower() == "true"

  data = request.get_json()
  if not data:
    return wrong_argument("POST content is not a proper json")
  if not isinstance(data, list):
    return wrong_argument("POST content is not a list: '{}'".format(request.form.keys()))
  if not len(data)==3:
    return wrong_argument("POST does not contain a list of 3 elements but '{}'".format(data))

  if to_build:
    if (not data[2]) or (not isinstance(data[2], list)):
      return wrong_argument("elements to build the histogram are not in a list but '{}'".format(data[2]))
    histogram_dict = tb_make_histogram(data[2])
  else:
    already_built_required_params = {
      "min": [float, int],
      "max": [float, int],
      "num": [int],
      "bucket_limit": [list],
      "bucket": [list],
    }
    histogram_dict = data[2]
    for required_param in already_built_required_params:
      if not (required_param in histogram_dict):
        message = "Missing argument '{}' to the given histogram".format(required_param)
        return wrong_argument(message)
      is_ok = False
      for required_type in already_built_required_params[required_param]:
        if isinstance(histogram_dict[required_param], required_type):
          is_ok = True
          break
      if not is_ok:
        message = "Argument '{}' should be of type '{}' and is '{}'"
        message = message.format(required_param, str(already_built_required_params[required_param]), str(type(histogram_dict[required_param])))
        return wrong_argument(message)

  tb_add_histogram(experiment, name, data[0], data[1], histogram_dict)

  return "ok"


### Backup data
@app.route('/backup', methods=['GET'])
def get_backup():
  experiment = request.args.get('xp')
  try:
    experiment = to_unicode(experiment)
  except:
    return wrong_argument("Experiment name should be a non-empty string or unicode instead of '{}'".format(type(experiment)))
  if not experiment:
    return wrong_argument("xp argument is required")

  folder_path = tensorboard_folder.format(experiment)

  if not path.isdir(folder_path):
    return wrong_argument("Requested experiment '{}' does not exist".format(experiment))

  zip_file = shutil.make_archive("/tmp/{}".format(experiment), 'zip', folder_path)

  return send_file(zip_file, mimetype='application/zip')

@app.route('/backup', methods=['POST'])
def post_backup():
  experiment = request.args.get('xp')
  try:
    experiment = to_unicode(experiment)
  except:
    return wrong_argument("Experiment name should be a non-empty string or unicode instead of '{}'".format(type(experiment)))
  force = request.args.get('force')
  if (not experiment) or (not force):
    return wrong_argument("xp and force argument are required")
  if not force.lower() == 'true':
    return wrong_argument("Force must be set to 1 to be able to override a folder")
  if tb_xp_writer_exists(experiment):
    return wrong_argument("Experiment '{}' already exists".format(experiment))

  folder_path = tensorboard_folder.format(experiment)
  zip_file_path = "/tmp/{}.zip".format(experiment)

  if "archive" in request.files:
    backup_data = request.files["archive"]
    backup_data.save(zip_file_path)
  else:
    content_type = request.headers.get('Content-type', '')
    if (not content_type) or (content_type != "application/zip"):
      return wrong_argument("Backup post request should contain a file or a zip")
    with open(zip_file_path, "wb") as f:
      f.write(request.data)

  folder_path = tensorboard_folder.format(experiment)
  Popen("mkdir -p {}".format(folder_path),stdout=PIPE, shell=True)
  Popen("cd {}; unzip {}".format(folder_path, zip_file_path),stdout=PIPE, shell=True)

  tb_get_xp_writer(experiment)

  return "ok"


app.run(host="0.0.0.0", port=cli_args.port)
