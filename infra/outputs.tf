output "s3_bucket_name" {
  value = aws_s3_bucket.job_market_raw.id
}

output "rds_endpoint" {
  value = aws_db_instance.job_market_db.endpoint
}

output "ec2_public_ip" {
  value = aws_instance.airflow_server.public_ip
}
