"""
AI Trading System - Error Handler
Global xatolarni boshqarish va javob qaytarish
"""

import logging
import traceback
from typing import Any, Dict, Optional
from datetime import datetime
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import uuid

from ..models.schemas import BaseResponse
from ..config.settings import settings

logger = logging.getLogger(__name__)

class ErrorCode:
    """Xato kodlari"""
    
    # Authentication errors
    AUTH_001 = "INVALID_CREDENTIALS"
    AUTH_002 = "TOKEN_EXPIRED"
    AUTH_003 = "INSUFFICIENT_PERMISSIONS"
    AUTH_004 = "USER_NOT_FOUND"
    AUTH_005 = "ACCOUNT_DISABLED"
    
    # Validation errors
    VAL_001 = "VALIDATION_ERROR"
    VAL_002 = "MISSING_REQUIRED_FIELD"
    VAL_003 = "INVALID_FORMAT"
    VAL_004 = "VALUE_OUT_OF_RANGE"
    
    # Business logic errors
    BUS_001 = "INSUFFICIENT_BALANCE"
    BUS_002 = "TRADE_EXECUTION_FAILED"
    BUS_003 = "RISK_LIMIT_EXCEEDED"
    BUS_004 = "MARKET_CLOSED"
    BUS_005 = "STRATEGY_NOT_AVAILABLE"
    
    # System errors
    SYS_001 = "DATABASE_ERROR"
    SYS_002 = "EXTERNAL_SERVICE_ERROR"
    SYS_003 = "MEMORY_LIMIT_EXCEEDED"
    SYS_004 = "TIMEOUT_ERROR"
    SYS_005 = "SERVICE_UNAVAILABLE"
    
    # Data errors
    DATA_001 = "RECORD_NOT_FOUND"
    DATA_002 = "DUPLICATE_RECORD"
    DATA_003 = "DATA_CORRUPTION"
    DATA_004 = "INVALID_DATA_FORMAT"

class ErrorMessage:
    """Xato xabarlari"""
    
    messages = {
        ErrorCode.AUTH_001: "Noto'g'ri foydalanuvchi nomi yoki parol",
        ErrorCode.AUTH_002: "Token vaqti tugagan",
        ErrorCode.AUTH_003: "Bu amaliyot uchun yetarli huquqlar yo'q",
        ErrorCode.AUTH_004: "Foydalanuvchi topilmadi",
        ErrorCode.AUTH_005: "Hisob faol emas",
        
        ErrorCode.VAL_001: "Ma'lumot validatsiyasi xatosi",
        ErrorCode.VAL_002: "Majburiy maydonlar to'ldirilmagan",
        ErrorCode.VAL_003: "Ma'lumot formati noto'g'ri",
        ErrorCode.VAL_004: "Qiymat ruxsat etilgan diapazonda emas",
        
        ErrorCode.BUS_001: "Yetarli mablag' mavjud emas",
        ErrorCode.BUS_002: "Savdo bajarilmadi",
        ErrorCode.BUS_003: "Risk limiti oshib ketdi",
        ErrorCode.BUS_004: "Bozor yopiq",
        ErrorCode.BUS_005: "Strategiya mavjud emas",
        
        ErrorCode.SYS_001: "Baza bilan bog'lanishda xato",
        ErrorCode.SYS_002: "Tashqi xizmat bilan bog'lanishda xato",
        ErrorCode.SYS_003: "Xotira limiti oshib ketdi",
        ErrorCode.SYS_004: "So'rov vaqti tugadi",
        ErrorCode.SYS_005: "Xizmat hozircha mavjud emas",
        
        ErrorCode.DATA_001: "Yozuv topilmadi",
        ErrorCode.DATA_002: "Bu ma'lumot allaqachon mavjud",
        ErrorCode.DATA_003: "Ma'lumot buzilgan",
        ErrorCode.DATA_004: "Ma'lumot formati noto'g'ri"
    }
    
    @classmethod
    def get_message(cls, code: str, default: str = "Noma'lum xato") -> str:
        """Xato xabarini olish"""
        return cls.messages.get(code, default)

class ErrorDetail:
    """Xato tafsilotlari"""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.message = message
        self.field = field
        self.value = value
        self.context = context or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Xato tafsilotlarini dictionary ga o'tkazish"""
        result = {
            "error_code": self.error_code,
            "message": self.message
        }
        
        if self.field:
            result["field"] = self.field
        
        if self.value is not None:
            result["value"] = str(self.value)
        
        if self.context:
            result["context"] = self.context
        
        return result

