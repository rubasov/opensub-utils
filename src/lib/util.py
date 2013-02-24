import errno
import itertools
import logging
import os
import shutil
import sys

import six
if six.PY3:
    import urllib.request as urllib_request
else:
    import urllib2 as urllib_request


class FilenameBuilder(object):

    """
    Construct filenames for subtitles.

    First, I wanted to write subtitles according to the standard subtitle
    lookup rules of video players. That is - given the movie path,
    replace the movie extension with the subtitle extension.

    Later, I ended up with a much more generic templating. For details
    see NAMING SCHEMES in the manual of opensub-get.
    """

    def __init__(self, template="{video/dir}{video/base}{subtitle/ext}"):

        """
        Takes:
            template - string optionally containing template variables
                see tpl_dict below for valid template variables
        """

        self.template = template

    def _split_dir_base_ext(self, path):

        """
        Split a file path 3-way.

        Example:

            path : foo/bar/baz.qux

            dir  : foo/bar/
            base : baz
            ext  : .qux

        The concatenation of dir, base and ext add up to a path
        equivalent to the original.
        """

        if path == "":
            raise Exception("invalid path: empty string")

        head, tail = os.path.split(path)
        dir = os.path.join(head, "")  # (1)
        base, ext = os.path.splitext(tail)

        # NOTE (1) os.path.split strips trailing (back)slashes,
        #          we have to add them back

        if tail in ("", ".", ".."):  # (2)
            raise Exception(
                "invalid (dir-like) path: {}".format(path))

        # NOTE (2) path looks like a dir, in unix terms:
        #                 path ends in /
        #              or last component of path is .
        #              or last component of path is ..
        #
        # We reject dir-like paths, because they can too easily lead
        # to hideous things like: /dir/ + subtitle.srt -> /dir/.srt

        return dir, base, ext

    def build(self, video=None, subtitle=None, num=None):

        """
        Takes:
            video - path to video file
            subtitle - path of subtitle in the archive
            num - file number for numbered templating

        Returns:
            path that can be used to write the subtitle to
        """

        v_dir, v_base, v_ext = self._split_dir_base_ext(video)
        s_dir, s_base, s_ext = self._split_dir_base_ext(subtitle)

        template_dict = {
            "num": num,

            "video/dir": v_dir,
            "video/base": v_base,
            "video/ext": v_ext,

            "subtitle/dir": s_dir,
            "subtitle/base": s_base,
            "subtitle/ext": s_ext,
            }

        # Delete keys whose value is None from the template dictionary.
        # This way format() will raise a KeyError when
        # it encounters a template variable without a value.
        if six.PY3:
            template_dict.update((k, v) for k, v
                in template_dict.items() if v is not None)
        else:
            template_dict.update((k, v) for k, v
                in template_dict.iteritems() if v is not None)

        # python3.2 gives PendingDeprecationWarning:
        #     object.__format__ with a non-empty format string is deprecated
        #
        # I'm completely lost what would be the non-deprecated version.
        # -- rubasov
        name_built = self.template.format(**template_dict)

        return name_built


def binary_stdout():

    """Binary stdout: accepts bytes, not strings."""

    if six.PY3:
        # switch to binary stdout, python3 only
        # http://bugs.python.org/issue4571#msg77230
        return sys.stdout.buffer
    else:
        return sys.stdout


def safe_open(path, overwrite=False):

    """
    Open but do not overwrite by default. Open and overwrite on request.

    Takes:
        path - path to open
        overwrite - allow/disallow to overwrite existing files (boolean)

    Special case:
        path='-': Return stdout without opening it.

    """

    if path == "-":
        return binary_stdout()

    if overwrite:
        return open(path, "wb")

    else:
        # Open the file only if the open actually creates it,
        # that is do not overwrite an existing file.

        # FIXME how much portable is this? unix only?
        # http://docs.python.org/2/library/os.html#open-flag-constants
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        return os.fdopen(fd, "wb")


def safe_close(file):

    """Close anything, but stdout."""

    if file != binary_stdout():
        file.close()


def extract_archive(archive, movie, builder, overwrite=False):

    """
    Extract subtitles from archive according to movie and naming scheme.

    Takes:
        archive - opensub.SubtitleArchive() object
        movie - list of video files in "natural order"
        builder - FilenameBuilder() object
        overwrite - pass down to safe_open

    Returns:
        number of subtitle files extracted and successfully written
    """

    template_counter = itertools.count(1)
    count_of_files_written = 0

    for template_num, video_path, subtitle_file in zip(
        template_counter, movie, archive.yield_open()):

        dst = builder.build(
            video=video_path,
            subtitle=subtitle_file.name,
            num=template_num,
            )

        logging.debug("src: {}".format(subtitle_file.name))
        logging.debug("dst: {}".format(dst))

        try:
            dst_file = safe_open(dst, overwrite=overwrite)
        except OSError as e:
            if e.errno == errno.EEXIST:
                logging.warning(
                    "refusing to overwrite file: {}".format(dst))
            else:
                raise
        else:
            shutil.copyfileobj(subtitle_file, dst_file)
            count_of_files_written += 1
            safe_close(dst_file)

    return count_of_files_written
