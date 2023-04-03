import sys
import os
import inspect

# Allows lambda_functions module to be found in GitHub Actions
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
functions_dir = current_dir.replace('lambda_functions', '')
sys.path.append(functions_dir)


import configparser
import json
import io
import requests
import logging
from typing import TypeVar, Generic
from functions.sqs import (
	delete_message_from_sqs_queue,
	transform_city_sqs_message_response_to_dictionary,
	)
from functions.s3 import (
	put_object_in_s3_bucket
	)
from functions.other import (
	create_s3_object_name_for_api_data_export,
	)
from functions.secrets_manager import (
	get_secret_from_secrets_manager
	)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
StringIO = TypeVar('StringIO')


def lambda_handler(event, context):
	"""
	Takes city location data from SQS queue, sends to N2YO api to get ISS passes over
	the city then uploads data to S3
	:param event: SQS message with payload consisting of city name, lat, lon, etc.
	from cities_to_sqs.py Lambda function
	:param context: Not used
	"""
	# Get N2YO api key from Secrets Manager
	passes_api_key_secret = get_secret_from_secrets_manager(
		region_env='MY_AWS_REGION',
		secret_name='n2yo_api_key'
		)

	# Gets N2YO api parameters for input into the call_passes_api function
	n2yo_parameters = get_passes_api_parameters_from_config()

	for msg in event['Records']:
		logger.info('Event metadata: %s', json.dumps(event))

		# Parses SQS event input to Lambda to dictionary
		city_data_input_dict = transform_city_sqs_message_response_to_dictionary(
			record=msg
			)

		# Calls N2YO api
		passes_response_json = call_passes_api(
			city_input_data=city_data_input_dict,
			n2yo_parameters=n2yo_parameters,
			api_key=passes_api_key_secret
			)

		# Transforms N2YO api response to raw json format for uploading to S3
		passes_response_dict, passes_response_stringio = \
			transform_passes_from_api_response(
				city_data_input_dict=city_data_input_dict,
				passes_response_json=passes_response_json
				)

		# Deletes message from SQS queue
		delete_message_from_sqs_queue(
			region_env='MY_AWS_REGION',
			queue_url='SQS_QUEUE_URL',
			sqs_message=msg
			)

		# Generates a unique key for the raw json file
		s3_object_key = create_s3_object_name_for_api_data_export(
			s3_bucket_prefix=os.environ['PASSES_RAW_PREFIX'],
			city_name=city_data_input_dict['city'],
			region=city_data_input_dict['region'],
			country_code=city_data_input_dict['country_code'],
			api_call_name='iss-passes'
			)

		# Puts the raw json file object in S3
		put_object_in_s3_bucket(
			s3_bucket='S3_BUCKET',
			body=passes_response_stringio,
			s3_key=s3_object_key
			)

		logger.info('Example of N2YO API response: %s', passes_response_json)


def get_passes_api_parameters_from_config():
	"""
	Gets N2YO api input parameters from lambdas_config.ini file for ISS passes over
	cities
	:return: N2YO parameters dictionary
	"""
	config = configparser.ConfigParser()
	config.read(rf'{current_dir}/lambdas_config.ini')

	# Adds N2YO request input variables
	n2yo_parameters = {
		"nor_id": f"{config['n2yo_config']['nor_id']}",
		"obs_alt": f"{config['n2yo_config']['obs_alt']}",
		"days": f"{config['n2yo_config']['days']}",
		"min_vis": f"{config['n2yo_config']['min_vis']}"
		}
	return n2yo_parameters


def call_passes_api(
	city_input_data: dict,
	n2yo_parameters: dict,
	api_key: str
	) -> dict:
	"""
	Calls N2YO api to get ISS passes over input (i.e. lat, lon) location
	:param city_input_data: contains lat, lon and other data
	:param n2yo_parameters: see lambdas_config.ini
	:param api_key: string from AWS Secrets Manager
	:return: N2YO api response based on parameters
	"""
	passes_api_response = requests.get(
		f'https://api.n2yo.com/rest/v1/satellite/visualpasses/'
		f'{n2yo_parameters["nor_id"]}/'
		f'{city_input_data["lat"]}/{city_input_data["lon"]}/'
		f'{n2yo_parameters["obs_alt"]}/'
		f'{n2yo_parameters["days"]}/{n2yo_parameters["min_vis"]}&apiKey={api_key}'
		)
	passes_response_json = passes_api_response.json()
	return passes_response_json


def transform_passes_from_api_response(
	city_data_input_dict: dict,
	passes_response_json: dict
	) -> [dict, Generic[StringIO]]:
	"""
	Transforms N2YO api response into desired raw data json output
	:param city_data_input_dict: Dictionary of city data to be appended to api
	json response data
	:param passes_response_json: json response data from api
	:return: A dictionary of pass data and a bytes stream
	"""
	passes_response_io = io.StringIO()

	# Try outputs dictionary based on whether there are ISS passes over a location
	# Except outputs dictionary even if there are no ISS passes over location
	try:
		# Add city name then concatenate 'hourly' and 'passes' arrays from response
		for row in passes_response_json['passes']:
			conc_passes_data = {
								   'city': city_data_input_dict['city'],
								   'lat': city_data_input_dict['lat'],
								   'lon': city_data_input_dict['lon'],
								   'region': city_data_input_dict['region'],
								   'country': city_data_input_dict['country']
								   } | passes_response_json['info'] | row

			# Print lines to file (i.e. without commas and brackets) so that Athena
			# can parse the json file
			# TODO check if still required using current method of updating table
			print(conc_passes_data, file=passes_response_io)

		return conc_passes_data, passes_response_io.getvalue()

	except KeyError:
		# For cities without any passes - Add city name (column index 0)
		conc_passes_data = {
						   'city': city_data_input_dict['city'],
						   'lat': city_data_input_dict['lat'],
						   'lon': city_data_input_dict['lon'],
						   'region': city_data_input_dict['region'],
						   'country': city_data_input_dict['country']
						   } | passes_response_json['info']

		# Print lines to file (i.e. without commas and brackets) so that Athena can
		# parse the json file
		print(conc_passes_data, file=passes_response_io)

	return conc_passes_data, passes_response_io.getvalue()
