#! /usr/bin/python

import logging
import os
import struct

def file_hash(file_to_hash):

    """
    http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
    """

    def chunk_hash(f, hash_value):

        fmt = "q" # long long
        bufsize = struct.calcsize(fmt)

        for _ in range( 64 * 1024 / bufsize ):
            buf = f.read(bufsize)
            hash_value += struct.unpack(fmt, buf)[0]
            hash_value &= 0xFFFFFFFFFFFFFFFF # to remain as 64 bit number

        return hash_value

    filesize = os.path.getsize(file_to_hash)
    assert filesize >= 2 * 64 * 1024, (
        "opensubtitles.org's hash spec doesn't allow files < 128 KiB" )

    hash_value = filesize
    with open(file_to_hash, "rb") as f:
        hash_value = chunk_hash(f, hash_value)
        f.seek( max( 0, filesize - 64 * 1024 ), 0 )
        hash_value = chunk_hash(f, hash_value)

    hex_string = "{:016x}".format(hash_value)
    logging.debug( "hash: {}".format(hex_string) )
    return hex_string

def movie_hash(movie_file_list):

    """
    Multi-CD movies are hashed by the first file, the rest is ignored.
    """

    movie_hash = file_hash( movie_file_list[0] )
    return movie_hash
