# The server is build completely inside a docker image.

IF you do not have the docker image yet, run in this folder:
```bash
docker build -t tensorboard/api:latest .
```

Then the server can be started with:
```bash
# In interactive mode:
docker run -P tensorboard/api
# In interactive mode:
docker run -P -it tensorboard/api
```

* Move to this folder
* Run `docker build -t tensorboard/api:latest .`
* You can now launch the image with `docker run -P -it tensorboard/api`
