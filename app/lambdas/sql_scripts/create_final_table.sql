CREATE EXTERNAL TABLE IF NOT EXISTS {} (
  city string,
  lat double,
  lon double,
  region string,
  country string,
  timezone string,
  start_time string,
  start_date string,
  startaz double,
  startazcompass string,
  startel double,
  maxaz double,
  maxazcompass string,
  maxel double,
  max_time string,
  max_date string,
  endaz double,
  endazcompass string,
  end_time string,
  end_date string,
  mag double,
  duration int,
  temp double,
  feels_like double,
  pressure int,
  humidity int,
  dew_point double,
  clouds int,
  visibility int,
  wind_speed double,
  wind_deg int,
  wind_gust double,
  pop double,
  main string,
  description string,
  rain struct<1h:double>,
  snow struct<1h:double>
    )
PARTITIONED BY (
  year string,
  month string,
  day string
    )
ROW FORMAT SERDE
  'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
STORED AS INPUTFORMAT
  'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat'
OUTPUTFORMAT
  'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat'
LOCATION
  's3://{}/query-results/'
