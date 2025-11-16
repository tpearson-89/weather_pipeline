import boto3
import time
import os

# Environment variables
AWS_REGION = os.environ.get('AWS_DEFAULT_REGION', 'eu-west-1')
ATHENA_DB = os.environ.get('ATHENA_DB', 'weather_db')
ATHENA_OUTPUT = os.environ.get('ATHENA_OUTPUT', 's3://weather-pipeline-tp-athena/')

# Athena query
QUERY = f"""
SELECT city, country, datetime_utc, temperature_celsius, weather_main
FROM {ATHENA_DB}.weather_data
ORDER BY datetime_utc DESC
LIMIT 30;
"""

# Initialize Athena client
session = boto3.Session(region_name=AWS_REGION)
athena_client = session.client('athena')

# Start query execution
response = athena_client.start_query_execution(
    QueryString=QUERY,
    QueryExecutionContext={'Database': ATHENA_DB},
    ResultConfiguration={'OutputLocation': ATHENA_OUTPUT}
)

query_execution_id = response['QueryExecutionId']
print(f"Athena Query started with ID: {query_execution_id}")

# Poll for query completion
status = 'RUNNING'
while status in ['RUNNING', 'QUEUED']:
    time.sleep(5)
    result = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
    status = result['QueryExecution']['Status']['State']
    print(f"Current Athena query status: {status}")

if status == 'SUCCEEDED':
    print("Athena query completed successfully!")
    print(f"Results available at: {ATHENA_OUTPUT}{query_execution_id}.csv")
else:
    raise Exception(f"Athena query FAILED with status: {status}")
