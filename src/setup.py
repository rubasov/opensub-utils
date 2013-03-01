import setuptools

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
    version="0.9",  # FIXME
    zip_safe=False,
    )
