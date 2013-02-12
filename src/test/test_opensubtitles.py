#! /usr/bin/python

import six
# implicit py2 import StringIO as six.BytesIO
# implicit py3 import io.BytesIO as six.BytesIO

import errno
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

import opensubtitles.hash
import opensubtitles.main


def test_data_dir():

    return os.path.join(
        os.path.dirname(
            os.path.realpath(
                __file__)),
        "test-data")


class HashTestCase(unittest.TestCase):

    def test__path__breakdance_avi(self):

        test_file = os.path.join(test_data_dir(), "breakdance.avi")
        try:
            hash = opensubtitles.hash.by_path(test_file)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise Exception("Missing test data. See {} .".format(
                    os.path.join(test_data_dir(), "README.txt")))
        self.assertEqual(hash, "8e245d9679d31e12")

    def test__path__file_too_small(self):

        """
        File hashing should fail on empty and small files, because the
        hash algorithm is undefined for files smaller than 128 KiB.
        """

        self.assertRaises(Exception, opensubtitles.hash.by_path, "/dev/null")


class MainTestCase(unittest.TestCase):

    def test__extract_subtitle_urls__found(self):

        expected = [
            "http://dl.opensubtitles.org/en/download/subad/4783694",
            "http://dl.opensubtitles.org/en/download/subad/4651408",
            "http://dl.opensubtitles.org/en/download/subad/4617272",
            "http://dl.opensubtitles.org/en/download/subad/4504568",
            "http://dl.opensubtitles.org/en/download/subad/3650786",
            "http://dl.opensubtitles.org/en/download/subad/3562667",
            "http://dl.opensubtitles.org/en/download/subad/93050",
            "http://dl.opensubtitles.org/en/download/subad/130331",
            "http://dl.opensubtitles.org/en/download/subad/141364",
            ]

        test_file = os.path.join(
            test_data_dir(),
            "en_search_imdbid-56119_sublanguageid-eng_simplexml.xml")
        with open(test_file, "r") as f:
            result_urls = opensubtitles.main.extract_subtitle_urls(f)

        self.assertEqual(result_urls, expected)

    def test__extract_subtitle_urls__not_found(self):

        """Search result extraction should fail on empty search results."""

        test_file = os.path.join(
            test_data_dir(),
            "en_search_imdbid-0_sublanguageid-eng_simplexml.xml")
        with open(test_file, "r") as f:
            self.assertRaises(opensubtitles.main.SubtitleNotFound,
                opensubtitles.main.extract_subtitle_urls, f)

    def test__extract_subtitle_urls__malformed_xml(self):

        """Search result extraction should fail on malformed documents."""

        self.assertRaises(Exception,
            opensubtitles.main.extract_subtitle_urls,
            six.BytesIO(six.b("<<junk>>")))

    def test__extract_subtitles__4130212_zip(self):

        expected = [
            "Birdman of Alcatraz - 1.srt",
            "Birdman of Alcatraz - 2.srt",
            ]

        test_file = os.path.join(test_data_dir(), "4130212.zip")
        with open(test_file, "rb") as z:
            subtitle_list = opensubtitles.main.extract_subtitles(
                zip_content=z.read())
            subtitle_names = [s.name for s in subtitle_list]

        self.assertEqual(subtitle_names, expected)


if __name__ == "__main__":
    unittest.main()
