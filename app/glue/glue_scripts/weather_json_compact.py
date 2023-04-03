from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from awsglue.transforms import *
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import *
from awsglue.dynamicframe import DynamicFrame
import datetime, sys

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'S3_BUCKET_NAME', 'WEATHER_RAW_PREFIX'])

date_prefix = datetime.datetime.now().strftime("year=%Y/month=%m/day=%d")
input_path = "s3://{}/{}/{}/".format(
    args['S3_BUCKET_NAME'],
    args['WEATHER_RAW_PREFIX'],
    date_prefix
    )
output_path = "s3://{}/{}_compacted/{}/".format(
    args['S3_BUCKET_NAME'],
    args['WEATHER_RAW_PREFIX'],
    date_prefix
    )


sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Define the schema
schema = StructType([
        StructField('city', StringType(), True),
        StructField('lat', DoubleType(), True),
        StructField('lon', DoubleType(), True),
        StructField('region', StringType(), True),
        StructField('country', StringType(), True),
        StructField('timezone', StringType(), True),
        StructField('timezone_offset', IntegerType(), True),
        StructField('dt', IntegerType(), True),
        StructField('temp', DoubleType(), True),
        StructField('feels_like', DoubleType(), True),
        StructField('pressure', IntegerType(), True),
        StructField('humidity', IntegerType(), True),
        StructField('dew_point', DoubleType(), True),
        StructField('uvi', DoubleType(), True),
        StructField('clouds', IntegerType(), True),
        StructField('visibility', IntegerType(), True),
        StructField('wind_speed', DoubleType(), True),
        StructField('wind_deg', IntegerType(), True),
        StructField('wind_gust', DoubleType(), True),
        StructField('pop', DoubleType(), True),
        StructField('id', IntegerType(), True),
        StructField('main', StringType(), True),
        StructField('description', StringType(), True),
        StructField('icon', StringType(), True),
        StructField('rain', StructType([StructField('1h', DoubleType(), True)])),
        StructField('snow', StructType([StructField('1h', DoubleType(), True)]))
        ])

# Reads the json file with the specified schema
df = spark.read.json(input_path, schema=schema)

df = df.coalesce(1)

glueContext.write_dynamic_frame.from_options(
    frame=DynamicFrame.fromDF(df, glueContext, "df"),
    connection_type="s3",
    connection_options={"path": output_path},
    format="parquet"
    )

