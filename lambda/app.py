import json
import logging
from time import sleep

from lib.build import (
    trigger_test_build,
    trigger_deploy_build)
from lib.result import set_build_result


logger = logging.getLogger()
logger.setLevel(logging.INFO)

HTTP_200_OK = 200
HTTP_400_BAD_REQUEST = 400


def handler(event, context):
    """
    One endpoint to trigger build on commits to github
    and record build results via github comments API

    Uses AWS SNS to pass messages
    """
    logger.info(json.dumps(event))
    message = _get_message_or_none(event)
    if not message:
        # smth got wrong: retun error
        return _error_repponse('No sns message found')
    # "after" has the numebr of last commit
    if message.get('after'):
        # deliberately fail with 500 error
        # if smth goes wrong here
        ref = message['ref']
        ref_type, lambda_name = _parse_github_reference(ref)
        if ref_type == 'tags':
            # trigger deployment on tag
            trigger_function = trigger_deploy_build
        else:
            # trigger test by default
            trigger_function = trigger_test_build
        data = trigger_function(
            commit=message['after'], lambda_name=lambda_name)
    elif message.get('buildId'):
        # FIXME: this is totally ugly
        # we need to order CodeBuild and lambda
        # so we first complete build project and only then
        # try to fetch results from lambda
        sleep(5)
        # deliberately fail with 500 error
        # if smth goes wrong here
        data = set_build_result(message['buildId'])
    else:
        # Strange message type:
        # return error an skip
        return _error_response('Unknow message type')
    logger.info(str(data))
    return _success_response()


def _get_message_or_none(event):
    """
    Helper to extract sns message from event
    """
    records = event.get('Records')
    if not records or not len(records) > 0:
        return None
    sns = records[0].get('Sns')
    if not sns:
        return None
    message = sns.get('Message')
    if not message:
        return None
    return json.loads(message)


def _error_response(
        error_message, status_code=HTTP_400_BAD_REQUEST):
    """
    Helper to return error reponse
    """
    return {
        'statusCode': status_code,
        'body': error_message}


def _success_response():
    """
    Helper to return success response
    """
    return {
        'statusCode': HTTP_200_OK,
    }


def _parse_github_reference(ref):
    """
    Extract lambda name and reference type
    """
    _, ref_type, name = ref.split('/')
    return ref_type, \
        _get_lambda_name(name)


def _get_lambda_name(name):
    """
    Extract lanbda name from ref name.
    Expects that lambda name will be separated by double dash
    """
    # FIXME: skip builds for master, staging or whatever called main branches
    return name.split('--')[0]
