"""
AI Trading System - File Operations
Fayl operatsiyalari uchun yordamchi funksiyalar
"""

import os
import mimetypes
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from pathlib import Path
import aiofiles
import magic
from fastapi import UploadFile, HTTPException
import uuid

from ..config.settings import settings

class FileValidator:
    """Fayl validatsiya"""
    
    ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
    ALLOWED_DOCUMENT_TYPES = {
        'application/pdf',
        'text/plain',
        'application/json',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
        'text/csv'
    }
    ALLOWED_ARCHIVE_TYPES = {
        'application/zip',
        'application/x-rar-compressed',
        'application/x-tar',
        'application/gzip'
    }
    
    @classmethod
    def validate_file(cls, file: UploadFile) -> Tuple[bool, str]:
        """Faylni validatsiya qilish"""
        if not file.filename:
            return False, "Fayl nomi kerak"
        
        # Check file extension
        extension = Path(file.filename).suffix.lower()
        if extension not in settings.ALLOWED_FILE_EXTENSIONS:
            return False, f"Ruxsat etilmagan fayl turi: {extension}"
        
        # Check file size
        if hasattr(file, 'size') and file.size and file.size > settings.MAX_FILE_SIZE:
            return False, f"Fayl hajmi {settings.MAX_FILE_SIZE} bytes dan katta bo'lishi mumkin emas"
        
        # Check content type
        content_type = file.content_type
        if content_type:
            allowed_types = (
                cls.ALLOWED_IMAGE_TYPES | 
                cls.ALLOWED_DOCUMENT_TYPES | 
                cls.ALLOWED_ARCHIVE_TYPES
            )
            if content_type not in allowed_types:
                return False, f"Ruxsat etilmagan content type: {content_type}"
        
        return True, "OK"
    
    @classmethod
    def get_file_type(cls, file_path: str) -> str:
        """Fayl turini aniqlash"""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or "application/octet-stream"
    
    @classmethod
    def is_image(cls, file_path: str) -> bool:
        """Rasm fayl ekanligini tekshirish"""
        mime_type = cls.get_file_type(file_path)
        return mime_type in cls.ALLOWED_IMAGE_TYPES
    
    @classmethod
    def is_document(cls, file_path: str) -> bool:
        """Hujjat fayl ekanligini tekshirish"""
        mime_type = cls.get_file_type(file_path)
        return mime_type in cls.ALLOWED_DOCUMENT_TYPES

class FileStorage:
    """Fayl saqlash"""
    
    @staticmethod
    def get_upload_path(user_id: str, date: Optional[datetime] = None) -> str:
        """Yuklash yo'lini olish"""
        if not date:
            date = datetime.utcnow()
        
        upload_dir = Path(settings.UPLOAD_PATH) / user_id / date.strftime("%Y%m%d")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        return str(upload_dir)
    
    @staticmethod
    def generate_filename(original_filename: str, user_id: str) -> str:
        """Fayl nomini yaratish"""
        extension = Path(original_filename).suffix
        unique_name = f"{uuid.uuid4().hex}{extension}"
        return unique_name
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """Fayl ma'lumotlarini olish"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {}
        
        stat = file_path.stat()
        return {
            "filename": file_path.name,
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime),
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "extension": file_path.suffix,
            "mime_type": FileValidator.get_file_type(str(file_path))
        }

class FileManager:
    """Fayl boshqaruvchisi"""
    
    def __init__(self):
        self.validator = FileValidator()
        self.storage = FileStorage()
    
    async def save_upload_file(
        self, 
        file: UploadFile, 
        user_id: str, 
        date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Yuklash faylini saqlash"""
        
        # Validate file
        is_valid, error_message = self.validator.validate_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Generate file path
        upload_dir = self.storage.get_upload_path(user_id, date)
        filename = self.storage.generate_filename(file.filename, user_id)
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Get file info
        file_info = self.storage.get_file_info(file_path)
        file_info.update({
            "upload_path": file_path,
            "user_id": user_id,
            "upload_time": datetime.utcnow()
        })
        
        return file_info
    
    async def read_file(self, file_path: str) -> bytes:
        """Fayl o'qish"""
        try:
            async with aiofiles.open(file_path, 'rb') as f:
                return await f.read()
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Fayl topilmadi")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Fayl o'qishda xato: {str(e)}")
    
    async def delete_file(self, file_path: str) -> bool:
        """Faylni o'chirish"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Fayl o'chirishda xato: {str(e)}")
    
    def list_user_files(self, user_id: str, date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Foydalanuvchi fayllar ro'yxati"""
        upload_dir = self.storage.get_upload_path(user_id, date)
        
        files = []
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                file_path = os.path.join(upload_dir, filename)
                if os.path.isfile(file_path):
                    file_info = self.storage.get_file_info(file_path)
                    file_info["user_id"] = user_id
                    file_info["upload_path"] = file_path
                    files.append(file_info)
        
        return sorted(files, key=lambda x: x["modified"], reverse=True)
    
    def get_file_url(self, file_path: str, user_id: str) -> str:
        """Fayl URL ni olish"""
        # This would generate a signed URL in a real implementation
        relative_path = os.path.relpath(file_path, settings.UPLOAD_PATH)
        return f"/api/v1/files/download/{relative_path}"

# File processing utilities
class FileProcessor:
    """Fayl qayta ishlash"""
    
    @staticmethod
    async def process_csv(file_path: str) -> Dict[str, Any]:
        """CSV fayl qayta ishlash"""
        try:
            import pandas as pd
            
            # Read CSV
            df = pd.read_csv(file_path)
            
            return {
                "rows": len(df),
                "columns": list(df.columns),
                "data_types": df.dtypes.astype(str).to_dict(),
                "memory_usage": df.memory_usage(deep=True).sum(),
                "sample_data": df.head().to_dict('records') if not df.empty else []
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"CSV fayl qayta ishlanmadi: {str(e)}")
    
    @staticmethod
    async def process_json(file_path: str) -> Dict[str, Any]:
        """JSON fayl qayta ishlash"""
        try:
            import json
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                "data_type": type(data).__name__,
                "keys": list(data.keys()) if isinstance(data, dict) else None,
                "items_count": len(data) if isinstance(data, (dict, list)) else 1,
                "sample": data[:100] if isinstance(data, list) and len(data) > 100 else data
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"JSON fayl qayta ishlanmadi: {str(e)}")
    
    @staticmethod
    async def process_image(file_path: str) -> Dict[str, Any]:
        """Rasm fayl qayta ishlash"""
        try:
            from PIL import Image
            
            with Image.open(file_path) as img:
                return {
                    "format": img.format,
                    "size": img.size,
                    "mode": img.mode,
                    "has_transparency": img.mode in ('RGBA', 'LA'),
                    "file_size": os.path.getsize(file_path)
                }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Rasm fayl qayta ishlanmadi: {str(e)}")
    
    @classmethod
    async def process_file(cls, file_path: str) -> Dict[str, Any]:
        """Umumiy fayl qayta ishlash"""
        extension = Path(file_path).suffix.lower()
        
        if extension == '.csv':
            return await cls.process_csv(file_path)
        elif extension in ['.json']:
            return await cls.process_json(file_path)
        elif extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return await cls.process_image(file_path)
        else:
            return {
                "message": f"{extension} fayl turi qo'llab-quvvatlanmaydi",
                "file_info": FileStorage.get_file_info(file_path)
            }

# Export
__all__ = [
    "FileValidator",
    "FileStorage", 
    "FileManager",
    "FileProcessor"
]

# Global instance
file_manager = FileManager()