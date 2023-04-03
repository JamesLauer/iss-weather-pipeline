import re
import unittest
from unittest import mock
from moto import mock_s3
import boto3
import csv
import os
from app.lambdas.functions.s3 import (
	get_list_from_s3_csv_object,
	get_sql_query_string_from_s3_sql_object,
	put_object_in_s3_bucket,
	count_objects_in_s3_prefix,
	)


# Patches Lambda environment variables into the tess class
@mock.patch.dict(
	'os.environ', {
		'LAMBDA_INPUT_DATA_NAME': 'testing.csv',
		'LAMBDA_INCORRECT_INPUT_DATA_NAME': 'testing.pdf',
		'S3_PREFIX': 'testing',
		'S3_BUCKET': 'testing'
		}
	)
class TestGetListFromS3CsvObject(unittest.TestCase):
	# Tests the get_list_from_s3_csv_object function
	mock_s3 = mock_s3()
	
	def setUp(self):
		# Sets up the test class' test requirements before tests run
		bucket_name = 'testing'
		self.mock_s3.start()
		s3 = boto3.client('s3', region_name='us-east-1')
		s3.create_bucket(Bucket=bucket_name)
	
	def tearDown(self):
		# Tears down the class test requirements after tests run
		self.mock_s3.stop()
	
	def test_result_equals_mocked_result(self):
		# Tests that the tested function result equals the mocked result
		# Mocks Lambda environmental variables
		LAMBDA_INPUT_DATA_NAME = os.environ['LAMBDA_INPUT_DATA_NAME']
		S3_PREFIX = os.environ['S3_PREFIX']
		S3_BUCKET = os.environ['S3_BUCKET']
		
		# Generates mocked file key name
		key = f'{S3_PREFIX}/{LAMBDA_INPUT_DATA_NAME}'
		
		# Mocks object content for assertion
		content: bytes = b'test content'
		content_str = content.decode('utf-8')
		content_str = list(csv.reader(content_str.splitlines()))
		
		# Mocks object to be returned in tested function
		s3 = boto3.client('s3', region_name='us-east-1')
		s3.put_object(
			Bucket=S3_BUCKET,
			Key=key,
			Body=content
			)
		
		# Calls function to be tested
		test_func = get_list_from_s3_csv_object(
			input_data='LAMBDA_INPUT_DATA_NAME',
			prefix='S3_PREFIX',
			s3_bucket='S3_BUCKET',
			log_index=0
			)
		
		# Runs assertions
		self.assertEqual(test_func, content_str)
	
	def test_error_for_non_csv_input(self):
		# Tests that an error is raised for a non csv file
		
		# Mocks Lambda environmental variables
		LAMBDA_INPUT_DATA_NAME = os.environ['LAMBDA_INCORRECT_INPUT_DATA_NAME']
		S3_PREFIX = os.environ['S3_PREFIX']
		S3_BUCKET = os.environ['S3_BUCKET']
		
		# Generates mocked file key name
		key = f'{S3_PREFIX}/{LAMBDA_INPUT_DATA_NAME}'
		
		# Generates mocked object content for assertion
		content: bytes = b'test content'
		
		# Mocks object to be returned in tested function
		s3 = boto3.client('s3', region_name='us-east-1')
		s3.put_object(
			Bucket=S3_BUCKET,
			Key=key,
			Body=content
			)
		
		# Runs assertions
		with self.assertRaises(Exception):
			get_list_from_s3_csv_object(
				input_data='LAMBDA_INPUT_DATA_NAME',
				prefix='S3_PREFIX',
				s3_bucket='S3_BUCKET',
				log_index=0
				)


# Patches Lambda environment variables into the tess class
@mock.patch.dict(
	'os.environ', {
		'S3_PREFIX': 'testing',
		'S3_BUCKET': 'testing'
		}
	)
