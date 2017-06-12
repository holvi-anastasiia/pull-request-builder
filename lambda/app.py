from lib.build import trigger_build
from lib.result import set_build_result


HTTP_200_OK = 200
HTTP_400_BAD_REQUEST = 400


def handler(event, context):
    """
    One endpoint to trigger build on commits to github
    and record build results via github comments API

    Uses AWS SNS to pass messages
    """
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
        # deliberately fail with 500 error
        # if smth goes wrong here
        data = set_build_result(message['buildId'])
    else:
        # Strange message type:
        # return error an skip
        return _error_response('Unknow message type')
    return _success_response(data)


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
    return sns.get('Message', None)


def _error_response(
        error_message, status_code=HTTP_400_BAD_REQUEST):
    """
    Helper to return error reponse
    """
    return {
        'statusCode': status_code,
        'body': error_message}


def _success_response(data):
    """
    Helper to return success response
    """
    import json
    return {
        'statusCode': HTTP_200_OK,
        'body': json.dumps(data),
        'headers': {
            'Content-Type': 'application/json',
        },
    }
