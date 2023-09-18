terraform {
  required_version = ">= 1.5.6"
}

provider "google" {
  credentials = file("../${var.gcp-key-name}")
  project     = var.project-name
  region      = var.region
  zone        = var.zone
}
