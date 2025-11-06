"""
AI Trading System - Unit Tests for API Components
Boshqa komponentlar uchun unit testlar
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient

# Import modules to test
from utils.cache import CacheManager
from utils.pagination import PaginatedResponse, apply_pagination, SortingHelper
from utils.error_handler import GlobalExceptionHandler, BusinessLogicError, ErrorCode
from utils.file_operations import FileValidator, FileManager
from auth.auth_handler import authenticate_user, create_access_token, verify_token
from models.schemas import AISignal, User, SignalType

class TestCacheManager:
    """Cache Manager testlari"""
    
    @pytest.mark.asyncio
    async def test_cache_initialization(self):
        """Cache manager initialization test"""
        cache = CacheManager()
        await cache.initialize()
        assert cache is not None
    
    @pytest.mark.asyncio 
    async def test_cache_set_get(self):
        """Cache set/get functionality test"""
        cache = CacheManager()
        await cache.initialize()
        
        await cache.set("test_key", "test_value")
        result = await cache.get("test_key")
        
        assert result == "test_value"
    
    @pytest.mark.asyncio
    async def test_cache_delete(self):
        """Cache delete functionality test"""
        cache = CacheManager()
        await cache.initialize()
        
        await cache.set("test_key", "test_value")
        await cache.delete("test_key")
        result = await cache.get("test_key")
        
        assert result is None

class TestPagination:
    """Pagination functionality testlari"""
    
    def test_paginated_response(self):
        """Paginated response creation test"""
        data = [1, 2, 3, 4, 5]
        response = PaginatedResponse(data, page=1, size=2, total=5)
        
        assert response.page == 1
        assert response.size == 2
        assert response.total == 5
        assert response.pages == 3
        assert response.has_next is True
        assert response.has_prev is False
    
    def test_apply_pagination(self):
        """Apply pagination test"""
        data = list(range(1, 11))  # [1, 2, 3, ..., 10]
        paginated_data, pagination = apply_pagination(data, page=2, size=3)
        
        assert len(paginated_data) == 3
        assert paginated_data == [4, 5, 6]
        assert pagination.total == 10
        assert pagination.page == 2
        assert pagination.size == 3
        assert pagination.pages == 4
    
    def test_sorting_helper(self):
        """Sorting helper test"""
        data = [
            {"name": "Charlie", "age": 30},
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 35}
        ]
        
        sorted_data = SortingHelper.sort_dict_list(data, "name", "asc")
        assert sorted_data[0]["name"] == "Alice"
        assert sorted_data[1]["name"] == "Bob"
        assert sorted_data[2]["name"] == "Charlie"

class TestErrorHandler:
    """Error handler testlari"""
    
    def test_business_logic_error(self):
        """Business logic error test"""
        error = BusinessLogicError(ErrorCode.AUTH_001, "Custom message")
        
        assert error.error_code == ErrorCode.AUTH_001
        assert error.message == "Custom message"
    
    def test_global_exception_handler(self):
        """Global exception handler test"""
        handler = GlobalExceptionHandler()
        
        # Create a mock request
        mock_request = MagicMock()
        mock_request.url = MagicMock()
        mock_request.url.__str__ = MagicMock(return_value="http://test.com")
        mock_request.method = "GET"
        mock_request.headers = {}
        
        # Test HTTPException handling
        http_exc = HTTPException(status_code=404, detail="Not found")
        response = handler.handle_exception(mock_request, http_exc)
        
        assert response.status_code == 404

class TestFileOperations:
    """File operations testlari"""
    
    def test_file_validator(self):
        """File validator test"""
        # Create mock upload file
        mock_file = MagicMock()
        mock_file.filename = "test.csv"
        mock_file.size = 1024
        mock_file.content_type = "text/csv"
        
        is_valid, message = FileValidator.validate_file(mock_file)
        assert is_valid is True
        assert message == "OK"
    
    def test_file_validator_invalid_extension(self):
        """Invalid file extension test"""
        mock_file = MagicMock()
        mock_file.filename = "test.exe"
        mock_file.size = 1024
        mock_file.content_type = "application/octet-stream"
        
        is_valid, message = FileValidator.validate_file(mock_file)
        assert is_valid is False
        assert "Ruxsat etilmagan fayl turi" in message

class TestAuthentication:
    """Authentication testlari"""
    
    def test_authenticate_user(self):
        """User authentication test"""
        # Test with existing user
        user = authenticate_user("admin", "admin123")
        assert user is not None
        assert user.username == "admin"
        
        # Test with invalid credentials
        user = authenticate_user("admin", "wrong_password")
        assert user is None
    
    def test_create_access_token(self):
        """Access token creation test"""
        token = create_access_token({"sub": "test_user"})
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_token(self):
        """Token verification test"""
        # Create and verify a valid token
        token = create_access_token({"sub": "test_user"})
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "test_user"
        
        # Test invalid token
        invalid_payload = verify_token("invalid_token")
        assert invalid_payload is None

class TestModels:
    """Data models testlari"""
    
    def test_ai_signal_model(self):
        """AI Signal model test"""
        from decimal import Decimal
        from datetime import datetime
        import uuid
        
        signal = AISignal(
            id=uuid.uuid4(),
            symbol="BTC/USDT",
            signal_type=SignalType.BUY,
            confidence=0.85,
            price=Decimal("45000.00"),
            timeframe="1h",
            model_version="v1.2.3",
            features={"rsi": 0.65},
            created_at=datetime.utcnow()
        )
        
        assert signal.symbol == "BTC/USDT"
        assert signal.signal_type == SignalType.BUY
        assert signal.confidence == 0.85
        assert signal.price == Decimal("45000.00")
    
    def test_user_model(self):
        """User model test"""
        from datetime import datetime
        import uuid
        
        user = User(
            id=uuid.uuid4(),
            username="testuser",
            email="test@example.com",
            role="trader",
            password="hashed_password",
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == "trader"
        assert user.is_active is True

# Test fixtures
@pytest.fixture
def mock_cache_manager():
    """Mock cache manager fixture"""
    cache = AsyncMock()
    cache.get.return_value = None
    cache.set.return_value = True
    cache.delete.return_value = True
    return cache

@pytest.fixture
def mock_user():
    """Mock user fixture"""
    return User(
        id="test-user-id",
        username="testuser",
        email="test@example.com",
        role="trader",
        password="hashed_password",
        is_active=True,
        created_at="2023-01-01T00:00:00"
    )

@pytest.fixture
def test_data():
    """Test data fixture"""
    return {
        "users": ["user1", "user2", "user3", "user4", "user5"],
        "signals": [
            {"id": 1, "symbol": "BTC/USDT", "confidence": 0.8},
            {"id": 2, "symbol": "ETH/USDT", "confidence": 0.7},
            {"id": 3, "symbol": "ADA/USDT", "confidence": 0.9}
        ]
    }

if __name__ == "__main__":
    # Run tests directly if this file is executed
    pytest.main([__file__, "-v"])