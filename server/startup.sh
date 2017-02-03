#!/bin/bash

# Try to patch tensorboard to reduce autorefresh time and allow subsecond backend refresh
# This will be changed by the patch script if the backend supports subsecond refresh
export BACKEND_RELOAD="1"
python /patch_tensorboard.py $1 $2

tensorboard --reload_interval $BACKEND_RELOAD --logdir /tmp/tensorboard --port 8888 &

python /server.py 8889 2>&1 1>/tmp/crayon.log
