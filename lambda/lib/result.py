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


def get_build_status(build_id):
    """
    Helper to fetch info about build from code build
    """
    builds = codebuild_client.batch_get_builds(
        ids=[
            build_id
        ])
    logger.info(str(builds))
    return builds['builds'][0]


def set_build_result(build_id):
    """
    Fetch bild result and send it back to github
    """
    build_status = get_build_status(build_id)
    return set_status_to_github(
        BUILD_STATUS_TO_GITHUB_STATUS.get(
            build_status['buildStatus'], 'pending'), 
        build_status['buildStatus'], # FIXME: generate build message
        build_status['sourceVersion'],
        build_status['id'])
