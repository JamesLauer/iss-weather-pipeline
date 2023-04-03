from functions.s3 import get_list_from_s3_csv_object
from functions.sqs import send_city_list_to_sqs_queue
import logging

# Sets logging level
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Gets city name, lat, lon and other data from S3 object then sends each location to
    SQS queue for iss_weather_queue
    :param event: Not used
    :param context: Not used
    """
    city_data_list = get_list_from_s3_csv_object(
        input_data="LAMBDA_INPUT_DATA",
        prefix="INPUT_DATA_PREFIX",
        s3_bucket="S3_BUCKET",
        )

    send_city_list_to_sqs_queue(
        region_env="MY_AWS_REGION",
        data=city_data_list,
        queue_url_env="SQS_QUEUE_URL"
        )
