# Crayon [![Build Status](https://travis-ci.org/torrvision/crayon.svg?branch=master)](https://travis-ci.org/torrvision/crayon) [![PyPI](https://img.shields.io/pypi/v/pycrayon.svg)](https://pypi.python.org/pypi/pycrayon/)

Crayon is a framework that gives you access to the visualisation power
of
[TensorBoard](https://github.com/tensorflow/tensorboard) with
**any language**. Currently it provides a Python and a Lua interface, however
you can easily implement a wrapper around the
provided [RESTful API](doc/specs.md).

---

This system is composed of two parts:
* A server running on a given machine that will be used to display tensorboard
  and store all the data.
* A client embedded inside your code that will send the datas to the server.

Note that the server and the client *do not* have to be on the same machine.


## Install

### Server machine

The machine that will host the server needs to
have [docker](https://www.docker.com/) installed. The server is completely
packaged inside a docker container. To get it, run:

```bash
$ docker pull alband/crayon
```

### Client machine

The client machine only need to install the client for the required language.
Detailed instructions can be read by nagivating to
their [respective directories](client/).

TL;DR:

* Lua / Torch - `$ luarocks install crayon`
* Python 2 - `$ pip install pycrayon`
* Python 3 - `$ pip3 install pycrayon`

## Usage

### Server machine

To start the server, run the following:

```bash
$ docker run -d -p 8888:8888 -p 8889:8889 --name crayon alband/crayon
```

Tensorboard is now accessible on a browser at `server_machine_address:8888`. The
client should send the data at `server_machine_address:8889`.

### Client

See the documentation for the required language:

* [Lua](client/lua/README.md#usage-example)
* [Python](client/python/README.md#usage-example)

