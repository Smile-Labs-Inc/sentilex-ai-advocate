"""
S3 Service Module

Provides utilities for uploading, downloading, and managing evidence files in Amazon S3.
Implements stream-to-cloud architecture with SHA-256 hashing and AES-256 encryption.
"""

import hashlib
import logging
from typing import Optional
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from config import settings

logger = logging.getLogger(__name__)


def get_s3_client():
    """
    Initialize and return a boto3 S3 client with s3v4 signature version.
    
    Returns:
        boto3.client: Configured S3 client
    """
    s3_config = Config(
        signature_version=settings.S3_SIGNATURE_VERSION,
        region_name=settings.AWS_REGION
    )
    
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=s3_config
    )


def calculate_sha256(content: bytes) -> str:
    """
    Calculate SHA-256 hash of file content for forensic audit trail.
    
    Args:
        content: File content as bytes
        
    Returns:
        str: Hexadecimal SHA-256 hash
    """
    sha256_hash = hashlib.sha256()
    sha256_hash.update(content)
    return sha256_hash.hexdigest()


def upload_file_to_s3(
    file_content: bytes,
    file_key: str,
    content_type: Optional[str] = None
) -> str:
    """
    Upload file to S3 with AES-256 server-side encryption.
    
    Args:
        file_content: File content as bytes
        file_key: S3 object key (path in bucket)
        content_type: MIME type of the file
        
    Returns:
        str: SHA-256 hash of the uploaded file
        
    Raises:
        Exception: If upload fails
    """
    s3_client = get_s3_client()
    
    # Calculate hash before upload
    file_hash = calculate_sha256(file_content)
    
    try:
        # Upload with AES-256 encryption
        put_params = {
            'Bucket': settings.S3_BUCKET_NAME,
            'Key': file_key,
            'Body': file_content,
            'ServerSideEncryption': 'AES256'
        }
        
        if content_type:
            put_params['ContentType'] = content_type
        
        s3_client.put_object(**put_params)
        
        logger.info(f"Successfully uploaded file to S3: {file_key} (hash: {file_hash})")
        return file_hash
        
    except ClientError as e:
        logger.error(f"Failed to upload file to S3: {file_key} - {str(e)}")
        raise Exception(f"S3 upload failed: {str(e)}")


def generate_presigned_url(file_key: str, expiration: int = 900) -> str:
    """
    Generate a presigned URL for temporary file access.
    
    Args:
        file_key: S3 object key
        expiration: URL expiration time in seconds (default: 900 = 15 minutes)
        
    Returns:
        str: Presigned URL for file download
        
    Raises:
        Exception: If URL generation fails
    """
    s3_client = get_s3_client()
    
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.S3_BUCKET_NAME,
                'Key': file_key
            },
            ExpiresIn=expiration
        )
        
        logger.info(f"Generated presigned URL for {file_key} (expires in {expiration}s)")
        return url
        
    except ClientError as e:
        logger.error(f"Failed to generate presigned URL for {file_key}: {str(e)}")
        raise Exception(f"Failed to generate download URL: {str(e)}")


def delete_file_from_s3(file_key: str) -> bool:
    """
    Delete a file from S3.
    
    Args:
        file_key: S3 object key to delete
        
    Returns:
        bool: True if deletion was successful
        
    Raises:
        Exception: If deletion fails
    """
    s3_client = get_s3_client()
    
    try:
        s3_client.delete_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=file_key
        )
        
        logger.info(f"Successfully deleted file from S3: {file_key}")
        return True
        
    except ClientError as e:
        logger.error(f"Failed to delete file from S3: {file_key} - {str(e)}")
        raise Exception(f"S3 deletion failed: {str(e)}")


def file_exists_in_s3(file_key: str) -> bool:
    """
    Check if a file exists in S3.
    
    Args:
        file_key: S3 object key to check
        
    Returns:
        bool: True if file exists, False otherwise
    """
    s3_client = get_s3_client()
    
    try:
        s3_client.head_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=file_key
        )
        return True
    except ClientError:
        return False
