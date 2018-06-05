#!/bin/bash
on_error() {
    echo "Error at $(caller), aborting"
    exit 1
}
trap on_error ERR

SCRIPT_DIR=`dirname $BASH_SOURCE`
ROOT_DIR="${SCRIPT_DIR}/.."
SOURCE_DIR="${ROOT_DIR}/src"

source ${SCRIPT_DIR}/setup_python.sh --style-only || exit $?
pushd ${SOURCE_DIR}
echo "Running flake8"
flake8 --count
popd
