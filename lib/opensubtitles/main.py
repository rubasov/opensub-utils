#! /usr/bin/python

import feedparser
import logging
import StringIO
import urlparse
import zipfile

import opensubtitles.hash
import opensubtitles.useragent
import subtitle

# FIXME use simplexml
#
# http://trac.opensubtitles.org/projects/opensubtitles/wiki/PageInXML
# http://www.opensubtitles.org
#     /en/search/sublanguageid-eng
#     /moviehash-e3d98ed94c65c038/subsumcd-2/simplexml
#
# xmlstarlet select --template --value-of \
#     "/search/results/subtitle[1]/download"
def extract_result_urls(atom_xml):

    """
    Extract search result URLs from atom feed.

    Takes:
        atom_xml - xml string of atom feed

    Returns:
        list of search result URLs (same order as in feed)
    """

    doc = feedparser.parse(atom_xml)

    if len(doc.entries) == 0:
        raise Exception("no search result in feed"
        + "maybe the movie has a subtitle stream?" )

    rv = map(
        lambda entry: entry.links[0]['href'],
        doc.entries )
    return rv

def extract_subtitle_id(href):

    """
    Extract subtitle id from search result URL.

    Takes:
        href - URL string
            e.g. "http://www.opensubtitles.org/en/subtitles/3910726/blow-en"

    Returns:
        subtitle ID string
            e.g. "3910726"

    Raises:
        Exception - missing subtitle id
        Exception - subtitle id is not numeric
    """

    url = urlparse.urlparse(href)
    path_elements = url.path.split("/") # maybe FIXME re.split(r"/+", ...)

    try:
        subtitle_id = path_elements[ path_elements.index("subtitles") + 1 ]
    except ValueError, IndexError:
        raise Exception("missing subtitle id from url: {}".format(href))

    if not subtitle_id.isdigit():
        raise Exception("subtitle id is not numeric: {}".format(subtitle_id))

    logging.debug( "subtitle_id: {}".format(subtitle_id) )
    return subtitle_id

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

def get_subtitle(movie_file_list, subtitle_language):

    def best_result_url(lst):
        return lst[0]

    #def best_candidate_for_subtitle(subtitle_list):
    #    for sub in sorted(subtitle_list):
    #        if subtitle.path_has_subtitle_extension( sub.name ):
    #            return sub
    #    raise Exception("could not find known subtitle extension in archive")

    ua = opensubtitles.useragent.UserAgent( server = "www.opensubtitles.org" )

    subtitle_list = \
        extract_subtitles(
        ua.get_subtitle_archive(
        extract_subtitle_id(
        best_result_url(
        extract_result_urls(
        ua.get_search_page(
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
