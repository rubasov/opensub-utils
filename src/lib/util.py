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
        verbosity - verbosity level like: 0, 1, 2

    Side effects:
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


def default_opener(program=sys.argv[0], version):

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


class ExtractBuilder(object):

    def build(self, archived_name, video_path):

        return os.path.basename(archived_name)


class TemplateBuilder(object):

    def __init__(self, template="{base}.{ext}", start=1):

        self.template = template
        self.num = start

    def build(self, archived_name, video_path):

        base = os.path.splitext(video_path)[0]
        ext = os.path.splitext(archived_name)[1][1:]

        out = self.template.format(base=base, ext=ext, num=self.num)

        self.num += 1
        return out


def safe_open(path, overwrite=False):

    """
    FIXME

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
