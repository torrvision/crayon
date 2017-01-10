tensorboard --logdir /tmp/tensorboard --port 8888 > /tmp/tensorboard.log &

nohup python /server.py 8889 > /tmp/server.log
