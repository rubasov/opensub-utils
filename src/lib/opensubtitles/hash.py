#! /usr/bin/python

"""
Hash files and movies.

The hash algorithm and some of the code comes from:
http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
"""

import logging
import os
import struct


def by_file(file, file_size=None):

    """
    Hash an open file.

    Takes:
        file - seekable file-like object
        file_size - size of file in bytes, optional

    Returns:
        hash as a zero-padded, 16-digit, lower case hex string

    Raises:
        AttributeError - on non-seekable files
        Exception - file too small
    """

    fmt = "q"  # long long
    buf_size = struct.calcsize(fmt)
    chunk_size = 64 * 1024  # bytes

    if chunk_size % buf_size != 0:
        raise Exception(
            "chunk_size should be multiple of buf_size: {}".format(
                buf_size))

    def chunk(hash, seek_args):
        file.seek(*seek_args)
        for _ in range(chunk_size // buf_size):
            buf = file.read(buf_size)
            hash += struct.unpack(fmt, buf)[0]
            hash &= 0xFFFFFFFFFFFFFFFF  # to remain as 64 bit number
        return hash

    saved_pos = file.tell()

    try:
        if file_size is None:
            file.seek(0, os.SEEK_END)
            file_size = file.tell()

        if file_size < 2 * chunk_size:
            raise Exception(
                "file too small: < {} bytes".format(2 * chunk_size))

        hash = file_size
        hash = chunk(hash, seek_args=(0, os.SEEK_SET))
        hash = chunk(hash, seek_args=(-chunk_size, os.SEEK_END))

    finally:
        file.seek(saved_pos, os.SEEK_SET)

    hex_str = "{:016x}".format(hash)
    logging.info("hash: {}".format(hex_str))
    return hex_str


def by_path(path):

    """
    Hash a file by path.

    Takes:
        path - path to file to hash

    Returns:
        hash in the same format as file() does

    Raises:
        OSError, errno.ENOENT - no such file
    """

    with open(path, "rb") as f:
        return by_file(f)


def by_movie(movie):

    """
    Hash a movie.

    Takes:
        movie - movie (that is a list of file paths) to hash

    Returns:
        hash in the same format as file() does

    Raises:
        IndexError - movie is an empty list
    """

    return by_path(movie[0])
