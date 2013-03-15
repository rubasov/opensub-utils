#! /usr/bin/python

import os
import setuptools
import sys

# FIXME explain why this is here
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
        "six",
        ],
    license="BSD",  # FIXME
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
    #test_suite="nose.collector",  # FIXME
    tests_require=[
        "nose",
        ],
    url="http://github.com/rubasov/...",  # FIXME
    version=opensub.__version__,
    zip_safe=False,
    )
