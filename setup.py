#!/usr/bin/env python

from setuptools import setup
import sys

def readdoc():
    if sys.version_info[0] >= 3:
        f = open('README.rst')
    else:
        f = open('README.rst', 'rb')
    data = f.read()
    f.close()
    return data

setup(
    name='astor',
    version='0.2.2',
    description='Read/rewrite/write Python ASTs',
    long_description=readdoc(),
    author='Patrick Maupin',
    author_email='pmaupin@gmail.com',
    platforms="Independent",
    url='https://github.com/pmaupin/astor.git',
    packages=['astor'],
    license="BSD",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Compilers',
    ],
    keywords='ast',
)
