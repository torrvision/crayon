# The server is build completely inside a docker image.

IF you do not have the docker image yet, run in this folder:
```bash
docker build -t tensorboard/api:latest .
```

Then the server can be started with:
```bash
docker run -dP -name tensorboard tensorboard/api
```
TODO: fix ports (because -P give random host ports) and document them here
