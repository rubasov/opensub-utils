"""See __init__.py for what is considered public here."""

import errno
import itertools
import logging
import os
import shutil
import struct
import sys
import tempfile
import xml.etree.ElementTree as etree
import zipfile

try:
    import six
except ImportError:
    class six(object):
        PY3 = False

if six.PY3:
    import urllib.request as urllib_request
else:
    import urllib2 as urllib_request


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

        # http://docs.python.org/2/library/os.html#open-flag-constants
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        return os.fdopen(fd, "wb")


def safe_close(file_):

    """Close anything, but stdout."""

    if file_ != binary_stdout():
        file_.close()


class NamedFile(object):

    """File-like object with a name attribute."""

    def __init__(self, file_, name):

        self.file_ = file_
        self.name = name

    def __getattr__(self, attr):

        """
        Delegate attribute lookups to the underlying file in the same manner
        as tempfile.NamedTemporaryFile does, but without attribute caching.
        """

        return getattr(self.__dict__["file_"], attr)


def hash_file(file_, file_size=None):

    """
    Hash an open file.

    The hash algorithm and some of the code comes from:
    http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes

    A multi-file movie's hash is the hash of the first file.

    Takes:
        file - seekable file-like object
        file_size - size of file in bytes

    Returns:
        hash as a zero-padded, 16-digit, lower case hex string

    Raises:
        Exception - file too small: < 128 KiB
    """

    fmt = "q"  # long long
    buf_size = struct.calcsize(fmt)
    chunk_size = 64 * 1024  # bytes

    assert chunk_size % buf_size == 0

    def chunk(hash_, seek_args):
        file_.seek(*seek_args)
        for _ in range(chunk_size // buf_size):
            buf = file_.read(buf_size)
            hash_ += struct.unpack(fmt, buf)[0]
            hash_ &= 0xFFFFFFFFFFFFFFFF  # to remain as 64 bit number
        return hash_

    saved_pos = file_.tell()
    try:
        if file_size is None:
            file_.seek(0, os.SEEK_END)
            file_size = file_.tell()

        if file_size < 2 * chunk_size:
            raise Exception(
                "file too small: < {} bytes".format(2 * chunk_size))

        hash_ = file_size
        hash_ = chunk(hash_, seek_args=(0, os.SEEK_SET))
        hash_ = chunk(hash_, seek_args=(-chunk_size, os.SEEK_END))

    finally:
        file_.seek(saved_pos, os.SEEK_SET)

    hex_str = "{:016x}".format(hash_)
    logging.info("hash: {}".format(hex_str))
    return hex_str


class UserAgent(object):

    """Communicate with subtitle servers."""

    def __init__(self, server, opener=urllib_request.build_opener()):

        """
        Takes:
            server - FQDN or IP of server
                e.g. "www.opensubtitles.org"
            opener - urllib(2) opener object
        """

        self.server = server
        self.opener = opener

    # FIXME Which variant of ISO 639 is accepted?
    #
    # So far I have used the 3-letter codes like 'eng', 'hun'...

    def _search_page_url(
        self, movie_hash, language, cd_count=1, _fmt="simplexml"):

        """
        Construct search page URL.

        Takes:
            movie_hash - hash of movie (hex string)
                cf. movie_hash()
            language - preferred language (ISO 639 code string)
            cd_count - how many video files make up the movie?

        Returns:
            search page URL
        """

        url = ("http://"
            + self.server
            + "/en"
            + "/search"
            + "/sublanguageid-{}".format(language)
            + "/moviehash-{}".format(movie_hash)
            + "/subsumcd-{}".format(cd_count)
            + "/{}".format(_fmt)
            )
        logging.debug("search_page_url: {}".format(url))
        return url

    def search(self, movie, language):

        """
        Takes:
            movie - list of video file paths in "natural order"
            language - ISO 639 code of subtitle language

        Returns:
            list of subtitle archive URLs (ordered as in the search results)
        """

        with open(movie[0], "rb") as file_:
            movie_hash = hash_file(file_)

        cd_count = len(movie)

        search_page_url = self._search_page_url(
            language=language,
            movie_hash=movie_hash,
            cd_count=cd_count,
            )

        # future FIXME use absolute xpath: /search/results/subtitle/download
        #
        # findall with an absolute xpath is broken in
        # xml.etree.Elementree 1.3.0 . I couldn't find the issue on
        # bugs.python.org, but here is the code issuing the warning:
        # /usr/lib/python2.7/xml/etree/ElementTree.py:745

        search_page_xml = self.opener.open(search_page_url)

        tree = etree.parse(search_page_xml)
        search_results = [elem.text for elem in
            tree.findall("./results/subtitle/download")]

        search_page_xml.close()

        return search_results

    def __repr__(self):

        return "{}({!r})".format(self.__class__, self.__dict__)

    def __str__(self):

        return "{}({!r})".format(self.__class__, self.server)


class SubtitleArchive(object):

    """
    Access subtitles in a subtitle archive.

    I haven't ever found a specification for opensubtitles.org's subtitle
    archive format, so I'm listing my basic assumptions here. -- rubasov

    The archive is a valid .zip file with any name.
    The .zip contains no directories.
        (Though we try to handle the presence of directories gracefully.)
    The .zip contains one ore more subtitle file(s).
    A subtitle file has one of the extensions listed here (case insensitive):
        http://trac.opensubtitles.org/projects/opensubtitles
            /wiki/DevReadFirst#Subtitlefilesextensions
    All subtitle files in one archive belong to the same movie.
    There is exactly one subtitle file for each video file of the movie.
        (Think of multi-CD movies.)
    There are no other subtitle files in the archive.
    All other files in the archive can be ignored.
        (e.g. .nfo files)
    The "natural order" of the subtitle files is the same as if we have
        ordered them by their archived names case insensitively.
    """

    def __init__(
        self,
        url,
        opener=urllib_request.build_opener(),
        sort_key=str.lower,
        extensions=set(
            [".srt", ".sub", ".smi", ".txt", ".ssa", ".ass", ".mpl"]),
        ):

        """
        Should use it as a context manager:
            with SubtitleArchive() as archive:
                ...

        Takes:
            url - url of the subtitle archive
            opener - urllib(2) opener object
            sort_key - determines yield order of subtitles
            extensions - iterable of valid subtitle extensions
                lower case, include leading dot
        """

        self.url = url
        self.opener = opener
        self.sort_key = sort_key
        self.extensions = extensions

        # We may set these directly for testing purposes.
        self.tempfile = None
        self.zipfile = None

        logging.debug("archive_url: {}".format(self.url))

    def __enter__(self):

        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):

        if self.zipfile is not None:
            self.zipfile.close()

        if self.tempfile is not None:
            self.tempfile.close()
            # tempfile is responsible to delete
            # the NamedTemporaryFile at this point

    def _urlopen_via_tempfile(self):

        # zipfile needs seekable file-like objects.
        # Therefore we download the remote file to a local temporary file.

        # See the notes here on why we need a *Named*TemporaryFile:
        # http://docs.python.org/2/library/zipfile#zipfile.ZipFile.open

        if self.tempfile is None:
            dst = tempfile.NamedTemporaryFile()
            src = self.opener.open(self.url)
            shutil.copyfileobj(src, dst)
            src.close()
            dst.seek(0, os.SEEK_SET)
            self.tempfile = dst

    def _open_as_zipfile(self):

        if self.zipfile is None:
            self._urlopen_via_tempfile()
            self.zipfile = zipfile.ZipFile(self.tempfile.name)

    def yield_open(self):

        """
        Yields:
            subtitle_file with an extra name attribute in the order
            determined by sort_key.
        """

        self._open_as_zipfile()

        for name in sorted(self.zipfile.namelist(), key=self.sort_key):

            ext = os.path.splitext(name)[1]
            if ext.lower() not in self.extensions:
                continue

            with self.zipfile.open(name) as file_:
                yield NamedFile(file_, name)

    def extract(self, movie, builder, overwrite=False):

        """
        Extract subtitles from archive according to movie and naming scheme.

        Takes:
            movie - list of video files in "natural order"
            builder - FilenameBuilder() object
            overwrite - pass down to safe_open

        Returns:
            number of subtitle files extracted and successfully written
        """

        template_counter = itertools.count(1)
        count_of_files_written = 0

        for template_num, video_path, subtitle_file in zip(
            template_counter, movie, self.yield_open()):

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

    def __repr__(self):

        return "{}({!r})".format(self.__class__, self.__dict__)

    def __str__(self):

        return "{}({!r})".format(self.__class__, self.url)


class FilenameBuilder(object):

    """
    Construct filenames for subtitles.

    First, I wanted to write subtitles according to the standard subtitle
    lookup rules of video players. That is - given the movie path,
    replace the movie extension with the subtitle extension.

    Later, I ended up with a much more generic templating. For details
    see Naming Schemes in the manual of opensub-get.

    NOTE We do not protect our user from silly combinations of
         templates and input filenames like:

    template  : {video/dir}{video/base}{subtitle/ext}
    filenames : /dir/ + subtitle.srt -> /dir/.srt
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
        equivalent to the original (roundtrip safety).
        """

        if path == "":
            raise Exception("invalid path: empty string")

        head, tail = os.path.split(path)

        # os.path.split stripped trailing slashes,
        # we have to add them back for roundtrip safety.
        dir_ = os.path.join(head, "")
        base, ext = os.path.splitext(tail)

        return dir_, base, ext

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

        # FIXME python3.2 PendingDeprecationWarning:
        #     object.__format__ with a non-empty format string is deprecated
        #
        # I'm completely lost what would be the non-deprecated version.
        # -- rubasov
        name_built = self.template.format(**template_dict)

        return name_built