class GlobalExceptionHandler:
    """Global xato boshqaruvchisi"""
    
    def __init__(self):
        self.error_id = str(uuid.uuid4())
    
    def handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Xatoni boshqarish"""
        
        # Log the error
        self._log_error(request, exc)
        
        # Create error response
        error_response = self._create_error_response(request, exc)
        
        # Determine HTTP status code
        status_code = self._get_http_status_code(exc)
        
        return JSONResponse(
            status_code=status_code,
            content=error_response
        )
    
    def _log_error(self, request: Request, exc: Exception):
        """Xatoni loglash"""
        error_details = {
            "error_id": self.error_id,
            "url": str(request.url),
            "method": request.method,
            "user_agent": request.headers.get("user-agent"),
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add user info if available
        try:
            from ..auth.auth_handler import get_current_user
            # This will be called in request context
        except:
            pass
        
        logger.error(f"Xato ID: {self.error_id}", extra=error_details)
    
    def _create_error_response(self, request: Request, exc: Exception) -> Dict[str, Any]:
        """Xato javobini yaratish"""
        
        # Handle different exception types
        if isinstance(exc, HTTPException):
            return self._handle_http_exception(exc)
        elif isinstance(exc, RequestValidationError):
            return self._handle_validation_error(exc)
        elif isinstance(exc, ValidationError):
            return self._handle_pydantic_validation_error(exc)
        elif isinstance(exc, ValueError):
            return self._handle_value_error(exc)
        elif isinstance(exc, TimeoutError):
            return self._handle_timeout_error(exc)
        elif isinstance(exc, ConnectionError):
            return self._handle_connection_error(exc)
        elif isinstance(exc, PermissionError):
            return self._handle_permission_error(exc)
        elif isinstance(exc, FileNotFoundError):
            return self._handle_file_not_found_error(exc)
        else:
            return self._handle_generic_error(exc)
    
    def _handle_http_exception(self, exc: HTTPException) -> Dict[str, Any]:
        """HTTPException ni boshqarish"""
        return self._create_error_response_dict(
            error_code="HTTP_ERROR",
            message=exc.detail,
            status_code=exc.status_code,
            field=None,
            context={"headers": dict(exc.headers) if exc.headers else {}}
        )
    
    def _handle_validation_error(self, exc: RequestValidationError) -> Dict[str, Any]:
        """RequestValidationError ni boshqarish"""
        error_details = []
        
        for error in exc.errors():
            field = ".".join(str(x) for x in error["loc"] if isinstance(x, str))
            error_type = error.get("type", "validation_error")
            
            if error_type == "value_error.missing":
                error_code = ErrorCode.VAL_002
                message = f"{field} maydoni talab qilinadi"
            elif error_type == "value_error.any_str.min_length":
                error_code = ErrorCode.VAL_004
                message = f"{field} kamida {error['ctx']['limit_value']} ta belgidan iborat bo'lishi kerak"
            elif error_type == "value_error.any_str.max_length":
                error_code = ErrorCode.VAL_004
                message = f"{field} ko'pi bilan {error['ctx']['limit_value']} ta belgidan iborat bo'lishi kerak"
            elif error_type == "value_error.number.lt":
                error_code = ErrorCode.VAL_004
                message = f"{field} {error['ctx']['limit_value']} dan kichik bo'lishi kerak"
            elif error_type == "value_error.number.gt":
                error_code = ErrorCode.VAL_004
                message = f"{field} {error['ctx']['limit_value']} dan katta bo'lishi kerak"
            else:
                error_code = ErrorCode.VAL_001
                message = error.get("msg", "Validatsiya xatosi")
            
            error_details.append(ErrorDetail(
                error_code=error_code,
                message=message,
                field=field,
                value=error.get("input")
            ))
        
        return self._create_error_response_dict(
            error_code=ErrorCode.VAL_001,
            message="So'rov ma'lumotlarida xato",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_details=[detail.to_dict() for detail in error_details]
        )
    
    def _handle_pydantic_validation_error(self, exc: ValidationError) -> Dict[str, Any]:
        """Pydantic ValidationError ni boshqarish"""
        return self._handle_validation_error(RequestValidationError(exc.errors()))
    
    def _handle_value_error(self, exc: ValueError) -> Dict[str, Any]:
        """ValueError ni boshqarish"""
        message = str(exc).lower()
        
        if "not found" in message:
            error_code = ErrorCode.DATA_001
            http_status = status.HTTP_404_NOT_FOUND
        elif "already exists" in message or "duplicate" in message:
            error_code = ErrorCode.DATA_002
            http_status = status.HTTP_409_CONFLICT
        elif "invalid" in message:
            error_code = ErrorCode.VAL_003
            http_status = status.HTTP_400_BAD_REQUEST
        else:
            error_code = ErrorCode.VAL_001
            http_status = status.HTTP_400_BAD_REQUEST
        
        return self._create_error_response_dict(
            error_code=error_code,
            message=str(exc),
            status_code=http_status
        )
    
    def _handle_timeout_error(self, exc: TimeoutError) -> Dict[str, Any]:
        """TimeoutError ni boshqarish"""
        return self._create_error_response_dict(
            error_code=ErrorCode.SYS_004,
            message="So'rov vaqti tugadi",
            status_code=status.HTTP_408_REQUEST_TIMEOUT
        )
    
    def _handle_connection_error(self, exc: ConnectionError) -> Dict[str, Any]:
        """ConnectionError ni boshqarish"""
        return self._create_error_response_dict(
            error_code=ErrorCode.SYS_002,
            message="Bog'lanishda xato yuz berdi",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    def _handle_permission_error(self, exc: PermissionError) -> Dict[str, Any]:
        """PermissionError ni boshqarish"""
        return self._create_error_response_dict(
            error_code=ErrorCode.AUTH_003,
            message="Bu amaliyot uchun ruxsat yo'q",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    def _handle_file_not_found_error(self, exc: FileNotFoundError) -> Dict[str, Any]:
        """FileNotFoundError ni boshqarish"""
        return self._create_error_response_dict(
            error_code=ErrorCode.DATA_001,
            message="Fayl topilmadi",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    def _handle_generic_error(self, exc: Exception) -> Dict[str, Any]:
        """Boshqa xatolarni boshqarish"""
        return self._create_error_response_dict(
            error_code=ErrorCode.SYS_005,
            message="Ichki server xatosi yuz berdi",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    def _create_error_response_dict(
        self,
        error_code: str,
        message: str,
        status_code: int,
        field: Optional[str] = None,
        error_details: Optional[list] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Xato javobini yaratish"""
        
        response_dict = {
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
                "error_id": self.error_id,
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": getattr(self, 'request_id', None)
            }
        }
        
        if error_details:
            response_dict["error"]["details"] = error_details
        
        if context:
            response_dict["error"]["context"] = context
        
        if field:
            response_dict["error"]["field"] = field
        
        return response_dict
    
    def _get_http_status_code(self, exc: Exception) -> int:
        """HTTP status kodini aniqlash"""
        if isinstance(exc, HTTPException):
            return exc.status_code
        elif isinstance(exc, RequestValidationError):
            return status.HTTP_422_UNPROCESSABLE_ENTITY
        elif isinstance(exc, ValidationError):
            return status.HTTP_422_UNPROCESSABLE_ENTITY
        elif isinstance(exc, ValueError):
            return status.HTTP_400_BAD_REQUEST
        elif isinstance(exc, TimeoutError):
            return status.HTTP_408_REQUEST_TIMEOUT
        elif isinstance(exc, ConnectionError):
            return status.HTTP_503_SERVICE_UNAVAILABLE
        elif isinstance(exc, PermissionError):
            return status.HTTP_403_FORBIDDEN
        elif isinstance(exc, FileNotFoundError):
            return status.HTTP_404_NOT_FOUND
        else:
            return status.HTTP_500_INTERNAL_SERVER_ERROR

