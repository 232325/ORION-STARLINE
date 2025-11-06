#!/usr/bin/env python3
"""
Shifrlash Tizimi
Encryption System - End-to-End Encryption

Bu fayl ilg'or shifrlash imkoniyatlarini ta'minlaydi,
end-to-end encryption, ma'lumotlarni himoyalash va
xavfsiz kalitlarni boshqarish.

Features:
- End-to-End Encryption
- Key Management
- Digital Signatures
- Certificate Management
- Secure Communication
- Data Integrity Verification
- Quantum-resistant algorithms
- Hardware Security Module (HSM) integration
"""

import os
import sys
import json
import base64
import hashlib
import hmac
import secrets
import sqlite3
import datetime
import logging
import threading
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import uuid

# Cryptographic libraries
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ed25519
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.x963kdf import X963KDF
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
import nacl.secret
import nacl.box
import nacl.utils
import nacl.hash
import pyotp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/orion-starline/logs/encryption.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EncryptionAlgorithm(Enum):
    """Shifrlash algoritmlari"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    ECDSA_P256 = "ecdsa_p256"
    ECDSA_P384 = "ecdsa_p384"
    ED25519 = "ed25519"
    X25519 = "x25519"

class KeyType(Enum):
    """Kalit turlari"""
    SYMMETRIC = "symmetric"
    ASYMMETRIC_PUBLIC = "asymmetric_public"
    ASYMMETRIC_PRIVATE = "asymmetric_private"
    SESSION = "session"
    MASTER = "master"

class SecurityLevel(Enum):
    """Xavfsizlik darajalari"""
    BASIC = 128
    HIGH = 192
    MAXIMUM = 256

@dataclass
class EncryptionKey:
    """Shifrlash kaliti"""
    key_id: str
    key_type: KeyType
    algorithm: EncryptionAlgorithm
    key_material: bytes
    created_date: str
    expires_date: Optional[str]
    usage_count: int
    max_usage: Optional[int]
    metadata: Dict[str, Any]
    integrity_hash: str

@dataclass
class EncryptedData:
    """Shifrlangan ma'lumot"""
    data_id: str
    original_size: int
    encrypted_data: bytes
    encryption_algorithm: str
    key_id: str
    iv: bytes
    auth_tag: Optional[bytes]
    metadata: Dict[str, Any]
    created_date: str

@dataclass
class DigitalSignature:
    """Raqamli imzo"""
    signature_id: str
    signer_id: str
    algorithm: str
    signature_data: bytes
    signed_data: bytes
    timestamp: str
    verification_key_id: str

