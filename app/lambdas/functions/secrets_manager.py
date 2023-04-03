import json
import boto3
import os
import logging

# Sets logging level
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_secret_from_secrets_manager(region_env: str, secret_name: str) -> str:
    """
    Returns secret from Secrets Manager for input into other lambda_functions.
    :param region_env: Secrets Manager region from Lambda function environment variables
    :param secret_name: Name of the secret to be retrieved
    :return: Secret as a string
    """
    # Connects to boto3 Secrets Manager client
    secrets_client = boto3.client("secretsmanager", region_name=os.environ[region_env])

    # Gets secret from Secrets Manager
    get_secret_value_response = secrets_client.get_secret_value(SecretId=secret_name)
    secret = json.loads(get_secret_value_response["SecretString"])
    secret = list(secret.values())[0]

    logger.info("Successfully retrieved secret: %s", secret_name)
    return secret
