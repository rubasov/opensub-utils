# opensub-utils

CLI utilities for opensubtitles.org written according to the Unix
philosophy: "do one thing and do it well".

## Intro

Do you hunt for subtitles based on movie title, file name, file size,
frame rate? Do you still adjust the subtitle delay and frame rate in
case you didn't find the perfect subtitle file? Are you tired of all this?

## opensub-get

This program calculates a hash of the movie you give it, and queries
opensubtitles.org by hash. The hash is a function of file size and
_content_. Therefore you're guaranteed to get an exact match.  Quality
still may be high or low, but someone uploaded the subtitle file(s)
for the exact same video file(s) you have.

## opensub-hash

This program calculates and prints the hash of video files you give it.

## Examples

    $ ls -1
    la jetee.mkv
    $ opensub-get -l eng "la jetee.mkv"
    $ ls -1
    la jetee.mkv
    la jetee.srt

    $ ls -1
    Birdman of Alcatraz (1962) DVDRip (SiRiUs sHaRe) CD1.avi
    Birdman of Alcatraz (1962) DVDRip (SiRiUs sHaRe) CD2.avi
    $ opensub-get *CD*.avi
    $ ls -1
    Birdman of Alcatraz (1962) DVDRip (SiRiUs sHaRe) CD1.avi
    Birdman of Alcatraz (1962) DVDRip (SiRiUs sHaRe) CD1.srt
    Birdman of Alcatraz (1962) DVDRip (SiRiUs sHaRe) CD2.avi
    Birdman of Alcatraz (1962) DVDRip (SiRiUs sHaRe) CD2.srt

    $ ls -1 Mad.Men.S05E*
    Mad.Men.S05E01-E02.HDTV.x264-ASAP.mp4
    Mad.Men.S05E03.HDTV.XviD-FQM.avi
    Mad.Men.S05E04.HDTV.x264-ASAP.mp4
    Mad.Men.S05E05.Signal.30.HDTV.XviD-FQM.avi
    ...
    $ for ep in Mad.Men.S05E* ; do opensub-get "$ep" ; done
    $ ls -1 Mad.Men.S05E*
    Mad.Men.S05E01-E02.HDTV.x264-ASAP.mp4
    Mad.Men.S05E01-E02.HDTV.x264-ASAP.srt
    Mad.Men.S05E03.HDTV.XviD-FQM.avi
    Mad.Men.S05E03.HDTV.XviD-FQM.srt
    Mad.Men.S05E04.HDTV.x264-ASAP.mp4
    Mad.Men.S05E04.HDTV.x264-ASAP.srt
    Mad.Men.S05E05.Signal.30.HDTV.XviD-FQM.avi
    Mad.Men.S05E05.Signal.30.HDTV.XviD-FQM.srt
    ...

    $ opensub-hash "la jetee.mkv"
    e279199f54b5cb9d la jetee.mkv

# See also

* http://opensubtitles.org
* `opensub-get --help`
* `opensub-get --manual`
* `opensub-hash --help`
* [install instructions](install.md)
* [notes for developers](developer-notes.md)
