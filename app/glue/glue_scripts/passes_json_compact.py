from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from awsglue.transforms import *
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import *
from awsglue.dynamicframe import DynamicFrame
import datetime, sys

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'S3_BUCKET_NAME', 'PASSES_RAW_PREFIX'])

date_prefix = datetime.datetime.now().strftime("year=%Y/month=%m/day=%d")
input_path = "s3://{}/{}/{}/".format(
    args['S3_BUCKET_NAME'],
    args['PASSES_RAW_PREFIX'],
    date_prefix
    )
output_path = "s3://{}/{}_compacted/{}/".format(
    args['S3_BUCKET_NAME'],
    args['PASSES_RAW_PREFIX'],
    date_prefix
    )

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Define the schema
schema = StructType([
        StructField('city', StringType(), True),
        StructField('lat', StringType(), True),
        StructField('lon', StringType(), True),
        StructField('region', StringType(), True),
        StructField('country', StringType(), True),
        StructField('satid', IntegerType(), True),
        StructField('satname', StringType(), True),
        StructField('transactionscount', IntegerType(), True),
        StructField('passescount', IntegerType(), True),
        StructField('startAz', DoubleType(), True),
        StructField('startAzCompass', StringType(), True),
        StructField('startEl', DoubleType(), True),
        StructField('startUTC', IntegerType(), True),
        StructField('maxAz', DoubleType(), True),
        StructField('maxAzCompass', StringType(), True),
        StructField('maxEl', DoubleType(), True),
        StructField('maxUTC', IntegerType(), True),
        StructField('endAz', DoubleType(), True),
        StructField('endAzCompass', StringType(), True),
        StructField('endEl', DoubleType(), True),
        StructField('endUTC', IntegerType(), True),
        StructField('mag', DoubleType(), True),
        StructField('duration', IntegerType(), True),
        StructField('startVisibility', IntegerType(), True)
        ])


# Reads the json file with the specified schema
df = spark.read.json(input_path, schema=schema)

# Converts the lat and lon fields to double type to match OpenWeather lat and lon format
df = df.withColumn("lat", df["lat"].cast(DoubleType()))
df = df.withColumn("lon", df["lon"].cast(DoubleType()))

df = df.coalesce(1)

glueContext.write_dynamic_frame.from_options(
    frame=DynamicFrame.fromDF(df, glueContext, "df"),
    connection_type="s3",
    connection_options={"path": output_path},
    format="parquet",
    )

