import gspread
import json
import os

#Load credentials from repo secret
credentials_json = os.getenv('GOOGLE_LOGUSER_SHEET_CREDENTIALS')

# Parse JSON string into a dictionary
credentials - json.loads(credentials_json)

#Authenticate with Google Sheets API
gc = gspread.service_account_from_dict(credentials)

#Open the Google Sheets spreadsheet by its ID
sheet_id = os.getenv('GOOGLE_LOGUSER_SPREADSHEET_ID')
sheet = client.open_by_key(sheet_id)

#Select the worksheet by its index (0 for the first worksheet)
worksheet = sheet.get_worksheet(0)

#Append the data to the worksheet
worksheet.append_row(data)

#Select the worksheet by its index (0 for the first worksheet)
worksheet = sheet.get_worksheet(0)

#Split log_entry
row = log_entry.split('|')

#Append the data to the worksheet
worksheet.append_row(row)
