

resource "google_storage_bucket" "bucket-raw-data" {
  name          = "etl-raw-data"
  location      = "US"
  force_destroy = false

  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "bucket-tf-states" {
  name          = "etl-tfstate"
  location      = "US"
  force_destroy = true

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}
