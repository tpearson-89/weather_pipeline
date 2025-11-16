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
                    bat 'python weather_pipeline\\src\\fetch_weather.py'
                }
            }
        }

        stage('Run Glue ETL job') {
            steps {
                echo "Running AWS Glue ETL job: weather-pipeline-tp-etl-job"
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-jenkins-creds']]) {
                    powershell '''
                    $jobName = "weather-pipeline-tp-etl-job"
                    $jobRunId = aws glue start-job-run --job-name $jobName --query "JobRunId" --output text
                    Write-Host "Glue Job started with JobRunId: $jobRunId"

                    do {
                        Start-Sleep -Seconds 10
                        $status = aws glue get-job-run --job-name $jobName --run-id $jobRunId --query "JobRun.JobRunState" --output text
                        Write-Host "Current Glue job status: $status"
                    } while ($status -eq "RUNNING" -or $status -eq "STARTING")

                    if ($status -eq "SUCCEEDED") {
                        Write-Host "Glue job completed successfully!"
                    } else {
                        Write-Error "Glue job FAILED with status: $status"
                        exit 1
                    }
                    '''
                }
            }
        }

        stage('Run Athena Query') {
            steps {
                echo "Running Athena query on ${ATHENA_DB}..."
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-jenkins-creds']]) {
                    powershell '''
                    $athenaDb = "${env.ATHENA_DB}"
                    $athenaOutput = "${env.ATHENA_OUTPUT}"
                    $query = "SELECT city, country, datetime_utc, temperature_celsius, weather_main FROM $athenaDb.weather_data ORDER BY datetime_utc DESC LIMIT 30;"

                    $queryExecutionId = aws athena start-query-execution `
                        --query-string "$query" `
                        --query-execution-context Database=$athenaDb `
                        --result-configuration OutputLocation=$athenaOutput `
                        --output text --query "QueryExecutionId"

                    Write-Host "Athena Query started with ID: $queryExecutionId"

                    do {
                        Start-Sleep -Seconds 5
                        $status = aws athena get-query-execution --query-execution-id $queryExecutionId --query "QueryExecution.Status.State" --output text
                        Write-Host "Current Athena query status: $status"
                    } while ($status -eq "RUNNING" -or $status -eq "QUEUED")

                    if ($status -eq "SUCCEEDED") {
                        Write-Host "Athena query completed successfully!"
                        Write-Host "Results available at: $athenaOutput$queryExecutionId.csv"
                    } else {
                        Write-Error "Athena query FAILED with status: $status"
                        exit 1
                    }
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
