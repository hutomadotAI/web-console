#!/bin/bash
# A script to build a Python package, requiring venv to install some build tools

trap exit 1 ERR
cd ../src
flake8 --count
