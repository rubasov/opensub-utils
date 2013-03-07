#! /bin/bash

set -e
set -u

##

pkg_name=opensub-utils
nosetests=nosetests-2.7
python=python2.7

##

usage_and_exit () {
cat <<EOF
Usage:

Cut new release:
    git checkout TAG_TO_BE_RELEASED
    $0

Test install new release:
    git checkout TAG_TO_BE_RELEASED
    $0 -d
    cd opensub-utils-*/src/
    python setup.py install --user
EOF
exit 1
}

##

debug=0

while getopts dh opt
do
    case "$opt" in
        d)  debug=1 ;;
        h)  usage_and_exit ;;
    esac
done
shift $(( $OPTIND - 1 ))

##

cd "$( dirname "$0" )"

##

$nosetests

version="$( git describe --always )"
dist_name="$pkg_name-$version"
template_dir="$( mktemp -d )"

# FIXME Shall we work out of a remote repo?

cd ..
git archive --format=tar --prefix="$dist_name/" "$version" \
    | tar -x -C "$template_dir"
cd - > /dev/null

# c.f. gitrevisions (7) section SPECIFYING RANGES
git log --decorate "$version" "$version^@" \
    > "$template_dir/$dist_name/changelog"

sed -i -e "s/\[% *version *%\]/$version/g" \
    "$template_dir/$dist_name/src/lib/opensub/version.py"

if test "$debug" == 1
then
    echo >&2 "! Starting debug shell, ^D to exit."
    cd "$template_dir"
    $SHELL -i
    cd - > /dev/null
fi

# if $deploy_py3:
#     sed -i -e "s/#! python$/#! python3/" $scripts

tarball="$dist_name.tar.gz"
tar -cz -C "$template_dir" "$dist_name" \
    > "$tarball"
echo tarball = "$tarball"
rm -rf "$template_dir"
