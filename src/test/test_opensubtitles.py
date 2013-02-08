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

        expected = map(
            "http://dl.opensubtitles.org/en/download/subad/{}".format,
                [ "4783694", "4651408", "4617272",
                "4504568", "3650786", "3562667",
                "93050", "130331", "141364", ])

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

    # TODO further tests
    #
    # test__extract_subtitles__*
    # test__UserAgent.*


if __name__ == "__main__":
    unittest.main()
