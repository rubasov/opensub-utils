"""
Version of the opensub-utils distribution.

  * Keep _one_ version number for the whole distribution.
    Don't start versioning the scripts, modules, etc separately.

  * Use Semantic Versioning v2 as a guide: http://semver.org/

  * Don't repeat the version in the commit message.

  * Tag the commit changing this file.
"""

# DO NOT FORGET TO TAG:
# python lib/opensub/version.py | xargs -r -I {} git tag -a {} -m {}

__version__ = "0.9.6"

if __name__ == "__main__":
    print(__version__)
