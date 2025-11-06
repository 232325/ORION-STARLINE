"""
Quantum Portfolio REST API
=========================

FastAPI-based REST API for quantum portfolio optimization.
Real-time portfolio management va optimization endpoints.

Muallif: Quantum Portfolio Team
 Sana: 2025-11-03
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import numpy as np
import logging
import asyncio
import uvicorn
from contextlib import asynccontextmanager

# Import quantum portfolio API
from .quantum_api import QuantumPortfolioAPI, OptimizationRequest, OptimizationResult
from .websocket_api import QuantumPortfolioWebSocketAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API
class PortfolioOptimizationRequest(BaseModel):
    portfolio_id: str = Field(..., description="Unique portfolio identifier")
    assets: List[str] = Field(..., description="List of asset symbols")
    constraints: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Portfolio constraints")
    quantum_algorithm: str = Field(default="VQE", description="Quantum algorithm to use")
    target_return: Optional[float] = Field(None, ge=0, le=1, description="Target expected return")
    max_risk: Optional[float] = Field(None, ge=0, le=1, description="Maximum risk tolerance")
    risk_free_rate: float = Field(default=0.02, ge=0, le=1, description="Risk-free rate")
    investment_budget: float = Field(default=1.0, gt=0, description="Total investment budget")

class EfficientFrontierRequest(BaseModel):
    assets: List[str] = Field(..., description="List of asset symbols")
    n_points: int = Field(default=50, ge=10, le=200, description="Number of frontier points")

class PortfolioResponse(BaseModel):
    portfolio_id: str
    weights: List[float]
    expected_return: float
    risk: float
    sharpe_ratio: float
    algorithm_used: str
    computation_time: float
    quantum_metrics: Dict[str, Any]
    timestamp: datetime

class EfficientFrontierResponse(BaseModel):
    assets: List[str]
    frontier_points: List[Dict[str, float]]
    algorithm_used: str
    computation_time: float
    quantum_metrics: Dict[str, Any]
    timestamp: str

class PerformanceResponse(BaseModel):
    portfolio_id: str
    current_performance: Dict[str, Any]
    optimization_details: Dict[str, Any]
    risk_analysis: Dict[str, Any]
    allocation_analysis: Dict[str, Any]

class QuantumMetricsResponse(BaseModel):
    portfolio_id: str
    algorithm_details: Dict[str, Any]
    quantum_advantage_analysis: Dict[str, Any]
    performance_comparison: Dict[str, Any]

class APIStatusResponse(BaseModel):
    status: str
    version: str
    active_optimizations: int
    completed_optimizations: int
    supported_algorithms: List[str]
    timestamp: str

# Global API instances
quantum_api: Optional[QuantumPortfolioAPI] = None
websocket_api: Optional[QuantumPortfolioWebSocketAPI] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    global quantum_api, websocket_api
    quantum_api = QuantumPortfolioAPI()
    websocket_api = QuantumPortfolioWebSocketAPI(quantum_api)
    logger.info("Quantum Portfolio REST API started")
    
    yield
    
    # Shutdown
    logger.info("Quantum Portfolio REST API shutting down")

# Initialize FastAPI app
app = FastAPI(
    title="Quantum Portfolio Optimization API",
    description="Advanced quantum computing-based portfolio optimization API",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API documentation"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Quantum Portfolio Optimization API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .endpoint { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px; }
            .method { color: #0066cc; font-weight: bold; }
            .url { font-family: monospace; background: #eee; padding: 2px 5px; }
        </style>
    </head>
    <body>
        <h1>Quantum Portfolio Optimization API</h1>
        <p>Welcome to the advanced quantum computing-based portfolio optimization API.</p>
        
        <div class="endpoint">
            <h2>Portfolio Optimization</h2>
            <p><span class="method">POST</span> <span class="url">/optimize</span></p>
            <p>Optimize portfolio using quantum algorithms (VQE, QAOA, Annealing, Hybrid)</p>
        </div>
        
        <div class="endpoint">
            <h2>Efficient Frontier</h2>
            <p><span class="method">POST</span> <span class="url">/efficient-frontier</span></p>
            <p>Compute quantum efficient frontier for asset set</p>
        </div>
        
        <div class="endpoint">
            <h2>Portfolio Performance</h2>
            <p><span class="method">GET</span> <span class="url">/portfolio/{portfolio_id}/performance</span></p>
            <p>Get portfolio performance analysis and metrics</p>
        </div>
        
        <div class="endpoint">
            <h2>Quantum Metrics</h2>
            <p><span class="method">GET</span> <span class="url">/portfolio/{portfolio_id}/quantum-metrics</span></p>
            <p>Get detailed quantum computation metrics</p>
        </div>
        
        <div class="endpoint">
            <h2>API Status</h2>
            <p><span class="method">GET</span> <span class="url">/status</span></p>
            <p>Get API status and system information</p>
        </div>
        
        <div class="endpoint">
            <h2>Documentation</h2>
            <p><span class="method">GET</span> <span class="url">/docs</span> - Interactive API documentation</p>
            <p><span class="method">GET</span> <span class="url">/redoc</span> - Alternative documentation format</p>
        </div>
        
        <h2>Quantum Algorithms Supported</h2>
        <ul>
            <li><strong>VQE</strong> - Variational Quantum Eigensolver</li>
            <li><strong>QAOA</strong> - Quantum Approximate Optimization Algorithm</li>
            <li><strong>ANNEALING</strong> - Quantum Annealing</li>
            <li><strong>HYBRID</strong> - Hybrid Quantum-Classical</li>
        </ul>
        
        <h2>WebSocket Support</h2>
        <p>Real-time updates available via WebSocket: <span class="url">/ws/portfolio/{portfolio_id}</span></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/optimize", response_model=PortfolioResponse)
async def optimize_portfolio(request: PortfolioOptimizationRequest):
    """Optimize portfolio using quantum algorithms"""
    if not quantum_api:
        raise HTTPException(status_code=503, detail="API not initialized")
    
    try:
        # Convert request to optimization request
        opt_request = OptimizationRequest(
            portfolio_id=request.portfolio_id,
            assets=request.assets,
            constraints=request.constraints,
            quantum_algorithm=request.quantum_algorithm,
            target_return=request.target_return,
            max_risk=request.max_risk,
            risk_free_rate=request.risk_free_rate,
            investment_budget=request.investment_budget
        )
        
        # Execute optimization
        result = await quantum_api.optimize_portfolio(opt_request)
        
        # Send WebSocket notification if available
        if websocket_api:
            await websocket_api.notify_optimization_complete(
                request.portfolio_id, 
                result.expected_return, 
                result.risk
            )
        
        return PortfolioResponse(
            portfolio_id=result.portfolio_id,
            weights=result.weights.tolist(),
            expected_return=result.expected_return,
            risk=result.risk,
            sharpe_ratio=result.sharpe_ratio,
            algorithm_used=result.algorithm_used,
            computation_time=result.computation_time,
            quantum_metrics=result.quantum_metrics,
            timestamp=result.timestamp
        )
        
    except Exception as e:
        logger.error(f"Portfolio optimization failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Optimization failed: {str(e)}")

@app.post("/efficient-frontier", response_model=EfficientFrontierResponse)
async def compute_efficient_frontier(request: EfficientFrontierRequest):
    """Compute quantum efficient frontier"""
    if not quantum_api:
        raise HTTPException(status_code=503, detail="API not initialized")
    
    try:
        result = await quantum_api.get_efficient_frontier(
            assets=request.assets, 
            n_points=request.n_points
        )
        
        return EfficientFrontierResponse(
            assets=result["assets"],
            frontier_points=result["frontier_points"],
            algorithm_used=result["algorithm_used"],
            computation_time=result["computation_time"],
            quantum_metrics=result["quantum_metrics"],
            timestamp=result["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Efficient frontier computation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Frontier computation failed: {str(e)}")

@app.get("/portfolio/{portfolio_id}/performance", response_model=PerformanceResponse)
async def get_portfolio_performance(portfolio_id: str):
    """Get portfolio performance analysis"""
    if not quantum_api:
        raise HTTPException(status_code=503, detail="API not initialized")
    
    try:
        performance = await quantum_api.get_portfolio_performance(portfolio_id)
        return PerformanceResponse(**performance)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Performance analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Performance analysis failed")

@app.get("/portfolio/{portfolio_id}/quantum-metrics", response_model=QuantumMetricsResponse)
async def get_quantum_metrics(portfolio_id: str):
    """Get detailed quantum computation metrics"""
    if not quantum_api:
        raise HTTPException(status_code=503, detail="API not initialized")
    
    try:
        metrics = await quantum_api.get_quantum_metrics(portfolio_id)
        return QuantumMetricsResponse(**metrics)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Quantum metrics retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Metrics retrieval failed")

@app.get("/status", response_model=APIStatusResponse)
async def get_api_status():
    """Get API status and system information"""
    if not quantum_api:
        raise HTTPException(status_code=503, detail="API not initialized")
    
    try:
        status = quantum_api.get_api_status()
        return APIStatusResponse(**status)
        
    except Exception as e:
        logger.error(f"Status retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Status retrieval failed")

@app.get("/history")
async def get_optimization_history(limit: int = 50):
    """Get optimization history"""
    if not quantum_api:
        raise HTTPException(status_code=503, detail="API not initialized")
    
    try:
        history = quantum_api.get_optimization_history(limit)
        return {"history": history}
        
    except Exception as e:
        logger.error(f"History retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="History retrieval failed")

@app.get("/assets")
async def get_available_assets():
    """Get list of available assets for optimization"""
    # This would typically come from a database
    # For demo purposes, return sample assets
    sample_assets = {
        "stocks": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "NFLX"],
        "forex": ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD"],
        "metals": ["GOLD", "SILVER", "PLATINUM", "PALLADIUM", "COPPER"]
    }
    return {"available_assets": sample_assets}

@app.get("/algorithms")
async def get_supported_algorithms():
    """Get list of supported quantum algorithms"""
    return {
        "algorithms": [
            {
                "name": "VQE",
                "description": "Variational Quantum Eigensolver",
                "best_for": "Small to medium portfolios (5-20 assets)",
                "complexity": "O(n²)"
            },
            {
                "name": "QAOA",
                "description": "Quantum Approximate Optimization Algorithm",
                "best_for": "Discrete optimization problems",
                "complexity": "O(n³)"
            },
            {
                "name": "ANNEALING",
                "description": "Quantum Annealing",
                "best_for": "Large portfolios with many constraints",
                "complexity": "O(log n)"
            },
            {
                "name": "HYBRID",
                "description": "Hybrid Quantum-Classical",
                "best_for": "Production environments with limited quantum resources",
                "complexity": "O(n²) classical + O(log n) quantum"
            }
        ]
    }

@app.websocket("/ws/portfolio/{portfolio_id}")
async def portfolio_websocket(websocket, portfolio_id: str):
    """WebSocket endpoint for real-time portfolio updates"""
    if not websocket_api:
        await websocket.close(code=1003, reason="WebSocket API not available")
        return
    
    try:
        await websocket_api.connect_websocket(websocket, portfolio_id)
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
        await websocket.close(code=1011, reason="Internal server error")

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "quantum_api_ready": quantum_api is not None,
        "websocket_api_ready": websocket_api is not None
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    if not quantum_api:
        raise HTTPException(status_code=503, detail="Quantum API not ready")
    return {"status": "ready"}

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return {"error": {"status_code": exc.status_code, "detail": exc.detail}}

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return {"error": {"status_code": 500, "detail": "Internal server error"}}

# Production deployment
def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    return app

if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "rest_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )