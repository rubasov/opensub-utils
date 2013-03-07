import os
import setuptools
import sys

# FIXME explain why this is here
sys.path.insert(0,
    os.path.join(
        os.path.dirname(__file__),
        "lib",
        ))

import opensub.version


setuptools.setup(
    author="Bence Romsics",
    author_email="rubasov@gmail.com",
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
    test_suite="nose.collector",
    tests_require=[
        "nose",
        ],
    url="http://github.com/rubasov/...",  # FIXME
    version=opensub.version.__version__,
    zip_safe=False,
    )
