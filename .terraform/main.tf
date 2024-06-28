terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.35.0"
    }
  }
  backend "gcs" {
    bucket = "codebc-airbnb-ai-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = "codebc-airbnb-ai"
  region  = "us-west1"
}


# create bucket for saving terraform state
resource "google_storage_bucket" "terraform_state" {
  name     = "codebc-airbnb-ai-terraform-state"
  location = "US-WEST1"
}


# upload csv file to bucket and trigger cloud run via pubsub
resource "google_cloud_run_service" "airbnb_ai" {
  name     = "airbnb-ai"
  location = "us-west1"
  project  = "codebc-airbnb-ai"
  template {
    spec {
      containers {
        image = "gcr.io/codebc-airbnb-ai/airbnb-ai"
      }
    }
  }
  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_pubsub_topic" "airbnb_ai" {
  name = "airbnb-ai"
}

resource "google_pubsub_subscription" "airbnb_ai" {
  name                 = "airbnb-ai"
  topic                = google_pubsub_topic.airbnb_ai.name
  ack_deadline_seconds = 10
  push_config {
    push_endpoint = google_cloud_run_service.airbnb_ai.status[0].url
  }
}

# resource "google_storage_bucket_object" "airbnb_ai" {
#   name   = "airbnb-ai.csv"
#   bucket = google_storage_bucket.terraform_state.name
#   source = "airbnb-ai.csv"
# }

# resource "google_storage_bucket_object_iam_member" "airbnb_ai" {
#   bucket = google_storage_bucket.terraform_state.name
#   object = google_storage_bucket_object.airbnb_ai.name
#   role   = "roles/storage.objectViewer"
#   member = "allUsers"
# }

# resource "google_storage_bucket_object_iam_member" "airbnb_ai" {
#   bucket = google_storage_bucket.terraform_state.name
#   object = google_storage_bucket_object.airbnb_ai.name
#   role   = "roles/storage.objectCreator"
#   member = "serviceAccount:
