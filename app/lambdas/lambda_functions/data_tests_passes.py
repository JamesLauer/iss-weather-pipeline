from data_test_functions.data_tests import (
	data_test_cities_input_and_output,
	data_test_no_duplicates,
	data_test_null_values,
	)
import logging
import time

# Sets logging level
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
	"""
	Runs a set of data quality test functions on the passes raw table
	:param event: Not used
	:param context: Not used
	:return: None, but function calls return PASS or FAIL logged result for each test in
	CloudWatch
	"""
	table_name = 'PASSES_RAW_TABLE_NAME'
	
	# Checks that the number of cities input and then output from the N2YO API
	# match in the raw table
	data_test_cities_input_and_output(
		table_name_env=table_name,
		sql_file='passes_data_test_cities_input_and_output.sql'
		)
	
	# Checks that there are no duplicates in the raw table
	data_test_no_duplicates(
		table_name_env=table_name,
		sql_file='passes_data_test_no_duplicates.sql'
		)
	
	# Checks that there are no unexpected null values in the raw table
	data_test_null_values(
		table_name_env=table_name,
		sql_file='passes_data_test_null_values.sql'
		)
