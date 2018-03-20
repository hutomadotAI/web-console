#!/bin/bash
# A script to build a Python package, requiring venv to install some build tools

function check_return_code {
    return_code=$?;
    if [[ $return_code != 0 ]]; then 
        exit $return_code; 
    fi
}

SCRIPT_DIR=`dirname $BASH_SOURCE`
echo "*** Setting up venv ***"
source "${SCRIPT_DIR}/setup_python.sh"
check_return_code

echo "*** Doing build ***"
python "${SCRIPT_DIR}/build.py" $*
