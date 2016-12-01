# install with pip
# * pip install httplib2 --upgrade
# * pip install google-api-python-client --upgrade
# * pip install python-dateutil --upgrade

# read the docs
# * https://developers.google.com/google-apps/calendar/quickstart/python
# * https://developers.google.com/google-apps/calendar/v3/reference/events
# * https://developers.google.com/google-apps/calendar/auth
# * https://console.developers.google.com/apis/credentials?project=eternal-autumn-142223

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

from datetime import datetime, timedelta
import dateutil.parser

import collections

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = 'Calendar Math'


def get_credentials():
    """Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def do_calendar_math():

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    p1 = '2016-11-28'
    p2 = '+06:00'

    timeMin = datetime.strptime(p1, '%Y-%m-%d')
    timeMax = timeMin + timedelta(seconds=-1, weeks=1)

    print ("======INPUT=======")
    print ("timeMin = ", timeMin.isoformat()+p2)
    print ("timeMax = ", timeMax.isoformat()+p2)

    page_token = None
    while True:
      calendar_list = service.calendarList().list(pageToken=page_token).execute()
      for calendar_list_entry in calendar_list['items']:
        print (calendar_list_entry['id'], calendar_list_entry['summary'])
      page_token = calendar_list.get('nextPageToken')
      if not page_token:
        break

    eventsResult = service.events().list(
        calendarId='alexk@handsome.is', timeMin=timeMin.isoformat()+p2, timeMax=timeMax.isoformat()+p2, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    iteratorDate = None
    iteratorLoad = 0

    if not events:
        print ("======SUMMARY=======")
        print ('No events for the period.')
    else:

        result = collections.OrderedDict({})

        print ("======EVENTS=======")
        for event in events:

            # print ('----', event['summary'], '----')

            try:

                if (event.get('attendees', None) != None):
                    for attendee in event.get('attendees'):
                        if ((attendee.get('self', False) == True) and (attendee.get('responseStatus') == 'declined')):
                            raise

                colorId = event.get('colorId', '-1')
                # -1: black (default)
                # 5: yellow (leadership)
                # 11: red (discipline - mobile & devices)
                # 3: purple (discipline - support)
                # 9: blue (project face-down work)
                # 1: light blue (project meetings)
                # 10: green (relax)
                # 6: orange (unavailable)

                if (not (colorId in ['-1', '5', '11', '9', '1', '3', '8'])):
                    raise

                #if ("Mobile Stand-up" in event["summary"]):
                #    raise

                #if ("Company.com - PM/TPO sync" in event["summary"]):
                #    raise

                startTime = dateutil.parser.parse(event['start'].get('dateTime'))
                endTime = dateutil.parser.parse(event['end'].get('dateTime'))
                minsDelta = (endTime - startTime).seconds / 60
                if minsDelta == 25:
                    minsDelta = 30
                if (result.has_key(startTime.date())):
                    result[startTime.date()] = result[startTime.date()] + minsDelta
                    # print(startTime.date(), '+', hoursDelta, '=', result[startTime.date()])
                else:
                    result[startTime.date()] = minsDelta
                    # print('new', startTime.date(), '=', result[startTime.date()])
                print (startTime, event["summary"], "(" + str(minsDelta) + " mins)", "color=" + colorId)
            except:
                print ("*********SKIPPING*********", event["summary"], "color=" + colorId)
                # print ('skipping event')

        print ("======SUMMARY=======")

        weekMins = 0
        for date, mins in result.iteritems():
            print (date, "=", format(mins / 60.0, '.1f'), 'hours')
            weekMins += mins

        print ("week =", format(weekMins / 60.0, '.1f'), 'hours')

if __name__ == '__main__':
    do_calendar_math()
