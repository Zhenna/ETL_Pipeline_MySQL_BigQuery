resource "google_cloud_scheduler_job" "trigger_run_table1" {
  name             = "run-table1-scheduler-trigger"
  description      = "cloud scheduler, managed by terraform, to trigger Cloud Run job run-table1"
  schedule         = "0 0 * * *"
  time_zone        = "Etc/UTC"
  attempt_deadline = "180s"

  retry_config {
    max_backoff_duration = "3600s"
    max_doublings        = 5
    max_retry_duration   = "0s"
    min_backoff_duration = "5s"
    retry_count          = 0
  }

  http_target {
    http_method = "POST"
    uri         = "https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.gcp-project-id}/jobs/run-table1:run"

    oauth_token {
      service_account_email = google_service_account.etl_account.email
    }
  }
}

resource "google_cloud_scheduler_job" "trigger_run_table2" {
  name             = "run-table2-scheduler-trigger"
  description      = "cloud scheduler, managed by terraform, to trigger Cloud Run job run-table2"
  schedule         = "10 0 * * *"
  time_zone        = "Etc/UTC"
  attempt_deadline = "180s"

  retry_config {
    max_backoff_duration = "3600s"
    max_doublings        = 5
    max_retry_duration   = "0s"
    min_backoff_duration = "5s"
    retry_count          = 0
  }

  http_target {
    http_method = "POST"
    uri         = "https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.gcp-project-id}/jobs/run-table2:run"

    oauth_token {
      service_account_email = google_service_account.etl_account.email
    }
  }
}
