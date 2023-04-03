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

# Sets logging level
logger = logging.getLogger()
logger.setLevel(logging.INFO)
StringIO = TypeVar("StringIO")


def lambda_handler(event, context):
    """
    Takes city location data from SQS queue, sends to OpenWeather api to get ISS weather over
    the city then uploads data to S3
    :param event: SQS message with payload consisting of city name, lat, lon, etc.
    from cities_to_sqs.py Lambda function
    :param context: Not used
    """
    # Get OpenWeather api key from Secrets Manager
    weather_api_key_secret = get_secret_from_secrets_manager(
        region_env="MY_AWS_REGION", secret_name="openweather_api_key"
    )

    # Gets OpenWeather api parameters for input into the call_passes_api function
    openweather_parameters = get_weather_api_parameters_from_config()

    for msg in event["Records"]:
        logger.info("Event metadata: %s", json.dumps(event))

        # Parses SQS event input to Lambda to dictionary
        city_data_input_dict = transform_city_sqs_message_response_to_dictionary(
            record=msg
            )

        # Calls OpenWeather api
        weather_response_json = call_weather_api(
            city_input_data=city_data_input_dict,
            openweather_parameters=openweather_parameters,
            api_key=weather_api_key_secret,
            )

        # Transforms openweather api response to raw json format for uploading to S3
        weather_response_dict, weather_response_stringio = \
            transform_weather_from_api_response(
                city_data_input_dict=city_data_input_dict,
                weather_response_json=weather_response_json,
                )

        # Deletes message from SQS queue
        delete_message_from_sqs_queue(
            region_env="MY_AWS_REGION",
            queue_url="SQS_QUEUE_URL",
            sqs_message=msg
            )

        # Generates a unique key for the raw json file
        s3_object_key = create_s3_object_name_for_api_data_export(
            s3_bucket_prefix=os.environ["WEATHER_RAW_PREFIX"],
            city_name=city_data_input_dict["city"],
            region=city_data_input_dict["region"],
            country_code=city_data_input_dict["country_code"],
            api_call_name="iss-weather",
            )

        # Puts the raw json file object in S3
        put_object_in_s3_bucket(
            s3_bucket="S3_BUCKET",
            body=weather_response_stringio,
            s3_key=s3_object_key
            )

        logger.info(
            "Example of OpenWeather API response: %s",
            weather_response_json["hourly"][0],
            )


def get_weather_api_parameters_from_config():
    """
    Gets OpenWeather api input parameters from lambdas_config.ini file for ISS weather
    over cities
    :return: openweather parameters dictionary
    """
    config = configparser.ConfigParser()
    config.read(rf"{current_dir}/lambdas_config.ini")

    # Adds openweather request input variables
    openweather_parameters = {
        "exclude": f"{config['openweather_config']['exclude']}",
        "units": f"{config['openweather_config']['units']}",
        }
    return openweather_parameters


def call_weather_api(
    city_input_data: dict, openweather_parameters: dict, api_key: str
) -> dict:
    """
    Calls OpenWeather api to get ISS weather over input (i.e. lat, lon) location
    :param city_input_data: contains lat, lon and other data
    :param openweather_parameters:
    :param api_key: string from AWS Secrets Manager
    :return: OpenWeather api response based on parameters
    """
    weather_api_response = requests.get(
        f'https://api.openweathermap.org/data/2.5/onecall?lat={city_input_data["lat"]}&'
        f'lon={city_input_data["lon"]}&exclude={openweather_parameters["exclude"]}&'
        f'units={openweather_parameters["units"]}&appid={api_key}'
    )
    weather_response_json = json.loads(weather_api_response.content)
    return weather_response_json


def transform_weather_from_api_response(
    city_data_input_dict: dict, weather_response_json: dict
) -> [dict, Generic[StringIO]]:
    """
    Transforms OpenWeather api response into desired raw data json output
    :param city_data_input_dict:
    :param weather_response_json:
    :return: TODO
    """
    weather_response_io = io.StringIO()

    # Add city name then concatenate 'hourly' and 'weather' arrays from response
    for rows in weather_response_json["hourly"]:
        conc_weather_data = {
                            "city": city_data_input_dict["city"],
                            "lat": city_data_input_dict["lat"],
                            "lon": city_data_input_dict["lon"],
                            "region": city_data_input_dict["region"],
                            "country": city_data_input_dict["country"],
                            } | weather_response_json | rows | rows["weather"][0]

        # Delete 'weather' array as has already been concatenated
        del conc_weather_data["hourly"]
        del conc_weather_data["weather"]

        # Print lines to file (i.e. without commas and brackets) so that Athena can
        # parse the json file
        print(conc_weather_data, file=weather_response_io)

    return conc_weather_data, weather_response_io.getvalue()
