import json
import boto3
import logging
import os
import botocore.session
from botocore.exceptions import ClientError
session = botocore.session.get_session()

logging.basicConfig(level=logging.DEBUG)
logger=logging.getLogger(__name__)

def lambda_handler(event, context):
	logger.setLevel(logging.DEBUG)
	eventname = event['detail']['eventName']
	snsARN = 'SNS_ARN_HERE'
	user = event['detail']['userIdentity']['type']
	
	logger.debug("Event is --- %s" %event)
	logger.debug("Event Name is--- %s" %eventname)
	logger.debug("SNSARN is-- %s" %snsARN)
	logger.debug("User Name is -- %s" %user)
	
	client = boto3.client('iam')
	snsclient = boto3.client('sns')
	response = client.list_account_aliases()
	logger.debug("List Account Alias response --- %s" %response)
	
	try:
		if not response['AccountAliases']:
			accntAliase = (boto3.client('sts').get_caller_identity()['Account'])
			logger.info("Account Aliase is not defined. Account ID is %s" %accntAliase)
		else:
			accntAliase = response['AccountAliases'][0]
			logger.info("Account Aliase is : %s" %accntAliase)
	
	except ClientError as e:
		logger.error("Client Error occured")
	
	try: 
		#Sending the notification...
		snspublish = snsclient.publish(
						TargetArn= snsARN,
						Subject=(("Root API call-\"%s\" detected in Account-\"%s\"" %(eventname,accntAliase))[:100]),
						Message=json.dumps({'default':json.dumps(event, indent=4)}),
						MessageStructure='json')
		logger.debug("SNS publish response is-- %s" %snspublish)
	except ClientError as e:
		logger.error("An error occured: %s" %e)
