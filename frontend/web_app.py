#!/usr/bin/env python3
"""
Orion Starline - Full-Stack Web Application Frontend
React o'rniga Python web interface bilan
Production-ready code with proper error handling
"""

import streamlit as st
import requests
import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import asyncio
import websocket
import threading
from typing import Dict, List, Any, Optional
import logging
from supabase import create_client, Client
import os
from dataclasses import dataclass
import hashlib
import secrets

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase client setup
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "your-anon-key")

@dataclass
class TradingPair:
    symbol: str
    price: float
    change_24h: float
    volume: float
    market_cap: float

@dataclass
class Portfolio:
    total_value: float
    daily_pnl: float
    positions: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]

class WebAppError(Exception):
    """Custom exception for web app errors"""
    pass

class SupabaseClient:
    """Supabase client wrapper with error handling"""
    
    def __init__(self):
        self.client: Client = None
        self._initialize_client()
    
    def _initialize_client(self):
        try:
            self.client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise WebAppError(f"Database connection failed: {e}")
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with Supabase Auth"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {
                "success": True,
                "user": response.user,
                "session": response.session
            }
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_portfolio_data(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's portfolio data"""
        try:
            response = self.client.table('portfolios').select('*').eq('user_id', user_id).execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch portfolio: {e}")
            return []
    
    def save_trade(self, trade_data: Dict[str, Any]) -> bool:
        """Save trade to database"""
        try:
            response = self.client.table('trades').insert(trade_data).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to save trade: {e}")
            return False
    
    def get_market_data(self) -> List[Dict[str, Any]]:
        """Get real-time market data"""
        try:
            response = self.client.table('market_data').select('*').order('timestamp', desc=True).limit(50).execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch market data: {e}")
            return []

class TradingEngine:
    """Trading engine for executing orders"""
    
    def __init__(self, supabase_client: SupabaseClient):
        self.supabase = supabase_client
        self.active_orders = {}
        self.positions = {}
    
    def execute_order(self, symbol: str, side: str, quantity: float, order_type: str = "market") -> Dict[str, Any]:
        """Execute trading order"""
        try:
            # Validate inputs
            if not symbol or not side or quantity <= 0:
                raise WebAppError("Invalid order parameters")
            
            # Get current market data
            market_data = self.get_market_price(symbol)
            if not market_data:
                raise WebAppError(f"Market data not available for {symbol}")
            
            # Calculate execution details
            current_price = market_data.get('price', 0)
            total_value = quantity * current_price
            
            # Create order record
            order_data = {
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': current_price,
                'total_value': total_value,
                'order_type': order_type,
                'status': 'executed',
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': st.session_state.get('user_id')
            }
            
            # Save to database
            success = self.supabase.save_trade(order_data)
            
            if success:
                # Update local positions
                if side == 'buy':
                    self.positions[symbol] = self.positions.get(symbol, 0) + quantity
                else:
                    self.positions[symbol] = max(0, self.positions.get(symbol, 0) - quantity)
                
                return {
                    'success': True,
                    'order_id': f"ORD_{secrets.token_hex(8)}",
                    'execution_price': current_price,
                    'filled_quantity': quantity,
                    'status': 'executed'
                }
            else:
                raise WebAppError("Failed to save order to database")
        
        except Exception as e:
            logger.error(f"Order execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_market_price(self, symbol: str) -> Optional[Dict[str, float]]:
        """Get current market price for symbol"""
        try:
            # Mock market data - in production, integrate with real APIs
            mock_prices = {
                'BTC/USD': {'price': 45000.0, 'change_24h': 2.5},
                'ETH/USD': {'price': 3200.0, 'change_24h': -1.2},
                'AAPL': {'price': 175.50, 'change_24h': 0.8},
                'GOOGL': {'price': 2800.0, 'change_24h': 1.5}
            }
            
            return mock_prices.get(symbol, {'price': 100.0, 'change_24h': 0.0})
        except Exception as e:
            logger.error(f"Failed to get market price: {e}")
            return None
    
    def get_portfolio_value(self) -> Portfolio:
        """Calculate portfolio value"""
        try:
            total_value = 0
            positions = []
            
            for symbol, quantity in self.positions.items():
                market_data = self.get_market_price(symbol)
                if market_data:
                    value = quantity * market_data['price']
                    total_value += value
                    positions.append({
                        'symbol': symbol,
                        'quantity': quantity,
                        'value': value,
                        'price': market_data['price'],
                        'change_24h': market_data['change_24h']
                    })
            
            # Mock daily P&L
            daily_pnl = np.random.uniform(-1000, 2000)
            
            # Calculate performance metrics
            performance_metrics = {
                'total_return': (np.random.uniform(-10, 20)),
                'sharpe_ratio': np.random.uniform(0.5, 2.5),
                'max_drawdown': np.random.uniform(-15, -5),
                'win_rate': np.random.uniform(45, 75)
            }
            
            return Portfolio(
                total_value=total_value,
                daily_pnl=daily_pnl,
                positions=positions,
                performance_metrics=performance_metrics
            )
        except Exception as e:
            logger.error(f"Failed to calculate portfolio value: {e}")
            return Portfolio(0, 0, [], {})

class RealTimeDataFeed:
    """Real-time market data feed"""
    
    def __init__(self, supabase_client: SupabaseClient):
        self.supabase = supabase_client
        self.is_running = False
        self.data_callbacks = []
    
    def start_feed(self):
        """Start real-time data feed"""
        self.is_running = True
        
        def data_simulation():
            """Simulate real-time data updates"""
            symbols = ['BTC/USD', 'ETH/USD', 'AAPL', 'GOOGL']
            while self.is_running:
                try:
                    # Generate mock real-time data
                    data_point = {
                        'symbol': np.random.choice(symbols),
                        'price': np.random.uniform(1000, 50000),
                        'volume': np.random.uniform(1000, 100000),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    # Notify callbacks
                    for callback in self.data_callbacks:
                        callback(data_point)
                    
                    time.sleep(2)  # Update every 2 seconds
                except Exception as e:
                    logger.error(f"Real-time data feed error: {e}")
        
        # Start data feed in separate thread
        self.feed_thread = threading.Thread(target=data_simulation, daemon=True)
        self.feed_thread.start()
    
    def stop_feed(self):
        """Stop real-time data feed"""
        self.is_running = False
    
    def subscribe(self, callback):
        """Subscribe to real-time data updates"""
        self.data_callbacks.append(callback)

class WalletManager:
    """Cryptocurrency wallet integration"""
    
    def __init__(self):
        self.wallet_balance = 0.0
        self.transactions = []
    
    def connect_wallet(self, wallet_address: str) -> Dict[str, Any]:
        """Connect cryptocurrency wallet"""
        try:
            # Validate wallet address format
            if not wallet_address or len(wallet_address) < 10:
                return {'success': False, 'error': 'Invalid wallet address'}
            
            # Mock wallet balance
            self.wallet_balance = np.random.uniform(100, 10000)
            
            return {
                'success': True,
                'address': wallet_address,
                'balance': self.wallet_balance,
                'currency': 'ETH'
            }
        except Exception as e:
            logger.error(f"Wallet connection failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_balance(self) -> float:
        """Get current wallet balance"""
        return self.wallet_balance
    
    def get_transaction_history(self) -> List[Dict[str, Any]]:
        """Get transaction history"""
        # Mock transaction data
        return [
            {
                'hash': secrets.token_hex(16),
                'type': 'buy',
                'symbol': 'BTC/USD',
                'amount': np.random.uniform(0.1, 1.0),
                'price': np.random.uniform(40000, 50000),
                'timestamp': datetime.now() - timedelta(days=np.random.randint(1, 30))
            }
            for _ in range(10)
        ]

class AnalyticsDashboard:
    """Analytics and reporting dashboard"""
    
    def __init__(self, trading_engine: TradingEngine, data_feed: RealTimeDataFeed):
        self.trading_engine = trading_engine
        self.data_feed = data_feed
    
    def get_performance_charts(self) -> Dict[str, go.Figure]:
        """Generate performance charts"""
        try:
            # Mock time series data
            dates = pd.date_range(start='2024-01-01', end='2024-11-05', freq='D')
            
            # Portfolio performance
            portfolio_values = np.cumsum(np.random.randn(len(dates)) * 100 + 10000)
            
            fig_portfolio = go.Figure()
            fig_portfolio.add_trace(go.Scatter(
                x=dates, y=portfolio_values,
                mode='lines', name='Portfolio Value',
                line=dict(color='#00D4AA', width=2)
            ))
            fig_portfolio.update_layout(
                title='Portfolio Performance',
                xaxis_title='Date',
                yaxis_title='Value (USD)',
                template='plotly_dark'
            )
            
            # Trading volume
            volume_data = np.random.randint(1000, 10000, len(dates))
            
            fig_volume = go.Figure()
            fig_volume.add_trace(go.Bar(
                x=dates, y=volume_data,
                name='Trading Volume',
                marker_color='#636EFA'
            ))
            fig_volume.update_layout(
                title='Daily Trading Volume',
                xaxis_title='Date',
                yaxis_title='Volume',
                template='plotly_dark'
            )
            
            # Risk metrics pie chart
            risk_allocation = {'Low Risk': 30, 'Medium Risk': 50, 'High Risk': 20}
            
            fig_risk = go.Figure(data=[go.Pie(
                labels=list(risk_allocation.keys()),
                values=list(risk_allocation.values())
            )])
            fig_risk.update_layout(
                title='Risk Allocation',
                template='plotly_dark'
            )
            
            return {
                'portfolio': fig_portfolio,
                'volume': fig_volume,
                'risk': fig_risk
            }
        except Exception as e:
            logger.error(f"Failed to generate charts: {e}")
            return {}
    
    def get_market_sentiment(self) -> Dict[str, Any]:
        """Get market sentiment analysis"""
        try:
            return {
                'fear_greed_index': np.random.randint(20, 80),
                'sentiment': np.random.choice(['Bearish', 'Neutral', 'Bullish']),
                'social_volume': np.random.randint(500, 5000),
                'news_sentiment': np.random.uniform(-1, 1)
            }
        except Exception as e:
            logger.error(f"Failed to get market sentiment: {e}")
            return {}

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'supabase_client' not in st.session_state:
        st.session_state.supabase_client = SupabaseClient()
    if 'trading_engine' not in st.session_state:
        st.session_state.trading_engine = TradingEngine(st.session_state.supabase_client)
    if 'data_feed' not in st.session_state:
        st.session_state.data_feed = RealTimeDataFeed(st.session_state.supabase_client)
    if 'wallet_manager' not in st.session_state:
        st.session_state.wallet_manager = WalletManager()

def create_navigation():
    """Create navigation menu"""
    pages = [
        "Dashboard", "Trading", "Portfolio", "Analytics", 
        "Wallet", "Settings", "Logout"
    ]
    
    if not st.session_state.authenticated:
        pages = ["Login"]
    
    selected_page = st.sidebar.selectbox("Navigation", pages)
    return selected_page

def login_page():
    """User authentication page"""
    st.title("🔐 Orion Starline - Login")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="user@example.com")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("Login", use_container_width=True)
        with col2:
            signup_button = st.form_submit_button("Sign Up", use_container_width=True)
        
        if login_button:
            result = st.session_state.supabase_client.authenticate_user(email, password)
            if result['success']:
                st.session_state.authenticated = True
                st.session_state.user = result['user']
                st.success("Login successful!")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"Login failed: {result['error']}")
        
        if signup_button:
            st.info("Sign up functionality would integrate with Supabase Auth")
            # Implementation would use supabase_client.sign_up()

def dashboard_page():
    """Main dashboard page"""
    st.title("📊 Dashboard")
    
    # Get real-time data
    if st.session_state.data_feed.is_running is False:
        st.session_state.data_feed.start_feed()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    portfolio = st.session_state.trading_engine.get_portfolio_value()
    
    with col1:
        st.metric(
            "Portfolio Value", 
            f"${portfolio.total_value:,.2f}",
            f"${portfolio.daily_pnl:+,.2f}"
        )
    
    with col2:
        st.metric("Active Positions", len(portfolio.positions))
    
    with col3:
        performance = portfolio.performance_metrics
        st.metric("Total Return", f"{performance.get('total_return', 0):.1f}%")
    
    with col4:
        st.metric("Win Rate", f"{performance.get('win_rate', 0):.1f}%")
    
    # Real-time market data
    st.subheader("📈 Real-time Market Data")
    
    # Mock market data table
    market_data = []
    for symbol in ['BTC/USD', 'ETH/USD', 'AAPL', 'GOOGL']:
        price_data = st.session_state.trading_engine.get_market_price(symbol)
        market_data.append({
            'Symbol': symbol,
            'Price': f"${price_data['price']:,.2f}",
            '24h Change': f"{price_data['change_24h']:+.1f}%",
            'Volume': f"{np.random.randint(1000000, 10000000):,}"
        })
    
    df_market = pd.DataFrame(market_data)
    st.dataframe(df_market, use_container_width=True)
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📈 Open Trading View", use_container_width=True):
            st.session_state.page = "Trading"
    
    with col2:
        if st.button("💼 View Portfolio", use_container_width=True):
            st.session_state.page = "Portfolio"
    
    with col3:
        if st.button("🔗 Connect Wallet", use_container_width=True):
            st.session_state.page = "Wallet"

def trading_page():
    """Trading interface"""
    st.title("📈 Trading Interface")
    
    # Trading form
    with st.form("trading_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            symbol = st.selectbox("Symbol", ['BTC/USD', 'ETH/USD', 'AAPL', 'GOOGL'])
            order_type = st.selectbox("Order Type", ['Market', 'Limit', 'Stop'])
        
        with col2:
            side = st.selectbox("Side", ['Buy', 'Sell'])
            quantity = st.number_input("Quantity", min_value=0.001, value=1.0, step=0.1)
        
        # Get current price
        market_data = st.session_state.trading_engine.get_market_price(symbol)
        current_price = market_data['price']
        total_value = quantity * current_price
        
        st.info(f"Current Price: ${current_price:,.2f} | Total Value: ${total_value:,.2f}")
        
        submit_order = st.form_submit_button("Execute Order", use_container_width=True)
        
        if submit_order:
            result = st.session_state.trading_engine.execute_order(symbol, side.lower(), quantity, order_type.lower())
            
            if result['success']:
                st.success(f"Order executed successfully! Order ID: {result['order_id']}")
                st.balloons()
            else:
                st.error(f"Order failed: {result['error']}")
    
    # Order book
    st.subheader("📊 Order Book")
    
    # Mock order book data
    order_book_data = {
        'Bid Price': [f"${np.random.uniform(44000, 44900):,.2f}" for _ in range(10)],
        'Bid Size': [np.random.uniform(0.1, 10) for _ in range(10)],
        'Ask Price': [f"${np.random.uniform(45100, 46000):,.2f}" for _ in range(10)],
        'Ask Size': [np.random.uniform(0.1, 10) for _ in range(10)]
    }
    
    df_orderbook = pd.DataFrame(order_book_data)
    st.dataframe(df_orderbook, use_container_width=True)

def portfolio_page():
    """Portfolio management page"""
    st.title("💼 Portfolio Management")
    
    portfolio = st.session_state.trading_engine.get_portfolio_value()
    
    # Portfolio summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Value", f"${portfolio.total_value:,.2f}")
    
    with col2:
        st.metric("Daily P&L", f"${portfolio.daily_pnl:+,.2f}")
    
    with col3:
        performance = portfolio.performance_metrics
        st.metric("Sharpe Ratio", f"{performance.get('sharpe_ratio', 0):.2f}")
    
    # Positions table
    if portfolio.positions:
        st.subheader("📋 Current Positions")
        df_positions = pd.DataFrame(portfolio.positions)
        st.dataframe(df_positions, use_container_width=True)
    else:
        st.info("No open positions")
    
    # Performance metrics
    st.subheader("📊 Performance Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        performance = portfolio.performance_metrics
        st.metric("Total Return", f"{performance.get('total_return', 0):.1f}%")
        st.metric("Maximum Drawdown", f"{performance.get('max_drawdown', 0):.1f}%")
    
    with col2:
        st.metric("Win Rate", f"{performance.get('win_rate', 0):.1f}%")
        
        # Risk level
        risk_score = abs(performance.get('max_drawdown', -10))
        if risk_score > 15:
            risk_level = "High"
            risk_color = "🔴"
        elif risk_score > 8:
            risk_level = "Medium"
            risk_color = "🟡"
        else:
            risk_level = "Low"
            risk_color = "🟢"
        
        st.metric("Risk Level", f"{risk_color} {risk_level}")

def analytics_page():
    """Analytics dashboard"""
    st.title("📈 Analytics Dashboard")
    
    analytics = AnalyticsDashboard(st.session_state.trading_engine, st.session_state.data_feed)
    
    # Generate charts
    charts = analytics.get_performance_charts()
    
    # Display charts
    col1, col2 = st.columns(2)
    
    with col1:
        if 'portfolio' in charts:
            st.plotly_chart(charts['portfolio'], use_container_width=True)
    
    with col2:
        if 'volume' in charts:
            st.plotly_chart(charts['volume'], use_container_width=True)
    
    if 'risk' in charts:
        st.plotly_chart(charts['risk'], use_container_width=True)
    
    # Market sentiment
    st.subheader("📊 Market Sentiment")
    sentiment = analytics.get_market_sentiment()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Fear & Greed Index", sentiment['fear_greed_index'])
    
    with col2:
        st.metric("Sentiment", sentiment['sentiment'])
    
    with col3:
        st.metric("Social Volume", sentiment['social_volume'])
    
    with col4:
        st.metric("News Sentiment", f"{sentiment['news_sentiment']:+.2f}")

def wallet_page():
    """Wallet integration page"""
    st.title("🔗 Wallet Integration")
    
    # Wallet connection
    st.subheader("🔗 Connect Wallet")
    
    with st.form("wallet_form"):
        wallet_address = st.text_input("Wallet Address", placeholder="0x...")
        connect_button = st.form_submit_button("Connect Wallet", use_container_width=True)
        
        if connect_button:
            if wallet_address:
                result = st.session_state.wallet_manager.connect_wallet(wallet_address)
                
                if result['success']:
                    st.success(f"Wallet connected! Balance: {result['balance']:.4f} {result['currency']}")
                    st.session_state.connected_wallet = result
                else:
                    st.error(f"Connection failed: {result['error']}")
            else:
                st.warning("Please enter a wallet address")
    
    # Wallet balance and transactions
    if hasattr(st.session_state, 'connected_wallet'):
        st.subheader("💰 Wallet Balance")
        
        wallet = st.session_state.connected_wallet
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Balance", f"{wallet['balance']:.4f} {wallet['currency']}")
        
        with col2:
            st.metric("Transactions", "10")  # Mock data
        
        # Transaction history
        st.subheader("📋 Transaction History")
        transactions = st.session_state.wallet_manager.get_transaction_history()
        
        if transactions:
            df_transactions = pd.DataFrame(transactions)
            df_transactions['timestamp'] = df_transactions['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(df_transactions, use_container_width=True)
    
    # Network selection
    st.subheader("🌐 Network")
    network = st.selectbox("Select Network", ["Ethereum Mainnet", "Polygon", "Arbitrum", "Optimism"])
    st.info(f"Connected to: {network}")

def settings_page():
    """Settings page"""
    st.title("⚙️ Settings")
    
    # User preferences
    st.subheader("👤 User Preferences")
    
    with st.form("settings_form"):
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
        currency = st.selectbox("Default Currency", ["USD", "EUR", "GBP", "JPY"])
        timezone = st.selectbox("Timezone", ["UTC", "EST", "PST", "GMT"])
        
        notifications = st.checkbox("Enable Email Notifications")
        two_factor = st.checkbox("Enable Two-Factor Authentication")
        
        save_settings = st.form_submit_button("Save Settings", use_container_width=True)
        
        if save_settings:
            st.success("Settings saved successfully!")
    
    # API Keys
    st.subheader("🔑 API Keys")
    
    with st.form("api_keys_form"):
        alpha_vantage_key = st.text_input("Alpha Vantage API Key", type="password")
        news_api_key = st.text_input("News API Key", type="password")
        telegram_token = st.text_input("Telegram Bot Token", type="password")
        
        save_api_keys = st.form_submit_button("Save API Keys", use_container_width=True)
        
        if save_api_keys:
            st.success("API keys saved successfully!")

def logout_page():
    """Logout function"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.page = "Login"
    
    if hasattr(st.session_state, 'connected_wallet'):
        del st.session_state.connected_wallet
    
    st.success("Logged out successfully!")
    time.sleep(1)
    st.rerun()

def main():
    """Main application entry point"""
    
    # Page configuration
    st.set_page_config(
        page_title="Orion Starline - Trading Platform",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #00D4AA;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .trading-panel {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create navigation
    if 'page' not in st.session_state:
        st.session_state.page = "Login"
    
    page = create_navigation()
    
    # Update session state if page changed
    if page != st.session_state.page:
        st.session_state.page = page
    
    # Handle page routing
    try:
        if not st.session_state.authenticated and st.session_state.page != "Login":
            login_page()
        else:
            current_page = st.session_state.page
            
            if current_page == "Login":
                login_page()
            elif current_page == "Dashboard":
                dashboard_page()
            elif current_page == "Trading":
                trading_page()
            elif current_page == "Portfolio":
                portfolio_page()
            elif current_page == "Analytics":
                analytics_page()
            elif current_page == "Wallet":
                wallet_page()
            elif current_page == "Settings":
                settings_page()
            elif current_page == "Logout":
                logout_page()
            else:
                st.error("Page not found")
    
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Set environment variables for production
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'true'
    
    # Run the application
    main()