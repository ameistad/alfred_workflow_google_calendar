#!/usr/bin/python
# encoding: utf-8

from __future__ import print_function
import httplib2
import os
import sys

import datetime
import locale

from apiclient import discovery
from oauth2client.file import Storage

from workflow import Workflow, ICON_WARNING

log = None

# SETTINGS
CALENDAR_NAME = u'Google Calendar'

# If you modify SCOPES deleted previous saved crendentials file.
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'

HOME_DIR = os.path.expanduser('~')

CLIENT_SECRET_DIR = HOME_DIR
CLIENT_SECRET_FILE = 'client_secret.json'
CLIENT_SECRET_FILE_PATH = os.path.join(CLIENT_SECRET_DIR, CLIENT_SECRET_FILE)

CREDENTIAL_DIR = os.path.join(HOME_DIR, '.credentials')
CREDENTIAL_FILE = 'alfred_google_calendar_credentials.json'
CREDENTIAL_FILE_PATH = os.path.join(CREDENTIAL_DIR, CREDENTIAL_FILE)


def rfc_3339_parse(time):
    return datetime.datetime.strptime(
        time.split('+')[0], '%Y-%m-%dT%H:%M:%S').strftime('%H:%M')


def get_credentials():
    store = Storage(CREDENTIAL_FILE_PATH)
    credentials = store.get()

    # Check if credentials exist and are valid.
    if not credentials or credentials.invalid:
        wf.add_item(
            title=CALENDAR_NAME,
            subtitle=u'Google credentials does not exist or is invalid.',
            icon=ICON_WARNING)
        wf.send_feedback()
        return 0
    return credentials


def get_events(days_from_now, time_min, time_max):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    eventsResult = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])
    result = []
    if events:
        for event in events:
            event_start_time = event['start'].get('dateTime')
            if event_start_time is None:
                time = u'All day event'
            else:
                time = u'{} - {}'.format(
                        rfc_3339_parse(event_start_time),
                        rfc_3339_parse(event['end'].get('dateTime')))

            result.append({
                'summary': event['summary'],
                'time': time,
                'htmlLink': event['htmlLink']
                })
    else:
        return [{
            'summary': u'No events...',
            'time': u'Hooray!',
            'htmlLink': u'https://calendar.google.com/calendar/render'
        }]

    return result


def main(wf):
    # Get days from now from Alfred
    if len(wf.args):
        days_from_now = wf.args[0]
    else:
        days_from_now = None

    try:
        days_from_now = int(days_from_now)
    except ValueError:
        wf.add_item(
            title=CALENDAR_NAME,
            subtitle=u'That\'s not a number...')
        wf.send_feedback()
        return 0

    if days_from_now > 999999:
        wf.add_item(
            title=CALENDAR_NAME,
            subtitle=u'Sorry, number too large')
        wf.send_feedback()
        return 0

    get_date = datetime.date.today() + datetime.timedelta(days=days_from_now)
    time_min = get_date.isoformat() + 'T00:00:00Z'
    time_max = get_date.isoformat() + 'T23:00:00Z'
    events = get_events(days_from_now, time_min, time_max)
    text_date = get_date.strftime(
        '%A %d. %B %Y'
        ).decode(locale.getpreferredencoding()).capitalize()
    wf.add_item(
        title=CALENDAR_NAME,
        subtitle=text_date,
        arg=u'https://calendar.google.com/calendar/render',
        valid=True
        )

    for event in events:
        wf.add_item(
            title=event['summary'],
            subtitle=event['time'],
            arg=event['htmlLink'],
            valid=True)

    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))
