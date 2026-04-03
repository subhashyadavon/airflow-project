import boto3
import json
import logging
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

class S3Manager:
    def __init__(self, bucket_name, endpoint_url=None):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id='test',
            aws_secret_access_key='test',
            region_name='us-east-1'
        )
        self.logger = logging.getLogger(__name__)

    def create_bucket(self):
        try:
            self.s3_client.create_bucket(Bucket=self.bucket_name)
            self.logger.info(f"Bucket {self.bucket_name} created successfully.")
        except self.s3_client.exceptions.BucketAlreadyOwnedByYou:
            self.logger.info(f"Bucket {self.bucket_name} already exists.")
        except Exception as e:
            self.logger.error(f"Error creating bucket: {e}")

    def upload_json(self, data, file_name):
        try:
            json_data = json.dumps(data)
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=json_data,
                ContentType='application/json'
            )
            self.logger.info(f"Successfully uploaded {file_name} to {self.bucket_name}")
        except Exception as e:
            self.logger.error(f"Error uploading to S3: {e}")

    def download_json(self, file_name):
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_name)
            return json.loads(response['Body'].read().decode('utf-8'))
        except Exception as e:
            self.logger.error(f"Error downloading from S3: {e}")
            return None
