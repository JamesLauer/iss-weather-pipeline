from data_test_functions.data_tests import (
	data_test_no_duplicates,
	)
import logging

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
	table_name = 'FINAL_TABLE_NAME'
	
	# Checks that there are no duplicates in the final table
	data_test_no_duplicates(
		table_name_env=table_name,
		sql_file='final_data_test_no_duplicates.sql'
		)
