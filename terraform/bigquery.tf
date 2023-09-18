
resource "google_bigquery_dataset" "schema_prod" {
  project       = var.gcp-project-id
  dataset_id    = "schema_prod"
  friendly_name = "schema_prod"
  description   = ""
  location      = "US"
}

resource "google_bigquery_dataset" "schema_dev" {
  project       = var.gcp-project-id
  dataset_id    = "schema_dev"
  friendly_name = "schema_dev"
  description   = ""
  location      = "US"
}
