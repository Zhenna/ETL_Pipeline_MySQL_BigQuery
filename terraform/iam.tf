# create a new service account
resource "google_service_account" "etl_account" {
  account_id   = "terraform-for-etl"
  display_name = "terraform-for-etl"
  project      = var.gcp-project-id
}

# allow this new service account to assume the role of secret accessor
resource "google_secret_manager_secret_iam_member" "secret-accessor" {
  project   = var.gcp-project-num
  secret_id = google_secret_manager_secret.my_secret.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.etl_account.email}"
}

# allow this new service account to assume the role of artifact registry writer
resource "google_artifact_registry_repository_iam_member" "artifact-registry-writer" {
  project    = google_artifact_registry_repository.repo_docker.project
  location   = google_artifact_registry_repository.repo_docker.location
  repository = google_artifact_registry_repository.repo_docker.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.etl_account.email}"
}

# allow this new service account to edit data in BigQuery datasets
resource "google_bigquery_dataset_iam_member" "prod-editor" {
  project    = var.gcp-project-id
  dataset_id = google_bigquery_dataset.schema_prod.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.etl_account.email}"
}

resource "google_bigquery_dataset_iam_member" "dev-editor" {
  project    = var.gcp-project-id
  dataset_id = google_bigquery_dataset.schema_dev.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.etl_account.email}"
}

# allow this new service account to run query in Big Query
resource "google_project_iam_member" "bigquery_job_user" {
  project = var.gcp-project-id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.etl_account.email}"
}

# add Cloud Scheduler Admin Role
resource "google_project_iam_member" "cloud_scheduler_admin" {
  project = var.gcp-project-id
  role    = "roles/cloudscheduler.admin"
  member  = "serviceAccount:${google_service_account.etl_account.email}"
}

# add Service Account User Role
resource "google_project_iam_member" "service_account_user" {
  project = var.gcp-project-id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.etl_account.email}"
}

# grant service account permission to trigger cloud run job
resource "google_cloud_run_v2_job_iam_member" "run_table1" {
  project  = google_cloud_run_v2_job.run_table1.project
  location = google_cloud_run_v2_job.run_table1.location
  name     = google_cloud_run_v2_job.run_table1.name
  role     = "roles/run.admin"
  member   = "serviceAccount:${google_service_account.etl_account.email}"
}

resource "google_cloud_run_v2_job_iam_member" "run_table2" {
  project  = google_cloud_run_v2_job.run_table2.project
  location = google_cloud_run_v2_job.run_table2.location
  name     = google_cloud_run_v2_job.run_table2.name
  role     = "roles/run.admin"
  member   = "serviceAccount:${google_service_account.etl_account.email}"
}
