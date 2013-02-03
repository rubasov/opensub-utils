#! /usr/bin/python

import errno
import logging
import os
import StringIO
import struct
import sys
import tempfile
import urllib2
import urlparse
import zipfile

from lxml import etree

def file_hash(file_to_hash):

    """
    Hash a file.

    The algorithm comes from this page:
    http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes

    Takes:
        file_to_hash - path of the file

    Returns:
        hex string of hash

    Raises:
        Exception - file too small: < 128 KiB
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
    if filesize < 2 * 64 * 1024:
        raise Exception( "file too small: < 128 KiB" )

    hash_value = filesize
    with open(file_to_hash, "rb") as f:
        hash_value = chunk_hash(f, hash_value)
        f.seek( max( 0, filesize - 64 * 1024 ), 0 )
        hash_value = chunk_hash(f, hash_value)

    hex_string = "{:016x}".format(hash_value)
    logging.debug( "hash: {}".format(hex_string) )
    return hex_string

def movie_hash(file_list):

    """
    Hash multi-CD movies by the first file, ignore the rest.

    Takes:
        file_list - list of video files belonging to the movie

    Returns:
        hex string of hash
    """

    movie_hash = file_hash( file_list[0] )
    return movie_hash

def extract_subtitle_urls(xml):

    """
    Extract search result URLs from simplexml.

    Takes:
        xml - xml string

    Returns:
        list of search result URLs (same order as in xml)
    """

    tree = etree.fromstring(xml)
    elements = tree.xpath("/search/results/subtitle/download")

    if len(elements) == 0:
        raise Exception("subtitle not found")

    url_list = map( lambda elem: elem.text, elements )
    logging.debug( "result_urls: {}".format(url_list) )
    return url_list

def extract_subtitles(archive_content):

    """
    Extract all subtitle files from subtitle zip archive.

    Ignore anything else in the archive (e.g. .nfo files).
    Store everything in memory, write nothing to the file system.

    Takes:
        archive_content - zip archive content as a string

    Returns:
        list of subtitles as Subtitle objects (order unspecified)

    Raises:
        AssertionError - no subtitle in the archive
    """

    rv = list()

    with zipfile.ZipFile( StringIO.StringIO(archive_content) ) as z:

        subtitle_names = filter(
            path_has_subtitle_extension, z.namelist() )

        # FIXME more informative error message
        assert len(subtitle_names) >= 1, "found no subtitle file in archive"

        for name in subtitle_names:
            with z.open(name) as s:
                rv.append(
                    Subtitle(
                        name = name,
                        content = s.read() ) )

    return rv

def recognized_subtitle_extensions():

    """
    http://trac.opensubtitles.org
          /projects/opensubtitles/wiki/DevReadFirst
          #Subtitlefilesextensions
    """

    return set([".srt", ".sub", ".smi", ".txt", ".ssa", ".ass", ".mpl"])

def path_has_subtitle_extension(path):

    base, extension = os.path.splitext(path)

    assert extension != "", "path has no extension: {}".format(path)

    if extension in recognized_subtitle_extensions():
        is_recognized = True
    else:
        is_recognized = False

    return is_recognized

class Subtitle(object):

    def __init__(self, name, content):

        self.name = name
        self.content = content

    def write_no_overwrite(self, path):

        # FIXME this is unix-only
        fd = os.open( path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644 )
        with os.fdopen(fd, "w") as fo:
            fo.write(self.content)
            #fo.flush()
            #os.fsync(fd)

    def write(self, path):

        with open(path, "w") as fo:
            fo.write(self.content)
            #fo.flush()
            #os.fsync(fo.fileno())

class UserAgent(object):

    """
    Communicate with subtitle servers.
    """

    def __init__(self, server, user_agent):
        self.server = server
        self.user_agent = user_agent

    # maybe FIXME encode urls
    #
    # Depending on where the inputs come from you may need to
    # construct the urls more carefully and care for url encoding.

    def search_page_url(
        self, movie_hash, language, cd_count=1, _fmt="simplexml"):

        """
        Construct search page URL for simplexml format.

        Takes:
            movie_hash - hash of movie (hex string)
                cf. movie_hash()
            language - subtitle language according to ISO 639 (string)
            cd_count - how many files make up the movie?

        Returns:
            search page URL
        """

        url = ( "http://"
            + self.server
            + "/en"
            + "/search"
            + "/sublanguageid-{}".format(language)
            + "/moviehash-{}".format(movie_hash)
            + "/subsumcd-{}".format(cd_count)
            + "/{}".format(_fmt)
            )
        logging.debug( "search_page_url: {}".format(url) )
        return url

    def get(self, url):

        """
        Wrap HTTP GET.

        Takes:
            url - URL to get

        Returns:
            content of resource at URL
        """

        headers = {}
        headers["User-Agent"] = self.user_agent
        if True: # dev mode
            headers["Cache-Control"] = "only-if-cached"

        req = urllib2.Request(url=url, headers=headers)
        stream = urllib2.urlopen(req)
        content = stream.read()
        stream.close()

        return content

    def get_subtitle(self, movie, language):

        def best_result_url(lst):
            return lst[0]

        subtitle_list = \
            extract_subtitles(
            self.get(
            best_result_url(
            extract_subtitle_urls(
            self.get(
            self.search_page_url(
                language = language,
                movie_hash = movie_hash(movie),
                cd_count = len(movie),
                ))))))

        video_file_count = len(movie)
        subtitle_count = len(subtitle_list)
        if video_file_count != subtitle_count:
            raise Exception(
                "unexpected number of subtitle files in archive: {}".format(
                    subtitle_count ) )

        subtitle_list.sort( key = lambda obj: obj.name )

        return subtitle_list
