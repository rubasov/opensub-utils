#! /usr/bin/python

import logging

import cache

class UserAgent(object):

    """
    Wrap HTTP queries to subtitle servers.
    """

    def __init__(self, server):
        self.server = server

    # maybe FIXME encode urls
    #
    # Depending on where the inputs come from you may need to
    # construct the urls more carefully and care for url encoding.

    def get_search_page(self, moviehash, sublanguageid, file_count=1):
        # keep signature and cache key in sync

        """
        GET search result simplexml (cached).

        http://trac.opensubtitles.org/projects/opensubtitles/wiki/PageInXML

        Takes:
            moviehash - hash of movie (hex string)
                cf. module opensubtitles.hash
            sublanguageid - subtitle language according to ISO 639-2 (string)
            file_count - how many files make up the movie?

        Returns:
            content of search result page (xml)

        Side effect:
            caching
        """

        cache_key = "{}-{}-{}.xml".format(moviehash, sublanguageid, file_count)

        url = ( "http://"
            + self.server
            + "/en"
            + "/search"
            + "/sublanguageid-{}".format(sublanguageid)
            + "/moviehash-{}".format(moviehash)
            + "/subsumcd-{}".format(file_count)
            + "/simplexml"
            )
        logging.debug( "search_page_url: {}".format(url) )

        content = cache.get_content_cached(
            cache_subdir = "search-results",
            cache_key = cache_key,
            url = url,
            )
        return content

    def get_subtitle_archive(self, url):
        # keep signature and cache key in sync

        """
        GET subtitle zip archive (cached).

        Takes:
            subtitle_id - subtitle id (numeric string)

        Returns:
            content of subtitle zip archive

        Side effect:
            caching
        """

        cache_key = "{}.zip".format( url.split("/")[-1] )

        content = cache.get_content_cached(
            cache_subdir = "subtitle-archive",
            cache_key = cache_key,
            url = url,
            )
        return content
