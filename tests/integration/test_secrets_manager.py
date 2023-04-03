import json
import unittest
from unittest import mock
from moto import (mock_secretsmanager)
import boto3
from app.lambdas.functions.secrets_manager import (
	get_secret_from_secrets_manager
	)

# Sets default region
AWS_DEFAULT_REGION = 'ap-southeast-2'

# Patches Lambda environment variables into the tess class
@mock.patch.dict(
	'os.environ', {
		'AWS_DEFAULT_REGION': f'{AWS_DEFAULT_REGION}'
		}
	)
class TestGetSecretFromSecretsManager(unittest.TestCase):
	# Tests the get_secret_from_secrets_manager function
	mock_secretsmanager = mock_secretsmanager()
	
	def setUp(self):
		# Sets up the test class' test requirements before tests run
		self.mock_secretsmanager.start()
	
	def tearDown(self):
		# Tests that the tested function result equals the mocked result
		self.mock_secretsmanager.stop()
	
	def test_result_equals_mocked_result(self):
		# Tests that the tested function result equals the mocked result
		# Connects to Secrets Manager boto
		secrets_client = boto3.client('secretsmanager', region_name=AWS_DEFAULT_REGION)
		
		# Mocks SecretId and value to be used as secret value in dictionary
		secret_id = 'TEST_SECRET'
		secret_value = 'actual_secret'
		secret_string = json.dumps({'test_key': f'{secret_value}'})
		
		# Mocks creation of secret so that it can be retrieved with function under test
		secrets_client.create_secret(
			Name=secret_id,
			SecretString=secret_string
			)
		
		# Calls function to be tested
		test_func = get_secret_from_secrets_manager(
			region_env='AWS_DEFAULT_REGION',
			secret_name=secret_id
			)
		
		# Runs assertions
		self.assertEqual(test_func, secret_value)


if __name__ == '__main__':
	unittest.main(verbosity=2)
