from datetime import date
import boto3
import os
import csv
import logging

# Sets logging level
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_list_from_s3_csv_object(
	input_data: str,
	prefix: str,
	s3_bucket: str,
	log_index: int = 0
	) -> list:
	"""
	Gets data from S3 object and converts to list.
	:param input_data: Input data filename from Lambda function environment variables
	:param prefix: Prefix name from Lambda function environment variables
	:param s3_bucket: S3 bucket name from Lambda function environment variables
	:param log_index: Used to specify a row index when logging contents of list
	:return: List of input data file contents
	"""
	# Gets Lambda environment variables
	# Checks that input_data file is a .csv file
	input_data_env = os.environ[input_data]
	if input_data_env.endswith('.csv'):
		pass
	else:
		logger.error('Invalid file extension for: %s, expected .csv', input_data_env)
		raise Exception
	s3_bucket_env = os.environ[s3_bucket]
	prefix_env = os.environ[prefix]
	
	# Connects to boto S3 client
	s3_client = boto3.client('s3')
	
	# Gets content of the target S3 object as a list
	content_object = s3_client.get_object(
		Bucket=s3_bucket_env,
		Key=f'{prefix_env}/{input_data_env}'
		)
	file_content = content_object.get('Body').read().decode('utf-8-sig')
	file_content = list(csv.reader(file_content.splitlines()))
	
	logger.info(
		'Successfully sent rows to SQS queue. Number of rows = %s', len(file_content) - 1
		)
	logger.info('First row of S3 object data: %s', file_content[log_index])
	return file_content


def get_sql_query_string_from_s3_sql_object(
	sql_filename: str,
	prefix: str,
	s3_bucket: str
	) -> str:
	"""
	Gets SQL queries from S3 and converts to string
	:param sql_filename: Target SQL filename
	:param prefix: Prefix name from Lambda function environment variables
	:param s3_bucket: S3 bucket name from Lambda function environment variables
	:return: SQL query as a string for Athena querying
	"""
	# Gets Lambda environment variables
	s3_bucket_env = os.environ[s3_bucket]
	prefix_env = os.environ[prefix]
	
	# Connects to boto3 S3 client
	s3_client = boto3.client("s3")
	
	# Checks that the sql_filename is a .sql file
	sql_file = sql_filename
	if sql_file.endswith('.sql'):  # Checks that input_data file is a csv file
		pass
	else:
		logger.error('Invalid file extension for: %s, expected .csv', sql_file)
		raise Exception
	
	# Gets content of the target S3 object as a string
	content_object = s3_client.get_object(
		Bucket=s3_bucket_env, Key=f"{prefix_env}/{sql_file}"
		)
	file_content = content_object.get("Body").read().decode("utf-8")
	
	logger.info("Successfully retrieved sql script: %s", sql_filename)
	return file_content


def put_object_in_s3_bucket(
	s3_bucket: str,
	body: str,
	s3_key: str
	) -> dict:
	"""
	Puts object into S3 bucket with a specified key.
	:param s3_bucket: S3 bucket name from Lambda function environment variables
	:param body: String contents to put in S3 bucket
	:param s3_key: Desired object filename
	:return:
	"""
	# Gets Lambda environment variables
	s3_bucket_name = os.environ[s3_bucket]
	
	# Connects to boto3 S3 client
	s3_client = boto3.client("s3")
	
	# Puts object in S3 bucket
	response = s3_client.put_object(
		Body=body,
		Bucket=s3_bucket_name,
		Key=s3_key
		)
	
	logger.info(
		"Successfully put object: %s, into S3 bucket: %s", s3_key, s3_bucket_name
		)
	return response


def count_objects_in_s3_prefix(
	s3_bucket_env: str,
	base_prefix_env: str
	) -> int:
	"""
	Counts number of saved objects in prefix with year=, month= and day= prefixes
	:param s3_bucket_env: S3 bucket name from Lambda function environment variables
	:param base_prefix_env: S3 prefix that comes after the S3 bucket e.g.
	s3_bucket/base_prefix/files
	:return: Number of objects in base prefix
	"""
	# Gets Lambda environment variables
	s3_bucket_name = os.environ[s3_bucket_env]
	base_prefix = os.environ[base_prefix_env]
	
	# Connects to boto3 S3 client
	client = boto3.client("s3")
	
	# Specifies S3 prefix format and Athena date partition format
	date_format = "year=%Y/month=%m/day=%d"
	
	# Gets current UTC date
	utc_date = date.today()
	utc_date = str(date.strftime(utc_date, date_format))
	
	# Returns number of objects in S3 prefix. If there are no objects then the KeyError
	# is handled and the count is set to 0.
	count = 0
	paginator = client.get_paginator("list_objects")
	for result in paginator.paginate(
		Bucket=s3_bucket_name,
		Prefix=f"{base_prefix}/{utc_date}/", Delimiter="/"):
		try:
			count += len(result["Contents"])
		except KeyError:
			count = 0
	
	logger.info("Number of objects in %s: %s", os.environ[base_prefix_env], count)
	return count

