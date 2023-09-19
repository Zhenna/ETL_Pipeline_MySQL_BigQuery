# Documentation 

## Current workflow for ETL:

1. create a new snapshot on the first day by extracting data from MySQL
2. incremental ingestion of raw data for processing everyday using python
3. load processed data to Google BigQuery

## Tech stack:
- MySQL (data source)
- Python 3.11 (data processing)
- Google Cloud Secret Manager (store credentials)
- Docker (containerize python pakcage)
- GCP Artifact Registry (store docker image)
- GCP Cloud Run (run daily job)
- GCP Cloud Scheduler (trigger Cloud Run job everyday)
- GCP Cloud Monitoring (trigger alert if job does not execute successfully)

## How to run

- (optional) create a new python3.11 virtual environment
- install dependencies 
```shell
pip install -r requirements.txt
```
- run incremental ETL locally
```shell
python main.py -env dev -tbl <table1> -t0 2023-08-01 -t1 2023-08-02 
```
- run snapshot locally
```shell
python main.py -env dev -tbl <table1> -snapshot
```

## How to deploy

- (first-time) Make `src/deploy.sh` executable.
```shell
chmod +x src/deploy.sh
```
- Run the script to deploy it.
```shell
src/deploy.sh
```
- Last, set up a CRON job to trigger docker run on a fixed schedule.

## How to edit Google Cloud Infrastructure

- Go to `/terraform`
```shell
cd terraform
```
- Initialize terraform by running
```shell
terraform init
```
- Edit terraform configuration file
- Check for changes by running
```shell
terraform plan
```
- Apply changes by running
```shell
terraform apply
```

## How to add new table for daily ETL?

Please create a new branch and merge to `main` after testing.

1. Add table name under `mySQL_tables` enum.

2. Declare schema in `src/properties.py` following the structure of `table_properties_mysql2bq` dataclass.

3. (optional) Under the circumstances that additional steps for data transformation is required, edit `src/etl.py`. 

4. Add new default choices for `ArgumentParser` `--table` argument in `src/main.py`.

5. Add new scheduled job accordly when it is ready for deployment. 

    5.1 Open `terraform/cloud_run.tf` and add a new `google_cloud_run_v2_job` resource block.
    5.2 Open `terraform/cloud_scheduler.tf` and add a new `google_cloud_scheduler_job` resource block.
    5.3 Open `terraform/iam.tf` and add a new `google_cloud_run_v2_job_iam_member` resource block.

## repo structure
```
.
├── ...
├── README.md
├── Dockerfile
├── .dockerignore
├── requirements.txt
├── (local) <gcp-key-file>.json   
│   # NEVER EVER PUSH CREDENTIALS TO GIT!
├── ...
│
├── terraform                     # Infrastructure as code            
│   ├── terraform_import.sh       # shell script to import resources
│   ├── cloud_run.tf              # runners for all jobs
│   ├── cloud_scheduler.tf        # triggers for all jobs
│   ├── iam.tf                    # service account and permissions
│   ├── monitoring.tf             # alert for job failure
│   ├── secret.tf                 # store credentials
│   ├── bigquery.tf               # datasets for fms-etl
│   ├── artifact_registry.tf      # GCP repo to host docker image  
│   ├── main.tf                   # cloud provider               
│   └── variables.tf              # project-specific variables 
│
├── src                    
│   ├── __init__.py
│   ├── deploy.sh                 # shell script to deploy the job
│   ├── sql_template.py           # sql templates to query mySQL    
│   ├── properties.py             # table schema
│   ├── etl.py                    # ETL functions
│   └── main.py                   # run ETL job
│     
├── test                           
│   ├── __init__.py
│   └── test_etl.py               # Unit tests and integration tests
│
└── ...
```