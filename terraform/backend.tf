terraform {
  backend "gcs" {
    bucket = "etl-tfstate"
    prefix = "terraform-state"
  }
}
