import json
import time
from typing import Optional
import boto3
import os
import logging

# Sets logging level
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def execute_athena_query(
	catalog_env: str,
	database_env: str,
	query_results_env: str,
	query_str: str,
	region_env: str,
	s3_bucket_env: str,
	parameters: Optional[list[str]] = None
	) -> dict:
	"""
	Executes Athena SQL query within specified context (e.g. Glue catalog and database).
	:param catalog_env: Glue data catalog name from Lambda function environment variables
	:param database_env: Glue database name from Lambda function environment variables
	:param query_results_env: Query result location from Lambda function environment
	variables
	:param query_str: SQL query as a string
	:param region_env: Athena region from Lambda function environment variables
	:param s3_bucket_env:
	:param parameters:
	:return:
	"""
	# Gets Lambda environment variables
	s3_bucket = os.environ[s3_bucket_env]
	query_result_location = os.environ[query_results_env]
	
	# Connects to boto3 Athena client
	athena_client = boto3.client("athena", region_name=os.environ[region_env])
	
	# Gets kwargs for use in athena_client.start_query_execution
	kwargs = {
		"QueryString": query_str,
		"QueryExecutionContext": {
			"Database": os.environ[database_env],
			"Catalog": os.environ[catalog_env],
			},
		"ResultConfiguration": {
			"OutputLocation": f"s3://{s3_bucket}/{query_result_location}/"
			},
		}
	
	# Execution parameters added to start_query_execution if passed to function
	if parameters:
		kwargs["ExecutionParameters"] = {"Parameters": parameters}
	
	# Executes query
	response = athena_client.start_query_execution(**kwargs)
	
	# Waits for the query to complete
	status = "RUNNING"
	while status in ["RUNNING", "QUEUED"]:
		get_query_execution_response = athena_client.get_query_execution(
			QueryExecutionId=response["QueryExecutionId"]
			)
		status = get_query_execution_response["QueryExecution"]["Status"]["State"]
		logger.info("Query execution status: %s", status)
		time.sleep(1)
		
	logger.info("Query execution response: %s", json.dumps(response))
	return response


def return_results_athena_query(
	query_id: str,
	max_results: int
	) -> dict:
	"""
	Returns results of Athena SQL query.
	:param query_id: Query execution ID
	:param max_results: Maximum number of results to return from query
	:return: response: Response from Boto3
	"""
	# Connects to boto3 Athena client
	athena_client = boto3.client("athena")
	
	# Gets query result
	response = athena_client.get_query_results(
		QueryExecutionId=query_id,
		MaxResults=max_results
		)
	
	logger.info("Query result metadata: %s", json.dumps(response))
	return response
