#!/bin/bash

# Try to patch tensorboard to reduce autorefresh time
python /patch_tensorboard.py $1

tensorboard --reload_interval 1 --logdir /tmp/tensorboard --port 8888 2>&1 1>/tmp/tensorboard.log &

python /server.py 8889 2>&1 1>/tmp/crayon.log
