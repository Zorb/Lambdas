import json
import boto3
sqs = boto3.resource('sqs')

def lambda_handler(event, context):
    queue = sqs.get_queue_by_name(QueueName='MedRetrieval')
    for message in queue.receive_messages():
        result = message
        message.delete()
        return {
        'statusCode': 200,
        'body': result.body,
        'headers': {
           'Content-Type': 'application/json', 
           'Access-Control-Allow-Origin': '*' 
            }
        }
   
    
