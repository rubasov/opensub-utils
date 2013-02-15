#! /usr/bin/python

import unittest

sys.path.append(
    os.path.join(
        os.path.dirname(
            os.path.realpath(
                __file__)),
        "..",
        "lib"))

import util


def test_data_dir():

    return os.path.join(
        os.path.dirname(
            os.path.realpath(
                __file__)),
        "test-data")


class UtilTestCase(unittest.TestCase):

    def test__pass(self):

        self.assertEqual(1, 1)


if __name__ == "__main__":
    unittest.main()
