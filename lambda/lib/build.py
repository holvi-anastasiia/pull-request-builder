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
