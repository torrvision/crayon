from distutils.core import setup

setup(name='pycrayon',
      description='Crayon client for python',
      author='torrvision',
      url='https://github.com/torrvision/crayon',
      packages=['pycrayon'],
      version="0.2",
      install_requires=[
        "docker",
        "requests"
      ]
     )