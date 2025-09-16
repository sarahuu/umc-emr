from typing import Optional
from datetime import datetime, timedelta
from app.core.config import settings
import redis
from cryptography.fernet import Fernet
import base64
import logging
import os

logger = logging.getLogger(__name__)

class SecureSessionStore:
    def __init__(self):
        self.client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.fernet = self._initialize_fernet()
    
    def _initialize_fernet(self) -> Fernet:
        encryption_key = getattr(settings, 'ENCRYPTION_KEY', None)
        
        if not encryption_key:
            encryption_key = Fernet.generate_key().decode()
            logger.warning("Using auto-generated encryption key. Set ENCRYPTION_KEY in settings for production.")
        if len(encryption_key) != 44:  # Fernet key length
            raise ValueError("Encryption key must be 32 url-safe base64-encoded bytes")
        return Fernet(encryption_key.encode())
    
    def encrypt_password(self, password: str) -> str:
        encrypted = self.fernet.encrypt(password.encode())
        return encrypted.decode()
    
    def decrypt_password(self, encrypted_password: str) -> Optional[str]:
        try:
            decrypted = self.fernet.decrypt(encrypted_password.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Password decryption failed: {e}")
            return None
    
    def save_user_credentials(self, uid: int, password: str, lifetime_minutes: int = 60):
        try:
            encrypted_password = self.encrypt_password(password)
            expiration_seconds = lifetime_minutes * 60
            self.client.setex(f"user:{uid}:encrypted_pwd", expiration_seconds, encrypted_password)
            logger.info(f"Encrypted password saved for user {uid}")
        except Exception as e:
            logger.error(f"Failed to save encrypted password: {e}")
            raise
    
    def get_user_password(self, uid: int) -> Optional[str]:
        try:
            encrypted_password = self.client.get(f"user:{uid}:encrypted_pwd")
            if not encrypted_password:
                logger.warning(f"No encrypted password found for user {uid}")
                return None
            return self.decrypt_password(encrypted_password)
        except Exception as e:
            logger.error(f"Failed to retrieve password: {e}")
            return None
    
    def remove_user_credentials(self, uid: int):
        """Remove stored credentials"""
        return self.client.delete(f"user:{uid}:encrypted_pwd")
    
    def get_credentials_ttl(self, uid: int) -> int:
        """Get remaining time for credentials"""
        return self.client.ttl(f"user:{uid}:encrypted_pwd")
    
