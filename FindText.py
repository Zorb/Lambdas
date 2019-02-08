from __future__ import print_function

import boto3
from decimal import Decimal
from boto3 import dynamodb 
import json
import urllib
from boto3.dynamodb.conditions import Key, Attr

rekognition = boto3.client('rekognition')
client = boto3.client('dynamodb')
sqs = boto3.resource('sqs')

# --------------- Helper Functions to call Rekognition APIs ------------------


def detect_text(bucket, key):
    response = rekognition.detect_text(Image={'S3Object': {'Bucket': bucket, 'Name': key}})
    return response
    
def search_db(name):
    response2 = client.get_item(TableName='medicine_mock', Key={'Name':{'S':name}})
    return response2



# --------------- Main handler ------------------


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(
        event['Records'][0]['s3']['object']['key'].encode('utf8'))

    try:

        response = detect_text(bucket, key)
        textDetections = response['TextDetections']
        name = textDetections[0]['DetectedText']
        response2 = search_db(name)
        queue = sqs.get_queue_by_name(QueueName='MedRetrieval')
        queue.send_message(MessageBody=json.dumps(response2))
        print("GetItem succeeded:")
        print(response2['Item']['Name']['S'])
        print(response2['Item']['Description']['S'])
        # print('Detected text')
        # for text in textDetections:
        #     print('Detected text:' + text['DetectedText'])
        #     print('Confidence: ' + "{:.2f}".format(text['Confidence']) + "%")
        #     print('Id: {}'.format(text['Id']))
        #     if 'ParentId' in text:
        #         print('Parent Id: {}'.format(text['ParentId']))
        #     print('Type:' + text['Type'])

    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e
