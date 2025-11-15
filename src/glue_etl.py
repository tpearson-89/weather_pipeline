import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import col, from_unixtime, coalesce, lit

# Glue job arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

# Initialise Spark and Glue contexts
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Log the job start
print(f"Starting Glue Job: {args['JOB_NAME']}")

# Input / Output paths
raw_bucket = "s3://weather-pipeline-tp-raw/raw/"
clean_bucket = "s3://weather-pipeline-tp-clean/clean/"

# Read JSON files from raw S3 bucket
raw_dyf = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={"paths": [raw_bucket]},
    format="json"
)

# Convert to Spark DataFrame for transformations
raw_df = raw_dyf.toDF()

# Rename 'name' column to 'city' to avoid UNRESOLVED_COLUMN error
if 'name' in raw_df.columns:
    raw_df = raw_df.withColumnRenamed("name", "city")
else:
    raw_df = raw_df.withColumn("city", lit("unknown"))

# Flatten JSON and select relevant fields
transformed_df = raw_df.select(
    col("city"),
    coalesce(col("sys").getField("country"), lit("unknown")).alias("country"),
    from_unixtime(coalesce(col("dt"), lit(0))).alias("datetime_utc"),
    coalesce(col("weather").getItem(0).getField("main"), lit("unknown")).alias("weather_main"),
    coalesce(col("weather").getItem(0).getField("description"), lit("unknown")).alias("weather_description"),
    coalesce(col("main").getField("temp"), lit(None)).alias("temperature_celsius"),
    coalesce(col("main").getField("feels_like"), lit(None)).alias("feels_like_celsius"),
    coalesce(col("main").getField("temp_min"), lit(None)).alias("temp_min_celsius"),
    coalesce(col("main").getField("temp_max"), lit(None)).alias("temp_max_celsius"),
    coalesce(col("main").getField("pressure"), lit(None)).alias("pressure_hpa"),
    coalesce(col("main").getField("humidity"), lit(None)).alias("humidity"),
    coalesce(col("wind").getField("speed"), lit(None)).alias("wind_speed"),
    coalesce(col("wind").getField("deg"), lit(None)).alias("wind_deg"),
    coalesce(col("clouds").getField("all"), lit(None)).alias("cloudiness_percent"),
)

# Convert to DynamicFrame for Glue
clean_dyf = DynamicFrame.fromDF(transformed_df, glueContext, "clean_dyf")

# Cleaned Parquet to clean bucket
glueContext.write_dynamic_frame.from_options(
    frame=clean_dyf,
    connection_type="s3",
    connection_options={"path": clean_bucket},
    format="parquet"
)

print("Glue job completed successfully!")