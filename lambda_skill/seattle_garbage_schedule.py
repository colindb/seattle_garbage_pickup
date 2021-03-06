import datetime
import logging
import skill_core
import pickup_api


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_welcome_response():
    card_title = "Seattle Garbage Pickup Schedule"
    card_output = 'Try asking: when is my next garbage pickup.'
    speech_output = 'This is the Seattle Garbage Pickup Schedule. Try asking: when is my next garbage pickup.'
    skill_response = skill_core.build_speechlet_response(title = card_title,
                                                         card_output = card_output,
                                                         output = speech_output,
                                                         reprompt_text = None,
                                                         should_end_session = False)
    return skill_core.build_response(session_attributes = {}, speechlet_response = skill_response)


def get_no_default_address_response():
    card_title = "Can't Access Your Address"
    card_output = 'You need to allow this skill to access your address using your Alexa app.'
    speech_output = 'This skill does not have access to your address. You need to allow ' \
                    'access using your Alexa app or specify an address by asking: ' \
                    'when is the next pickup for [your address].'
    skill_response = skill_core.build_speechlet_response(title = card_title,
                                                         card_output = card_output,
                                                         output = speech_output,
                                                         reprompt_text = None,
                                                         should_end_session = True)
    return skill_core.build_response(session_attributes = {}, speechlet_response = skill_response)


def get_invalid_address_response():
    card_title = "Invalid Address"
    card_output = 'Your device does not have a valid Seattle address. Please update your address using your Alexa app.'
    speech_output = 'Your device does not have a valid Seattle address. You need to either update ' \
                    'your address using your Alexa app or specify an address by asking: ' \
                    'when is the next pickup for [your address].'
    skill_response = skill_core.build_speechlet_response(title = card_title,
                                                         card_output = card_output,
                                                         output = speech_output,
                                                         reprompt_text = None,
                                                         should_end_session = True)
    return skill_core.build_response(session_attributes = {}, speechlet_response = skill_response)


def get_session_end_response():
    card_title = "Session Ended"
    card_output = "Thank you for using Seattle Garbage Pickup"
    speech_output = "Thank you for using Seattle Garbage Pickup"
    speechlet_response = skill_core.build_speechlet_response(title = card_title,
                                                             card_output = card_output,
                                                             output = speech_output,
                                                             reprompt_text = None,
                                                             should_end_session = True)
    return skill_core.build_response({}, speechlet_response)


def get_schedule_response(street_address, pickup_start_date = None):
    start_time = 0
    if pickup_start_date:
        # Convert date to unix timestamp
        a_date = datetime.datetime.strptime(pickup_start_date, "%Y-%m-%d")
        start_time = int(a_date.timestamp())

    try:
        upcoming_pickups = pickup_api.get_seattle_garbage_pickup_schedule(street_address, start_time)
    except Exception as exc:
        logger.error("Unable to get schedule for address %s and time %s: %s" % (street_address, start_time, exc))
        card_title = "Can't Find Your Address"
        card_output = "Unable to find a pickup schedule for %s. Schedules are only available for house addresses, not apartments or businesses." % street_address
        address_str = '<say-as interpret-as="address">%s</say-as>' % street_address
        speech_output = "Unable to find a pickup schedule for %s. Schedules are only available for house addresses, not apartments or businesses." % address_str
        speechlet_response = skill_core.build_speechlet_response(title = card_title,
                                                                 card_output = card_output,
                                                                 output = speech_output,
                                                                 reprompt_text = None,
                                                                 should_end_session = True)
        return skill_core.build_response({}, speechlet_response)

    if pickup_start_date:
        start_looking_from = datetime.datetime.strptime(pickup_start_date, "%Y-%m-%d").date()
    else:
        start_looking_from = datetime.date.today()

    next_pickup = None
    for a_pickup in upcoming_pickups:
        logger.info("Looking at upcoming pickup: %s" % a_pickup)
        a_pickup_date = datetime.datetime.strptime(a_pickup['date'], "%Y-%m-%d").date()
        if a_pickup_date > start_looking_from:
            logger.info("Found the next pickup")
            next_pickup = a_pickup
            break

    if not next_pickup:
        card_title = "Unable To Find Pickup"
        card_output = "Sorry, unable to find the next scheduled pickup for your address."
        speech_output = "Sorry, unable to find the next scheduled pickup for your address."
    else:
        card_title = "Next Scheduled Pickup"
        pickup_date_str = next_pickup['date']
        next_pickup_datetime = datetime.datetime.strptime(pickup_date_str, "%Y-%m-%d")
        next_pickup_date = next_pickup_datetime.date()
        date_pickup_str = next_pickup_date.strftime("%A, %B %d")
        # Pretty, pretttty hacky. Assuming garbage and yard waste are every week
        if next_pickup['recycling']:
            pickup_list_str = "garbage, recycling and yardwaste"
        else:
            pickup_list_str = "garbage and recycling"
        address_str = '<say-as interpret-as="address">%s</say-as>' % street_address
        card_output = "The next pickup for %s is %s, for %s." % (street_address, date_pickup_str, pickup_list_str)
        speech_output = "The next pickup for %s is %s, for %s." % (address_str, date_pickup_str, pickup_list_str)

    speechlet_response = skill_core.build_speechlet_response(title = card_title,
                                                             card_output = card_output,
                                                             output = speech_output,
                                                             reprompt_text = None,
                                                             should_end_session = True)
    return skill_core.build_response({}, speechlet_response)
