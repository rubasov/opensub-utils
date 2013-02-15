import logging
import os
import sys

import six
if six.PY3:
    import urllib.request as urllib_request
else:
    import urllib2 as urllib_request


def setup_logging(verbosity,
    fmt="%(levelname)s: %(filename)s:%(lineno)d: %(message)s"):

    """
    Set log level and format.

    Takes:
        verbosity - verbosity level: 0, 1, 2

    Side effect:
        changes global logging settings
    """

    verbosity_to_level = {0: "WARNING", 1: "INFO", 2: "DEBUG"}

    try:
        # turn symbolic level to numeric level
        num_level = getattr(logging, verbosity_to_level[verbosity])
    except KeyError:
        raise Exception("invalid verbosity level: {}".format(verbosity))

    logging.basicConfig(level=num_level, format=fmt)

    return None


def default_opener(version, program=sys.argv[0]):

    """Create urllib(2) opener to always add user-agent header."""

    user_agent = "{}/{}".format(os.path.basename(program), version)

    headers = list()
    headers.append(("User-Agent", user_agent))

    # This is a hack for less intrusive testing. Do not rely on it ever.
    # $ magic=more http_proxy=127.0.0.1:8123 program ...
    if "magic" in os.environ:
        logging.warning("env(magic) present, anything may happen")
        headers.append(("Cache-Control", "only-if-cached"))

    opener = urllib_request.build_opener()
    opener.addheaders = headers

    return opener


class FilenameBuilder(object):

    """
    Construct filenames for subtitles.

    First, I wanted to write subtitles according to the standard subtitle
    lookup rules of video players. That is - given the movie path,
    replace the movie extension with the subtitle extension.

    Later, I ended up with a much more generic templating. For details
    see NAMING SCHEMES in the manual of opensub-get.
    """

    def __init__(self,
        template="{video/dir}{video/base}{subtitle/ext}",
        start=1, step=1):

        """
        Takes:
            template - string optionally containing template variables
                see tpl_dict below for valid template variables
        """

        self.template = template
        self.start = start
        self.step = start

        self.num = self.start

    def build(self, video, subtitle):

        """
        Takes:
            video - path to video file
            subtitle - path of subtitle in the archive

        Returns:
            path that can be used to write the subtitle to
        """

        v_dir, v_unix_base = os.path.split(video)
        v_base, v_ext = os.path.splitext(v_unix_base)

        s_dir, s_unix_base = os.path.split(subtitle)
        s_base, s_ext = os.path.splitext(s_unix_base)

        tpl_dict = {
            "num": self.num,

            "video/dir": v_dir,
            "video/base": v_base,
            "video/ext": v_ext,

            "subtitle/dir": s_dir,
            "subtitle/base": s_base,
            "subtitle/ext": s_ext,
            }

        name_built = self.template.format(**tpl_dict)

        self.num += self.step
        return name_built


def safe_open(path, overwrite=False):

    """
    Open but do not overwrite by default. Open and overwrite on request.

    Handle Unix convention of path="-" too.

    Takes:
        path - path to open
        overwrite - allow/disallow to overwrite existing files (boolean)
    """

    if path == "-":
        return sys.stdout

    if overwrite:
        return open(path, "wb")

    else:
        # Open the file only if the open actually creates it,
        # that is do not overwrite an existing file.

        # FIXME how much portable is this? unix only?
        # http://docs.python.org/2/library/os.html#open-flag-constants
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        return os.fdopen(fd, "wb")
