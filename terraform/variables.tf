variable "region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "eu-north-1"
}

variable "docker_image_uri" {
  description = "The Docker image URI for the Flask app"
  type        = string
}
