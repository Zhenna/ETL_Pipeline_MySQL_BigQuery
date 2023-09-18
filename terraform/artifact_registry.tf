
resource "google_artifact_registry_repository" "repo_docker" {
  format        = "DOCKER"
  location      = var.region
  project       = var.gcp-project-id
  repository_id = "${var.project-name}-docker"
  description   = "docker repository for ${var.project-name}"

  docker_config {
    immutable_tags = false
  }

}
