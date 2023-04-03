import json
import unittest
from unittest import mock
from moto import (mock_sqs)
import boto3
import os
from app.lambdas.functions.sqs import (
	send_city_list_to_sqs_queue
	)

# Sets default region
AWS_DEFAULT_REGION = 'ap-southeast-2'


# Patches Lambda environment variables into the tess class
@mock.patch.dict(
	'os.environ', {
		'AWS_DEFAULT_REGION': f'{AWS_DEFAULT_REGION}'
		}
	)
class TestSendCityListToSqsQueue(unittest.TestCase):
	# Tests the send_city_list_to_sqs_queue function
	mock_sqs = mock_sqs()
	queue_name = 'testing-queue'
	
	def setUp(self):
		# Sets up the test class' test requirements before tests run
		self.mock_sqs.start()
		sqs = boto3.client('sqs', region_name=AWS_DEFAULT_REGION)
		self.queue_url = sqs.create_queue(QueueName=self.queue_name)
	
	def tearDown(self):
		# Tears down the class test requirements after tests run
		self.mock_sqs.stop()
	
	def test_result_equals_mocked_result(self):
		# Tests that the tested function result equals the mocked result
		# Dynamically sets environment variable value to queue_url from setUp()
		with mock.patch.dict(
			'os.environ', {
				'QUEUE_URL': f'{self.queue_url["QueueUrl"]}'
				}
			):
			# Mocks Lambda environmental variables
			QUEUE_URL = os.environ['QUEUE_URL']
			
			# Mocks data to be sent to SQS queue. Each row not including header to be
			# sent.
			mocked_data = [
				['city', 'region', 'country', 'country_code', 'latitude', 'longitude'],
				['Perth', 'Western Australia', 'Australia', 'AUS', '-31.9522',
				 '115.8589']
				]
			
			# Calls function to be tested
			send_city_list_to_sqs_queue(
				region_env='AWS_DEFAULT_REGION',
				data=mocked_data,
				queue_url_env='QUEUE_URL'
				)
			
			# Mocks receiving of message for assertion
			sqs = boto3.client('sqs', region_name=AWS_DEFAULT_REGION)
			received_message = sqs.receive_message(
				QueueUrl=QUEUE_URL
				)
			message_body = json.loads(received_message["Messages"][0]["Body"])
			
			# Convert mocked_data to dictionary for assertions
			mocked_data_dict = dict(zip(mocked_data[0], mocked_data[1]))
			
			# Runs assertions
			self.assertIn(mocked_data_dict['city'], message_body['city'])
			self.assertIn(mocked_data_dict['region'], message_body['region'])
			self.assertIn(mocked_data_dict['country'], message_body['country'])
			self.assertIn(mocked_data_dict['country_code'], message_body['country_code'])
			self.assertIn(mocked_data_dict['latitude'], message_body['latitude'])
			self.assertIn(mocked_data_dict['longitude'], message_body['longitude'])


if __name__ == '__main__':
	unittest.main(verbosity=2)
