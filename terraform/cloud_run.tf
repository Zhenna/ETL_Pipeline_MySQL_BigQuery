resource "google_cloud_run_v2_job" "run_table1" {
  name     = "run-table1"
  location = var.region

  template {
    parallelism = 0
    task_count  = 1

    template {
      service_account = google_service_account.etl_account.email
      containers {
        image = var.container_image_url
        args = [
          "-env",
          "prod",
          "-tbl",
          "<table1>",
          "-snapshot",
        ]
        resources {
          limits = {
            memory = "1Gi"
            cpu    = "1000m"
          }
        }
      }
    }
  }
}

resource "google_cloud_run_v2_job" "run_table2" {
  name     = "run-table2"
  location = var.region

  template {
    parallelism = 0
    task_count  = 1

    template {
      service_account = google_service_account.etl_account.email
      containers {
        image = var.container_image_url
        args = [
          "-env",
          "prod",
          "-tbl",
          "<table2>",
          "-snapshot",
        ]
        resources {
          limits = {
            memory = "1Gi"
            cpu    = "1000m"
          }
        }
      }
    }
  }
}
