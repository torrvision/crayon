from distutils.core import setup
from pycrayon.crayon import __version__

setup(name='pycrayon',
      description='Crayon client for python',
      author='torrvision',
      url='https://github.com/torrvision/crayon',
      packages=['pycrayon'],
      version=__version__,
      install_requires=[
        "requests"
      ]
     )