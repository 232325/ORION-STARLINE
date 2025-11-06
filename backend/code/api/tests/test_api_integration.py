"""
AI Trading System - API Integration Tests
API endpointlari uchun integration testlar
"""

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import patch, MagicMock

# Import the app
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

class TestHealthEndpoints:
    """Health check endpoint testlari"""
    
    def test_health_check(self):
        """Health check test"""
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "services" in data
    
    def test_system_status_requires_auth(self):
        """System status authentication test"""
        client = TestClient(app)
        response = client.get("/api/v1/system/status")
        
        assert response.status_code == 401  # Unauthorized

class TestAuthentication:
    """Authentication endpoint testlari"""
    
    def test_login_success(self):
        """Successful login test"""
        client = TestClient(app)
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert "user_info" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self):
        """Invalid credentials test"""
        client = TestClient(app)
        login_data = {
            "username": "admin",
            "password": "wrong_password"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Noto'g'ri ma'lumotlar" in response.json()["detail"]
    
    def test_get_current_user(self):
        """Get current user test"""
        client = TestClient(app)
        
        # First login to get token
        login_data = {"username": "admin", "password": "admin123"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Get user info
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        user_data = response.json()
        assert "username" in user_data
        assert "email" in user_data
        assert "role" in user_data

class TestAISignals:
    """AI Signals endpoint testlari"""
    
    def get_auth_headers(self, client):
        """Get authentication headers helper"""
        login_data = {"username": "admin", "password": "admin123"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_ai_signals(self):
        """Get AI signals test"""
        client = TestClient(app)
        headers = self.get_auth_headers(client)
        
        response = client.get("/api/v1/ai-signals", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "signals" in data
        assert "pagination" in data
        assert isinstance(data["signals"], list)
    
    def test_get_ai_signals_with_filters(self):
        """Get AI signals with filters test"""
        client = TestClient(app)
        headers = self.get_auth_headers(client)
        
        # Test with symbol filter
        response = client.get(
            "/api/v1/ai-signals?symbol=BTC/USDT",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "signals" in data
        assert "pagination" in data
    
    def test_create_ai_signal(self):
        """Create AI signal test"""
        client = TestClient(app)
        headers = self.get_auth_headers(client)
        
        signal_data = {
            "symbol": "BTC/USDT",
            "signal_type": "buy",
            "confidence": 0.85,
            "price": 45000.00,
            "timeframe": "1h"
        }
        
        response = client.post("/api/v1/ai-signals", json=signal_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert "signal" in data
        assert data["signal"]["symbol"] == "BTC/USDT"
        assert data["signal"]["confidence"] == 0.85
    
    def test_bulk_create_ai_signals(self):
        """Bulk create AI signals test"""
        client = TestClient(app)
        headers = self.get_auth_headers(client)
        
        bulk_data = {
            "symbols": ["BTC/USDT", "ETH/USDT"],
            "timeframes": ["1h", "4h"],
            "include_predictions": True
        }
        
        response = client.post("/api/v1/ai-signals/bulk", json=bulk_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "operation_id" in data
        assert data["status"] == "processing"
        assert "total_requests" in data

class TestQuantumAnalysis:
    """Quantum Analysis endpoint testlari"""
    
    def get_auth_headers(self, client):
        """Get authentication headers helper"""
        login_data = {"username": "admin", "password": "admin123"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_quantum_analyses(self):
        """Get quantum analyses test"""
        client = TestClient(app)
        headers = self.get_auth_headers(client)
        
        response = client.get("/api/v1/quantum-analysis", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "analyses" in data
        assert "pagination" in data
    
    def test_create_quantum_analysis(self):
        """Create quantum analysis test"""
        client = TestClient(app)
        headers = self.get_auth_headers(client)
        
        analysis_data = {
            "symbol": "BTC/USDT",
            "quantum_state": "superposition",
            "qbit_count": 128
        }
        
        response = client.post("/api/v1/quantum-analysis", json=analysis_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert "analysis" in data
        assert data["analysis"]["symbol"] == "BTC/USDT"

class TestBlockchain:
    """Blockchain endpoint testlari"""
    
    def get_auth_headers(self, client):
        """Get authentication headers helper"""
        login_data = {"username": "admin", "password": "admin123"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_blockchain_info(self):
        """Get blockchain info test"""
        client = TestClient(app)
        headers = self.get_auth_headers(client)
        
        response = client.get("/api/v1/blockchain/info", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "network" in data
        assert "latest_block" in data

class TestDAOGovernance:
    """DAO Governance endpoint testlari"""
    
    def get_auth_headers(self, client):
        """Get authentication headers helper"""
        login_data = {"username": "admin", "password": "admin123"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_dao_overview(self):
        """Get DAO overview test"""
        client = TestClient(app)
        headers = self.get_auth_headers(client)
        
        response = client.get("/api/v1/dao-governance/governance/overview", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "dao_info" in data
        assert "total_proposals" in data["dao_info"]

class TestHFTEngine:
    """HFT Engine endpoint testlari"""
    
    def get_auth_headers(self, client):
        """Get authentication headers helper"""
        login_data = {"username": "admin", "password": "admin123"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_hft_metrics(self):
        """Get HFT metrics test"""
        client = TestClient(app)
        headers = self.get_auth_headers(client)
        
        response = client.get("/api/v1/hft-engine/metrics/real-time", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "hft_status" in data
        assert "total_trades" in data

class TestNFTHedge:
    """NFT Hedge endpoint testlari"""
    
    def get_auth_headers(self, client):
        """Get authentication headers helper"""
        login_data = {"username": "admin", "password": "admin123"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_nft_collections(self):
        """Get NFT collections test"""
        client = TestClient(app)
        headers = self.get_auth_headers(client)
        
        response = client.get("/api/v1/nft-hedge/collections", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "collections" in data

class TestSelfLearning:
    """Self Learning endpoint testlari"""
    
    def get_auth_headers(self, client):
        """Get authentication headers helper"""
        login_data = {"username": "admin", "password": "admin123"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_learning_models(self):
        """Get learning models test"""
        client = TestClient(app)
        headers = self.get_auth_headers(client)
        
        response = client.get("/api/v1/self-learning/models", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "models" in data

class TestFileOperations:
    """File operations endpoint testlari"""
    
    def get_auth_headers(self, client):
        """Get authentication headers helper"""
        login_data = {"username": "admin", "password": "admin123"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_file_upload(self):
        """File upload test"""
        client = TestClient(app)
        headers = self.get_auth_headers(client)
        
        # Create a test file
        test_content = b"test,data,content\n1,2,3"
        files = {"file": ("test.csv", test_content, "text/csv")}
        
        response = client.post("/api/v1/files/upload", files=files, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "filename" in data
        assert data["filename"] == "test.csv"

class TestWebSocket:
    """WebSocket endpoint testlari"""
    
    def test_websocket_connection(self):
        """WebSocket connection test"""
        client = TestClient(app)
        
        with client.websocket_connect("/api/v1/websocket/trading") as websocket:
            # Send a test message
            websocket.send_text("test message")
            
            # Receive response
            data = websocket.receive_json()
            
            assert "type" in data
            assert data["type"] in ["trading_data", "connection_established"]

class TestBulkOperations:
    """Bulk operations testlari"""
    
    def get_auth_headers(self, client):
        """Get authentication headers helper"""
        login_data = {"username": "admin", "password": "admin123"}
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_bulk_status_check(self):
        """Bulk operation status check test"""
        client = TestClient(app)
        headers = self.get_auth_headers(client)
        
        # First create a bulk operation
        bulk_data = {
            "symbols": ["BTC/USDT"],
            "timeframes": ["1h"]
        }
        create_response = client.post("/api/v1/bulk/ai-signals", json=bulk_data, headers=headers)
        operation_id = create_response.json()["operation_id"]
        
        # Check status
        response = client.get(f"/api/v1/bulk/status/{operation_id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "operation_id" in data
        assert "status" in data

# Test fixtures
@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    """Authenticated headers fixture"""
    login_data = {"username": "admin", "password": "admin123"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_signal_data():
    """Sample signal data fixture"""
    return {
        "symbol": "BTC/USDT",
        "signal_type": "buy",
        "confidence": 0.85,
        "price": 45000.00,
        "timeframe": "1h"
    }

if __name__ == "__main__":
    # Run tests directly if this file is executed
    pytest.main([__file__, "-v"])