class BusinessLogicError(Exception):
    """Biznes mantiq xatosi"""
    
    def __init__(self, error_code: str, message: str = None, context: Dict[str, Any] = None):
        self.error_code = error_code
        self.message = message or ErrorMessage.get_message(error_code)
        self.context = context or {}
        super().__init__(self.message)

class ValidationFieldError(Exception):
    """Field validatsiya xatosi"""
    
    def __init__(self, field: str, error_code: str, message: str = None, value: Any = None):
        self.field = field
        self.error_code = error_code
        self.message = message or ErrorMessage.get_message(error_code)
        self.value = value
        super().__init__(self.message)

def create_error_response(
    error_code: str,
    message: str = None,
    field: str = None,
    value: Any = None,
    context: Dict[str, Any] = None,
    status_code: int = 400
) -> Dict[str, Any]:
    """Xato javobini yaratish"""
    if not message:
        message = ErrorMessage.get_message(error_code)
    
    response = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "error_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    if field:
        response["error"]["field"] = field
    
    if value is not None:
        response["error"]["value"] = str(value)
    
    if context:
        response["error"]["context"] = context
    
    return response, status_code

def raise_validation_error(field: str, error_code: str, message: str = None, value: Any = None):
    """Validatsiya xatosini ko'tarish"""
    raise ValidationFieldError(field, error_code, message, value)

def raise_business_error(error_code: str, message: str = None, context: Dict[str, Any] = None):
    """Biznes mantiq xatosini ko'tarish"""
    raise BusinessLogicError(error_code, message, context)

# Middleware for request tracking
async def request_tracking_middleware(request: Request, call_next):
    """So'rovni kuzatish middleware"""
    from ..auth.auth_handler import get_current_user
    
    # Add request ID
    request.state.request_id = str(uuid.uuid4())
    
    # Try to get current user
    try:
        # This might fail for public endpoints
        user = await get_current_user()
        request.state.current_user = user
    except:
        request.state.current_user = None
    
    # Process request
    response = await call_next(request)
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request.state.request_id
    
    return response

# Export
__all__ = [
    "ErrorCode",
    "ErrorMessage", 
    "ErrorDetail",
    "GlobalExceptionHandler",
    "BusinessLogicError",
    "ValidationFieldError",
    "create_error_response",
    "raise_validation_error",
    "raise_business_error",
    "request_tracking_middleware"
]