class TestGetSqlQueryStringFromS3Object(unittest.TestCase):
	# Tests the get_sql_query_string_from_s3_sql_object function
	mock_s3 = mock_s3()
	
	def setUp(self):
		# Sets up the test class' test requirements before tests run
		bucket_name = 'testing'
		self.mock_s3.start()
		s3 = boto3.client('s3', region_name='us-east-1')
		s3.create_bucket(Bucket=bucket_name)
	
	def tearDown(self):
		# Tears down the class test requirements after tests run
		self.mock_s3.stop()
	
	def test_result_equals_mocked_result(self):
		# Tests that the tested function result equals the mocked result
		# Mocks Lambda environmental variables
		S3_PREFIX = os.environ['S3_PREFIX']
		S3_BUCKET = os.environ['S3_BUCKET']
		
		# Generates mocked file key name
		filename = 'testing.sql'
		key = f'{S3_PREFIX}/{filename}'
		
		# Generates mocked object content for assertion
		content: bytes = b'SELECT * FROM {}'
		content_str = content.decode('utf-8')
		
		# Mocks object to be returned in tested function
		s3 = boto3.client('s3', region_name='us-east-1')
		s3.put_object(
			Bucket=S3_BUCKET,
			Key=key,
			Body=content
			)
		
		# Calls function to be tested
		test_func = get_sql_query_string_from_s3_sql_object(
			sql_filename=filename,
			prefix='S3_PREFIX',
			s3_bucket='S3_BUCKET'
			)
		
		# Runs assertions
		self.assertEqual(test_func, content_str)
	
	def test_error_for_non_sql_input(self):
		# Tests that an error is raised for a non sql file
		# Mocks Lambda environmental variables
		S3_PREFIX = os.environ['S3_PREFIX']
		S3_BUCKET = os.environ['S3_BUCKET']
		
		# Generates mocked file key name
		key = f'{S3_PREFIX}/testing.sql'
		
		# Generates mocked object content for assertion
		content: bytes = b'test content'
		
		# Mocks object to be returned in tested function
		s3 = boto3.client('s3', region_name='us-east-1')
		s3.put_object(
			Bucket=S3_BUCKET,
			Key=key,
			Body=content
			)
		
		# Runs assertions
		with self.assertRaises(Exception):
			get_sql_query_string_from_s3_sql_object(
				sql_filename='test.sql',
				prefix='S3_PREFIX',
				s3_bucket='S3_BUCKET'
				)


# Patches Lambda environment variables into the tess class
@mock.patch.dict(
	'os.environ', {
		'S3_BUCKET': 'testing'
		}
	)
class TestPutObjectInS3Bucket(unittest.TestCase):
	# Tests the put_object_in_s3_bucket function
	mock_s3 = mock_s3()

	def setUp(self):
		# Sets up the test class' test requirements before tests run
		bucket_name = 'testing'
		self.mock_s3.start()
		s3 = boto3.client('s3', region_name='us-east-1')
		s3.create_bucket(Bucket=bucket_name)
	
	def tearDown(self):
		# Tears down the class test requirements after tests run
		self.mock_s3.stop()
	
	def test_result_equals_mocked_result(self):
		# Tests that the tested function result equals the mocked result
		
		# Mocks Lambda environmental variables
		S3_BUCKET = os.environ['S3_BUCKET']
		
		# Generates mocked file key name
		key: str = 'testing.csv'
		
		# Generates mocked object content for assertion
		content: bytes = b'test content'
		content_str = content.decode('utf-8')
		
		# Calls function to be tested
		put_object_in_s3_bucket(
			s3_bucket='S3_BUCKET',
			body=content_str,
			s3_key=key
			)
		
		# Mocks object to be returned for assertion
		s3 = boto3.client('s3', region_name='us-east-1')
		s3_object = s3.get_object(
			Bucket=S3_BUCKET,
			Key=key
			)
		returned_object = s3_object.get('Body').read().decode('utf-8')
		
		# Runs assertions
		self.assertEqual(returned_object, content_str)
	
	def test_date_format_is_correct(self):
		# Tests that the date format is correct, if not then function will fail
		# Defines the expected date format
		expected_date_format = r"year=%Y/month=%m/day=%d"
		
		# Gets the actual date format used in the function
		actual_date_format = str(count_objects_in_s3_prefix.__code__.co_consts[2])
		
		# Uses regular expressions to check if the date format is correct
		self.assertTrue(re.match(expected_date_format, actual_date_format),
		f"Date format mismatch, expected: {expected_date_format}, actual: "
		f" {actual_date_format}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
	