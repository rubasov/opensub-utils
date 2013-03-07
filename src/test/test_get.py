"""
TODO test opensub-get

It is recommended to test with a multi-cd movie.

It is a good idea to use a caching http proxy to avoid hitting the
daily request limit on opensubtitles.org due to testing. For example:

$ sudo apt-get install polipo # it listens at 127.0.0.1:8123

You may also want to populate the cache, before running this script:

http_proxy=127.0.0.1:8123 ./bin/opensub-get -vv -t - >/dev/null ...

export http_proxy=127.0.0.1:8123
export http_cache_control="only-if-cached"

python bin/opensub-get -vv -t - >/dev/null -- "$@"
python3 bin/opensub-get -vv -t - >/dev/null -- "$@"
"""
