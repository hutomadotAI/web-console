#!/bin/bash
# A script to setup a Python 3.5 virtual environment
# So that project Python setup doesn't mess up main machine
# or other projects.
SCRIPT_DIR=`dirname $BASH_SOURCE`
ROOT_DIR="${SCRIPT_DIR}/.."
SOURCE_DIR=${ROOT_DIR}
VE_DIR="${ROOT_DIR}/venv/django_unix"
if [ ! -d $VE_DIR ]; then
    echo Initializing virtualenv at $VE_DIR
	python3.5 -m venv $VE_DIR
fi

echo Entering Python 3.5 virtual environment at $VE_DIR
source $VE_DIR/bin/activate
pip install --upgrade pip
pushd ${SOURCE_DIR}
pip install --upgrade -r development.ini
popd
