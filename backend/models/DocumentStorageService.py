import hashlib
import os
from datetime import timedelta
from typing import Tuple
from fastapi import UploadFile, HTTPException
import boto3
from botocore.exceptions import ClientError
from services.s3_service import get_s3_client

# Import settings from config
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

class DocumentStorageService:
    """
    Handles secure document storage with S3.
    Legal requirements:
    - Private storage only
    - SHA-256 hashing for integrity
    - Organized by lawyer ID
    - Signed URLs for temporary access
    """
    def __init__(self):
        self.s3_client = get_s3_client()
        self.bucket_name = settings.S3_BUCKET_NAME
        self.max_file_size = 10*1024*1024 # 10 MB
        self.allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png'}

    def _validate_file(self, file: UploadFile) -> None:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in self.allowed_extensions:
            raise HTTPException(400, f"Invalid file type. Allowed: {self.allowed_extensions}")

        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(0)  

        if size > self.max_file_size:
            raise HTTPException(400, f"File size exceeds {self.max_file_size/(1024*1024)} MB limit.")
        
    def _compute_hash(self, file_content: bytes) -> str:
        sha256 = hashlib.sha256()
        sha256.update(file_content)
        return sha256.hexdigest()
    
    def _generate_s3_key(self, lawyer_id: int, document_type: str, filename: str) -> str:
        """Generate organized S3 key structure"""
        ext = os.path.splitext(filename)[1]
        return f"lawyers/{lawyer_id}/verification/{document_type}{ext}"
    
    
    async def upload_document(
        self, 
        lawyer_id: int, 
        document_type: str, 
        file: UploadFile,
        existing_hash: str = None
    ) -> Tuple[str, str]:
        """
        Upload document to S3 and return (URL, hash).
        Prevents replacement if existing_hash is provided.
        """
        self._validate_file(file)
        
        # Read file content
        content = await file.read()
        file_hash = self._compute_hash(content)
        
        # CRITICAL: Prevent document replacement after submission
        if existing_hash and existing_hash != file_hash:
            raise HTTPException(
                403, 
                "Document replacement not allowed after submission. Contact admin for changes."
            )
        
        # Generate S3 key
        s3_key = self._generate_s3_key(lawyer_id, document_type, file.filename)
        
        try:
            # Upload with private ACL
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=content,
                ContentType=file.content_type,
                Metadata={
                    'lawyer_id': str(lawyer_id),
                    'document_type': document_type,
                    'sha256': file_hash
                },
                ServerSideEncryption='AES256'  # Encryption at rest
            )
            
            # Return permanent S3 URL (not signed - signed URLs generated on-demand)
            url = f"s3://{self.bucket_name}/{s3_key}"
            return url, file_hash
            
        except ClientError as e:
            raise HTTPException(500, f"Storage error: {str(e)}")
        
    def generate_signed_url(self, s3_url: str, expiration: int = 3600) -> str:
        """
        Generate temporary signed URL for document access.
        Default: 1 hour expiration.
        """
        if not s3_url.startswith('s3://'):
            raise ValueError("Invalid S3 URL format")
        
        s3_key = s3_url.replace(f"s3://{self.bucket_name}/", "")
        
        try:
            signed_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return signed_url
        except ClientError as e:
            raise HTTPException(500, f"Failed to generate signed URL: {str(e)}")
    
    def delete_document(self, s3_url: str) -> None:
        """Delete document (admin only - for rejected verifications)"""
        s3_key = s3_url.replace(f"s3://{self.bucket_name}/", "")
        
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
        except ClientError as e:
            raise HTTPException(500, f"Failed to delete document: {str(e)}")

# Singleton instance
document_storage = DocumentStorageService()
