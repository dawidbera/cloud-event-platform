import os
import boto3
from botocore.config import Config

class AWSClientFactory:
    """
    Factory to create boto3 clients configured either for LocalStack (local dev) 
    or real AWS (production) based on environment variables.
    """
    
    @staticmethod
    def get_client(service_name: str, region_name: str = "us-east-1"):
        """Instantiates a boto3 client pointing either to LocalStack (for local dev) or real AWS based on environment configuration."""
        use_localstack = os.environ.get("USE_LOCALSTACK", "true").lower() == "true"
        localstack_url = os.environ.get("LOCALSTACK_URL", "http://localhost:4566")
        
        if use_localstack:
            # For LocalStack, we must point the endpoint_url and use dummy credentials
            return boto3.client(
                service_name,
                endpoint_url=localstack_url,
                aws_access_key_id="test",
                aws_secret_access_key="test",
                region_name=region_name,
                config=Config(retries={'max_attempts': 3})
            )
        else:
            # For Real AWS, use the standard boto3 initialization (relies on IAM/Env vars)
            return boto3.client(
                service_name,
                region_name=region_name
            )

# Example usage for SQS
def get_sqs_client():
    """Helper function to obtain an AWS SQS client configured via AWSClientFactory."""
    return AWSClientFactory.get_client("sqs")

# Example usage for S3
def get_s3_client():
    """Helper function to obtain an AWS S3 client configured via AWSClientFactory."""
    return AWSClientFactory.get_client("s3")
