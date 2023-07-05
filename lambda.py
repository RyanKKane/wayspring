# import urllib to process URL requests
from urllib.request import urlopen

# import json to deal with the json response
import json

# import boto3 to work with DynamoDB/SNS
import boto3
import sys
import os
from boto3.dynamodb.conditions import Key

# import datetime to do date manipulation
from datetime import datetime, timedelta


def check_sms():
    # JSON from API
    # URL of third-party api about messages received.
    url = "https://thirdpartyapi.com/sms_received"

    # store response from the URL
    response = urlopen(url)

    # process the response into JSON for further processing
    message_json = json.loads(response.read())

    d = dict();
    d['phone_number'] = message_json["payload"]["object"]["sender"]["phone_number"]
    d['time_stamp'] = message_json["payload"]["object"]["date_time"]
    # return dict object with phone_numer and time_stamp to process
    return d



def compare_timestamp(new_sms):

    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    # Static DynamoDB Table name. This should really be pulled as a parameter
    table = dynamodb.Table('ddb-AfterHours-MessagesSent')

    one_hour_check = new_sms["time_stamp"] - timedelta(minutes=60)
    # Pull any item from the table that is newer than 60min prior to prevent multiple texts.
    return table.query(
        KeyConditionExpression=Key('phone_number').eq(new_sms["phone_number"]) & Key('time_stamp').gt(one_hour_check)
    )

def send_sms(new_sms):
    # Prepare SMS message
    client = boto3.client("sns", region_name="us-east-1")
    client.set_sms_attributes(
        attributes={
            'DefaultSMSType': 'Transactional',
            'DeliveryStatusSuccessSamplingRate': '100',
            'DefaultSenderID': 'NuWellness'
        }
    )

    # Publish SMS message
    response = client.publish(
        PhoneNumber=new_sms["phone_number"],
        Message="Hello, we are sorry but NuWellness is currently closed. Our normal hours are Mon-Fri, 8am-5pm CT. Someone will return your message during normal business hours. Thank you "
    )

    # Write item to DynamoDB table about new response
    dynamodb = boto3.client('dynamodb')
    item = {
        'phone_number':{'S':new_sms['phone_number']},
        'time_stamp':{'S':new_sms['time_stamp']}
    }
    response = dynamodb.put_item(
        TableName='ddb-AfterHours-MessagesSent',
        Item=item
    )




def lambda_handler(event, context):
    # Check for new SMS
    new_sms = check_sms()
    # returns a value if a message was sent in the last hour. If null is returned send new SMS response.
    if not compare_timestamp(new_sms):
        send_sms(new_sms)














