#!/usr/bin/env python

from distutils.core import setup

def readdoc():
    f = open('README.rst', 'rb')
    data = f.read()
    f.close()
    return data

setup(
    name='astor',
    version='0.2.1',
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
