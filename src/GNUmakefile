# This Makefile is to cut a new release, not to install the software.
#
# For installation instructions see 'install.md'.

# Cut new release:
#     git checkout TAG_TO_BE_RELEASED
#     make

# Test install new release:
#     git checkout TAG_TO_BE_RELEASED
#     make debug=1
#     python opensub-utils-*/src/setup.py install --user


## global config

pkg_name=opensub-utils
debug=0


## programs

bash=bash
git=git
nosetests=nosetests-2.7
python=python2.7
sed=sed
tar=tar
wget=wget


## default target

.PHONY : default
default : tarball


## targets

test/test-data/breakdance.avi :
	$(wget) \
	    --tries=1 \
	    --no-clobber \
	    --output-document=$@ \
	    http://www.opensubtitles.org/addons/avi/breakdance.avi

.PHONY : test-data
test-data : test/test-data/breakdance.avi

.PHONY : test
test :
	@ nosetests

# FIXME Shall we work out of a remote repo?

.PHONY : template
template : test
	$(eval version := $(shell $(git) describe --always))
	@ echo version = $(version)

	$(eval dist_name := $(pkg_name)-$(version))

	$(eval template_dir := $(shell mktemp -d))

	@ \
	cd .. ; \
	    $(git) archive \
	        --format=tar \
	        --prefix="$(dist_name)/" \
	        "$(version)" \
	    | $(tar) -x -C "$(template_dir)" ; \
	cd - > /dev/null

	@ # c.f. gitrevisions (7) section SPECIFYING RANGES
	@ $(git) log --decorate "$(version)" "$(version)^@" \
	    > "$(template_dir)/$(dist_name)/changelog"

	$(sed) -i -e "s/\[% *version *%\]/$(version)/g" \
	    "$(template_dir)/$(dist_name)/src/lib/opensub/version.py"

	@ # TODO early abort based on bash exit code
	-@ \
	if test "$(debug)" = 1 ; \
	then \
	    echo >&2 '!!! Starting debug shell, ^D to exit.' ; \
	    cd "$(template_dir)" ; \
	    $(bash) -i ; \
	    cd - > /dev/null ; \
	fi

	@ # if $deploy_py3:
	@ #     sed -i -e "s/#! python$/#! python3/" $scripts

.PHONY : tarball
tarball : template
	@ tar -cz -C "$(template_dir)" "$(dist_name)" \
	    > "$(dist_name).tar.gz"
	-@ rm -rf $(template_dir);
