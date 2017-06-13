import json
import logging
from time import sleep

from lib.build import trigger_build
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
    if message.get('after'):
        # FIXME: figure out why is param to
        # trigger build is called after
        # deliberately fail with 500 error
        # if smth goes wrong here
        data = trigger_build(message['after'])
    elif message.get('buildId'):
    	# FIXME: this is totally ugly
    	# we need to order CodeBuild and lambda 
    	# so we first complete build project and only then
    	# try to fetch results from lambda
    	sleep(1)
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
