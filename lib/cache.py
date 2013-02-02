#! /usr/bin/python

import errno
import logging
import os
import sys
import tempfile
import urllib2

def make_cache_dir(
    subdir,
    home = os.environ["HOME"],
    cache = ".cache",
    # FIXME 2013-01-29 rubasov: The cache should belong to the library.
    #       That is to the direct user of this cache code: opensub.py.:q
    program = os.path.basename( sys.argv[0] ),
    ):

    if os.path.isabs(subdir):
        full_path = subdir
    else:
        full_path = os.path.join( home, cache, program, subdir )

    def make_sure_dir_exists(path):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    make_sure_dir_exists(full_path)
    return full_path

# FIXME 2013-01-28 rubasov: Implement expiry.
def get_content_cached(
    url,
    cache_key,
    cache_subdir,
    cache_expiry=None,
    ):

    # FIXME 2013-01-28 rubasov: make_cache_dir gets called too often.
    #
    # Originally I wanted to make cache_dir a parameter,
    # but cache_subdir is not defined at that time yet.

    cache_dir  = make_cache_dir(subdir=cache_subdir)
    cache_file = os.path.join(cache_dir, cache_key)

    def get_cache():
        with open(cache_file, "rb") as f:
            content = f.read()
        return content

    def put_cache(content):
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=cache_dir, delete=False,) as f:
            f.write(content)
            tmpname = f.name
        os.rename(tmpname, cache_file)

    def get():

        # FIXME 2013-01-27 rubasov: Version should not be stored here.
        def user_agent(
            program = os.path.basename( sys.argv[0] ),
            version = "0.9",
            ):
            return "{}/{}".format(program, version)

        headers = { "User-Agent" : user_agent() }
        req     = urllib2.Request(url=url, headers=headers)
        stream  = urllib2.urlopen(req)
        content = stream.read()
        stream.close()

        return content

    try:
        content = get_cache()
        logging.debug( "cache_hit: {}".format(cache_file) )
    except:
        logging.debug( "cache_miss: {}".format(cache_file) )
        content = get()
        put_cache(content)

    return content
