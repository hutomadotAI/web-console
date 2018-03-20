# Hutoma WNET scripts

### setup-python.sh
This script creates a Python 3 virtualenv with correct modules 
installed, and the code modules inplace PIP installed. 

The virtualenv is created at `/venv/django_unix` from top level.

To launch this environment you should call `source setup_python.sh` or the shortcut `. setup-python.sh`.
Alternatively, for IntelliJ installation for instance, you can directly reference the Python binary at `venv/django_unix/bin/python`.

To reset the virtualenv, delete the `/venv` directory and re-run this script.

### build.sh
This is a wrapper to build.py, making sure that `setup_python.sh` has been called so the venv is initialized with the hu_build dependency in particular.

### code_style.sh
This script initializes the venv just with the code style requirements and then runs flake8. Designed to be wired to a build job for a quick check of the code style.
