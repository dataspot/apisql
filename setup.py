# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import io
from setuptools import setup, find_packages


# Helpers
def read(*paths):
    """Read a text file."""
    basedir = os.path.dirname(__file__)
    fullpath = os.path.join(basedir, *paths)
    contents = io.open(fullpath, encoding='utf-8').read().strip()
    return contents


# Prepare
PACKAGE = 'apisql'
NAME = PACKAGE.replace('_', '-')
INSTALL_REQUIRES = [
    'Flask-SQLAlchemy>=2.1,<3.0',
    'psycopg2-binary>=2.6.2,<3.0.0',
    'flask-cors>=3.0.2,<4.0.0',
    'flask_jsonpify',
    'XlsxWriter',
    'backports.cached-property',
]
LINT_REQUIRES = [
    'pylama',
]
TESTS_REQUIRE = [
    'tox',
]
README = read('README.md')
VERSION = read(PACKAGE, 'VERSION')
PACKAGES = find_packages(exclude=['examples', 'tests', '.tox'])

# Run
setup(
    name=NAME,
    version=VERSION,
    packages=PACKAGES,
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
    extras_require={
        'develop': LINT_REQUIRES + TESTS_REQUIRE,
    },
    zip_safe=False,
    long_description=README,
    long_description_content_type='text/markdown',
    description='A flask blueprint providing a read-lny API for querying RDBMS',
    author='Adam Kariv',
    author_email='adam.kariv@gmail.com',
    url='https://github.com/dataspot/apisql',
    license='MIT',
    keywords=[
        'data',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

)
