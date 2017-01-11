import tensorflow as tf

# The folder where everything will be writen
writer = tf.train.SummaryWriter("/tmp/tensorboard/test", flush_secs=1)

# Borrowed from tensorflow/tensorboard/scripts/generate_testdata.py
# Create a histogram from a list of values
# Not sure if we want to use this
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


def _MakeHistogram(values):
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
  return summary_pb2.HistogramProto(
      min=min(values),
      max=max(values),
      num=len(values),
      sum=sum(values),
      sum_squares=sum_sq,
      bucket_limit=bucket_limit,
      bucket=bucket)
## END of borrowed

# Temporary code for test
from time import sleep
i = 0
while True:
  summary = tf.Summary(value=[
      tf.Summary.Value(tag="summary_tag", simple_value=i*i),
  ])
  event = tf.Event(wall_time=i/10, step=i, summary=summary)
  writer.add_event(event)
  writer.flush()
  i += 1
  sleep(1)
