import os
import shutil
import subprocess
import sys
import unittest

try:
    import six
except ImportError:
    class six(object):
        PY3 = False

if six.PY3:
    import urllib.request as urllib_request
else:
    import urllib2 as urllib_request

# Make it possible to run out of the working copy.
sys.path.insert(0,
    os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        "lib",
        ))

import opensub


def _bin_dir():

    return os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        "bin",
        )


def _test_data_dir():

    return os.path.join(
        os.path.dirname(__file__),
        "test-data",
        )


class MovieHash(unittest.TestCase):

    def setUp(self):

        """Download breakdance.avi, if we don't have it yet."""

        self.test_avi = os.path.join(_test_data_dir(), "breakdance.avi")
        self.test_avi_correct_hash = "8e245d9679d31e12"

        if not os.path.exists(self.test_avi):
            src = urllib_request.urlopen(
                "http://www.opensubtitles.org/addons/avi/breakdance.avi")
            with open(self.test_avi, "wb") as dst:
                shutil.copyfileobj(src, dst)
            src.close()

    def test__hash_of_breakdance_avi(self):

        """Calculate proper hash via function interface."""

        with open(self.test_avi, "rb") as file_:
            hash_ = opensub.hash_file(file_)
        self.assertEqual(hash_, self.test_avi_correct_hash)

    def test__file_too_small(self):

        """
        Fail to hash empty and small files.

        Because the hash is undefined for files < 128 KiB.
        """

        with open(os.devnull, "rb") as file_:
            with self.assertRaises(Exception):
                opensub.hash_file(file_)

    def test__cli_breakdance_avi(self):

        """Calculate proper hash via command line interface."""

        expected = "{} {}\n".format(
            self.test_avi_correct_hash, self.test_avi).encode("utf8")

        out = subprocess.check_output([
            sys.executable,
            os.path.join(_bin_dir(), "opensub-hash"),
            self.test_avi])

        self.assertEqual(out, expected)

    def test__cli_no_such_file(self):

        """Exit with non-zero for non-existent files."""

        exit_code = os.system(
            "{python} {script} no-such-file 2>/dev/null".format(
                python=sys.executable,
                script=os.path.join(_bin_dir(), "opensub-hash"),
                ))

        self.assertTrue(exit_code != 0)

    def test__cli_handle_errors_gracefully(self):

        """Hash files despite previous error."""

        expected = "{} {}\n".format(
            self.test_avi_correct_hash, self.test_avi).encode("utf8")

        out = subprocess.check_output(
            "{python} {script} no-such-file {test_avi} 2>/dev/null || true"
                .format(
                    python=sys.executable,
                    script=os.path.join(_bin_dir(), "opensub-hash"),
                    test_avi=self.test_avi,
                    ),
            shell=True,
            )

        self.assertEqual(out, expected)


if __name__ == "__main__":
    unittest.main()
