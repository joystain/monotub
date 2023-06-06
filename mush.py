# import needed libraries
import time 
import Adafruit_DHT as DHT
import RPi.GPIO as GPIO
import csv
from datetime import datetime

# libraries for sheets api

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# set gpio pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(20,GPIO.OUT)
GPIO.setup(21,GPIO.OUT)
GPIO.setup(26,GPIO.OUT)

# set relay numbers Left/Right

relay1=26
relay2=20
relay3=[21, "Fan"]
dht_sensor = DHT.DHT22
dht_pin = 4 

# turn all relays off just incase
GPIO.output(relay3[0],False)
GPIO.output(relay2,False)
GPIO.output(relay1,False)

# script delays

fan_delay=5
sensor_delay=5
set_temp=60
fan_time1=['06:00','12:00','18:00','23:29']
fan_time2=['06:31','12:31','18:31','24:00']

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1FQrfd-JQ8TTcgqR2BoMKC9lmwRdS5ZBPZiWGZWcyfVk'
RANGE_NAME = 'Data!A:D'

# Set up definitions

def relay_on(relay):
	GPIO.output(relay[0], True)
	print(f"{relay[1]} ON")

def relay_off(relay):
		GPIO.output(relay[0], False)
		print(f"{relay[1]} OFF")

def timed_fan(relay, t1,t2):
	now=datetime.now().strftime('%H:%M')
	for x,y in zip(t1,t2):
		if now >= x and now <= y:
			relay_on(relay)
			time.sleep(120)
			relay_off(relay)
	else:
		pass

def sheets_data(d,t,hum,temp):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=RANGE_NAME).execute()
        values = result.get('values', [])
        
        #enter th
        for x in range(1):
            sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=f"Data!A{len(values)+1}",
                                   valueInputOption="USER_ENTERED", body={"values": [[d]]}).execute()
            sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=f"Data!B{len(values)+1}",
                                   valueInputOption="USER_ENTERED", body={"values": [[t]]}).execute()
            sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=f"Data!C{len(values)+1}",
                                   valueInputOption="USER_ENTERED", body={"values": [[hum]]}).execute()
            sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=f"Data!D{len(values)+1}",
                                   valueInputOption="USER_ENTERED", body={"values": [[temp]]}).execute()
    except HttpError as error:
        print(error)
# Main loop here

try:
	while True:
		hum, temp = DHT.read(dht_sensor,dht_pin)
		if hum is not None and temp is not None:
			fahrenheit = (temp*9/5)+32
			print(f"Temp={fahrenheit:0.1f}F Humidity={hum:0.1f}%")

# save sensor data
			time_box=datetime.now().strftime('%H:%M')
			day=datetime.now().strftime('%m-%d-%Y')
			sheets_data(day,time_box,round(hum,1),round(fahrenheit,1))
            
# fan check
			timed_fan(relay3,fan_time1,fan_time2)
			time.sleep(sensor_delay)
# catch sensor failures
		else:
			print("Sensor Failure")
finally:
# clear GPIO
	GPIO.cleanup()
	print('Script Stopped')

