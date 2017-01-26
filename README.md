# Crayon [![Build Status](https://travis-ci.org/albanD/crayon.svg?branch=master)](https://travis-ci.org/albanD/crayon)

#### Crayon allows you to easily write any data that you want on [tensorboard](https://github.com/tensorflow/tensorflow/tree/master/tensorflow/tensorboard)

#####################

This system is composed of two parts:
* A server running on a given machine that will be used to display tensorboard and store all the data.
* A client embedded inside your code that will send the datas to the server.

Note that the server and the client *do no* have to be on the same machine.


## Install

### Server machine
The machine that will host the server needs to have [docker](https://www.docker.com/) installed. The server is completely packaged inside a docker container. To get it, run:
```bash
$ docker pull alband/crayon
```

### Client machine
The client machine only need to install the client for the required language:
* python:
```bash
$ pip install pycrayon
```


## Usage


### Server machine

To start the server, run the following:

```bash
$ docker run -d -p 8888:8888 -p 8889:8889 --name crayon alband/crayon
```

Tensorboard is now accessible on a browser at `server_machine_address:8888`.
The client should send the data at `server_machine_address:8889`.


### Client

See the documentation for the required language:
* [python](client/python/README.md#usage-example)

