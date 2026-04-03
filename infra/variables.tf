variable "aws_region" {
  description = "AWS region"
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "S3 bucket for raw data"
  default     = "job-market-raw-data"
}

variable "db_password" {
  description = "Password for RDS PostgreSQL"
  sensitive   = true
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t3.medium"
}