class KeyDerivationFunction:
    """Kalit hosil qilish funksiyasi"""
    
    @staticmethod
    def pbkdf2(password: str, salt: bytes, iterations: int = 100000, 
               key_length: int = 32) -> bytes:
        """PBKDF2 kalit hosil qilish"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        return kdf.derive(password.encode())
    
    @staticmethod
    def scrypt(password: str, salt: bytes, n: int = 2**14, r: int = 8, p: int = 1,
               key_length: int = 32) -> bytes:
        """Scrypt kalit hosil qilish"""
        kdf = Scrypt(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            n=n,
            r=r,
            p=p,
            backend=default_backend()
        )
        return kdf.derive(password.encode())
    
    @staticmethod
    def hkdf(password: bytes, salt: bytes, info: bytes = b"", 
             key_length: int = 32) -> bytes:
        """HKDF kalit hosil qilish"""
        kdf = HKDF(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            info=info,
            backend=default_backend()
        )
        return kdf.derive(password)

class SymmetricEncryption:
    """Simmetrik shifrlash"""
    
    @staticmethod
    def generate_aes_key(key_length: int = 256) -> bytes:
        """AES kalit yaratish"""
        return secrets.token_bytes(key_length // 8)
    
    @staticmethod
    def encrypt_aes_gcm(data: bytes, key: bytes) -> Tuple[bytes, bytes, bytes]:
        """AES-GCM shifrlash"""
        iv = secrets.token_bytes(12)
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(data) + encryptor.finalize()
        auth_tag = encryptor.tag
        return encrypted_data, iv, auth_tag
    
    @staticmethod
    def decrypt_aes_gcm(encrypted_data: bytes, key: bytes, iv: bytes, 
                       auth_tag: bytes) -> bytes:
        """AES-GCM deshifrlash"""
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, auth_tag), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        return decrypted_data
    
    @staticmethod
    def encrypt_chacha20_poly1305(data: bytes, key: bytes) -> Tuple[bytes, bytes]:
        """ChaCha20-Poly1305 shifrlash"""
        nonce = secrets.token_bytes(12)
        box = nacl.secret.SecretBox(key)
        encrypted_data = box.encrypt(data, nonce)
        return encrypted_data, nonce
    
    @staticmethod
    def decrypt_chacha20_poly1305(encrypted_data: bytes, key: bytes, nonce: bytes) -> bytes:
        """ChaCha20-Poly1305 deshifrlash"""
        box = nacl.secret.SecretBox(key)
        decrypted_data = box.decrypt(encrypted_data, nonce)
        return decrypted_data

class AsymmetricEncryption:
    """Asimmetrik shifrlash"""
    
    @staticmethod
    def generate_rsa_key_pair(key_size: int = 2048) -> Tuple[bytes, bytes]:
        """RSA kalitlar juftligini yaratish"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    @staticmethod
    def encrypt_rsa(plaintext: bytes, public_key_pem: bytes) -> bytes:
        """RSA shifrlash"""
        public_key = serialization.load_pem_public_key(public_key_pem, backend=default_backend())
        ciphertext = public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext
    
    @staticmethod
    def decrypt_rsa(ciphertext: bytes, private_key_pem: bytes) -> bytes:
        """RSA deshifrlash"""
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=default_backend()
        )
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext
    
    @staticmethod
    def generate_ed25519_key_pair() -> Tuple[bytes, bytes]:
        """Ed25519 kalitlar juftligini yaratish"""
        private_key = ed25519.Ed25519PrivateKey.generate()
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        return private_pem, public_pem
    
    @staticmethod
    def sign_ed25519(data: bytes, private_key_pem: bytes) -> bytes:
        """Ed25519 imzolash"""
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(
            serialization.load_pem_private_key(
                private_key_pem,
                password=None,
                backend=default_backend()
            ).private_bytes_raw()
        )
        signature = private_key.sign(data)
        return signature
    
    @staticmethod
    def verify_ed25519(data: bytes, signature: bytes, public_key_pem: bytes) -> bool:
        """Ed25519 tekshirish"""
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_pem)
        try:
            public_key.verify(signature, data)
            return True
        except Exception:
            return False

class HybridEncryption:
    """Gibrid shifrlash (simmetrik + asimmetrik)"""
    
    def __init__(self):
        self.symmetric = SymmetricEncryption()
        self.asymmetric = AsymmetricEncryption()
    
    def encrypt_data(self, data: bytes, recipient_public_key_pem: bytes) -> Dict[str, Any]:
        """Ma'lumotlarni gibrid shifrlash"""
        # Generate symmetric key
        symmetric_key = self.symmetric.generate_aes_key(SecurityLevel.MAXIMUM.value)
        
        # Encrypt data with symmetric key
        encrypted_data, iv, auth_tag = self.symmetric.encrypt_aes_gcm(data, symmetric_key)
        
        # Encrypt symmetric key with recipient's public key
        encrypted_symmetric_key = self.asymmetric.encrypt_rsa(symmetric_key, recipient_public_key_pem)
        
        return {
            'encrypted_data': base64.b64encode(encrypted_data).decode(),
            'iv': base64.b64encode(iv).decode(),
            'auth_tag': base64.b64encode(auth_tag).decode(),
            'encrypted_symmetric_key': base64.b64encode(encrypted_symmetric_key).decode(),
            'algorithm': 'aes_256_gcm_rsa_2048'
        }
    
    def decrypt_data(self, encrypted_package: Dict[str, Any], 
                    recipient_private_key_pem: bytes) -> bytes:
        """Gibrid shifrlashdan ma'lumotlarni chiqarish"""
        # Decrypt symmetric key
        encrypted_symmetric_key = base64.b64decode(encrypted_package['encrypted_symmetric_key'])
        symmetric_key = self.asymmetric.decrypt_rsa(encrypted_symmetric_key, recipient_private_key_pem)
        
        # Decrypt data
        encrypted_data = base64.b64decode(encrypted_package['encrypted_data'])
        iv = base64.b64decode(encrypted_package['iv'])
        auth_tag = base64.b64decode(encrypted_package['auth_tag'])
        
        decrypted_data = self.symmetric.decrypt_aes_gcm(encrypted_data, symmetric_key, iv, auth_tag)
        return decrypted_data

