#! /usr/bin/python

import os
import StringIO
import sys
import unittest

sys.path.append(
    os.path.join(
        os.path.dirname(
            os.path.realpath(
                __file__)),
        "..",
        "lib"))

import opensubtitles


class OpensubtitlesTestCase(unittest.TestCase):

    def setUp(self):

        self.test_data_dir = os.path.join(
            os.path.dirname(
                os.path.realpath(
                    __file__)),
            "test-data")

    def test__file_hash__breakdance_avi(self):

        test_file = os.path.join(self.test_data_dir, "breakdance.avi")
        hash_value = opensubtitles.file_hash(path=test_file)
        self.assertEqual(hash_value, "8e245d9679d31e12")

    def test__file_hash__file_too_small(self):

        test_file = os.path.join(self.test_data_dir, "empty.avi")
        self.assertRaises(Exception,
            opensubtitles.file_hash, {'path': test_file})

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
            self.test_data_dir, "search-results-simplexml.xml")
        with open(test_file, "r") as f:
            result_urls = opensubtitles.extract_subtitle_urls(f)

        self.assertEqual(result_urls, expected)

    def test__extract_subtitle_urls__not_found(self):

        test_file = os.path.join(
            self.test_data_dir, "no-results-simplexml.xml")
        with open(test_file, "r") as f:
            self.assertRaises(Exception,
                opensubtitles.extract_subtitle_urls, f)

    def test__extract_subtitle_urls__malformed_xml(self):

        self.assertRaises(Exception,
            opensubtitles.extract_subtitle_urls,
            StringIO.StringIO("<<junk>>"))

    def test__extract_subtitles__4130212_zip(self):

        expected = [
            "Birdman of Alcatraz - 1.srt",
            "Birdman of Alcatraz - 2.srt",
            ]

        test_file = os.path.join(self.test_data_dir, "4130212.zip")
        with open(test_file, "r") as z:
            subtitle_list = opensubtitles.extract_subtitles(
                zip_content=z.read())
            subtitle_names = [s.name for s in subtitle_list]

        self.assertEqual(subtitle_names, expected)


if __name__ == "__main__":
    unittest.main()
