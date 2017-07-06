"""
Set build status to github
"""
import logging

import boto3

from lib.github_wrapper import set_status_to_github


logger = logging.getLogger()
logger.setLevel(logging.INFO)

codebuild_client = boto3.client('codebuild')
BUILD_STATUS_TO_GITHUB_STATUS = {
  'PENDING': 'pending',
  'IN_PROGRESS': 'pending',
  'FAILED': 'failure',
  'SUCCEEDED': 'success',
  'ERROR': 'error'}


def get_build_info(build_id):
    """
    Helper to fetch info about build from code build
    """
    builds = codebuild_client.batch_get_builds(
        ids=[
            build_id
        ])
    logger.info(str(builds))
    return builds


def set_build_result(build_id):
    """
    Fetch bild result and send it back to github
    """
    build_info = get_build_info(build_id)
    source_version = _get_initial_commit(build_info)
    build_status = _try_fetch_build_status(build_info)
    return set_status_to_github(
        BUILD_STATUS_TO_GITHUB_STATUS.get(
            build_status['buildStatus'], 'pending'), 
        build_status['buildStatus'], # FIXME: generate build message
        source_version,
        build_status['id'])


def _try_fetch_build_status(build_info):
    """
    Try to retrieve status from build
    """
    return build_info['builds'][0]


def _get_initial_commit(build_status):
    """
    Try get github commit
    from build env variables
    """
    variables = build_status['builds'][0]['environment']['environmentVariables']
    for variable in variables:
      if variable['name'] == 'GITHUB_COMMIT': return variable['value']
    return None
