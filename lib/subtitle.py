#! /usr/bin/python

import os

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

def possible_subtitle_paths(movie_path):
    base, extension = os.path.splitext(movie_path)

    assert extension != "", (
        "movie path has no extension: {}".format(movie_path) )

    path_set = set()
    for sub_ext in recognized_subtitle_extensions():
        path_set.add(base + sub_ext)

    return path_set

def movie_has_subtitle(movie_path):
    rv = any(
        map(
            os.path.isfile,
            possible_subtitle_paths(movie_path) ) )
    return rv

class Subtitle(object):

    def __init__( self, name, content ):
        self.name = name
        self.content = content

