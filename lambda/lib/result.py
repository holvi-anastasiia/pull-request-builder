"""
Set build status to github
"""
import boto3

from lib.status import set_status_to_github


codebuild_client = boto3.client('codebuild')


def get_build_status(build_id):
    """
    Helper to fetch info about build from code build
    """
    builds = codebuild_client.batch_get_builds(
        ids=[
            build_id
        ])
    return builds[0]


def set_build_result(build_id):
    """
    Fetch bild result and send it back to github
    """
    build_status = get_build_status(build_id)
    return set_status_to_github(
        build_status['buildStatus'], 
        build_status['buildStatus'], # FIXME: generate build message
        build_status['sourceVersion'],
        build_status['id'])
