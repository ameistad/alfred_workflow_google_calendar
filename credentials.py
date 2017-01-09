#!/usr/bin/python
# encoding: utf-8
from __future__ import print_function
import os
import sys
import argparse

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from workflow import Workflow
from workflow.notify import notify

from google_calendar import (
    CALENDAR_NAME,
    SCOPES,
    HOME_DIR,
    CLIENT_SECRET_DIR,
    CLIENT_SECRET_FILE,
    CLIENT_SECRET_FILE_PATH,
    CREDENTIAL_DIR,
    CREDENTIAL_FILE,
    CREDENTIAL_FILE_PATH
)


def main(wf):
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    if not os.path.exists(CREDENTIAL_DIR):
        os.makedirs(CREDENTIAL_DIR)

    store = Storage(CREDENTIAL_FILE_PATH)
    credentials = store.get()
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE_PATH, SCOPES)
    flow.user_agent = CALENDAR_NAME
    credentials = tools.run_flow(flow, store, flags)
    notify(title=CALENDAR_NAME,
           text=u'Google credentials has been stored in {}'.format(
                CREDENTIAL_FILE_PATH),
           sound=None)


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
