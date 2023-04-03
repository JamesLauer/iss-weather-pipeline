import json
import unittest
from app.lambdas.lambda_functions.sqs_to_passes_api import (
	get_passes_api_parameters_from_config,
	transform_passes_from_api_response
	)

# Gets test mock data from test data files
with open('tests/unit/test_data/test_sqs_to_passes_api_mock_data.json', 'r') as f:
	mock_data = json.load(f)
	mocked_sqs_location_data = mock_data['mocked_sqs_location_data']
	passes_api_parameters = mock_data['passes_api_parameters']
	expected_transformed_passes_from_api_with_passes = mock_data['expected_transformed_passes_from_api_with_passes']
	expected_transformed_passes_from_api_without_passes = mock_data['expected_transformed_passes_from_api_without_passes']
	expected_passes_api_output_with_passes = mock_data['expected_passes_api_output_with_passes']
	expected_passes_api_output_without_passes = mock_data['expected_passes_api_output_without_passes']


class TestGetPassesApiParametersFromConfig(unittest.TestCase):
	# Tests the get_passes_api_parameters_from_config function

	def test_result_equals_mocked_result(self):
		# Tests that the tested function result equals the mocked result
		# Calls function to be tested
		test_func = get_passes_api_parameters_from_config()

		# Runs assertions
		self.assertEqual(test_func, passes_api_parameters)
	
	
class TestTransformPassesFromApiResponse(unittest.TestCase):
	# Tests the transform_passes_from_api_response function
	
	def test_result_equals_mocked_result(self):
		# Tests that the tested function result equals the mocked result
		# Calls function to be tested
		test_func_response_dict, test_func_response_stringio = transform_passes_from_api_response(
				city_data_input_dict=mocked_sqs_location_data,
				passes_response_json=expected_passes_api_output_with_passes
				)

		# Runs assertions
		self.assertEqual(test_func_response_dict, expected_transformed_passes_from_api_with_passes)
	
	
class TestTransformPassesFromApiResponseWithoutPasses(unittest.TestCase):
	# Tests the transform_passes_from_api_response function
	
	def test_result_equals_mocked_result(self):
		# Tests that the tested function result equals the mocked result
		# Calls function to be tested
		test_func_response_dict, test_func_response_stringio = transform_passes_from_api_response(
			city_data_input_dict=mocked_sqs_location_data,
			passes_response_json=expected_passes_api_output_without_passes
			)

		# Runs assertions
		self.assertEqual(test_func_response_dict, expected_transformed_passes_from_api_without_passes)


if __name__ == '__main__':
	unittest.main(verbosity=2)
