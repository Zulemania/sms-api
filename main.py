# Download the helper library from https://www.twilio.com/docs/python/install
import os
import json
from twilio.rest import Client
import boto3
from botocore.exceptions import ClientError
from boto3 import Session
from datetime import datetime
from elasticsearch import Elasticsearch, helpers



# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure


def get_secret(secret_name):
    region_name = "eu-west-1"

    session = boto3.session.Session(profile_name='trash')
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
    )
    

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        #print(get_secret_value_response['SecretString'])
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secret_name + " was not found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", e)
        elif e.response['Error']['Code'] == 'DecryptionFailure':
            print("The requested secret can't be decrypted using the provided KMS key:", e)
        elif e.response['Error']['Code'] == 'InternalServiceError':
            print("An error occurred on service side:", e)
    else:
        # Secrets Manager decrypts the secret value using the associated KMS CMK
        # Depending on whether the secret was a string or binary, only one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            return get_secret_value_response['SecretString']


def send_sms(message):
    es = Elasticsearch(
    "localhost: 9200"
    
)

    account_sid = get_secret('ACCOUNT_SID')
    auth_token = get_secret("ACCOUNT_AUTH")
    client = Client(account_sid, auth_token)

    #doc = {'_version': <Twilio.Api.V2010>, '_properties': {'body': 'Hello there', 'num_segments': '1', 'direction': 'outbound-api', 'from_': '+14845099095', 'to': '+2348060073375', 'date_updated': datetime.datetime(2022, 2, 28, 18, 4, 4, tzinfo=<UTC>), 'price': None, 'error_message': None, 'uri': '/2010-04-01/Accounts/ACa0b11da3a6989c6b48dcc3acc2d2032c/Messages/SMdc3a132855634883ad1b5c93eb40ce2c.json', 'account_sid': 'ACa0b11da3a6989c6b48dcc3acc2d2032c', 'num_media': '0', 'status': 'queued', 'messaging_service_sid': None, 'sid': 'SMdc3a132855634883ad1b5c93eb40ce2c', 'date_sent': None, 'date_created': datetime.datetime(2022, 2, 28, 18, 4, 4, tzinfo=<UTC>), 'error_code': None, 'price_unit': 'USD', 'api_version': '2010-04-01', 'subresource_uris': {'media': '/2010-04-01/Accounts/ACa0b11da3a6989c6b48dcc3acc2d2032c/Messages/SMdc3a132855634883ad1b5c93eb40ce2c/Media.json'}}, '_context': None, '_solution': {'account_sid': 'ACa0b11da3a6989c6b48dcc3acc2d2032c', 'sid': 'SMdc3a132855634883ad1b5c93eb40ce2c'}}

    message = client.messages \
                    .create(
                     body=message,
                     from_='+14845099095',
                     to='+4915222072245'
                 )

    es_data = {
        "account_sid": message.account_sid,
        "api_version": "2010-04-01",
        "body": "Hello there",
        "date_created": message.date_created,
        "date_sent": message.date_sent,
        "date_updated": message.date_updated,
        "direction": "outbound-api",
        "error_code": "null",
        "error_message": "null",
        "from": "+14845099095",
        "messaging_service_sid": "null",
        "num_media": "0",
        "num_segments": "1",
        "price": "null",
        "price_unit": "null",
        "sid": message.sid,
        "status": "sent",
        "subresource_uris": {
            "media": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages/SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Media.json"
        },
        "to": "+4915222072245",
        "uri": "/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages/SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.json"
        }
    resp = es.index(index="mofesola", document=es_data)


    print(resp['result'])
    print(es_data)

if __name__ == "__main__":
    send_sms("Hello there")
