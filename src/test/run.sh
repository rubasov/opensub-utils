#! /bin/sh

# quick-and-dirty test runner script

if test $# = 0
then

cat >&2 <<EOF
usage: $0 <movie_cd1.avi> <movie_cd2.avi> ...

It is recommended to test with a multi-cd movie.

It is a good idea to use a caching http proxy to avoid hitting the
daily request limit on opensubtitles.org due to testing. For example:

$ sudo apt-get install polipo # it listens at 127.0.0.1:8123

You may also want to populate the cache, before running this script:

http_proxy=127.0.0.1:8123 ./bin/opensub-get -vv -t - >/dev/null ...
EOF

exit 1
fi

cd "$( dirname "$0" )"/..

test_avi_path="test/test-data/breakdance.avi"
if ! test -f "$test_avi_path"
then
    wget \
        --tries=1 \
        --no-clobber \
        --output-document="$test_avi_path" \
        "http://www.opensubtitles.org/addons/avi/breakdance.avi"
fi

find . -type f \( -name "*.py" -o -name "opensub-*" \) | xargs pep8

ls test/test_* | xargs -n1 python
ls test/test_* | xargs -n1 python3

python bin/opensub-hash "$test_avi_path"
python3 bin/opensub-hash "$test_avi_path"

export http_proxy=127.0.0.1:8123
export http_cache_control="only-if-cached"

python bin/opensub-get -vv -t - >/dev/null -- "$@"
python3 bin/opensub-get -vv -t - >/dev/null -- "$@"

tmpdir="$( mktemp -d )"
python bin/opensub-get -vv -t "$tmpdir/test-{num}{subtitle/ext}" -- "$@"
python3 bin/opensub-get -vv -t "$tmpdir/test3-{num}{subtitle/ext}" -- "$@"
rm -f -- "$tmpdir"/test*
rmdir -- "$tmpdir"
