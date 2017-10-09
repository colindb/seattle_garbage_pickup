import json
import logging
import urllib.request
import urllib.parse
import datetime


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def make_http_request(base_url, params):
    encoded_params = urllib.parse.urlencode(params, safe = '~')
    url = base_url + '?' + encoded_params
    logger.info("Making URL request to: %s" % url)
    resp = urllib.request.urlopen(url)
    resp_data = resp.read().decode('utf-8')
    resp_json = json.loads(resp_data)
    logger.info("Response JSON: %s" % resp_json)
    return resp_json


def format_raw_pickup_data(raw_pickup):
    logger.info("Formatting raw pickup data: %s" % raw_pickup)
    raw_date_str = raw_pickup['start']
    date_obj = datetime.datetime.strptime(raw_date_str, "%a, %d %b %Y").date()
    date_str = date_obj.strftime("%Y-%m-%d")

    cleaned_data = {'date': date_str,
                    'garbage': raw_pickup['Garbage'],
                    'recycling': raw_pickup['Recycling'],
                    'yard_waste': raw_pickup['FoodAndYardWaste']}
    logger.info("Cleaned pickup info: %s" % cleaned_data)
    return cleaned_data


def get_seattle_garbage_pickup_schedule(street_address, start_time = 0):
    # Note: using start_time = 0 defaults the API to the current month.
    # Passing in an epoch value overrides start_time with that value (for QA).
    logger.info("Fetching Seattle address for street_address: %s and start_time %s" % (street_address, start_time))
    address_base = "http://www.seattle.gov/UTIL/WARP/Home/GetAddress"
    address_params = {'pAddress': street_address,
                      'pActiveOnly': 'spu',
                      'pUnit': '',
                      'pRequireSolidWasteServices': 'true'}

    address_json = make_http_request(address_base, address_params)
    if len(address_json) < 1:
        logger.error("No address data found")
        raise Exception("No address data found")
    elif len(address_json) > 1:
        logger.error("Multiple addresses found (%s), using first entry" % address_json)

    garbage_address = address_json[0]
    logger.info("Fetching Seattle garbage schedule time (%s) for address: %s" % (start_time, garbage_address))
    garbage_base = 'http://www.seattle.gov/UTIL/WARP/CollectionCalendar/GetCollectionDays'
    garbage_params_this_month = {'pAccount': '',
                                 'pAddress': garbage_address,
                                 'pJustChecking': '',
                                 'pApp': 'CC',
                                 'pIE': '',
                                 'start': start_time}

    garbage_json_this_month = make_http_request(garbage_base, garbage_params_this_month)

    if start_time == 0:
        today = datetime.datetime.today()
    else:
        today = datetime.datetime.fromtimestamp(start_time)
    next_year = today.year
    next_month = today.month + 1
    if next_month > 12:
        next_month = 1
        next_year = next_year + 1
    first_of_next_month = datetime.datetime(next_year, next_month, 1)
    next_month_start = int(first_of_next_month.timestamp())

    logger.info("Fetching next month's Seattle garbage schedule with start: %s" % next_month_start)
    garbage_params_next_month = {'pAccount': '',
                                 'pAddress': garbage_address,
                                 'pJustChecking': '',
                                 'pApp': 'CC',
                                 'pIE': '',
                                 'start': next_month_start}

    garbage_json_next_month = make_http_request(garbage_base, garbage_params_next_month)

    pickup_schedule = []
    for a_raw_pickup in garbage_json_this_month:
        pickup_schedule.append(format_raw_pickup_data(a_raw_pickup))

    for a_raw_pickup in garbage_json_next_month:
        pickup_schedule.append(format_raw_pickup_data(a_raw_pickup))

    return pickup_schedule
