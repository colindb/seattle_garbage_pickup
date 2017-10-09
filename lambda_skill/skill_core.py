"""
Helper functions that build the skill response.
"""
import logging
import urllib.request
import json


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def build_speechlet_response(title, card_output, output, reprompt_text, should_end_session):
    logger.info("Response (%s): %s" % (title, output))
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': '<speak>%s</speak>' % output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': card_output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


def get_alexa_location(device_id, consent_token):
    logger.info("Getting location info for device (%s) with token (%s)" % (device_id, consent_token))
    if not device_id or not consent_token:
        return None

    url = "https://api.amazonalexa.com/v1/devices/%s/settings/address" % device_id
    header = {'Accept': 'application/json',
              'Authorization': 'Bearer %s' % consent_token}

    req = urllib.request.Request(url, None, header)
    try:
        resp = urllib.request.urlopen(req)
    except urllib.error.HTTPError as exc:
        logger.error("Unable to get device address: %s" % exc)
        return None

    resp_data = resp.read().decode('utf-8')
    resp_json = json.loads(resp_data)
    logger.info("Response JSON: %s" % resp_json)
    return resp_json
