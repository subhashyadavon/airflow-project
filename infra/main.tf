provider "aws" {
  region = var.aws_region
}

# S3 Bucket for raw data
resource "aws_s3_bucket" "job_market_raw" {
  bucket = var.bucket_name
  acl    = "private"

  tags = {
    Name = "Job Market Raw Data"
  }
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "job_market_db" {
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "15.3"
  instance_class       = "db.t3.micro"
  db_name              = "jobmarket"
  username             = "airflow"
  password             = var.db_password
  parameter_group_name = "default.postgres15"
  skip_final_snapshot  = true
  publicly_accessible  = true

  tags = {
    Name = "Job Market DB"
  }
}

# EC2 Instance for Airflow
resource "aws_instance" "airflow_server" {
  ami           = "ami-0c55b159cbfafe1f0" # Ubuntu 22.04 in us-east-1
  instance_type = var.instance_type
  key_name      = "airflow-key"

  tags = {
    Name = "Airflow Server"
  }

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update
              sudo apt-get install -y docker.io docker-compose
              sudo systemctl enable --now docker
              # Setup instructions would go here (clone repo, docker-compose up)
              EOF
}

# Security group to allow traffic to Postgres and Airflow webserver
resource "aws_security_group" "job_pipeline_sg" {
  name        = "job_pipeline_sg"
  description = "Allow inbound traffic for Postgres and Airflow"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
