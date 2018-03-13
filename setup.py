import sys
import os
from setuptools import setup
from setuptools.config import read_configuration
from setuputils import find_version
this_dir = os.path.dirname(__file__)

def here(*paths):
    return os.path.join(this_dir, *paths)

config = read_configuration(here('setup.cfg'))
config['metadata']['version'] = find_version(here('astor', '__init__.py'))
config['options'].update(config['metadata'])
config = config['options']
setup(**config)
