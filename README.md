# Weather Data Engineering Pipeline  
*A cloud-native data pipeline ingesting real-time weather data into AWS for analytics and BI reporting in PowerBi.*

---

## How I approached the project

I built this project to demonstrate my end-to-end data engineering capability—moving beyond simple scripting into full cloud architecture, automation, and analytics.

I approached the workflow for this data pipeline project as follows:

### **1. Architecture First**
Before starting with Python, I designed how the data should flow from source → storage → ETL → analytics.

I wanted to ensure the solution wasn’t just a script, but rather a scalable pipeline.

### **2. Infrastructure as Code**
Similarly, to ensure repeatability, I steered away from manually provisioning the S3 buckets and IAM policies from the AWS console and instead utilised **Terraform**, allowing me to:

- Stand up the environment instantly
- Version-control infrastructure
- Avoid configuration drift

This was to better mirror production environments where IaC is essential and display my knowledge of such.

### **3. Build Modular Python for Ingestion & Analytics**
I wrote dedicated Python scripts for:

- Fetching weather data
- Uploading raw data to S3
- Running Athena queries programmatically

This separation of processes allowed for a modular approach to each step of the pipeline and ease of evolution moving forward.

Initially, I ran these scripts manually, validating API ingestion and S3 storage before introducing automation via Jenkins.

### **4. Implement a Robust ETL Layer Using Glue & Parquet**
I designed the Glue transformation script to:

- Normalise and flatten the JSON API
- Apply schema consistency
- Convert to Parquet

Parquet was chosen over CSV given I was looking to minimise storage costs whilst also wanting to ensure performant query capability. Acknowledging the dataset I was going to be storing is small, this allowed for future scalability.

### **5. Automate the Pipeline Using Jenkins CI/CD**
I orchestrated the entire workflow via Jenkins to include the following:

- Dependency installation
- Weather API ingestion
- AWS Glue ETL job execution
- Athena processing & verification

This turned the project from a batch process into a **repeatable pipeline** suitable for real operations. I did not however implement regular scheduling of the workflow as I am working in the bounds of the AWS Free Tier Access. This is included in the *Future Improvements* section.

### **6. Enable Analytics With Athena & Power BI**
Finally, using Athena’s ODBC connector, I connected to Power BI to deliver the potential for clean, interactive weather dashboards for possible future business intelligence needs.

### **7. Focus on Professionalism Throughout**
Throughout the project, I looked to apply real-world engineering practices:

- Secrets stored securely via an ENV locally, and then later added functionality to incorporate the Jenkins Credentials manager
- Regions and bucket naming aligned with AWS best practices
- Terraform standardised deployment
- Logging and error handling added to ETL steps

With the end goal of building a testable, secure, and maintainable pipeline.

---

## Overview

This project implements an automated, production-style data engineering pipeline designed to ingest, process, store, and visualise real-time weather data. It integrates:

- **OpenWeatherMap API** for data ingestion
- **Terraform** for infrastructure provisioning
- **AWS S3** for raw + processed storage
- **AWS Glue** for ETL and schema transformation
- **AWS Athena** for queryable analytics
- **Jenkins CI/CD** for orchestration
- **Power BI** for dashboarding

This project was created to demonstrate my knowledge and ability to utilise:

- Cloud architecture
- Infrastructure as Code (IaC)
- ETL design
- Pipeline orchestration
- Python development
- CI/CD and automated deployments

---

# Architecture Diagram

            ┌────────────────────┐
            │ Terraform IaC      │
            │  (S3, IAM, Glue)   │
            └─────────┬──────────┘
                      │
                      ▼
    ┌────────────────────────────────┐
    │ Jenkins CI/CD Pipeline         │
    └─────────────┬──────────────────┘
                  │
                  ▼
    ┌──────────────────────────────┐
    │ Python Weather Ingestion     │
    │  (API → S3 Raw Zone)         │
    └─────────┬────────────────────┘
              │
              ▼
    ┌──────────────────────────────┐
    │ Raw S3 Bucket                │
    │  Provisioned by Terraform    │
    └─────────┬────────────────────┘
              │
              ▼
    ┌──────────────────────────────┐
    │ AWS Glue ETL (PySpark)       │
    │  Clean → Normalise → Parquet │
    └─────────┬────────────────────┘
              │
              ▼
    ┌──────────────────────────────┐
    │ Athena Schema + Query Layer  │
    └─────────┬────────────────────┘
              │
              ▼
    ┌──────────────────────────────┐
    │ Power BI Dashboard           │
    │  via Athena ODBC             │
    └──────────────────────────────┘

---

# Technologies Used

### Cloud
- **AWS S3 (Terraform-provisioned)**
- AWS IAM
- AWS Glue
- AWS Athena

