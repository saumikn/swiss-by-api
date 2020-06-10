from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from main import sheet_id, pairing_sheet

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_creds():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def update_pairing(p):
    sheet = build('sheets', 'v4', credentials=get_creds()).spreadsheets()
    values = {'values':[[p.white, p.result, p.black, p.link]]}
    result = sheet.values().update(spreadsheetId=sheet_id,
                                    range=f'{pairing_sheet}!{p.cell}',
                                    valueInputOption='USER_ENTERED',
                                    body=values).execute()

def find_missing_arena(username, score, sheet_name, sheet_id, col1, col2):
    sheet = build('sheets', 'v4', credentials=get_creds()).spreadsheets()
    values = {'values':[[f'=IFERROR(ROW(INDIRECT(ADDRESS(MATCH("{username}",{col1}:{col1},0),1))),"None")']]}
    sheet.values().update(spreadsheetId=sheet_id,
                            range=f'{sheet_name}!a1',
                            valueInputOption='USER_ENTERED',
                            body=values).execute()
    row = sheet.values().get(spreadsheetId=sheet_id,range=f'{sheet_name}!a1').execute()
    row = row['values'][0][0]
    if row == 'None':
        print(username)
        return

def update_arena(username, score, sheet_name, sheet_id, col1, col2):
    sheet = build('sheets', 'v4', credentials=get_creds()).spreadsheets()

    values = {'values':[[f'=IFERROR(ROW(INDIRECT(ADDRESS(MATCH("{username}",{col1}:{col1},0),1))),"None")']]}
    sheet.values().update(spreadsheetId=sheet_id,
                            range=f'{sheet_name}!a1',
                            valueInputOption='USER_ENTERED',
                            body=values).execute()
    row = sheet.values().get(spreadsheetId=sheet_id,range=f'{sheet_name}!a1').execute()
    row = row['values'][0][0]
    if row == 'None':
        print(username)
        return

    values = {'values':[[str(score)]]}
    sheet.values().update(spreadsheetId=sheet_id,
                            range=f'{sheet_name}!{col2}{row}',
                            valueInputOption='USER_ENTERED',
                            body=values).execute()


def update_cell(values, sheet_name, cell, sheet_id=sheet_id):
    sheet = build('sheets', 'v4', credentials=get_creds()).spreadsheets()
    result = sheet.values().update(spreadsheetId=sheet_id,
                                    range=f'{sheet}!{cell}',
                                    valueInputOption='RAW',
                                    body=values).execute()
    
if __name__ == '__main__':
    get_creds()