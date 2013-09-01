# How to install opensub-utils

## Dependencies

* A Unix-like OS.

  I develop, test and use it on Debian GNU/Linux (sid). I did not test it on
any other OS, though I believe it should run unmodified or with minor
modifications on any recent Linux distribution or other POSIX OS.

* [python2.7](http://python.org/)

  Likely you have it already. Check it with `python --version`. See below if
you want python3.

* [docopt 0.6.1+](https://github.com/docopt/docopt)

## Get the source

    # Pick a directory to store the source.
    mkdir ~/src
    cd ~/src

    # Download opensub-utils...

    # ...either by cloning the repository:
    git clone https://github.com/rubasov/opensub-utils.git
    cd opensub-utils

    # ...or by downloading a tarball (pick the latest tag from github):
    wget https://github.com/rubasov/opensub-utils/archive/$TAG.tar.gz
    tar xvzf $TAG.tar.gz
    cd opensub-utils-$TAG

## Install methods

### Don't actually install, run from working copy

It works in place, without installation.

    # Download docopt.py from github to src/lib/ .
    wget -O ... http://.../docopt.py

    # Add src/bin/ to your PATH.
    vi ~/.bashrc

### Install by pip and setuptools

    # pip is available as Debian package python-pip if you don't have it yet.

    # Install docopt by pip.
    pip install --user docopt

    # Install opensub-utils to your home by setuptools.
    cd src/
    python setup.py install --user

    # Add $HOME/.local/bin/ to your PATH if you didn't do that already.
    vi ~/.bashrc

## Test the result

    opensub-hash --version
    opensub-hash --help
    opensub-get --version
    opensub-get --help

# Uninstall

Just delete the files. In case you used `--user` to install it to your home
directory than you need to remove:

    rm -ir ~/.local/bin/opensub-* \
        ~/.local/lib/python2.7/site-packages/opensub-*

# Running the test suite

In case you want to run the tests.

## by hand

    apt-get install pep8
    ls src/test/test_*.py | xargs -n1 python

## by nose ;-)

    apt-get install pep8 python-nose
    nosetests

# Python3

The source is basically valid under both python2 and python3. On the other
hand I only occasionally test it using python3, so I wouldn't be surprised if
a few errors slipped through. Let me know if you actually use it under
python3. One more thing: you may want to change the hashbang lines to python3.

## Additional dependencies for python3

    apt-get install python3-six
    pip-3.2 install --user docopt

    # plus depending on your needs:
    apt-get install python3-setuptools python3-pip python3-nose
