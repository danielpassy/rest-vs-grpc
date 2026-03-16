variable "aws_region" {
  default = "us-east-1"
}

variable "sentry_dsn" {
  default   = ""
  sensitive = true
}

variable "image_tag" {
  default = "latest"
}

variable "project_name" {
  default = "rest-vs-grpc"
}

variable "ecr_repo_go_server" {
  description = "ECR repo URI for go-server"
}

variable "ecr_repo_fastapi" {
  description = "ECR repo URI for fastapi-client"
}
