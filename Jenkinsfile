pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = 'eu-west-1'
        ATHENA_DB = 'weather_db'
        ATHENA_OUTPUT = 's3://weather-pipeline-tp-athena/' // Athena query results bucket
    }

    stages {

        stage('Checkout Code') {
            steps {
                echo "Pulling latest repository..."
                checkout scm
            }
        }

        stage('Run Weather Ingestion Script') {
            steps {
                echo "Running weather ingestion script..."
                withCredentials([usernamePassword(credentialsId: 'aws-jenkins-creds', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                    sh '''
                    python3 weather_pipeline/src/fetch_weather.py
                    '''
                }
            }
        }

        stage('Run Glue ETL job') {
            steps {
                echo "Running AWS Glue ETL job: weather-pipeline-tp-etl-job"
                withCredentials([usernamePassword(credentialsId: 'aws-jenkins-creds', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                    sh '''
                    JOB_RUN_ID=$(aws glue start-job-run --job-name weather-pipeline-tp-etl-job --query 'JobRunId' --output text)
                    echo "Glue Job started with JobRunId: $JOB_RUN_ID"

                    STATUS="RUNNING"
                    while [ "$STATUS" == "RUNNING" ] || [ "$STATUS" == "STARTING" ]; do
                        sleep 10
                        STATUS=$(aws glue get-job-run --job-name weather-pipeline-tp-etl-job --run-id $JOB_RUN_ID --query 'JobRun.JobRunState' --output text)
                        echo "Current Glue job status: $STATUS"
                    done

                    if [ "$STATUS" == "SUCCEEDED" ]; then
                        echo "Glue job completed successfully!"
                    else
                        echo "Glue job FAILED with status: $STATUS"
                        exit 1
                    fi
                    '''
                }
            }
        }

        stage('Run Athena Query') {
            steps {
                echo "Running Athena query on ${ATHENA_DB}..."
                withCredentials([usernamePassword(credentialsId: 'aws-jenkins-creds', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                    sh '''
                    QUERY="SELECT city, country, datetime_utc, temperature_celsius, weather_main FROM ${ATHENA_DB}.weather_data ORDER BY datetime_utc DESC LIMIT 30;"

                    QUERY_EXECUTION_ID=$(aws athena start-query-execution \
                        --query-string "$QUERY" \
                        --query-execution-context Database=${ATHENA_DB} \
                        --result-configuration OutputLocation=${ATHENA_OUTPUT} \
                        --output text --query 'QueryExecutionId')

                    echo "Athena Query started with ID: $QUERY_EXECUTION_ID"

                    # Poll for Athena query completion
                    STATUS="RUNNING"
                    while [ "$STATUS" == "RUNNING" ] || [ "$STATUS" == "QUEUED" ]; do
                        sleep 5
                        STATUS=$(aws athena get-query-execution --query-execution-id $QUERY_EXECUTION_ID --query 'QueryExecution.Status.State' --output text)
                        echo "Current Athena query status: $STATUS"
                    done

                    if [ "$STATUS" == "SUCCEEDED" ]; then
                        echo "Athena query completed successfully!"
                        echo "Results available at: ${ATHENA_OUTPUT}$QUERY_EXECUTION_ID.csv"
                    else
                        echo "Athena query FAILED with status: $STATUS"
                        exit 1
                    fi
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Jenkins pipeline completed successfully!"
        }
        failure {
            echo "Jenkins pipeline failed! Check logs."
        }
    }
}