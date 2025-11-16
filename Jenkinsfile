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
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-jenkins-creds']]) {
                    bat "python src\\fetch_weather.py"
                }
            }
        }

        stage('Run Glue ETL job') {
            steps {
                echo "Running AWS Glue ETL job: weather-pipeline-tp-etl-job"
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-jenkins-creds']]) {
                    bat """
                    REM Start Glue job and get JobRunId
                    for /f "tokens=*" %%i in ('aws glue start-job-run --job-name weather-pipeline-tp-etl-job --query "JobRunId" --output text') do set JOB_RUN_ID=%%i
                    echo Glue Job started with JobRunId: !JOB_RUN_ID!

                    REM Poll until job finishes
                    :glueLoop
                    for /f "tokens=*" %%s in ('aws glue get-job-run --job-name weather-pipeline-tp-etl-job --run-id !JOB_RUN_ID! --query "JobRun.JobRunState" --output text') do set STATUS=%%s
                    echo Current Glue job status: !STATUS!
                    if "!STATUS!"=="RUNNING" timeout /t 10 & goto glueLoop
                    if "!STATUS!"=="STARTING" timeout /t 10 & goto glueLoop

                    REM Check final status
                    if "!STATUS!"=="SUCCEEDED" (
                        echo Glue job completed successfully!
                    ) else (
                        echo Glue job FAILED with status: !STATUS!
                        exit /b 1
                    )
                    """
                }
            }
        }

        stage('Run Athena Query') {
            steps {
                echo "Running Athena query on ${ATHENA_DB}..."
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-jenkins-creds']]) {
                    bat """
                    REM Define query
                    set QUERY=SELECT city, country, datetime_utc, temperature_celsius, weather_main FROM ${ATHENA_DB}.weather_data ORDER BY datetime_utc DESC LIMIT 30;

                    REM Start Athena query and get execution ID
                    for /f "tokens=*" %%q in ('aws athena start-query-execution --query-string "!QUERY!" --query-execution-context Database=${ATHENA_DB} --result-configuration OutputLocation=${ATHENA_OUTPUT} --output text --query "QueryExecutionId"') do set QUERY_EXECUTION_ID=%%q
                    echo Athena Query started with ID: !QUERY_EXECUTION_ID!

                    REM Poll until query finishes
                    :athenaLoop
                    for /f "tokens=*" %%s in ('aws athena get-query-execution --query-execution-id !QUERY_EXECUTION_ID! --query "QueryExecution.Status.State" --output text') do set STATUS=%%s
                    echo Current Athena query status: !STATUS!
                    if "!STATUS!"=="RUNNING" timeout /t 5 & goto athenaLoop
                    if "!STATUS!"=="QUEUED" timeout /t 5 & goto athenaLoop

                    REM Check final status
                    if "!STATUS!"=="SUCCEEDED" (
                        echo Athena query completed successfully!
                        echo Results available at: ${ATHENA_OUTPUT}!QUERY_EXECUTION_ID!.csv
                    ) else (
                        echo Athena query FAILED with status: !STATUS!
                        exit /b 1
                    )
                    """
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
