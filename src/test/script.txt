# FIXME comment this file

sudo apt-get install polipo

cd opensub-utils/src/

find . -type f \( -name '*.py' -o -name 'opensub-*' \) | xargs pep8

wget -O test/test-data/breakdance.avi ...

ls test/test_* | xargs -n1 python
ls test/test_* | xargs -n1 python3

python bin/opensub-hash test/test-data/breakdance.avi
python3 bin/opensub-hash test/test-data/breakdance.avi

# populate cache
http_proxy=127.0.0.1:8123 ./bin/opensub-get -vv -t /dev/null -f some_multi_cd_movie*.avi

magic=more http_proxy=127.0.0.1:8123 python bin/opensub-get -vv -t - >/dev/null some_multi_cd_movie*.avi
magic=more http_proxy=127.0.0.1:8123 python3 bin/opensub-get -vv -t - >/dev/null some_multi_cd_movie*.avi
