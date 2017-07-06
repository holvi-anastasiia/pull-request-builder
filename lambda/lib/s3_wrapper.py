"""
S3 API wrapper. Used to load new source code version
to s3
"""
import logging
import os
import urllib2 as urllib

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
    source_code_file = _load_code_zipfile(
        source_code_archive_url)
    # can uploads to a new version be a bottleneck in concurrent requests?
    # TODO: delete old versions
    response = s3_client.put_object(
        Body=source_code_file,
        Bucket=os.environ['SOURCE_CODE_S3_BUCKET'],
        Key=os.environ['SOURCE_CODE_S3_KEY'])   
    return response['VersionId']


def _load_code_zipfile(
        source_code_archive_url):
    """
    Download content from url and return int as file object
    """
    # WARNING: if the code won't fit to memory
    # we will miserably fail
    zipfile = urllib.urlopen(
        source_code_archive_url)
    return zipfile.read()
