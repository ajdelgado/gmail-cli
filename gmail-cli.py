#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This script is licensed under GNU GPL version 3.0
# (c) 2020 Antonio J. Delgado
import json
import pickle
import os
import click
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

@click.command()
@click.option('--query', '-q', help='Google Mail query to run')
def get_messages(query):
    home_folder = os.environ.get('HOME', os.environ.get('USERPROFILE',''))
    with open(os.path.join(home_folder, '.local', 'client_secret_gmail.json'), 'r') as cred_file:
        credentials = json.load(cred_file)
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify',
        ]
    creds = None
    token_file = os.path.join(home_folder, '.local', 'gmail-cli_token.pickle')
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
                credentials,
                scopes=SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=creds)

    #results = service.users().labels().list(userId='me').execute()
    results = service.users().messages().list(userId='me', q=query).execute()
    output = list()
    for iter_message in results.get('messages', list()):
        gmessage = service.users().messages().get(userId='me', format='full', id=iter_message['id']).execute()
        message = dict()
        payload = gmessage.get('payload',dict())
        headers = payload.get('headers', list())
        for header in headers:
            if 'name' in header and 'value' in header:
                message[header['name']] = header['value']
        for key in gmessage.keys():
            message[key] = gmessage[key]
        #print(f"({iter_message['id']}) {subject}")
        output.append(message)
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    get_messages()