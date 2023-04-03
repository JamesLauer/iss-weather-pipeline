import json
import boto3
import os
import logging

# Sets logging level
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def send_city_list_to_sqs_queue(
    region_env: str, data: list, queue_url_env: str
) -> dict:
    """
    Iterates through city input data list and sends each city/row to an SQS queue
    :param region_env: SQS queue region from Lambda function environment variables
    :param data: City input data list
    :param queue_url_env: SQS queue url from Lambda function environment variables
    :return: boto3 sqs_client.send_message response
    """
    # Gets Lambda environment variables
    sqs_queue_env = os.environ[queue_url_env]

    # Creates dictionary of column header (key) and column index (value)
    headers = []
    for count, value in enumerate(iterable=data[0]):
        headers.extend([[value, count]])
    headers = dict(headers)

    # Connects to boto3 SQS client
    sqs_client = boto3.client("sqs", region_name=os.environ[region_env])

    # Adds location data to SQS message. Enumerate used to count number of messages for
    # logging.
    for count, row in enumerate(iterable=data[1:], start=1):
        response = sqs_client.send_message(
            QueueUrl=sqs_queue_env,
            MessageBody=json.dumps(
                {
                    "city": row[headers["city"]],
                    "region": row[headers["region"]],
                    "latitude": row[headers["latitude"]],
                    "longitude": row[headers["longitude"]],
                    "country": row[headers["country"]],
                    "country_code": row[headers["country_code"]],
                    }
                ),
            )

    logger.info("Successfully sent message to SQS queue: %s", queue_url_env)
    logger.info("Message sent: %s", json.dumps(response))
    logger.info("Number of messages sent to SQS queue = %s", count)
    return response


def transform_city_sqs_message_response_to_dictionary(
    record: dict,
) -> dict:
    """
    Transforms city data from SQS queue into a dictionary for input into api call.
    :param record: Takes event['Records'] input from SQS invoked lambda function. See
    https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html for more info.
    :return: Dictionary containing city, region, country, lat and lon.
    """
    # Gets SQS messages from queue
    sqs_message_data = json.loads(record["body"])

    # Gets city name, latitude and longitude from SQS message for input into ISS api
    # request
    city = sqs_message_data["city"]
    lat = sqs_message_data["latitude"]
    lon = sqs_message_data["longitude"]

    # Gets other information to add to data
    region = sqs_message_data["region"]
    country = sqs_message_data["country"]
    country_code = sqs_message_data["country_code"]

    # Creates data stream for iss passes api request
    city_data_dict = {
        "city": city,
        "lat": lat,
        "lon": lon,
        "region": region,
        "country": country,
        "country_code": country_code,
        }

    logger.info("Successfully transformed data from SQS message to dictionary")
    return city_data_dict


def delete_message_from_sqs_queue(
    region_env: str,
    queue_url: str,
    sqs_message: dict,
) -> dict:
    """
    Deletes message from SQS queue to ensure no double-ups during concurrent invocation.
    Note: not unit or integration tested!
    :param region_env: SQS queue region from Lambda function environment variables
    :param queue_url: SQS queue url from Lambda function environment variables
    :param sqs_message: boto3 sqs_client.send_message response event['Records]
    :return: sqs_client.delete_message response
    """
    # Gets Lambda environment variables
    sqs_queue_url = os.environ[queue_url]

    # Connects to boto3 SQS client
    sqs_client = boto3.client("sqs", region_name=os.environ[region_env])

    # Deletes message from SQS queue
    response = sqs_client.delete_message(
        QueueUrl=sqs_queue_url, ReceiptHandle=sqs_message["receiptHandle"]
        )

    logger.info("Successfully deleted SQS message")
    return response
