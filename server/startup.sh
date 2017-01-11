stdbuf -i0 -o0 -e0 tensorboard --logdir /tmp/tensorboard --port 8888 2>&1 1>/tmp/tensorboard.log &

stdbuf -i0 -o0 -e0 python /server.py 8889 2>&1 1>/tmp/server.log
