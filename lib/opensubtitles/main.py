#! /usr/bin/python

import logging
import os
import StringIO
import sys
import urlparse
import zipfile

from lxml import etree

import opensubtitles.hash
import opensubtitles.useragent
import subtitle

def extract_result_urls(xml):

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
        raise Exception("no search result in feed")
        # FIXME nice error msg
        #
        # "maybe the movie has a subtitle stream?"
        # print url for manual search

    rv = map( lambda elem: elem.text, elements )
    logging.debug( "result_urls: {}".format(rv) )
    return rv

def extract_subtitles(archive_content):

    """
    Extract all subtitle files from subtitle zip archive.

    Ignore anything else in the archive (e.g. .nfo files).
    Store everything in memory, write nothing to the file system.

    Takes:
        archive_content - zip archive content as a string

    Returns:
        list of subtitles as subtitle.Subtitle objects (order unspecified)

    Raises:
        AssertionError - no subtitle in the archive
    """

    rv = list()

    with zipfile.ZipFile( StringIO.StringIO(archive_content) ) as z:

        subtitle_names = filter(
            subtitle.path_has_subtitle_extension, z.namelist() )

        # FIXME more informative error message
        assert len(subtitle_names) >= 1, "found no subtitle file in archive"

        for name in subtitle_names:
            with z.open(name) as s:
                rv.append(
                    subtitle.Subtitle(
                        name = name,
                        content = s.read() ) )

    return rv

def get_subtitle(movie_file_list, subtitle_language, http_proxy):

    def best_result_url(lst):
        return lst[0]

    def user_agent(
        program = os.path.basename( sys.argv[0] ),
        version = "0.9",
        ):
        return "{}/{}".format(program, version)

    ua = opensubtitles.useragent.UserAgent(
        server = "www.opensubtitles.org",
        user_agent = user_agent(),
        http_proxy = http_proxy,
        )

    subtitle_list = \
        extract_subtitles(
        ua.get(
        best_result_url(
        extract_result_urls(
        ua.get(
        ua.search_page_url(
            sublanguageid = subtitle_language,
            moviehash = opensubtitles.hash.movie_hash(movie_file_list),
            file_count = len(movie_file_list),
            ))))))

    movie_file_count = len(movie_file_list)
    subtitle_count = len(subtitle_list)
    assert movie_file_count == subtitle_count, (
        "unexpected number of subtitle files in archive: {}".format(
            subtitle_count ) )

    subtitle_list.sort( key = lambda obj: obj.name )

    return subtitle_list
