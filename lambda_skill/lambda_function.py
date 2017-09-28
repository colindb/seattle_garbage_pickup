import logging
import seattle_garbage_schedule
import skill_core

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def on_session_started(session_started_request, session):
    """ Called when the session starts """
    logger.info("on_session_started requestId=" + session_started_request['requestId'] + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """
    Called when the user launches the skill without specifying what they want.
    """
    logger.info("on_launch requestId=" + launch_request['requestId'] + ", sessionId=" + session['sessionId'])
    return seattle_garbage_schedule.get_welcome_response()


def on_intent(intent_request, session, context):
    """
    Called when the user specifies an intent for this skill.
    """
    logger.info("on_intent requestId=" + intent_request['requestId'] + ", sessionId=" + session['sessionId'])
    intent = intent_request['intent']
    slots = intent_request['intent']['slots']
    intent_name = intent_request['intent']['name']

    if intent_name == "GetGarbageSchedule":
        # First see if user specified an address
        if 'address' in slots and 'value' in slots['address']:
            street_address = slots['address']['value']
        else:
            # Attempt to load default address from device
            logger.info("Context: %s" % context)
            device_id = context.get('System', {}).get('device', {}).get('deviceId')
            consent_token = context.get('System', {}).get('user', {}).get('permissions', {}).get('consentToken')
            location = skill_core.get_alexa_location(device_id, consent_token)
            if not location:
                return seattle_garbage_schedule.get_no_default_address_response()

            if location.get('city').lower() != 'seattle' or not location.get('addressLine1'):
                return seattle_garbage_schedule.get_invalid_address_response()

            street_address = location['addressLine1']
            logger.info("Using device's default location: %s" % street_address)
            
            
        return seattle_garbage_schedule.get_schedule_response(street_address)
    elif intent_name == "AMAZON.HelpIntent":
        return seattle_garbage_schedule.get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return seattle_garbage_schedule.get_session_end_response()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """
    Called when the user ends the session.
    Note: is not called when the skill returns should_end_session=true
    """
    logger.info("on_session_ended requestId=" + session_ended_request['requestId'] + ", sessionId=" + session['sessionId'])


def lambda_handler(event, context):
    """
    Main input handler. Route the incoming request based on type (LaunchRequest, IntentRequest, etc.)
    The JSON body of the request is provided in the event parameter.
    """
    logger.info("event.session.application.applicationId=" + event['session']['application']['applicationId'])

    # Don't allow other skills to call
#    if event['session']['application']['applicationId'] != "amzn1.echo-sdk-ams.app.[unique-value-here]":
#        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']}, event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'], event['context'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
