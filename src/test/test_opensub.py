#! /usr/bin/python

import errno
import os
import sys
import xml.etree.ElementTree as etree
import unittest

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


class HashTestCase(unittest.TestCase):

    def test__hash_file__breakdance_avi(self):

        test_file = os.path.join(test_data_dir(), "breakdance.avi")
        try:
            with open(test_file, "rb") as f:
                hash = opensub.hash_file(f)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise Exception("Missing test data. See {} .".format(
                    os.path.join(test_data_dir(), "README.txt")))

        self.assertEqual(hash, "8e245d9679d31e12")

    def test__hash_file__file_too_small(self):

        """
        File hashing should fail on empty and small files, because the
        hash algorithm is undefined for files smaller than 128 KiB.
        """

        with open("/dev/null", "rb") as f:
            with self.assertRaises(Exception):
                opensub.hash_file(f)


class ExtractTestCase(unittest.TestCase):

    def test__extract_by_xpath__found(self):

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
            result_urls = opensub.main.extract_by_xpath(
                xml_file=f,
                xpath="./results/subtitle/download",
                fun=lambda elem: elem.text,
                )

        self.assertEqual(result_urls, expected)

    def test__extract_by_xpath__not_found(self):

        test_file = os.path.join(
            test_data_dir(),
            "en_search_imdbid-0_sublanguageid-eng_simplexml.xml")
        with open(test_file, "r") as f:
            result_urls = opensub.main.extract_by_xpath(
                xml_file=f,
                xpath="./results/subtitle/download",
                fun=lambda elem: elem.text,
                )

        self.assertEqual(result_urls, [])

    def test__extract_by_xpath__junk(self):

        """Search result extraction should fail on malformed documents."""

        test_file = os.path.join(test_data_dir(), "junk.xml")
        with open(test_file, "r") as f:
            with self.assertRaises(etree.ParseError):
                opensub.main.extract_by_xpath(xml_file=f, xpath="junk")


class ArchiveTestCase(unittest.TestCase):

    def test__extract_subtitles__4130212_zip(self):

        expected = [
            "Birdman of Alcatraz - 1.srt",
            "Birdman of Alcatraz - 2.srt",
            ]

        test_file = os.path.join(test_data_dir(), "4130212.zip")

        with open(test_file, "rb") as f:

            archive = opensub.SubtitleArchive(url="http://127.0.0.1/dummy/")
            archive.tempfile = f
            subtitle_names = [t[1] for t in archive.open_subtitle_files()]

            self.assertEqual(subtitle_names, expected)


if __name__ == "__main__":
    unittest.main()
