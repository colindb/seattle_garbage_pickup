import os
import copy
import subprocess
import json

payload_template = {
  "session": {
    "new": True,
    "sessionId": "SessionId.TEST",
    "application": {
      "applicationId": "amzn1.ask.skill.TEST"
    },
    "attributes": {},
    "user": {
      "userId": "amzn1.ask.account.TEST"
    }
  },
  "request": {
    "type": "IntentRequest",
    "requestId": "EdwRequestId.TEST",
    "intent": {
      "name": "GetGarbageSchedule",
      "slots": {}
    },
    "locale": "en-US",
    "timestamp": "2017-09-29T20:23:07Z"
  },
  "context": {
    "AudioPlayer": {
      "playerActivity": "IDLE"
    },
    "System": {
      "application": {
        "applicationId": "amzn1.ask.skill.TEST"
      },
      "user": {
        "userId": "amzn1.ask.account.TEST"
      },
      "device": {
        "supportedInterfaces": {}
      }
    }
  },
  "version": "1.0"
}


test_data = [{'slots': {},
              'response_text': "This skill does not have access to your address."},
             {'slots': {
                 'address': {'name': 'address', 'value': '324 N 76th St'},
                 'date': {'name': 'date', 'value': '2017-10-01'}},
              'response_text': 'Monday, October 02, for garbage, recycling and yardwaste.'},
             {'slots': {
                 'address': {'name': 'address', 'value': '7055 7th AVE NW'},
                 'date': {'name': 'date', 'value': '2017-10-01'}},
              'response_text': 'Wednesday, October 04, for garbage, recycling and yardwaste.'},
             {'slots': {
                 'address': {'name': 'address', 'value': '119 Lee St'},
                 'date': {'name': 'date', 'value': '2017-10-01'}},
              'response_text': 'Wednesday, October 04, for garbage and recycling.'},
             {'slots': {
                 'address': {'name': 'address', 'value': '1614 7th Ave W'},
                 'date': {'name': 'date', 'value': '2017-10-01'}},
              'response_text': 'Tuesday, October 03, for garbage and recycling.'},
             {'slots': {
                 'address': {'name': 'address', 'value': '1123 27th Ave'},
                 'date': {'name': 'date', 'value': '2017-10-01'}},
              'response_text': 'Friday, October 06, for garbage, recycling and yardwaste.'},
             {'slots': {
                 'address': {'name': 'address', 'value': '3202 E Spruce st'},
                 'date': {'name': 'date', 'value': '2017-10-01'}},
              'response_text': 'Friday, October 06, for garbage, recycling and yardwaste.'},
             {'slots': {
                 'address': {'name': 'address', 'value': '325 17th Ave'},
                 'date': {'name': 'date', 'value': '2017-10-01'}},
              'response_text': 'Friday, October 06, for garbage and recycling.'},
             {'slots': {
                 'address': {'name': 'address', 'value': '325 17th Ave'},
                 'date': {'name': 'date', 'value': '2017-10-02'}},
              'response_text': 'Friday, October 06, for garbage and recycling.'},
             {'slots': {
                 'address': {'name': 'address', 'value': '325 17th Ave'},
                 'date': {'name': 'date', 'value': '2017-10-03'}},
              'response_text': 'Friday, October 06, for garbage and recycling.'},
             {'slots': {
                 'address': {'name': 'address', 'value': '325 17th Ave'},
                 'date': {'name': 'date', 'value': '2017-10-04'}},
              'response_text': 'Friday, October 06, for garbage and recycling.'},
             {'slots': {
                 'address': {'name': 'address', 'value': '325 17th Ave'},
                 'date': {'name': 'date', 'value': '2017-10-05'}},
              'response_text': 'Friday, October 06, for garbage and recycling.'},
             {'slots': {
                 'address': {'name': 'address', 'value': '325 17th Ave'},
                 'date': {'name': 'date', 'value': '2017-10-30'}},
              'response_text': 'Friday, November 03, for garbage and recycling.'},
             {'slots': {
                 'address': {'name': 'address', 'value': '325 17th Ave'},
                 'date': {'name': 'date', 'value': '2017-10-31'}},
              'response_text': 'Friday, November 03, for garbage and recycling.'},
             {'slots': {
                 'address': {'name': 'address', 'value': '325 17th Ave'},
                 'date': {'name': 'date', 'value': '2017-11-01'}},
              'response_text': 'Friday, November 03, for garbage and recycling.'},
             {'slots': {
                 'address': {'name': 'address', 'value': '325 17th Ave'},
                 'date': {'name': 'date', 'value': '2017-11-02'}},
              'response_text': 'Friday, November 03, for garbage and recycling.'},
             {'slots': {
                 'address': {'name': 'address', 'value': '325 17th Ave'},
                 'date': {'name': 'date', 'value': '2017-12-30'}},
              'response_text': 'Saturday, January 06, for garbage, recycling and yardwaste.'},
             {'slots': {
                 'address': {'name': 'address', 'value': '325 17th Ave'},
                 'date': {'name': 'date', 'value': '2017-12-31'}},
              'response_text': 'Saturday, January 06, for garbage, recycling and yardwaste.'},
             {'slots': {
                 'address': {'name': 'address', 'value': '325 17th Ave'},
                 'date': {'name': 'date', 'value': '2018-01-01'}},
              'response_text': 'Saturday, January 06, for garbage, recycling and yardwaste.'}]

outfile_name = "testoutput.txt"
for a_test in test_data:
    try:
        os.remove(outfile_name)
    except OSError:
        pass
    a_payload = copy.deepcopy(payload_template)
    a_payload['request']['intent']['slots'] = a_test['slots']

    subprocess.run(["aws", "lambda", "invoke",
                    "--invocation-type", "RequestResponse",
                    "--function-name", "seattleGarbagePickupAlexaSkill",
                    "--region", "us-east-1",
                    "--payload", json.dumps(a_payload),
                    outfile_name])

    fo = open(outfile_name, "r")
    file_str = fo.read()
    fo.close()

    if file_str.find(a_test['response_text']) == -1:
        print("ERROR: Text not found: %s" % a_test['response_text'])
        print("Response text: %s" % file_str)
