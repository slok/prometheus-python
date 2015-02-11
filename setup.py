#!/usr/bin/env python

import os
import sys

import prometheus

from codecs import open

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = [
    'prometheus',
]

requires = []

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name='prometheus',
    version=prometheus.__version__,
    description='Python Prometheus client',
    long_description=readme,
    author='Xabier Larrakoetxea',
    author_email='slok69@gmail.com',
    url='https://github.com/slok/prometheus-python',
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'prometheus': 'prometheus'},
    include_package_data=True,
    install_requires=requires,
    license='Apache 2.0',
    zip_safe=False,
    keywords=['prometheus', 'client', 'metrics'],
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'

    ),
)
