import os
import unittest


def _repo_root_dir():

    return os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        )


class Pep8Conformance(unittest.TestCase):

    """
    Check PEP8 conformance of all Python source files in this repo.

    Use pep8 as a command to be compatible with older versions of pep8:

    $ pep8 --version
    1.2

    future FIXME Use the pep8 module via 'import pep8' when you have
                 a sufficiently new version of pep8, like 1.4.4:

    http://pep8.readthedocs.org/en/1.4.4/advanced.html#automated-tests
    """

    def test__scripts(self):

        """pep8 bin/opensub-*"""

        exit_status = os.system(
            "pep8 {}".format(
                os.path.join(
                    _repo_root_dir(),
                    "bin",
                    "opensub-*",
                    )))
        self.assertEqual(exit_status, 0)

    def test__modules(self):

        """pep8 **/*.py"""

        exit_status = os.system("pep8 {}".format(_repo_root_dir()))
        self.assertEqual(exit_status, 0)


if __name__ == "__main__":
    unittest.main()
