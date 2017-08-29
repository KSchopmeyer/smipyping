# ------------------------------------------------------------------------------
# Makefile for smipyping project
#
# Basic prerequisites for running this Makefile, to be provided manually:
#   One of these OS platforms:
#     Windows with CygWin
#     Linux (any)
#     OS-X
#   These commands on all OS platforms:
#     make (GNU make)
#     bash
#     rm, mv, find, tee, which
#   These commands on all OS platforms in the active Python environment:
#     python (or python3 on OS-X)
#     pip (or pip3 on OS-X)
#     twine
#   These commands on Linux and OS-X:
#     uname
# Environment variables:
#   PYTHON_CMD: Python command to use (OS-X needs to distinguish Python 2/3)
#   PIP_CMD: Pip command to use (OS-X needs to distinguish Python 2/3)
#   PACKAGE_LEVEL: minimum/latest - Level of Python dependent packages to use
# Additional prerequisites for running this Makefile are installed by running:
#   make develop
# ------------------------------------------------------------------------------

# Python / Pip commands
ifndef PYTHON_CMD
  PYTHON_CMD := python
endif
ifndef PIP_CMD
  PIP_CMD := pip
endif

# Package level
ifndef PACKAGE_LEVEL
  PACKAGE_LEVEL := latest
endif
ifeq ($(PACKAGE_LEVEL),minimum)
  pip_level_opts := -c minimum-constraints.txt
else
  ifeq ($(PACKAGE_LEVEL),latest)
    pip_level_opts := --upgrade
  else
    $(error Error: Invalid value for PACKAGE_LEVEL variable: $(PACKAGE_LEVEL))
  endif
endif

# Determine OS platform make runs on
ifeq ($(OS),Windows_NT)
  PLATFORM := Windows
else
  # Values: Linux, Darwin
  PLATFORM := $(shell uname -s)
endif

# Name of this Python package (top-level Python namespace + Pypi package name)
package_name := smipyping

# Name of the Python namespace for the CLI
cli_package_name := smicli

# Package version (full version, including any pre-release suffixes, e.g. "0.1.0-alpha1")
package_version := $(shell $(PYTHON_CMD) -c "import sys, $(package_name); sys.stdout.write($(package_name).__version__)")

# Python major version
python_major_version := $(shell $(PYTHON_CMD) -c "import sys; sys.stdout.write('%s'%sys.version_info[0])")

# Python major+minor version for use in file names
python_version_fn := $(shell $(PYTHON_CMD) -c "import sys; sys.stdout.write('%s%s'%(sys.version_info[0],sys.version_info[1]))")

# Directory for the generated distribution files
dist_dir := dist

# Distribution archives (as built by setup.py)
bdist_file := $(dist_dir)/$(package_name)-$(package_version)-py2.py3-none-any.whl
sdist_file := $(dist_dir)/$(package_name)-$(package_version).tar.gz

# Windows installable (as built by setup.py)
win64_dist_file := $(dist_dir)/$(package_name)-$(package_version).win-amd64.exe

# dist_files := $(bdist_file) $(sdist_file) $(win64_dist_file)
dist_files := $(bdist_file) $(sdist_file)

# Directory for generated API documentation
doc_build_dir := build_doc

# Directory where Sphinx conf.py is located
doc_conf_dir := docs

# Documentation generator command
doc_cmd := sphinx-build
doc_opts := -v -d $(doc_build_dir)/doctrees -c $(doc_conf_dir) .

# File names of automatically generated utility help message text output
doc_utility_help_files := \

