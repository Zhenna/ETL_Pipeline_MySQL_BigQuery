resource "google_secret_manager_secret" "my_secret" {
  project = var.gcp-project-num
  replication {
    automatic = true
  }
  secret_id = "my_secret"
}
