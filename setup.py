from setuptools import setup, find_packages

from setuputils import find_version, read


setup(
    name='astor',
    version=find_version('astor/__init__.py'),
    description='Read/rewrite/write Python ASTs',
    long_description=read('README.rst'),
    author='Patrick Maupin',
    author_email='pmaupin@gmail.com',
    platforms='Independent',
    url='https://github.com/berkerpeksag/astor',
    packages=find_packages(exclude=['tests']),
    py_modules=['setuputils'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Compilers',
    ],
    keywords='ast, codegen, PEP8',
)
