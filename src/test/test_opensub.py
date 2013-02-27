#! /usr/bin/python

import errno
import os
import sys
import tempfile
import xml.etree.ElementTree as etree
import unittest

from os.path import join

sys.path.append(
    os.path.join(
        os.path.dirname(
            os.path.realpath(
                __file__)),
        "..",
        "lib"))

import opensub
import opensub.main


def test_data_dir():

    return os.path.join(
        os.path.dirname(
            os.path.realpath(
                __file__)),
        "test-data")


class LookIntoArchive(unittest.TestCase):

    def test__extract_filenames_from_zip(self):

        """Should see filenames in the archive."""

        expected = [
            "Birdman of Alcatraz - 1.srt",
            "Birdman of Alcatraz - 2.srt",
            ]

        test_file = os.path.join(test_data_dir(), "4130212.zip")

        with open(test_file, "rb") as tfile:

            archive = opensub.SubtitleArchive(url="http://127.0.0.1/dummy/")
            archive.tempfile = tfile
            subtitle_names = [sfile.name for sfile in archive.yield_open()]

            self.assertEqual(subtitle_names, expected)


# Yeah, I know that multiple asserts are not recommended in a single
# test method, but I couldn't bear the repetitive code. In the
# traceback you'll see which assert failed anyway... -- rubasov

class DefaultTemplate(unittest.TestCase):

    def setUp(self):

        self.template = "{video/dir}{video/base}{subtitle/ext}"

    def _assertEqual(self, video, subtitle, expected):

        builder = opensub.FilenameBuilder(template=self.template)
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

        builder = opensub.FilenameBuilder(template=self.template)
        with self.assertRaises(expected):
            builder.build(video=video, subtitle=subtitle)

    def test__empty_string_is_invalid_path(self):

        self._assertRaises("", "junk", Exception)
        self._assertRaises("junk", "", Exception)


class RoundTrip(unittest.TestCase):

    def setUp(self):

        self.template = "{subtitle/dir}{subtitle/base}{subtitle/ext}"

    def _assertEqual(self, video, subtitle, expected):

        builder = opensub.FilenameBuilder(template=self.template)
        fname = builder.build(video=video, subtitle=subtitle)
        self.assertEqual(os.path.normpath(fname), expected)

    def test__roundtrip_safety(self):

        """A break-to-pieces-assemble cycle should result in the original."""

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


class Extract(unittest.TestCase):

    def setUp(self):

        self.template = "{subtitle/base}{subtitle/ext}"

    def test__extract_to_current_dir(self):

        builder = opensub.FilenameBuilder(template=self.template)
        fname = builder.build(
            video="junk",
            subtitle=join("", "dir", "subdir", "subtitle.srt"),
            )
        self.assertEqual(os.path.normpath(fname), "subtitle.srt")


class NumberedTemplate(unittest.TestCase):

    def setUp(self):

        self.template = "episode{num:02}{subtitle/ext}"

    def test__number_formatting(self):

        builder = opensub.FilenameBuilder(template=self.template)
        fname = builder.build(
            video="junk",
            subtitle="subtitle.srt",
            num=7,
            )
        self.assertEqual(os.path.normpath(fname), "episode07.srt")

    def test__missing_value_for_template_variable(self):

        builder = opensub.FilenameBuilder(template=self.template)
        with self.assertRaises(Exception):
            fname = builder.build(
                video="junk",
                subtitle="subtitle.srt",
                )


class SafeOpen(unittest.TestCase):

    def test__no_overwrite(self):

        """safe_open should not overwrite existing files."""

        tmpfile = tempfile.NamedTemporaryFile()
        with self.assertRaises(OSError) as cm:
            opensub.main.safe_open(tmpfile.name)
        self.assertEqual(cm.exception.errno, errno.EEXIST)
        tmpfile.close()


class BinaryStdoutTestCase(unittest.TestCase):

    def test__binary_write(self):

        try:
            opensub.main.binary_stdout().write(b"")
        except TypeError:
            self.fail("should be able to write binary data")


if __name__ == "__main__":
    unittest.main()
