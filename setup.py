import os
import sys

from setuptools import setup
from setuptools.config import read_configuration

from setuputils import find_version


def here(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)

config = read_configuration(here('setup.cfg'))
config['metadata']['version'] = find_version(here('astor', '__init__.py'))
config['options'].update(config['metadata'])

setup(**config['options'])
