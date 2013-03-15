#! /usr/bin/python

import os
import setuptools
import sys

# Do not store version number redundantly, but import package before
# install and get the version number from there.
sys.path.insert(0,
    os.path.join(
        os.path.dirname(__file__),
        "lib",
        ))

import opensub


setuptools.setup(
    author="Bence Romsics",
    author_email="rubasov+opensub@gmail.com",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "Topic :: Multimedia :: Video",
        "Topic :: Utilities",
        ],
    description="CLI utilities for opensubtitles.org.",
    install_requires=[
        "docopt",
        ],
    name="opensub",
    package_dir={
        "": "lib",
        },
    packages=[
        "opensub",
        ],
    scripts=[
        "bin/opensub-get",
        "bin/opensub-hash",
        ],
    tests_require=[
        "nose",
        ],
    url="https://github.com/rubasov/opensub-utils",
    version=opensub.__version__,
    zip_safe=False,
    )
