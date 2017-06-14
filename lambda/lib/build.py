"""
Start CodeBuild building
"""
import os

import boto3

codebuild_client = boto3.client('codebuild')


def trigger_deploy_build(commit, lambda_name):
    """
    Trigger build and specify deploy config
    """
    return trigger_build(
        commit, lambda_name, 'buildspec-build.yml')


def trigger_test_build(commit, lambda_name):
    """
    Trigger build and specifu test config
    """
    return trigger_build(
        commit, lambda_name, 'buildspec-test.yml')


def trigger_build(
        commit, lambda_name, buildspec_file_name):
    """
    Trigger build for given source_version

    Assumes that  we have PROJECT environment variable set
    """
    buildspec_override = \
        _get_buildspec_override(
            lambda_name, buildspec_file_name)
    # return codebuild response for debug
    return codebuild_client.start_build(
        projectName=os.environ['PROJECT'],
        sourceVersion=commit,
        environmentVariablesOverride=[
            {
                'name': 'LAMBDA',
                # TODO: get lambda value on the flight
                'value': lambda_name,
            } 
        ],
        buildspecOverride=buildspec_file_name)


def _get_buildspec_override(
        lambda_name, file_name):
    """
    Read buildspec from specified file

    Dirs structure:
    -/ lambda
    ---/ buildspecs 
    -----/ lambda_name
    -------/ buildspec_file_name
    """
    full_buildspec_name = \
        _get_buildspec_filename(lambda_name, file_name)
    with open(full_buildspec_name) as buildspec_file:
        return buildspec_file.read()


def get_buildspec_filename(
        lambda_name, file_name):
    """
    Generate full path to specified buildspec
    """
    import os
    from settings import BASE_PATH
    return os.path.join(
        BASE_PATH, 'buildspecs', lambda_name, file_name)
