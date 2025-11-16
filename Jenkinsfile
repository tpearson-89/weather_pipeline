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

        stage('Install Python Dependencies') {
            steps {
                echo "Installing Python dependencies..."
                bat 'python -m pip install --upgrade pip'
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('Run Weather Ingestion Script') {
            steps {
                echo "Running weather ingestion script..."
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-jenkins-creds'
                ]]) {
                    bat 'python src\\fetch_weather.py'
                }
            }
        }

        stage('Run Glue ETL Script') {
            steps {
                echo "Running Glue ETL script..."
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-jenkins-creds'
                ]]) {
                    bat 'python src\\glue_etl.py'
                }
            }
        }

        stage('Run Athena ETL Script') {
            steps {
                echo "Running Athena ETL script..."
                withCredentials([[
                    $class: 'AmazonWebServicesCredentialsBinding',
                    credentialsId: 'aws-jenkins-creds'
                ]]) {
                    bat 'python src\\athena_etl.py'
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
