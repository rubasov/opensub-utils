#! /usr/bin/python

import six
# implicit py2 import StringIO as six.BytesIO
# implicit py3 import io.BytesIO as six.BytesIO

import logging
import os
# NOTE The nicest would be to 'import ... as urllib.request',
#      but that's not possible, sigh...
if six.PY3:
    import urllib.request as urllib_request
else:
    import urllib2 as urllib_request
import xml.etree.ElementTree as etree
import zipfile

import opensubtitles.hash


class SubtitleNotFound(Exception):
    pass


def extract_subtitle_urls(xml_file):

    """
    Extract search result URLs from simplexml.

    Takes:
        xml - file-like object of simplexml search results

    Returns:
        list of search result URLs (same order as in xml)
    """

    tree = etree.parse(xml_file)

    # FIXME use absolute xpath: /search/results/subtitle/download
    #
    # findall with an absolute xpath is broken in xml.etree.Elementree 1.3.0
    # I couldn't find the issue on bugs.python.org, but here is the code
    # issuing the warning: /usr/lib/python2.7/xml/etree/ElementTree.py:745
    elements = tree.findall("./results/subtitle/download")

    if len(elements) == 0:
        raise SubtitleNotFound()

    url_list = [e.text for e in elements]
    logging.debug("search_result_urls: {}".format(url_list))
    return url_list


class Subtitle(object):

    """Subtitle struct."""

    def __init__(self, name, content):

        self.name = name
        self.content = content

    def __repr__(self):

        return "{}({!r})".format(self.__class__, self.__dict__)

    def __str__(self):

        return "{}({!r})".format(self.__class__, self.name)


# NOTE zipfile.ZipFile requires a seekable file handle.
#      File-like objects returned by urlopen are not seekable.
#      So we must take the whole archive content.
#
# NOTE I tried returning the open file-like objects (plus the name).
#      That way we wouldn't have to keep both compressed and uncompressed
#      subtitles in memory. The zipfile package prevents us doing this,
#      because it shares seek positions between open files inside the archive.
#      For details see:
#      http://stackoverflow.com/questions/5624669
#      http://docs.python.org/2/library/zipfile.html#zipfile.ZipFile.open
#
def extract_subtitles(
    zip_content,
    extensions=set(
        [".srt", ".sub", ".smi", ".txt", ".ssa", ".ass", ".mpl"])
    ):

    """
    Extract all subtitle files from subtitle zip archive.

    Ignore anything else in the archive (e.g. .nfo files).
    Store everything in memory, write nothing to the file system.

    Source of recognized extension list:
        http://trac.opensubtitles.org/projects/opensubtitles
            /wiki/DevReadFirst#Subtitlefilesextensions

    Takes:
        zip_content - zip archive content as a bytestring
        extensions - iterable of recognized subtitle extensions

    Returns:
        list of subtitles as Subtitle objects (order unspecified)

    Raises:
        Exception - subtitle not found in archive
    """

    # FIXME stringio vs bytearrayio
    with zipfile.ZipFile(six.BytesIO(zip_content)) as z:

        logging.debug("files_in_archive: {}".format(z.namelist()))

        subtitle_list = list()
        for name in z.namelist():
            ext = os.path.splitext(name)[1]
            if ext in extensions:
                with z.open(name) as s:
                    subtitle_list.append(
                        Subtitle(name=name, content=s.read()))

        if len(subtitle_list) == 0:
            raise Exception("subtitle not found in archive")

    return subtitle_list


class UserAgent(object):

    """Communicate with subtitle servers."""

    def __init__(self, server, opener=urllib_request.build_opener()):

        self.server = server
        self.opener = opener

    def __repr__(self):

        return "{}({!r})".format(self.__class__, self.__dict__)

    def __str__(self):

        return "{}({!r})".format(self.__class__, self.server)

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

    def get_subtitles(self, movie, language):

        """
        Get subtitles of movie.

        Wire elements together:
            Query for subtitles of movie.
            Download first search result.
            Extract archive.
            Return subtitle objects ordered by subtitle name.

        Takes:
            movie - list of video files belonging to movie ("natural order")
            language - preferred language (ISO 639 code string)

        Returns:
            list of Subtitle objects (sorted by subtitle name)
        """

        def best(lst):
            return lst[0]

        subtitle_archive_url = best(
            extract_subtitle_urls(
            self.opener.open(
            self.search_page_url(
                language=language,
                movie_hash=opensubtitles.hash.by_movie(movie),
                cd_count=len(movie),
                ))))

        zip_file = self.opener.open(subtitle_archive_url)
        zip_content = zip_file.read()
        zip_file.close()

        subtitle_list = extract_subtitles(zip_content=zip_content)

        if len(movie) != len(subtitle_list):
            raise Exception(
                "unexpected number of subtitle files in archive: {}".format(
                    len(subtitle_list)))

        subtitle_list.sort(key=lambda obj: obj.name)

        return subtitle_list
