#! /usr/bin/python

import logging
import urllib2

class UserAgent(object):

    """
    Wrap HTTP communication to subtitle servers.
    """

    def __init__(self, server, user_agent, http_proxy):
        self.server = server
        self.user_agent = user_agent
        self.http_proxy = http_proxy

    # maybe FIXME encode urls
    #
    # Depending on where the inputs come from you may need to
    # construct the urls more carefully and care for url encoding.

    def search_page_url(self, moviehash, sublanguageid, file_count=1):

        """
        Construct search page URL for simplexml format.

        http://trac.opensubtitles.org/projects/opensubtitles/wiki/PageInXML

        Takes:
            moviehash - hash of movie (hex string)
                cf. module opensubtitles.hash
            sublanguageid - subtitle language according to ISO 639 (string)
            file_count - how many files make up the movie?

        Returns:
            search page URL
        """

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
        return url

    def get(self, url):

        """
        GET URL with preset user agent and proxy.

        Takes:
            url - URL to get

        Returns:
            content of resource at URL
        """

        headers = { "User-Agent" : self.user_agent }
        req     = urllib2.Request(url=url, headers=headers)
        stream  = urllib2.urlopen(req)
        content = stream.read()
        stream.close()

        return content
