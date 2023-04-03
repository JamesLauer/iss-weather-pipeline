import unittest
import datetime
from app.lambdas.functions.sqs import (
	transform_city_sqs_message_response_to_dictionary
	)
from app.lambdas.functions.other import (
	create_s3_object_name_for_api_data_export
	)


class TestParseLocationSqsMessageResponseToDictionary(unittest.TestCase):
	# Tests the parse_location_sqs_message_response_to_dictionary function
	
	def test_result_equals_mocked_result(self):
		# Tests that the tested function result equals the mocked result
		# Mocks expected  sqs message content for input into function under test
		expected_record_from_sqs_message = {
			"body": "{\"city\": \"Perth\", \"region\": \"Western Australia\", "
					"\"latitude\": \"-31.9522\", \"longitude\": \"115.8589\", "
					"\"country\": \"Australia\", \"country_code\": \"AUS\"}",
			}
		
		# Mocks expected test function output result
		expected_test_city_data_dict = {
			'city': 'Perth',
			'lat': '-31.9522',
			'lon': '115.8589',
			'region': 'Western Australia',
			'country': 'Australia',
			'country_code': 'AUS'
			}
		
		# Calls function to be tested
		test_func = transform_city_sqs_message_response_to_dictionary(
			record=expected_record_from_sqs_message
			)
		
		# Runs assertions
		self.assertEqual(test_func, expected_test_city_data_dict)


class TestCreateS3ObjectNameForApiDataExport(unittest.TestCase):
	# Tests the create_s3_object_name_for_api_data_export function
	
	def test_result_equals_mocked_result(self):
		# Tests that the tested function result equals the mocked result
		# Mocks expected object name
		date = datetime.datetime.now().strftime('%Y_%m_%d')
		date_prefix = datetime.datetime.now().strftime("year=%Y/month=%m/day=%d")
		expected_object_name = f's3-bucket/{date_prefix}/api_call_name-CC-region-' \
							   f'{date}-City-utc.json'
		
		# Calls function to be tested
		test_func = create_s3_object_name_for_api_data_export(
			s3_bucket_prefix='s3-bucket',
			city_name='City',
			region='region',
			country_code='CC',
			api_call_name='api_call_name'
			)
		
		# Runs assertions
		self.assertEqual(test_func, expected_object_name)


if __name__ == '__main__':
	unittest.main(verbosity=2)