### Infrastructure as Code
- **Terraform**
  - S3 buckets
  - IAM roles/policies
  - Glue job configuration

### Pipeline / Orchestration
- Jenkins (Declarative Pipeline)

### Processing
- Python
- Glue PySpark

### Visualisation
- Power BI (Athena ODBC)

---

# Repository Structure

```text
weather_pipeline/
│
├── logs/
│
├── src/
│   ├── fetch_weather.py
│   ├── athena_etl.py
│   └── glue_etl.py
│
├── terraform/
│   ├── glue.tf
│   ├── iam.tf
│   ├── main.tf
│   ├── outputs.tf
│   ├── s3.tf
│   └── variables.tf
│
├── .gitignore
├── Jenkinsfile
├── key.env
├── LICENSE
├── README.md
└── requirements.txt
```
---

# Infrastructure Provisioning (Terraform)

Terraform was used to automate all infrastructure deployment, ensuring:

### ✔ Reproducibility
Deploying the entire environment from scratch is possible using:

- terraform init
- terraform plan
- terraform apply

### ✔ Benefits
- Automated creation of S3 buckets
- IAM roles/policies for Glue + Athena
- Consistent environment across deployment
- Full infrastructure version control

---

# Testing & Data Quality Controls

A combination of logging, schema validation, infrastructure testing, and CI/CD checks were used to ensure data quality and pipeline reliability.

### 1️⃣ Python Testing for Ingestion & S3 Upload
Logging-Driven Testing

The ingestion script (fetch_weather.py) includes comprehensive logging written to both console and log files. This allowed for debugging during development.


Functional Script Validation
As part of the ingestion process I manually validated the following to ensure there were no bugs in readiness for automation:

- API response correctness
- JSON structure integrity
- Environment variable loading
- S3 bucket uploads and paths
- File naming consistency


### 2️⃣ Data Quality Checks

## ✔ Completeness
Checked for presence of essential fields before upload.

## ✔ JSON Validity

Caught:

- Failed API calls
- Empty payloads
- Unexpected formats

## ✔ Logging as a Quality Gate
All ingestion anomalies were captured by the logging system, enabling early correction.

### 3️⃣ Infrastructure Testing (Terraform)

Initial manual implementation utilising:
- terraform fmt
- terraform validate
- terraform plan

To ensure correct syntax, predictable behaviour, and idempotent deployments.

### 4️⃣ AWS Glue ETL Testing
Schema Validation

Ensured Glue produced a consistent schema across runs.

Transformation Logic Testing

Verified:
- Nested JSON flattening
- Conversion of UNIX timestamps
- Handling optional fields
- Parquet File Inspection

Checked:
- Correct column names
- Clean schema
- No duplicates

### 5️⃣ Athena Query Validation
Automated Query Polling

athena_etl.py executed queries and validated:

- SUCCESS or FAILURE state
- Error handling
- Query output location
- Manual Sanity Checks

Verified table schema and consistency in Athena.

### 6️⃣ Jenkins Pipeline Testing

Validated each stage individually:

- Dependency installation
- Python ingestion
- Glue ETL execution
- Athena transformation
- AWS credential injection
- Multiple test runs confirmed end-to-end reliability.

---

# Challenges & What I Learned

### Secure Credential Handling
Secrets stored first in ENV file whilst deploying a manual pipeline prior to Github. Adapting the process within the Jenkins Credentials Manager alongside updates to the associated python script was an excellent opportunity to further extend my data security management skills.

### Infrastructure Consistency
Utilising Terraform for a project to ensure resources were reproducible and correctly configured, was a great expansion on a previous AWS Cloud Practitioner course which primarily focused on actions in the console.

### Glue ETL Schema Issues
Flattening and normalising the JSON file following API ingestion, ensuring the correct PySpark syntax was used during the transformation process was a good learning experience.

### Jenkins
Being the first time writing and deploying a Jenkinsfile, troubleshooting errors was an excellent learning curve to the process, especially when ensuring correct syntax was utilised for a windows based deployment.

---

# Future Improvements

- Add automated retries & exponential backoff for API ingestion
- Add DBT transformation for better version control and testing
- Create SNS alerts for pipeline failures
- Build schedule for Jenkins
- Introduce Glue partitioning by date/hour depending on frequency of the build schedule

---

# Conclusion

This project demonstrates end-to-end data engineering skills, including:

- Secure ingestion from an external API
- Infrastructure automation with Terraform
- Data lake architecture (raw → clean)
- Glue ETL development
- Athena query modelling
- Jenkins CI/CD orchestration
- Power BI reporting

It represents a realistic, scalable, production-ready data pipeline suitable for modern cloud data platforms.