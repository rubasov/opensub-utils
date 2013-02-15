import logging
import os
import shutil
import struct
import tempfile
import xml.etree.ElementTree as etree
import zipfile

import six
if six.PY3:
    import urllib.request as urllib_request
else:
    import urllib2 as urllib_request


def hash_file(file, file_size=None):

    """
    Hash an open file.

    The hash algorithm and some of the code comes from:
    http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes

    A multi-file movie's hash is the hash of the first file.

    Takes:
        file - seekable file-like object
        file_size - size of file in bytes

    Returns:
        hash as a zero-padded, 16-digit, lower case hex string

    Raises:
        Exception - file too small
    """

    fmt = "q"  # long long
    buf_size = struct.calcsize(fmt)
    chunk_size = 64 * 1024  # bytes

    assert chunk_size % buf_size == 0

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


def extract_by_xpath(xml_file, xpath, fun=lambda x: x):

    tree = etree.parse(xml_file)
    lst = [fun(elem) for elem in tree.findall(xpath)]
    return lst


class UserAgent(object):

    """Communicate with subtitle servers."""

    def __init__(self, server, opener=urllib_request.build_opener()):

        """
        Takes:
            server - FQDN or IP of server
                e.g. "www.opensubtitles.org"
            opener - urllib(2) opener object
        """

        self.server = server
        self.opener = opener

    # maybe FIXME encode urls
    #
    # Depending on where the inputs come from you may need to
    # construct the urls more carefully and care for url encoding.

    # FIXME Which variant of ISO 639 is accepted?
    #
    # So far I have used the 3-letter codes like 'eng', 'hun'...

    def search_page_url(
        self, movie_hash, language, cd_count=1, _fmt="simplexml"):

        """
        Construct search page URL.

        Takes:
            movie_hash - hash of movie (hex string)
                cf. movie_hash()
            language - preferred language (ISO 639 code string)
            cd_count - how many video files make up the movie?

        Returns:
            search page URL
        """

        url = ("http://"
            + self.server
            + "/en"
            + "/search"
            + "/sublanguageid-{}".format(language)
            + "/moviehash-{}".format(movie_hash)
            + "/subsumcd-{}".format(cd_count)
            + "/{}".format(_fmt)
            )
        logging.debug("search_page_url: {}".format(url))
        return url

    def search(self, movie, language):

        """
        Takes:
            movie - list of video file paths in "natural order"
            language - ISO 639 code of subtitle language

        Returns:
            list of subtitle archive URLs (ordered as in the search results)
        """

        with open(movie[0], "rb") as f:
            movie_hash = hash_file(f)

        cd_count = len(movie)

        search_page_url = self.search_page_url(
            language=language,
            movie_hash=movie_hash,
            cd_count=cd_count,
            )

        # FIXME use absolute xpath: /search/results/subtitle/download
        #
        # findall with an absolute xpath is broken in
        # xml.etree.Elementree 1.3.0 . I couldn't find the issue on
        # bugs.python.org, but here is the code issuing the warning:
        # /usr/lib/python2.7/xml/etree/ElementTree.py:745

        search_page_xml = self.opener.open(search_page_url)
        search_results = extract_by_xpath(
            xml_file=search_page_xml,
            xpath="./results/subtitle/download",
            fun=lambda elem: elem.text,
            )
        search_page_xml.close()

        return search_results

    def __repr__(self):

        return "{}({!r})".format(self.__class__, self.__dict__)

    def __str__(self):

        return "{}({!r})".format(self.__class__, self.server)


class SubtitleArchive(object):

    """
    Access subtitles in a subtitle archive.

    I haven't ever found a specification for opensubtitles.org's
    subtitle archive format, so I'm listing my basic assumptions here:

    The archive is a valid .zip file with any name.
    The .zip contains no directories.
        (Though we try to handle the presence of directories gracefully.)
    The .zip contains one ore more subtitle file(s).
    A subtitle file has one of the extensions listed here (case insensitive):
        http://trac.opensubtitles.org/projects/opensubtitles
            /wiki/DevReadFirst#Subtitlefilesextensions
    All subtitle files in one archive belong to the same movie.
    There is exactly one subtitle file for each video file of the movie.
        (Think of multi-CD movies.)
    There are no other subtitle files in the archive.
    All other files in the archive can be ignored.
        (e.g. .nfo files)
    The "natural order" of the subtitle files is the same as if we have
        ordered them by their archived names case insensitively.
    """

    def __init__(
        self,
        url,
        opener=urllib_request.build_opener(),
        sort_key=str.lower,
        extensions=set(
            [".srt", ".sub", ".smi", ".txt", ".ssa", ".ass", ".mpl"]),
        ):

        """
        Prefer using it as a context manager: with SubtitleArchive() as ...

        Takes:
            url - url of the subtitle archive
            opener - urllib(2) opener object
            sort_key - yield order of subtitles
            extensions - iterable of valid subtitle extensions
                lower case, include leading dot
        """

        self.url = url
        self.opener = opener
        self.sort_key = sort_key
        self.extensions = extensions

        # We may set these directly for testing purposes.
        self.tempfile = None
        self.zipfile = None

        logging.debug("archive_url: {}".format(self.url))

    def __enter__(self):

        return self

    def __exit__(self, type, value, traceback):

        if self.zipfile is not None:
            self.zipfile.close()

        if self.tempfile is not None:
            self.tempfile.close()
            # tempfile is responsible to delete
            # the NamedTemporaryFile at this point

    def _urlopen_via_tempfile(self):

        # zipfile needs a seekable file-like objects.
        # Therefore we cache the remote file in a local temporary file.

        # See the notes here on why we need a *Named*TemporaryFile:
        # http://docs.python.org/2/library/zipfile#zipfile.ZipFile.open

        if self.tempfile is None:
            dst = tempfile.NamedTemporaryFile()
            src = self.opener.open(self.url)
            shutil.copyfileobj(src, dst)
            src.close()
            dst.seek(0, os.SEEK_SET)
            self.tempfile = dst

    def _open_as_zipfile(self):

        if self.zipfile is None:
            self._urlopen_via_tempfile()
            self.zipfile = zipfile.ZipFile(self.tempfile.name)

    def open_subtitle_files(self):

        """
        Yields:
            tuple(subtitle_file, archived_filename) in the order
            determined by sort_key.
        """

        self._open_as_zipfile()

        for name in sorted(self.zipfile.namelist(), key=self.sort_key):

            ext = os.path.splitext(name)[1]
            if ext.lower() not in self.extensions:
                continue

            with self.zipfile.open(name) as f:
                yield (f, name)

    def __repr__(self):

        return "{}({!r})".format(self.__class__, self.__dict__)

    def __str__(self):

        return "{}({!r})".format(self.__class__, self.url)
