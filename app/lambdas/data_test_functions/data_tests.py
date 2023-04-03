from functions.s3 import (
	get_sql_query_string_from_s3_sql_object
	)
from functions.athena import (
	execute_athena_query,
	return_results_athena_query,
	)
import os
import logging

# Sets logging level
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def data_test_cities_input_and_output(
	table_name_env: str,
	sql_file: str
	) -> bool:
	"""
	Checks whether all cities were processed from cities_to_sqs.py Lambda function
	:param table_name_env: Athena table name
	:param sql_file: Filename of SQL file to use in query
	:return: PASS or FAIL logged result
	"""
	logger.info("Name of test: %s", data_test_no_duplicates.__name__)
	
	# Gets query parameters from Lambda environment variables
	expected_num_of_cities = os.environ["EXPECTED_OBJECT_NUMBER"]
	
	# Gets query result from "get_query_result_from_sql_script" function
	query_result = get_query_result_from_sql_script(
		table_name_env=table_name_env,
		sql_file=sql_file
		)

	# Gets number of unique cities from query result
	num_unique_cities_found = query_result["ResultSet"]["Rows"][1]["Data"][0][
		"VarCharValue"]

	# Logs results
	logger.info(
		"Number of unique cities input/output: %s/%s",
		expected_num_of_cities,
		num_unique_cities_found,
		)

	# Runs test and logs result
	if num_unique_cities_found == expected_num_of_cities:
		logger.info("Test result PASS: input = output")
		return True
	else:
		logger.error("Test result FAIL: input != output")
		return False


def data_test_no_duplicates(
	table_name_env: str,
	sql_file: str
	) -> bool:
	"""
	Checks that there are no duplicates in the target table
	:param table_name_env: Athena table name
	:param sql_file: Filename of SQL file to use in query
	:return: PASS or FAIL logged result
	"""
	logger.info("Name of test: %s", data_test_no_duplicates.__name__)

	# Gets query result from "get_query_result_from_sql_script" function
	query_result = get_query_result_from_sql_script(
		table_name_env=table_name_env,
		sql_file=sql_file
		)

	# Checks for duplicates
	duplicates = []
	for target in query_result["ResultSet"]["Rows"]:
		duplicates.append(target["Data"])
	if len(query_result["ResultSet"]["Rows"]) > 1:
		logger.error("Test result FAIL: duplicate rows found")
		return False
	else:
		logger.info("Test result PASS: no duplicates")
		return True


def data_test_null_values(
	table_name_env: str,
	sql_file: str
	) -> bool:
	"""
	Checks that there are no unexpected NULL values
	:param table_name_env: Athena table name
	:param sql_file: Filename of SQL file to use in query
	:return: PASS or FAIL logged result
	"""
	logger.info("Name of test: %s", data_test_no_duplicates.__name__)

	# Gets query result from "get_query_result_from_sql_script" function
	query_result = get_query_result_from_sql_script(
		table_name_env=table_name_env,
		sql_file=sql_file
		)

	# Checks for null values
	rows_with_nulls = []
	for target in query_result["ResultSet"]["Rows"]:
		rows_with_nulls.append(target["Data"])
	if len(query_result["ResultSet"]["Rows"]) > 1:
		logger.error("Test result FAIL: unexpected null values found")
		return False
	else:
		logger.info("Test result PASS: no unexpected null values found")
		return True


def get_query_result_from_sql_script(
	table_name_env: str,
	sql_file: str,
	max_result_num: int = 100,
	query_string_prefix_env: str = "SQL_LOCATION_PREFIX",
	s3_bucket_env: str = "S3_BUCKET",
	aws_region_env: str = "MY_AWS_REGION",
	glue_db_env: str = "GLUE_DB_NAME",
	data_catalog_env: str = "DATA_CATALOG_NAME",
	query_result_env: str = "QUERY_RESULT_LOCATION"
	) -> dict:
	"""
	Returns query result dictionary for use in data quality test functions
	:param table_name_env: Athena table name
	:param sql_file: Filename of SQL file to use in query
	:param max_result_num: Maximum number or rows to return
	:param query_string_prefix_env: S3 prefix of SQL query file object
	:param s3_bucket_env: S3 bucket name
	:param aws_region_env: Athena AWS region
	:param glue_db_env: Glue database name
	:param data_catalog_env: Glue data catalog name
	:param query_result_env: Query result location
	:return: Athena query result dictionary
	"""
	# Gets query string from SQL file in S3
	query_string = get_sql_query_string_from_s3_sql_object(
		sql_filename=sql_file,
		prefix=query_string_prefix_env,
		s3_bucket=s3_bucket_env,
		)
	
	# Executes Athena query
	query_response = execute_athena_query(
		region_env=aws_region_env,
		database_env=glue_db_env,
		catalog_env=data_catalog_env,
		s3_bucket_env=s3_bucket_env,
		query_results_env=query_result_env,
		query_str=query_string.format(os.environ[table_name_env]),
		)
	
	# Gets query results
	query_result = return_results_athena_query(
		query_id=query_response["QueryExecutionId"],
		max_results=max_result_num
		)
	return query_result