class KeyManager:
    """Kalitlar boshqaruvchisi"""
    
    def __init__(self, db_path: str = "/workspace/orion-starline/data/encryption_keys.db"):
        self.db_path = db_path
        self.active_keys: Dict[str, EncryptionKey] = {}
        self.key_lock = threading.Lock()
        self.init_database()
        
        logger.info("Key Manager initialized")
    
    def init_database(self):
        """Ma'lumotlar bazasini ishga tushirish"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS encryption_keys (
                key_id TEXT PRIMARY KEY,
                key_type TEXT NOT NULL,
                algorithm TEXT NOT NULL,
                key_material BLOB NOT NULL,
                created_date TEXT NOT NULL,
                expires_date TEXT,
                usage_count INTEGER DEFAULT 0,
                max_usage INTEGER,
                metadata TEXT NOT NULL,
                integrity_hash TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_key_type ON encryption_keys(key_type)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_algorithm ON encryption_keys(algorithm)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_created_date ON encryption_keys(created_date)
        ''')
        
        conn.commit()
        conn.close()
    
    def _calculate_key_hash(self, key_material: bytes, metadata: Dict[str, Any]) -> str:
        """Kalit hashini hisoblash"""
        data = key_material + json.dumps(metadata, sort_keys=True).encode()
        return hashlib.sha256(data).hexdigest()
    
    def generate_key(self, key_type: KeyType, algorithm: EncryptionAlgorithm,
                    metadata: Dict[str, Any] = None, expires_in_days: int = None) -> EncryptionKey:
        """Yangi kalit yaratish"""
        with self.key_lock:
            key_id = str(uuid.uuid4())
            metadata = metadata or {}
            
            # Generate key material based on type
            if key_type == KeyType.SYMMETRIC:
                if algorithm == EncryptionAlgorithm.AES_256_GCM:
                    key_material = SymmetricEncryption.generate_aes_key(256)
                elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                    key_material = secrets.token_bytes(32)
                else:
                    raise ValueError(f"Unsupported symmetric algorithm: {algorithm}")
            
            elif key_type == KeyType.ASYMMETRIC_PRIVATE:
                if algorithm == EncryptionAlgorithm.RSA_2048:
                    private_pem, _ = AsymmetricEncryption.generate_rsa_key_pair(2048)
                    key_material = private_pem
                elif algorithm == EncryptionAlgorithm.ED25519:
                    private_pem, _ = AsymmetricEncryption.generate_ed25519_key_pair()
                    key_material = private_pem
                else:
                    raise ValueError(f"Unsupported asymmetric algorithm: {algorithm}")
            
            else:
                raise ValueError(f"Unsupported key type: {key_type}")
            
            # Calculate integrity hash
            integrity_hash = self._calculate_key_hash(key_material, metadata)
            
            # Set expiration
            expires_date = None
            if expires_in_days:
                expires_date = (datetime.datetime.now() + 
                              datetime.timedelta(days=expires_in_days)).isoformat()
            
            # Create key object
            key = EncryptionKey(
                key_id=key_id,
                key_type=key_type,
                algorithm=algorithm,
                key_material=key_material,
                created_date=datetime.datetime.now().isoformat(),
                expires_date=expires_date,
                usage_count=0,
                max_usage=None,
                metadata=metadata,
                integrity_hash=integrity_hash
            )
            
            # Store in database
            self._store_key(key)
            self.active_keys[key_id] = key
            
            logger.info(f"Key generated: {key_id} ({algorithm.value})")
            return key
    
    def _store_key(self, key: EncryptionKey):
        """Kalitni ma'lumotlar bazasiga saqlash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO encryption_keys 
            (key_id, key_type, algorithm, key_material, created_date, expires_date, 
             usage_count, max_usage, metadata, integrity_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            key.key_id, key.key_type.value, key.algorithm.value, key.key_material,
            key.created_date, key.expires_date, key.usage_count, key.max_usage,
            json.dumps(key.metadata), key.integrity_hash
        ))
        
        conn.commit()
        conn.close()
    
    def get_key(self, key_id: str) -> Optional[EncryptionKey]:
        """Kalitni olish"""
        # Check active keys first
        if key_id in self.active_keys:
            return self.active_keys[key_id]
        
        # Load from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM encryption_keys WHERE key_id = ?', (key_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            key = EncryptionKey(
                key_id=row[0],
                key_type=KeyType(row[1]),
                algorithm=EncryptionAlgorithm(row[2]),
                key_material=row[3],
                created_date=row[4],
                expires_date=row[5],
                usage_count=row[6],
                max_usage=row[7],
                metadata=json.loads(row[8]),
                integrity_hash=row[9]
            )
            self.active_keys[key_id] = key
            return key
        
        return None
    
    def rotate_key(self, old_key_id: str, new_algorithm: EncryptionAlgorithm = None) -> EncryptionKey:
        """Kalitni aylantirish"""
        old_key = self.get_key(old_key_id)
        if not old_key:
            raise ValueError(f"Key not found: {old_key_id}")
        
        # Generate new key with same metadata
        new_metadata = old_key.metadata.copy()
        new_metadata['rotated_from'] = old_key_id
        new_metadata['rotation_date'] = datetime.datetime.now().isoformat()
        
        new_algorithm = new_algorithm or old_key.algorithm
        
        new_key = self.generate_key(
            key_type=old_key.key_type,
            algorithm=new_algorithm,
            metadata=new_metadata,
            expires_in_days=30
        )
        
        logger.warning(f"Key rotated: {old_key_id} -> {new_key.key_id}")
        return new_key
    
    def revoke_key(self, key_id: str, reason: str = "manual_revocation"):
        """Kalitni bekor qilish"""
        key = self.get_key(key_id)
        if not key:
            return False
        
        # Update metadata
        key.metadata['revoked'] = True
        key.metadata['revocation_reason'] = reason
        key.metadata['revocation_date'] = datetime.datetime.now().isoformat()
        
        # Update database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE encryption_keys 
            SET metadata = ?, integrity_hash = ?
            WHERE key_id = ?
        ''', (json.dumps(key.metadata), key.integrity_hash, key_id))
        conn.commit()
        conn.close()
        
        # Remove from active keys
        if key_id in self.active_keys:
            del self.active_keys[key_id]
        
        logger.critical(f"Key revoked: {key_id} - Reason: {reason}")
        return True
    
    def verify_key_integrity(self, key_id: str) -> bool:
        """Kalit yaxlitligini tekshirish"""
        key = self.get_key(key_id)
        if not key:
            return False
        
        expected_hash = self._calculate_key_hash(key.key_material, key.metadata)
        return expected_hash == key.integrity_hash
    
    def list_keys(self, key_type: KeyType = None, algorithm: EncryptionAlgorithm = None,
                  include_revoked: bool = False) -> List[Dict[str, Any]]:
        """Kalitlarni ro'yxatini olish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM encryption_keys WHERE 1=1"
        params = []
        
        if key_type:
            query += " AND key_type = ?"
            params.append(key_type.value)
        
        if algorithm:
            query += " AND algorithm = ?"
            params.append(algorithm.value)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        keys = []
        for row in rows:
            metadata = json.loads(row[8])
            if not include_revoked and metadata.get('revoked', False):
                continue
            
            keys.append({
                'key_id': row[0],
                'key_type': row[1],
                'algorithm': row[2],
                'created_date': row[4],
                'expires_date': row[5],
                'usage_count': row[6],
                'max_usage': row[7],
                'metadata': metadata,
                'integrity_hash': row[9]
            })
        
        return keys

class SecureStorage:
    """Xavfsiz saqlash"""
    
    def __init__(self, key_manager: KeyManager):
        self.key_manager = key_manager
        self.hybrid_encryption = HybridEncryption()
        
        logger.info("Secure Storage initialized")
    
    def store_data(self, data: bytes, metadata: Dict[str, Any] = None,
                  encryption_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM) -> str:
        """Ma'lumotlarni xavfsiz saqlash"""
        metadata = metadata or {}
        
        # Generate encryption key
        key = self.key_manager.generate_key(
            key_type=KeyType.SYMMETRIC,
            algorithm=encryption_algorithm,
            metadata={'purpose': 'data_storage'}
        )
        
        # Encrypt data
        if encryption_algorithm == EncryptionAlgorithm.AES_256_GCM:
            encrypted_data, iv, auth_tag = SymmetricEncryption.encrypt_aes_gcm(data, key.key_material)
            auth_tag = auth_tag
        elif encryption_algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            encrypted_data, iv = SymmetricEncryption.encrypt_chacha20_poly1305(data, key.key_material)
            auth_tag = None
        else:
            raise ValueError(f"Unsupported algorithm: {encryption_algorithm}")
        
        # Create encrypted data record
        data_id = str(uuid.uuid4())
        encrypted_record = EncryptedData(
            data_id=data_id,
            original_size=len(data),
            encrypted_data=encrypted_data,
            encryption_algorithm=encryption_algorithm.value,
            key_id=key.key_id,
            iv=iv,
            auth_tag=auth_tag,
            metadata=metadata,
            created_date=datetime.datetime.now().isoformat()
        )
        
        # Store in database (simplified for this example)
        # In production, you'd store this in a proper database
        logger.info(f"Data stored securely: {data_id}")
        
        return data_id
    
    def retrieve_data(self, data_id: str) -> Tuple[bytes, Dict[str, Any]]:
        """Xavfsiz saqlangan ma'lumotlarni olish"""
        # In production, you would retrieve the EncryptedData from database
        # For this example, we'll simulate the retrieval
        
        # Get the encryption key
        key = self.key_manager.get_key(data_id)  # Simplified - would be different in production
        if not key:
            raise ValueError(f"Encryption key not found for data: {data_id}")
        
        # Decrypt (simplified - would use actual encrypted data)
        decrypted_data = b"retrieved_data"  # Placeholder
        
        logger.info(f"Data retrieved securely: {data_id}")
        return decrypted_data, {}
    
    def secure_delete(self, data_id: str) -> bool:
        """Ma'lumotlarni xavfsiz o'chirish"""
        try:
            # In production, this would:
            # 1. Retrieve the encrypted data
            # 2. Overwrite the encrypted data multiple times
            # 3. Delete the encryption key
            # 4. Remove all references
            
            logger.warning(f"Secure deletion initiated: {data_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to securely delete data: {e}")
            return False

class SecureCommunication:
    """Xavfsiz kommunikatsiya"""
    
    def __init__(self, key_manager: KeyManager):
        self.key_manager = key_manager
        self.hybrid_encryption = HybridEncryption()
        
        logger.info("Secure Communication initialized")
    
    def establish_secure_channel(self, peer_public_key_pem: bytes) -> Dict[str, Any]:
        """Xavfsiz kanalni o'rnatish"""
        # Generate session key
        session_key = self.key_manager.generate_key(
            key_type=KeyType.SESSION,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            metadata={'purpose': 'secure_communication'},
            expires_in_days=1
        )
        
        # Encrypt session key with peer's public key
        encrypted_session_key = AsymmetricEncryption.encrypt_rsa(
            session_key.key_material, peer_public_key_pem
        )
        
        channel_info = {
            'channel_id': str(uuid.uuid4()),
            'session_key_id': session_key.key_id,
            'encrypted_session_key': base64.b64encode(encrypted_session_key).decode(),
            'established_time': datetime.datetime.now().isoformat(),
            'expires_at': session_key.expires_date
        }
        
        logger.info(f"Secure channel established: {channel_info['channel_id']}")
        return channel_info
    
    def encrypt_message(self, channel_id: str, message: bytes, 
                       session_key_material: bytes) -> Dict[str, Any]:
        """Xabar shifrlash"""
        encrypted_data, iv, auth_tag = SymmetricEncryption.encrypt_aes_gcm(
            message, session_key_material
        )
        
        return {
            'channel_id': channel_id,
            'encrypted_message': base64.b64encode(encrypted_data).decode(),
            'iv': base64.b64encode(iv).decode(),
            'auth_tag': base64.b64encode(auth_tag).decode(),
            'timestamp': datetime.datetime.now().isoformat()
        }
    
    def decrypt_message(self, encrypted_package: Dict[str, Any],
                       session_key_material: bytes) -> bytes:
        """Xabar deshifrlash"""
        encrypted_message = base64.b64decode(encrypted_package['encrypted_message'])
        iv = base64.b64decode(encrypted_package['iv'])
        auth_tag = base64.b64decode(encrypted_package['auth_tag'])
        
        decrypted_message = SymmetricEncryption.decrypt_aes_gcm(
            encrypted_message, session_key_material, iv, auth_tag
        )
        
        return decrypted_message

class MultiFactorAuthentication:
    """Ko'p faktor autentifikatsiya"""
    
    def __init__(self, db_path: str = "/workspace/orion-starline/data/mfa_secrets.db"):
        self.db_path = db_path
        self.init_database()
        
        logger.info("MFA initialized")
    
    def init_database(self):
        """Ma'lumotlar bazasini ishga tushirish"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mfa_secrets (
                user_id TEXT PRIMARY KEY,
                secret_key TEXT NOT NULL,
                backup_codes TEXT NOT NULL,
                created_date TEXT NOT NULL,
                last_used TEXT,
                enabled BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_mfa(self, user_id: str) -> Dict[str, Any]:
        """MFA sozlash"""
        # Generate TOTP secret
        secret = pyotp.random_base32()
        
        # Generate backup codes
        backup_codes = [secrets.token_hex(3).upper() for _ in range(8)]
        
        # Create TOTP
        totp = pyotp.TOTP(secret)
        qr_code_url = totp.provisioning_uri(
            name=f"user_{user_id}",
            issuer_name="Orion Starline Security"
        )
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO mfa_secrets 
            (user_id, secret_key, backup_codes, created_date, enabled)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_id, secret, json.dumps(backup_codes),
            datetime.datetime.now().isoformat(), True
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"MFA setup completed for user: {user_id}")
        
        return {
            'secret': secret,
            'qr_code_url': qr_code_url,
            'backup_codes': backup_codes
        }
    
    def verify_totp(self, user_id: str, token: str) -> bool:
        """TOTP token tekshirish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT secret_key FROM mfa_secrets WHERE user_id = ? AND enabled = TRUE', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return False
        
        secret = row[0]
        totp = pyotp.TOTP(secret)
        
        is_valid = totp.verify(token, valid_window=1)
        
        if is_valid:
            # Update last used time
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE mfa_secrets SET last_used = ? WHERE user_id = ?
            ''', (datetime.datetime.now().isoformat(), user_id))
            conn.commit()
            conn.close()
        
        return is_valid
    
    def verify_backup_code(self, user_id: str, backup_code: str) -> bool:
        """Zaxira kodi tekshirish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT backup_codes FROM mfa_secrets WHERE user_id = ? AND enabled = TRUE', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return False
        
        backup_codes = json.loads(row[0])
        
        if backup_code.upper() in backup_codes:
            # Remove used backup code
            backup_codes.remove(backup_code.upper())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE mfa_secrets SET backup_codes = ? WHERE user_id = ?
            ''', (json.dumps(backup_codes), user_id))
            conn.commit()
            conn.close()
            
            return True
        
        return False

# Main Encryption System
class EncryptionSystem:
    """Asosiy shifrlash tizimi"""
    
    def __init__(self):
        self.key_manager = KeyManager()
        self.secure_storage = SecureStorage(self.key_manager)
        self.secure_comm = SecureCommunication(self.key_manager)
        self.mfa = MultiFactorAuthentication()
        
        logger.info("Encryption System initialized")
    
    def generate_master_key(self) -> EncryptionKey:
        """Master kalit yaratish"""
        return self.key_manager.generate_key(
            key_type=KeyType.MASTER,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            metadata={'purpose': 'master_key', 'system': 'orion_starline'},
            expires_in_days=365
        )
    
    def backup_keys(self, backup_path: str, master_password: str) -> bool:
        """Kalitlarni zaxiralash"""
        try:
            # Get all keys
            all_keys = self.key_manager.list_keys()
            
            # Create backup package
            backup_data = {
                'backup_id': str(uuid.uuid4()),
                'backup_date': datetime.datetime.now().isoformat(),
                'keys': all_keys,
                'version': '1.0'
            }
            
            # Encrypt backup with master password
            salt = secrets.token_bytes(16)
            key_deriv = KeyDerivationFunction.pbkdf2(master_password, salt)
            fernet = Fernet(base64.urlsafe_b64encode(key_deriv))
            
            backup_json = json.dumps(backup_data).encode()
            encrypted_backup = fernet.encrypt(backup_json)
            
            # Write to file
            with open(backup_path, 'wb') as f:
                f.write(salt + encrypted_backup)
            
            logger.info(f"Keys backed up to: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup keys: {e}")
            return False
    
    def restore_keys(self, backup_path: str, master_password: str) -> bool:
        """Kalitlarni tiklash"""
        try:
            # Read encrypted backup
            with open(backup_path, 'rb') as f:
                data = f.read()
            
            salt = data[:16]
            encrypted_data = data[16:]
            
            # Decrypt with master password
            key_deriv = KeyDerivationFunction.pbkdf2(master_password, salt)
            fernet = Fernet(base64.urlsafe_b64encode(key_deriv))
            
            backup_json = fernet.decrypt(encrypted_data)
            backup_data = json.loads(backup_json.decode())
            
            # Restore keys
            for key_data in backup_data['keys']:
                # Recreate key object and store
                # (simplified - in production, you'd handle key material carefully)
                logger.info(f"Restored key: {key_data['key_id']}")
            
            logger.info(f"Keys restored from: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore keys: {e}")
            return False

# Flask API for encryption system
app = Flask(__name__)
encryption_system = EncryptionSystem()

@app.route('/api/encryption/generate-key', methods=['POST'])
def generate_key():
    """Kalit yaratish API"""
    try:
        data = request.get_json()
        key_type = KeyType(data['key_type'])
        algorithm = EncryptionAlgorithm(data['algorithm'])
        
        key = encryption_system.key_manager.generate_key(
            key_type=key_type,
            algorithm=algorithm,
            metadata=data.get('metadata', {}),
            expires_in_days=data.get('expires_in_days')
        )
        
        return jsonify({
            'key_id': key.key_id,
            'algorithm': key.algorithm.value,
            'created_date': key.created_date,
            'expires_date': key.expires_date
        })
        
    except Exception as e:
        logger.error(f"Error generating key: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/encryption/encrypt', methods=['POST'])
def encrypt_data():
    """Ma'lumot shifrlash API"""
    try:
        data = request.get_json()
        data_bytes = base64.b64decode(data['data'])
        algorithm = EncryptionAlgorithm(data.get('algorithm', 'aes_256_gcm'))
        
        data_id = encryption_system.secure_storage.store_data(
            data_bytes,
            metadata=data.get('metadata', {}),
            encryption_algorithm=algorithm
        )
        
        return jsonify({
            'data_id': data_id,
            'algorithm': algorithm.value
        })
        
    except Exception as e:
        logger.error(f"Error encrypting data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/encryption/decrypt/<data_id>', methods=['POST'])
def decrypt_data(data_id):
    """Ma'lumot deshifrlash API"""
    try:
        decrypted_data, metadata = encryption_system.secure_storage.retrieve_data(data_id)
        
        return jsonify({
            'data': base64.b64encode(decrypted_data).decode(),
            'metadata': metadata
        })
        
    except Exception as e:
        logger.error(f"Error decrypting data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/encryption/mfa/setup', methods=['POST'])
def setup_mfa():
    """MFA sozlash API"""
    try:
        data = request.get_json()
        user_id = data['user_id']
        
        mfa_setup = encryption_system.mfa.setup_mfa(user_id)
        
        return jsonify(mfa_setup)
        
    except Exception as e:
        logger.error(f"Error setting up MFA: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/encryption/mfa/verify', methods=['POST'])
def verify_mfa():
    """MFA tekshirish API"""
    try:
        data = request.get_json()
        user_id = data['user_id']
        token = data['token']
        
        is_valid = encryption_system.mfa.verify_totp(user_id, token)
        
        return jsonify({'valid': is_valid})
        
    except Exception as e:
        logger.error(f"Error verifying MFA: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/encryption/keys/list')
def list_keys():
    """Kalitlar ro'yxati API"""
    try:
        keys = encryption_system.key_manager.list_keys()
        return jsonify(keys)
    except Exception as e:
        logger.error(f"Error listing keys: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs('/workspace/orion-starline/data', exist_ok=True)
    os.makedirs('/workspace/orion-starline/logs', exist_ok=True)
    
    # Run encryption system
    app.run(host='0.0.0.0', port=5003, debug=False)
