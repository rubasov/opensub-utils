# Notes for developers

## Basic library usage pattern

1. calculate hash of movie: `opensub.file_hash()`

2. search for subtitles by: `opensub.UserAgent().search()`

    * movie hash
    * movie cd count
    * subtitle language

3. download and access subtitles

    * get them as file-like objects:
      `opensub.SubtitleArchive().yield_open()`
    * extract them next to the movie files:
      `opensub.SubtitleArchive().extract()`

## Glossary

* movie

  A movie is an ordered (in the order you would play them) list of video
  files. Think of multi-cd movies.

  This abstraction has its natural limits when it comes to tv show
  episodes. Most of the time episodes are represented as a movie, though
  it is perfectly possible to represent the whole tv series as a movie.

  Both may have valid uses, think of:

    * one subtitle file uploaded for an episode right after it came out
    * subtitle collection uploaded for the whole series after the series
      ended (for consistent quality, ease of download, etc)

* file hash

  The hash of a file as defined by (originally, I believe) Movie Player
  Classic. Our definition comes from opensubtitles.org.

  The hash is a function of:

    * file size
    * first 64 KiB chunk of file
    * last 64 KiB chunk of file

  So we need minimal I/O to calculate it.

* movie hash

  The hash of the first video file. Yeah, this is not ideal.

* template

  Template to use during subtitle extraction. Think of (re)naming files while
  extracting them from a zip archive.

## Debatable decisions

* Using simplexml interface to opensubtitles.org instead of xml-rpc api.

  By using xml-rpc we could:

    * make mass searches and downloads perform better
    * make subtitle upload possible
    * access standalone subtitle files instead of archives

  So far I didn't need any of these so I just kept it simple.

* Identifying multi-cd movies by the hash of the first file and cd count.

  My basic choices were:

    1. Handle collections of video/subtitle files as a unit,
       i.e. identify movie by hash of first file and cd count.
    2. Handle standalone video/subtitle files as a unit,
       i.e. identify each video file by its own file hash.

  Option (2) seems to be simpler and more generic, but there is a hidden
  drawback for multi-cd movies: We could end up having subtitle files
  coming from different sources, for example from different rips or
  from different translators.

  Ideally this problem could be eliminated by the subtitle database by
  letting us know what movie a file hash belongs to.

  This may be possible with the current search interface, but I couldn't
  find a definitive answer how to do it.

  I also don't know whether we can expect the hashes of the later cds
  to be present in the database. (We could have a practical answer by
  looking at how others handle uploads.)

  All this seems to be a confusingly gray area in the interface of the
  subtitle database, and I may have added a bit to the confusion by
  favoring
    * option (1) in opensub-get, but
    * option (2) in opensub-hash.

  With option (1) we have a mapping like:

  many        - one              - many (same count as video files)
  video files - subtitle archive - subtitle files

  It may be a good idea to experiment with option (3):

    3. Perform search by each file hash.
       Cluster (group by) results by movie title returned by search.
       Download subtitles for clusters.

       In other words: transfer the responsibility of clustering
       from our user to the subtitle database.

* Not implementing search by name or upload.

  These were intentional omissions. Download-by-hash can be expressed in a
  well automated manner via a utility following the philosphy of "do one
  thing and do it well". This is not the same for search-by-name or upload
  because they must involve user interactivity (or too much guessing).
