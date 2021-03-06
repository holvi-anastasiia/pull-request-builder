"""
Start CodeBuild building
"""
import os

import boto3

codebuild_client = boto3.client('codebuild')


def trigger_deploy_build(
        commit, source_version, lambda_name):
    """
    Trigger build and specify deploy config
    """
    return trigger_build(
        commit, source_version, lambda_name, 'buildspec-build')


def trigger_test_build(
        commit, source_version, lambda_name):
    """
    Trigger build and specifu test config
    """
    return trigger_build(
        commit, source_version, lambda_name, 'buildspec-test')


def trigger_build(
        commit, source_version, lambda_name, buildspec_file_name):
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
        sourceVersion=source_version,
        environmentVariablesOverride=[
            {
                'name': 'LAMBDA',
                'value': lambda_name,
            },
            # WARNING: this is rather ugly hack
            # since now we are getting code from s3
            # we lose information about initail commit
            {
                'name': 'GITHUB_COMMIT',
                'value': commit
            }
        ],
        buildspecOverride=buildspec_override)


def _get_buildspec_override(
        lambda_name, file_name):
    """
    Import buildspecs from buildspec module

    Dirs structure:
    -/ lambda
    ---/ buildspecs 
    -----/ lambda_name
    -------/ buildspec_file_name
    """
    import importlib
    full_buildspec_name = \
        _get_buildspec_filename(lambda_name, file_name)
    return importlib.import_module(
            full_buildspec_name).YAML_CONFIG


def _get_buildspec_filename(
        lambda_name, file_name):
    """
    Generate full path to specified buildspec module
    """
    return '.'.join(
        ('buildspecs', lambda_name, file_name))
