#! /usr/bin/python

import os
import sys
import unittest

from os.path import join

sys.path.append(
    os.path.join(
        os.path.dirname(
            os.path.realpath(
                __file__)),
        "..",
        "lib"))

import util


# Yeah, I know that multiple asserts are not recommended in a single
# test method, but I couldn't bear the repetitive code. In the
# traceback you'll see which assert failed anyway... -- rubasov

class DefaultTemplateTestCase(unittest.TestCase):

    def setUp(self):

        self.template = "{video/dir}{video/base}{subtitle/ext}"

    def _assertEqual(self, video, subtitle, expected):

        builder = util.FilenameBuilder(template=self.template)
        fname = builder.build(video=video, subtitle=subtitle)
        self.assertEqual(os.path.normpath(fname), expected)

    def test__combinations(self):

        self._assertEqual(
            "video.avi",
            "subtitle.srt",
            "video.srt",
            )
        self._assertEqual(
            "video",
            "subtitle.srt",
            "video.srt",
            )
        self._assertEqual(
            "video.avi",
            "subtitle",
            "video",
            )
        self._assertEqual(
            "foo.bar.avi",
            "baz.qux.srt",
            "foo.bar.srt",
            )
        self._assertEqual(
            ".video.avi",
            ".subtitle.srt",
            ".video.srt",
            )
        self._assertEqual(
            join("dir", "video.avi"),
            "subtitle.srt",
            join("dir", "video.srt"),
            )
        self._assertEqual(
            "video.avi",
            join("dir", "subtitle.srt"),
            "video.srt",
            )
        self._assertEqual(
            join("", "dir", "video.avi"),
            "subtitle.srt",
            join("", "dir", "video.srt"),
            )
        self._assertEqual(
            "video.avi",
            join("", "dir", "subtitle.srt"),
            "video.srt",
            )
        self._assertEqual(
            join("", "video.avi"),
            "subtitle.srt",
            join("", "video.srt"),
            )
        self._assertEqual(
            "video.avi",
            join("", "subtitle.srt"),
            "video.srt",
            )

    def _assertRaises(self, video, subtitle, expected):

        builder = util.FilenameBuilder(template=self.template)
        with self.assertRaises(expected):
            builder.build(video=video, subtitle=subtitle)

    def test__empty_string_is_invalid_path(self):

        self._assertRaises("",     "junk", Exception)
        self._assertRaises("junk", "",     Exception)

    def test__dir_like_path_is_invalid(self):

        self._assertRaises(".",                 "junk", Exception)
        self._assertRaises("..",                "junk", Exception)
        self._assertRaises(join("", ""),        "junk", Exception)
        self._assertRaises(join("", "dir", ""), "junk", Exception)
        self._assertRaises(join("dir", ".."),   "junk", Exception)

        self._assertRaises("junk", ".",                 Exception)
        self._assertRaises("junk", "..",                Exception)
        self._assertRaises("junk", join("", ""),        Exception)
        self._assertRaises("junk", join("", "dir", ""), Exception)
        self._assertRaises("junk", join("dir", ".."),   Exception)


class RoundTripTestCase(unittest.TestCase):

    def setUp(self):

        self.template = "{subtitle/dir}{subtitle/base}{subtitle/ext}"

    def _assertEqual(self, video, subtitle, expected):

        builder = util.FilenameBuilder(template=self.template)
        fname = builder.build(video=video, subtitle=subtitle)
        self.assertEqual(os.path.normpath(fname), expected)

    def test__all(self):

        self._assertEqual(
            "junk",
            "subtitle.srt",
            "subtitle.srt",
            )
        self._assertEqual(
            "junk",
            join("dir", "subtitle.srt"),
            join("dir", "subtitle.srt"),
            )
        self._assertEqual(
            "junk",
            join("", "dir", "subtitle.srt"),
            join("", "dir", "subtitle.srt"),
            )
        self._assertEqual(
            "junk",
            join("", "subtitle.srt"),
            join("", "subtitle.srt"),
            )


class ExtractTestCase(unittest.TestCase):

    def setUp(self):

        self.template = "{subtitle/base}{subtitle/ext}"

    def test__extract_to_current_dir(self):

        builder = util.FilenameBuilder(template=self.template)
        fname = builder.build(
            video="junk",
            subtitle=join("", "dir", "subdir", "subtitle.srt"),
            )
        self.assertEqual(os.path.normpath(fname), "subtitle.srt")


class NumTestCase(unittest.TestCase):

    def setUp(self):

        self.template = "movie-cd{num}{subtitle/ext}"

    def test__one(self):

        """movie-cd1.srt"""

        builder = util.FilenameBuilder(template=self.template)
        fname = builder.build(
            video="junk",
            subtitle="subtitle.srt",
            )
        self.assertEqual(os.path.normpath(fname), "movie-cd1.srt")

    def test__two(self):

        """movie-cd2.srt"""

        builder = util.FilenameBuilder(template=self.template)
        _ = builder.build(
            video="junk",
            subtitle="junk",
            )
        fname = builder.build(
            video="junk",
            subtitle="subtitle2.srt",
            )
        self.assertEqual(os.path.normpath(fname), "movie-cd2.srt")


class SafeOpenTestCase(unittest.TestCase):

    # TODO test util.safe_open()
    pass


if __name__ == "__main__":
    unittest.main()
