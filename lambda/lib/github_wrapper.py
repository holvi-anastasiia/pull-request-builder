"""
GitHub API wrapper

Used to set build status to github
and generate url for archive with source code
"""
import os

import github


def set_status_to_github(
        status, message, source_version, build_id):
    """
    Api wrapper for seting build status to github
    """
    g = github.Github(os.environ['GITHUB_OAUTH'])
    repo = g.get_repo(os.environ['GITHUB_LAMBDAS_REPO'])
    commit = repo.get_commit(source_version)
    return commit.create_status(
        status,
        _get_status_url(build_id),
        message)


def _get_status_url(build_id):
    """
    Helper to generate url with build status
    """
    return 'https://console.aws.amazon.com/codebuild/home?region=%s#/builds/%s/view/new' % (
        os.environ['AWS_REGION'], build_id)


def get_archive_url(
        github_reference):
    """
    Api wrapper for generating temporary url for zip file
    with source code
    """
    g = github.Github(os.environ['GITHUB_OAUTH'])
    repo = g.get_repo(os.environ['GITHUB_LAMBDAS_REPO'])
    return repo.get_archive_link(
        'zip', ref=github_reference)
