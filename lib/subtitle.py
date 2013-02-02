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

class Subtitle(object):

    def __init__( self, name, content ):
        self.name = name
        self.content = content

