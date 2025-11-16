pipeline {
    agent any

    // --- Environment variables accessible in all stages ---
    environment {
        AWS_DEFAULT_REGION = 'eu-west-1'              // Default AWS region
        ATHENA_DB = 'weather_db'                       // Athena database
        ATHENA_OUTPUT = 's3://weather-pipeline-tp-athena/' // S3 bucket for Athena query results
        GLUE_JOB_NAME = 'weather-pipeline-tp-etl-job' // Glue ETL job name
        S3_BUCKET = 'weather-pipeline-tp-raw' // S3 bucket for raw API data
        CITY = 'Plymouth,GB' // OpenWeather API City
        UNITS = 'metric'  // Units of temperature
    }

    stages {

        // --- Stage 1: Checkout the latest code from SCM ---
        stage('Checkout Code') {
            steps {
                echo "Pulling latest repository..."
                checkout scm
            }
        }

        // --- Stage 2: Install Python dependencies ---
        stage('Install Python Dependencies') {
            steps {
                echo "Installing Python dependencies..."
                // Upgrade pip first to avoid old-version issues
                bat 'python -m pip install --upgrade pip'
                // Install dependencies listed in requirements.txt
                bat 'python -m pip install -r requirements.txt'
            }
        }

        // --- Stage 3: Run weather ingestion script ---
        stage('Run Weather Ingestion Script') {
            steps {
                echo "Running weather ingestion script..."
                // Bind both AWS credentials and OpenWeatherMap API key
                withCredentials([
                    [
                        $class: 'AmazonWebServicesCredentialsBinding',
                        credentialsId: 'aws-jenkins-creds'
                    ],
                    [
                        $class: 'StringBinding',
                        credentialsId: 'owm-api-key',
                        variable: 'OWM_API_KEY'
                    ]
                ]) {
                    // Run Python script to fetch weather and upload to S3
                    bat 'python src\\fetch_weather.py'
                }
            }
        }

        // --- Stage 4: Run Glue ETL Job ---
        stage('Run Glue ETL Job') {
            steps {
                echo "Starting AWS Glue ETL job..."
                withAWS(credentials: 'aws-jenkins-creds', region: "${AWS_DEFAULT_REGION}") {
                    // Use Windows batch script to start Glue job and poll status
                    bat """
                    @echo off
                    set JOB_RUN_ID=
                    for /f "delims=" %%i in ('aws glue start-job-run --job-name ${GLUE_JOB_NAME} --query JobRunId --output text') do set JOB_RUN_ID=%%i
                    echo Glue Job started with JobRunId: %JOB_RUN_ID%

                    :poll
                    set STATUS=
                    for /f "delims=" %%i in ('aws glue get-job-run --job-name ${GLUE_JOB_NAME} --run-id %JOB_RUN_ID% --query JobRun.JobRunState --output text') do set STATUS=%%i
                    echo Current Glue job status: %STATUS%
                    if "%STATUS%"=="RUNNING" (
                        timeout /t 10
                        goto poll
                    ) else if "%STATUS%"=="STARTING" (
                        timeout /t 10
                        goto poll
                    )

                    if "%STATUS%"=="SUCCEEDED" (
                        echo Glue job completed successfully!
                    ) else (
                        echo Glue job FAILED with status: %STATUS%
                        exit /b 1
                    )
                    """
                }
            }
        }

        // --- Stage 5: Run Athena ETL Script ---
        stage('Run Athena ETL Script') {
            steps {
                echo "Running Athena ETL script..."
                withCredentials([[ 
                    $class: 'AmazonWebServicesCredentialsBinding', 
                    credentialsId: 'aws-jenkins-creds' 
                ]]) {
                    // Runs Python script that executes Athena query and polls for completion
                    bat 'python src\\athena_etl.py'
                }
            }
        }
    }

    // --- Post Actions ---
    post {
        success {
            echo "Jenkins pipeline completed successfully!"
        }
        failure {
            echo "Jenkins pipeline failed! Check logs."
        }
    }
}
