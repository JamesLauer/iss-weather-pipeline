import json
import unittest
from app.lambdas.lambda_functions.sqs_to_weather_api import (
	get_weather_api_parameters_from_config,
	transform_weather_from_api_response,
	)

# Gets test mock data from test data files
with open('tests/unit/test_data/test_sqs_to_weather_api_mock_data.json', 'r') as f:
	mock_data = json.load(f)
	mocked_sqs_location_data = mock_data['mocked_sqs_location_data']
	weather_api_parameters = mock_data['openweather_api_parameters']
	expected_transformed_weather_from_api = mock_data['expected_transformed_weather_from_api']
	expected_weather_api_output = mock_data['expected_weather_api_output']


class TestGetweatherApiParametersFromConfig(unittest.TestCase):
	# Tests the get_weather_api_parameters_from_config function
	
	def test_result_equals_mocked_result(self):
		# Tests that the tested function result equals the mocked result
		# Calls function to be tested
		test_func = get_weather_api_parameters_from_config()
		
		# Runs assertions
		self.assertEqual(test_func, weather_api_parameters)


class TestTransformWeatherFromApiResponse(unittest.TestCase):
	# Tests the transform_weather_from_api_response function
	
	def test_result_equals_mocked_result(self):
		# Tests that the tested function result equals the mocked result
		# Calls function to be tested
		test_func_response_dict, test_func_response_stringio = \
			transform_weather_from_api_response(
				city_data_input_dict=mocked_sqs_location_data,
				weather_response_json=expected_weather_api_output
				)
		
		# Runs assertions
		self.assertEqual(test_func_response_dict, expected_transformed_weather_from_api)


if __name__ == '__main__':
	unittest.main(verbosity=2)
