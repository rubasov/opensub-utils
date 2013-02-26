#! /usr/bin/python

import os
import shutil
import subprocess
import sys
import unittest

import six
if six.PY3:
    import urllib.request as urllib_request
else:
    import urllib2 as urllib_request

sys.path.append(
    os.path.join(
        os.path.dirname(
            os.path.realpath(
                __file__)),
        "..",
        "lib"))

import opensub


def bin_dir():

    return os.path.join(
        os.path.dirname(
            os.path.realpath(
                __file__)),
        "..",
        "bin")


def test_data_dir():

    return os.path.join(
        os.path.dirname(
            os.path.realpath(
                __file__)),
        "test-data")


class HashTestCase(unittest.TestCase):

    def setUp(self):

        """Download breakdance.avi, if we don't have it yet."""

        self.test_avi = os.path.join(test_data_dir(), "breakdance.avi")

        if not os.path.exists(self.test_avi):
            src = urllib_request.urlopen(
                "http://www.opensubtitles.org/addons/avi/breakdance.avi")
            with open(self.test_avi, "wb") as dst:
                shutil.copyfileobj(src, dst)
            src.close()

    def test__hash_file__breakdance_avi(self):

        with open(self.test_avi, "rb") as f:
            hash = opensub.hash_file(f)
        self.assertEqual(hash, "8e245d9679d31e12")

    def test__hash_file__file_too_small(self):

        """
        File hashing should fail on empty and small files, because the
        hash algorithm is undefined for files smaller than 128 KiB.
        """

        with open("/dev/null", "rb") as f:
            with self.assertRaises(Exception):
                opensub.hash_file(f)

    def test__opensub_hash__breakdance_avi(self):

        expected = "8e245d9679d31e12 {}\n".format(self.test_avi).encode("utf8")

        out = subprocess.check_output([
            sys.executable,
            os.path.join(bin_dir(), "opensub-hash"),
            self.test_avi])

        self.assertEqual(out, expected)

    def test__opensub_hash__no_such_file(self):

        exit_code = os.system("{} {} {}".format(
            sys.executable,
            os.path.join(bin_dir(), "opensub-hash"),
            "non-existent",
            ))

        self.assertTrue(exit_code != 0)


if __name__ == "__main__":
    unittest.main()
