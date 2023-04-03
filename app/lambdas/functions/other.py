from datetime import datetime, date
import logging

# Sets logging level
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_s3_object_name_for_api_data_export(
    s3_bucket_prefix: str,
    city_name: str,
    region: str,
    country_code: str,
    api_call_name: str,
) -> str:
    """
    Creates key name for saving api data into S3 bucket. Note that the s3_object_key (
    excluding filename) will become partitions in Athena.
    :param s3_bucket_prefix: S3 prefix to save file to
    :param city_name: Name of the city
    :param region: Name of the region or state of the city
    :param country_code: 3-letter country code
    :param api_call_name: Name to use in the key/filename e.g. iss_passes or iss_weather
    :return: Object S3 key name
    """
    # Gets current date to use in filename
    date = datetime.now().strftime("%Y_%m_%d")
    year_prefix = "year=" + datetime.now().strftime("%Y")
    month_prefix = "month=" + datetime.now().strftime("%m")
    day_prefix = "day=" + datetime.now().strftime("%d")

    # Generates filename
    filename = "".join(
        [api_call_name, "-", country_code, "-", region, "-", date, "-", city_name,
         "-utc", ".json"]
        )

    # Generates final object key name (including the S3 prefixes)
    s3_object_key = "/".join(
        [s3_bucket_prefix, year_prefix, month_prefix, day_prefix, filename]
        )

    logger.info("Successfully created S3 object name: %s", s3_object_key)
    return s3_object_key
