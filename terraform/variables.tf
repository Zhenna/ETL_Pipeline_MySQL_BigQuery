variable "gcp-project-id" {
  description = "unique project ID defined in string"
  default     = "<gcp-project-id>"
  type        = string
}

variable "gcp-key-name" {
  default = "<gcp-key-file-name>.json"
  type    = string
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "zone" {
  type    = string
  default = "us-central1-c"
}

variable "gcp-project-num" {
  description = "unique numeric identifider for google cloud project"
  default     = "<gcp-project-num>"
  type        = string
}

variable "container_image_url" {
  default = "us-central1-docker.pkg.dev/<gcp-project-id>/<repo-name>/<image-name>:latest"
  type    = string
}

