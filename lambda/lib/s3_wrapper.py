"""
S3 API wrapper. Used to load new source code version
to s3
"""
import logging
import os

import boto3

from lib.github_wrapper import get_archive_url


logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3_client = boto3.client('s3')


def load_source_code_to_s3(reference):
    """
    Uploads new source with new version to s3
    """
    source_code_archive_url = get_archive_url(reference)
    # can uploads to a new version be a bottleneck in concurrent requests?
    # TODO: delete old versions
    response = s3_client.upload_file(
        source_code_archive_url,
        os.environ['SOURCE_CODE_S3_BUCKET'],
        os.environ['SOURCE_CODE_S3_KEY'])
    logger.info(response)
    return response['VersionId']
