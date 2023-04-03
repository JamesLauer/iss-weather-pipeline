import time

from functions.s3 import (
    get_sql_query_string_from_s3_sql_object
    )
from functions.athena import (
    execute_athena_query,
    return_results_athena_query
    )
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Creates the final table if it doesn't exist and inserts new data into final table
    :param event: Not used
    :param context: Not used
    :return: None
    """
    create_final_table_if_not_exists()
    insert_update_final_table()


def create_final_table_if_not_exists():
    """
    Creates the final table from joining the silver passes and weather tables
    """
    # Gets query parameters
    final_table_name = os.environ["FINAL_TABLE_NAME"]
    s3_bucket_name = os.environ["S3_BUCKET"]

    # Gets query string from SQL file in S3
    query_string = get_sql_query_string_from_s3_sql_object(
        sql_filename="create_final_table.sql",
        prefix="SQL_LOCATION_PREFIX",
        s3_bucket="S3_BUCKET",
        )

    # Executes Athena query
    query_response = execute_athena_query(
        region_env="MY_AWS_REGION",
        database_env="GLUE_DB_NAME",
        catalog_env="DATA_CATALOG_NAME",
        s3_bucket_env="S3_BUCKET",
        query_results_env="QUERY_RESULT_LOCATION",
        query_str=query_string.format(
            final_table_name,
            s3_bucket_name,
            final_table_name
            ),
        )

    # Gets query results
    return_results_athena_query(
        query_id=query_response["QueryExecutionId"],
        max_results=100
        )


def insert_update_final_table():
    """
    Inserts data from silver passes and weather tables into final table
    """
    # Gets query parameters
    final_table_name = os.environ["FINAL_TABLE_NAME"]
    passes_raw_table_name = os.environ["PASSES_RAW_TABLE_NAME"]
    weather_raw_table_name = os.environ["WEATHER_RAW_TABLE_NAME"]

    # Gets query string from SQL file in S3
    query_string = get_sql_query_string_from_s3_sql_object(
        sql_filename="insert_update_final_table.sql",
        prefix="SQL_LOCATION_PREFIX",
        s3_bucket="S3_BUCKET",
        )

    # Execute Athena query
    query_response = execute_athena_query(
        region_env="MY_AWS_REGION",
        database_env="GLUE_DB_NAME",
        catalog_env="DATA_CATALOG_NAME",
        s3_bucket_env="S3_BUCKET",
        query_results_env="QUERY_RESULT_LOCATION",
        query_str=query_string.format(
            final_table_name,
            passes_raw_table_name,
            weather_raw_table_name
            ),
        )
    
    # Gets query results
    return_results_athena_query(
        query_id=query_response["QueryExecutionId"],
        max_results=100
        )
