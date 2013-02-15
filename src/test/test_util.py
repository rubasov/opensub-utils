#! /usr/bin/python

import os
import sys
import unittest

sys.path.append(
    os.path.join(
        os.path.dirname(
            os.path.realpath(
                __file__)),
        "..",
        "lib"))

import util


class DefaultTemplateTestCase(unittest.TestCase):

    def setUp(self):

        self.template = "{video/dir}{video/base}{subtitle/ext}"

    def _assert(self, video, subtitle, expected):

        builder = util.FilenameBuilder(template=self.template)
        fname = builder.build(video=video, subtitle=subtitle)
        self.assertEqual(fname, expected)

    def test__all(self):

        # Yeah, I know that multiple asserts are not recommended in a single
        # test method, but I couldn't bear the repetitive code. In the
        # traceback you'll see which assert failed anyway... -- rubasov

        a = self._assert

        a("",               "",                  "")
        a("",               "subtitle.srt",      ".srt")
        a("video.avi",      "",                  "video")
        a("video.avi",      "subtitle.srt",      "video.srt")
        a("video",          "subtitle.srt",      "video.srt")
        a("video.avi",      "subtitle",          "video")
        a("foo.bar.avi",    "baz.qux.srt",       "foo.bar.srt")
        a(".video.avi",     ".subtitle.srt",     ".video.srt")
        a("dir/video.avi",  "subtitle.srt",      "dir/video.srt")
        a("video.avi",      "dir/subtitle.srt",  "video.srt")
        a("/dir/video.avi", "subtitle.srt",      "/dir/video.srt")
        a("video.avi",      "/dir/subtitle.srt", "video.srt")
        a("/video.avi",     "subtitle.srt",      "/video.srt")
        a("video.avi",      "/subtitle.srt",     "video.srt")
        a("/dir/",          "subtitle.srt",      "/dir/.srt")  # (1)
        a("video.avi",      "/dir/",             "video")

        # NOTE (1) This is hideous, we should prevent such input.


class RoundTripTestCase(unittest.TestCase):

    def setUp(self):

        self.template = "{subtitle/dir}{subtitle/base}{subtitle/ext}"

    def _assert(self, video, subtitle, expected):

        builder = util.FilenameBuilder(template=self.template)
        fname = builder.build(video=video, subtitle=subtitle)
        self.assertEqual(fname, expected)

    def test__all(self):

        a = self._assert

        a("junk", "subtitle.srt",      "subtitle.srt")
        a("junk", "dir/subtitle.srt",  "dir/subtitle.srt")
        a("junk", "/dir/subtitle.srt", "/dir/subtitle.srt")
        a("junk", "/subtitle.srt",     "/subtitle.srt")


class ExtractTestCase(unittest.TestCase):

    def setUp(self):

        self.template = "{subtitle/base}{subtitle/ext}"

    def test__extract_to_current_dir(self):

        builder = util.FilenameBuilder(template=self.template)
        fname = builder.build(
            video="junk",
            subtitle="/dir/subdir/subtitle.srt",
            )
        self.assertEqual(fname, "subtitle.srt")


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
        self.assertEqual(fname, "movie-cd1.srt")

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
        self.assertEqual(fname, "movie-cd2.srt")


class SafeOpenTestCase(unittest.TestCase):

    # TODO test util.safe_open()
    pass


if __name__ == "__main__":
    unittest.main()
