#Lambda function 1:

import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input
    key = event['s3_key'] ## TODO: fill in
    bucket = event['s3_bucket'] ## TODO: fill in

    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    local_path = '/tmp/image.png'
    s3.download_file(bucket, key, local_path)

    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }

#################################

#Lambda function 2:

import json
import boto3
import base64

# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2022-11-25-03-32-22-412"

runtime = boto3.client('runtime.sagemaker')

def lambda_handler(event, context):
    print("Event:", event.keys())
    
    # Decode the image data
    image = base64.b64decode(event['body']['image_data'])

    # Instantiate a Predictor
    response = runtime.invoke_endpoint(EndpointName = ENDPOINT, ContentType = 'image/png', Body = image) ## TODO: fill in

    # For this model the IdentitySerializer needs to be "image/png"
#    predictor.serializer = IdentitySerializer("image/png")

    # Make a prediction:
    event['body']["inferences"] = json.loads(response['Body'].read()) ## TODO: fill in

    # We return the data back to the Step Function    
    #event["inferences"] = inferences.decode('utf-8')
    
    return {
        'statusCode': 200,
        'body': {
            "image_data": event['body']['image_data'],
            "s3_bucket": event['body']['s3_bucket'],
            "s3_key": event['body']['s3_key'],
            "inferences": event['body']["inferences"]
        }
    }

#################################

#Lambda function 3:

import json

THRESHOLD = .8

def lambda_handler(event, context):

    # Grab the inferences from the event
    inferences = event['body']["inferences"] ## TODO: fill in

    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = (inferences[0] >= THRESHOLD) or (inferences[1] >= THRESHOLD) ## TODO: fill in

    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': {
            "image_data": event['body']['image_data'],
            "s3_bucket": event['body']['s3_bucket'],
            "s3_key": event['body']['s3_key'],
            "inferences": event['body']["inferences"]
        }
    }