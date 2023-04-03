import unittest
from unittest import mock
from moto import (mock_athena)
from app.lambdas.functions.athena import (
	execute_athena_query
	)

# Sets default AWS region
AWS_DEFAULT_REGION = "ap-southeast-2"

# Patches Lambda environment variables into the tess class
@mock.patch.dict(
	"os.environ",
	{
		"AWS_DEFAULT_REGION": f"{AWS_DEFAULT_REGION}",
		"CATALOG": "testing_catalog",
		"GLUE_DB": "testing_db",
		"QUERY_RESULTS": "testing_query",
		"S3_BUCKET": "testing",
		},
	)
class TestExecuteAthenaQuery(unittest.TestCase):
	# Tests the execute_athena_query function
	mock_athena = mock_athena()
	
	def setUp(self):
		# Sets up the test class' test requirements before tests run
		self.mock_athena.start()
	
	def tearDown(self):
		# Tears down the class test requirements after tests run
		self.mock_athena.stop()
	
	def test_result_equals_mocked_result(self):
		# Tests that the tested function result equals the mocked result
		# Create mock QueryExecutionID
		mock_query_execution_response = {
			"QueryExecutionId": "561cc857-8cf6-4911-ac98-b75d314b8d28",
			"ResponseMetadata": {
				"HTTPStatusCode": 200,
				"HTTPHeaders": {"server": "amazon.com"},
				"RetryAttempts": 0,
				},
			}
		
		# Mocks sql query string for assertion
		query_string = "SELECT * FROM db"
		
		# Calls function to be tested
		test_func = execute_athena_query(
			catalog_env="CATALOG",
			database_env="GLUE_DB",
			query_results_env="QUERY_RESULTS",
			query_str=query_string,
			region_env="AWS_DEFAULT_REGION",
			s3_bucket_env="S3_BUCKET",
			)
		
		# Runs assertions
		self.assertEqual(len(test_func), len(mock_query_execution_response))
		self.assertEqual(type(test_func), type(mock_query_execution_response))


if __name__ == '__main__':
	unittest.main()
	