# Contributing

## Contributing Code

* Fork the repo.
* Write your contribution.
* Make sure your code follows our coding style (e.g.Python code should follow PEP8).
* Run tests. For instance, if you are editing the server or the python client:

```bash
$ cd client/python
$ $PYTHON_VERSION -m unittest discover
```

* Push to your fork. Write a [good commit message][commit]. Submit a pull request (PR).

  [commit]: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html

* Wait for your PR to be reviewed by one of the maintainers.

## Other details

### Bumping versions

* Edit the `__VERSION__` variable in server code and clients.
* Create a new rockspec:

```bash
$ luarocks new_version crayonx.x-1.rockspec y.y-1 \
      https://raw.githubusercontent.com/torrvision/crayon/<new_hash>/client/lua/crayon.lua
```