# Dependents for Sphinx documentation build
doc_dependent_files := \
    $(doc_conf_dir)/conf.py \
    $(wildcard $(doc_conf_dir)/*.rst) \
    $(wildcard $(doc_conf_dir)/notebooks/*.ipynb) \
    $(package_name)/__init__.py \
    $(package_name)/_cmd_*.py \
    $(package_name)/smicli.py \

# Flake8 config file
flake8_rc_file := .flake8

# PyLint config file
pylint_rc_file := .pylintrc

# Source files for check (with PyLint and Flake8)
check_py_files := \
    setup.py \
    $(wildcard $(package_name)/*.py) \
    $(wildcard tests/*.py)

# Test log
test_log_file := test_$(python_mn_version).log
test_tmp_file := test_$(python_mn_version).tmp.log

ifdef TESTCASES
pytest_opts := -k $(TESTCASES)
else
pytest_opts :=
endif

# Files the distribution archive depends upon.
dist_dependent_files := \
    $(package_name)/LICENSE.txt \
    README.rst \
    requirements.txt \
    INSTALL.md \
    $(wildcard *.py) \
    $(wildcard $(package_name)/*.py) \
    $(wildcard $(cli_package_name)/*.py) \

# No built-in rules needed:
.SUFFIXES:

.PHONY: help
help:
	@echo 'Makefile for $(package_name) project'
	@echo 'Package version will be: $(package_version)'
	@echo 'Uses the currently active Python environment: Python $(python_version_fn)'
	@echo 'Valid targets are (they do just what is stated, i.e. no automatic prereq targets):'
	@echo '  develop    - Prepare the development environment by installing prerequisites'
	@echo '  build      - Build the distribution files in: $(dist_dir) (requires Linux or OSX)'
	@echo '  buildwin   - Build the Windows installable in: $(dist_dir) (requires Windows 64-bit)'
	@echo '  builddoc   - Build documentation in: $(doc_build_dir)'
	@echo '  check      - Run PyLint and Flake8 on sources and save results in: pylint.log and flake8.log'
	@echo '  test       - Run unit tests (and test coverage) and save results in: $(test_log_file)'
	@echo '               Env.var TESTCASES can be used to specify a py.test expression for its -k option'
	@echo '  all        - Do all of the above (except buildwin when not on Windows)'
	@echo '  install    - Install package in active Python environment and test import (includes build)'
	@echo '  uninstall  - Uninstall package from active Python environment'
	@echo '  upload     - Upload the distribution files to PyPI (includes uninstall+build)'
	@echo '  clean      - Remove any temporary files'
	@echo '  clobber    - Remove any build products (includes uninstall+clean)'
	@echo '  pyshow     - Show location and version of the python and pip commands'
	@echo 'Environment variables:'
	@echo '  PACKAGE_LEVEL="minimum" - Install minimum version of dependent Python packages'
	@echo '  PACKAGE_LEVEL="latest" - Default: Install latest version of dependent Python packages'
	@echo '  PYTHON_CMD=... - Name of python command. Default: python'
	@echo '  PIP_CMD=... - Name of pip command. Default: pip'

.PHONY: _pip
_pip:
	@echo 'Installing/upgrading pip, setuptools and wheel with PACKAGE_LEVEL=$(PACKAGE_LEVEL)'
	$(PIP_CMD) install --upgrade pip
	$(PIP_CMD) install $(pip_level_opts) pip
	$(PIP_CMD) install $(pip_level_opts) setuptools
	$(PIP_CMD) install $(pip_level_opts) wheel

.PHONY: develop
develop: _pip
	@echo 'Installing runtime and development requirements with PACKAGE_LEVEL=$(PACKAGE_LEVEL)'
	$(PIP_CMD) install $(pip_level_opts) -r dev-requirements.txt
	@echo '$@ done.'

.PHONY: build
build: $(bdist_file) $(sdist_file)
	@echo '$@ done.'

.PHONY: buildwin
buildwin: $(win64_dist_file)
	@echo '$@ done.'

.PHONY: builddoc
builddoc: html
	@echo '$@ done.'

.PHONY: html
html: $(doc_build_dir)/html/docs/index.html
	@echo '$@ done.'

$(doc_build_dir)/html/docs/index.html: Makefile $(doc_utility_help_files) $(doc_dependent_files)
	rm -f $@
	PYTHONPATH=. $(doc_cmd) -b html $(doc_opts) $(doc_build_dir)/html
	@echo "Done: Created the HTML pages with top level file: $@"

.PHONY: pdf
pdf: Makefile $(doc_utility_help_files) $(doc_dependent_files)
	rm -fv $@
	$(doc_cmd) -b latex $(doc_opts) $(doc_build_dir)/pdf
	@echo "Running LaTeX files through pdflatex..."
	$(MAKE) -C $(doc_build_dir)/pdf all-pdf
	@echo "Done: Created the PDF files in: $(doc_build_dir)/pdf/"
	@echo '$@ done.'

.PHONY: man
man: Makefile $(doc_utility_help_files) $(doc_dependent_files)
	rm -f $@
	$(doc_cmd) -b man $(doc_opts) $(doc_build_dir)/man
	@echo "Done: Created the manual pages in: $(doc_build_dir)/man/"
	@echo '$@ done.'

.PHONY: docchanges
docchanges:
	$(doc_cmd) -b changes $(doc_opts) $(doc_build_dir)/changes
	@echo
	@echo "Done: Created the doc changes overview file in: $(doc_build_dir)/changes/"
	@echo '$@ done.'

.PHONY: doclinkcheck
doclinkcheck:
	$(doc_cmd) -b linkcheck $(doc_opts) $(doc_build_dir)/linkcheck
	@echo
	@echo "Done: Look for any errors in the above output or in: $(doc_build_dir)/linkcheck/output.txt"
	@echo '$@ done.'

.PHONY: doccoverage
doccoverage:
	$(doc_cmd) -b coverage $(doc_opts) $(doc_build_dir)/coverage
	@echo "Done: Created the doc coverage results in: $(doc_build_dir)/coverage/python.txt"
	@echo '$@ done.'

.PHONY: pyshow
pyshow:
	which $(PYTHON_CMD)
	$(PYTHON_CMD) --version
	which $(PIP_CMD)
	$(PIP_CMD) --version
	@echo '$@ done.'

.PHONY: check
check: pylint.log flake8.log
	@echo '$@ done.'

.PHONY: pylint
pylint: pylint.log
	@echo '$@ done.'

.PHONY: flake8
flake8: flake8.log
	@echo '$@ done.'

.PHONY: install
install: _pip
	@echo 'Installing runtime requirements with PACKAGE_LEVEL=$(PACKAGE_LEVEL)'
	$(PIP_CMD) install $(pip_level_opts) .
	$(PYTHON_CMD) -c "import smipyping; print('Import: ok')"
	@echo 'Done: Installed $(package_name) into current Python environment.'
	@echo '$@ done.'

.PHONY: uninstall
uninstall:
	bash -c '$(PIP_CMD) show $(package_name) >/dev/null; rc=$$?; if [[ $$rc == 0 ]]; then $(PIP_CMD) uninstall -y $(package_name); fi'
	@echo '$@ done.'

.PHONY: test
test: $(test_log_file)
	@echo '$@ done.'

.PHONY: clobber
clobber: uninstall clean
	rm -Rf $(doc_build_dir) htmlcov .tox
	rm -fv pylint.log flake8.log test_*.log
	rm -fv $(bdist_file) $(sdist_file) $(win64_dist_file)
	@echo 'Done: Removed all build products to get to a fresh state.'
	@echo '$@ done.'

# Also remove any build products that are dependent on the Python version
.PHONY: clean
clean:
	rm -Rf build .cache $(package_name).egg-info .eggs
	rm -f MANIFEST MANIFEST.in AUTHORS ChangeLog .coverage
	find . -name "*.pyc" -delete -o -name "__pycache__" -delete -o -name "*.tmp" -delete -o -name "tmp_*" -delete
	@echo 'Done: Cleaned out all temporary files.'
	@echo '$@ done.'

.PHONY: all
all: develop check build builddoc test
	@echo '$@ done.'

.PHONY: upload
upload: uninstall $(dist_files)
ifeq (,$(findstring .dev,$(package_version)))
	@echo '==> This will upload $(package_name) version $(package_version) to PyPI!'
	@echo -n '==> Continue? [yN] '
	@bash -c 'read answer; if [[ "$$answer" != "y" ]]; then echo "Aborted."; false; fi'
	twine upload $(dist_files)
	@echo 'Done: Uploaded $(package_name) version to PyPI: $(package_version)'
	@echo '$@ done.'
else
	@echo 'Error: A development version $(package_version) of $(package_name) cannot be uploaded to PyPI!'
	@false
endif

# Distribution archives.
$(bdist_file) $(sdist_file): Makefile setup.py $(dist_dependent_files)
ifneq ($(PLATFORM),Windows)
	rm -Rfv $(package_name).egg-info .eggs
	$(PYTHON_CMD) setup.py sdist -d $(dist_dir) bdist_wheel -d $(dist_dir) --universal
	@echo 'Done: Created distribution files: $@'
else
	@echo 'Error: Creating distribution archives requires to run on Linux or OSX'
	@false
endif

$(win64_dist_file): Makefile setup.py $(dist_dependent_files)
ifeq ($(PLATFORM),Windows)
	rm -Rfv $(package_name).egg-info .eggs
	$(PYTHON_CMD) setup.py bdist_wininst -d $(dist_dir) -o -t "$(package_name) v$(package_version)"
	@echo 'Done: Created Windows installable: $@'
else
	@echo 'Error: Creating Windows installable requires to run on Windows'
	@false
endif

# TODO: Once PyLint has no more errors, remove the dash "-"
pylint.log: Makefile $(pylint_rc_file) $(check_py_files)
ifeq ($(python_major_version), 2)
	rm -fv $@
	-bash -c 'set -o pipefail; pylint --rcfile=$(pylint_rc_file) --output-format=text $(check_py_files) 2>&1 |tee $@.tmp'
	mv -f $@.tmp $@
	@echo 'Done: Created PyLint log file: $@'
else
	@echo 'Info: PyLint requires Python 2; skipping this step on Python $(python_major_version)'
endif

# TODO: Once Flake8 has no more errors, remove the dash "-"
flake8.log: Makefile $(flake8_rc_file) $(check_py_files)
	rm -fv $@
	-bash -c 'set -o pipefail; flake8 $(check_py_files) 2>&1 |tee $@.tmp'
	mv -f $@.tmp $@
	@echo 'Done: Created Flake8 log file: $@'

$(test_log_file): Makefile $(package_name)/*.py tests/*.py .coveragerc
	rm -fv $(test_log_file)
	# TODO fix. For some reason cov losing packagename. NOTE: Should not
	# be package name either.
	# bash -c 'set -o pipefail; PYTHONWARNINGS=default py.test --cov $(package_name) --cov-config .coveragerc --cov-report=html --ignore=attic --ignore=releases --ignore=tests/testclient -s 2>&1 |tee $(test_tmp_file)'
	# bash -c 'set -o pipefail; PYTHONWARNINGS=default py.test --ignore=attic --ignore=releases --ignore=tests/testclient -s 2>&1 |tee $(test_tmp_file)'
	# mv -f $(test_tmp_file) $(test_log_file)
	rm -fv $@
	bash -c 'set -o pipefail; PYTHONWARNINGS=default py.test --cov $(package_name) --cov-config .coveragerc --cov-report=html $(pytest_opts) -s 2>&1 |tee $@.tmp'
	mv -f $@.tmp $@
	@echo 'Done: Created test log file: $@'

# Create the help text.rst files for each separate script

$(doc_conf_dir)/smicli_help.rst: $(package_name)/smicli.py $(package_name)/_cmd*.py
	tools/click_help_capture.py --help >$@
	@echo 'Done: Created smicli script help message file: $@'

