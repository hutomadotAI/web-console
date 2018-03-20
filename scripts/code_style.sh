#!/bin/bash
function check_return_code {
    return_code=$?;
    if [[ $return_code != 0 ]]; then
        echo "*** code_style.sh: previous command failed, exiting ***"
        exit $return_code;
    fi
}

SCRIPT_DIR=`dirname $BASH_SOURCE`
ROOT_DIR="${SCRIPT_DIR}/.."
SOURCE_DIR="${ROOT_DIR}/src"

. ${SCRIPT_DIR}/setup_python.sh --style-only
pushd ${SOURCE_DIR}
echo "Running flake8"
flake8 --count
check_return_code
popd
