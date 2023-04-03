from functions.s3 import count_objects_in_s3_prefix


def lambda_handler(event, context) -> dict:
    """
    Returns number of objects in specified S3 bucket and prefix. This Lambda function
    is used to check if the pipeline has already been run for that specific day.
    :param event: Not used
    :param context: Not used
    :return: Number of objects in specified S3 bucket and prefix
    """
    number_of_objects = count_objects_in_s3_prefix(
        s3_bucket_env="S3_BUCKET",
        base_prefix_env="BASE_PREFIX"
        )

    return {"objects": number_of_objects}
