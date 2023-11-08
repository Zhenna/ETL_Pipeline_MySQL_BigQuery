resource "google_monitoring_alert_policy" "etl_alert_policy" {
  display_name = "No successful job execution in one day"
  combiner     = "OR"

  conditions {
    display_name = "Cloud Run Job - Completed Executions"
    condition_absent {
      filter   = "resource.type = \"cloud_run_job\" AND resource.labels.job_name = has_substring(\"etl-\") AND metric.type = \"run.googleapis.com/job/completed_execution_count\" AND metric.labels.result = \"succeeded\""
      duration = "86400s"
      trigger {
        percent = 100
      }
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  enabled               = true
  notification_channels = ["projects/${var.gcp-project-id}/notificationChannels/<notification-channel-id>"]
}


resource "google_monitoring_alert_policy" "etl_alert_policy2" {
  display_name = "Error running job for ETL"
  combiner     = "OR"

  conditions {
    display_name = "Cloud Run Job - Log entries"
    condition_threshold {
      filter     = "resource.type = \"cloud_run_job\" AND resource.labels.job_name = starts_with(\"run-etl-\") AND metric.type = \"logging.googleapis.com/log_entry_count\" AND metric.labels.severity = \"ERROR\""
      duration   = "0s"
      comparison = "COMPARISON_GT"
      trigger {
        count = 1
      }
      # aggregations {
      #   alignment_period   = "60s"
      #   per_series_aligner = "ALIGN_RATE"
      # }
    }
  }

  enabled               = true
  notification_channels = ["projects/${var.gcp-project-id}/notificationChannels/2405835085951824497"]
}
