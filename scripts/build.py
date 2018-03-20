#!/usr/bin/env python
"""Script to build code"""
import argparse
import os
import shutil
import subprocess

from pathlib import Path

import hu_build.build_docker
from hu_build.build_docker import DockerImage


class DockerRunError(Exception):
    pass


SCRIPT_PATH = Path(os.path.dirname(os.path.realpath(__file__)))
ROOT_DIR = SCRIPT_PATH.parent


def build_test(src_path):
    """Builds the test docker image"""

    # make sure there is at least a blank secrets file
    env_file = src_path / 'secrets.env'
    if not env_file.exists():
        print("Creating blank secrets.env file")
        env_file.touch()

    # We make sure that we set environment variable with IDs
    # the current user so that docker-compose build can pick it up
    userid = os.getuid()
    groupid = os.getegid()
    os.environ['USERID'] = str(userid)
    os.environ['GROUPID'] = str(groupid)

    cmdline = ["docker-compose", "build", "test"]
    subprocess.run(cmdline, cwd=str(src_path), check=True)


def run_test(src_path: Path, clean_images: bool):
    """Runs the test"""
    # Clean any previous test results
    test_output = src_path / 'test_output'
    if test_output.is_dir():
        shutil.rmtree(str(test_output))

    container_name = 'hu_console_v2_test_container'

    try:
        # run test - it will return non-zero if a test fails, which we will throw later
        cmdline = [
            "docker-compose", "run", "--name={}".format(container_name), "test"
        ]
        completed_process = subprocess.run(cmdline, cwd=str(src_path))
        cmdline = [
            "docker", "cp",
            "{}:/usr/src/app/test_output".format(container_name),
            "{}/test_output".format(src_path)
        ]
        print(cmdline)
        subprocess.run(cmdline, cwd=str(src_path))

        if completed_process.returncode != 0:
            raise DockerRunError("docker-compose run failed")
    finally:
        # clean up the docker artifacts, even on failure
        cmdline = ["docker-compose", "down"]
        subprocess.run(cmdline, cwd=str(src_path), check=True)
        if clean_images:
            cmdline = ["docker", "rmi", "hu_console_v2_test"]
            subprocess.run(cmdline, cwd=str(src_path), check=True)


def main(build_args):
    """Main function"""
    src_path = ROOT_DIR / 'src'
    if not build_args.no_test:
        build_test(src_path)
        run_test(src_path, build_args.clean_images)

    if build_args.docker_build:
        tag_version = build_args.version
        services = []
        service = DockerImage(
            src_path,
            'web/dev_console2',
            tag_version=tag_version,
            build_args={'ENVIRONMENT': "production"})
        services.append(service)
        hu_build.build_docker.build_images('eu.gcr.io/hutoma-backend',
                                           services, build_args.docker_push)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(
        description='Python Django build command-line')
    PARSER.add_argument('--version', help='build version', default='latest')
    PARSER.add_argument('--no-test', help='skip tests', action="store_true")
    PARSER.add_argument(
        '--clean-images',
        help='clean test images after test run',
        action="store_true")
    PARSER.add_argument(
        '--docker-build',
        help='Build docker image for Django',
        action="store_true")
    PARSER.add_argument(
        '--docker-push',
        help='Push Django docker images to GCR',
        action="store_true")
    BUILD_ARGS = PARSER.parse_args()
    main(BUILD_ARGS)
