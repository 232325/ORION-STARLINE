"""
AI Voice Assistant - Advanced Voice-to-Trade Platform
Innovatsion ovoz bilan boshqariladigan trading tizimi

Bu modul quyidagi xususiyatlarni ta'minlaydi:
- Real-time ovoz recognition
- Natural language processing
- Voice-to-trade commands
- Multi-language support
- Risk assessment va confirmation
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import speech_recognition as sr
import pyttsx3
import numpy as np
from datetime import datetime
import websockets
from cryptography.fernet import Fernet

# Configuration and constants
class VoiceCommandType(Enum):
    """Voice command types enumeration"""
    TRADE_ORDER = "trade_order"
    PORTFOLIO_QUERY = "portfolio_query"
    MARKET_ANALYSIS = "market_analysis"
    RISK_MANAGEMENT = "risk_management"
    NEWS_QUERY = "news_query"
    ALERT_SETTING = "alert_setting"
    STRATEGY_UPDATE = "strategy_update"
    HELP_REQUEST = "help_request"

class VoiceCommandPriority(Enum):
    """Command execution priorities"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class VoiceCommand:
    """Voice command data structure"""
    command_type: VoiceCommandType
    priority: VoiceCommandPriority
    parameters: Dict[str, Any]
    user_id: str
    timestamp: datetime
    confirmation_required: bool = True
    risk_score: float = 0.0

class AIProcessingEngine:
    """AI-powered natural language processing for voice commands"""
    
    def __init__(self):
        self.intent_classifier = self._load_intent_classifier()
        self.entity_extractor = self._load_entity_extractor()
        self.risk_assessor = RiskAssessmentEngine()
        
    def _load_intent_classifier(self) -> Dict[str, Any]:
        """Load pre-trained intent classification model"""
        return {
            "trading_patterns": [
                "sotib ol", "sotaman", "buy", "sell", "position ochish",
                "stop loss qo'yish", "take profit", "limit order"
            ],
            "portfolio_patterns": [
                "portfolio", "balansim", "holdings", "positions", "p&l"
            ],
            "market_patterns": [
                "narx", "market", "trend", "analiz", "signal"
            ],
            "risk_patterns": [
                "risk", "stop loss", "risk management", "protection"
            ]
        }
    
    def _load_entity_extractor(self) -> Dict[str, Any]:
        """Load entity extraction patterns"""
        return {
            "symbols": [r'\b[A-Z]{2,6}\b', r'\b(BTC|ETH|USDT|BNB)\b'],
            "amounts": [r'\d+(?:\.\d+)?', r'\d+(?:\.\d+)? USDT'],
            "percentages": [r'\d+%', r'\d+(?:\.\d+)?%'],
            "actions": [r'(buy|sell|sotib|sotaman|limit|market)']
        }
    
    async def process_voice_command(self, voice_text: str) -> VoiceCommand:
        """Process voice command and extract intent"""
        try:
            # Normalize text
            normalized_text = voice_text.lower().strip()
            
            # Intent classification
            intent = self._classify_intent(normalized_text)
            
            # Entity extraction
            entities = self._extract_entities(normalized_text)
            
            # Risk assessment
            risk_score = await self.risk_assessor.calculate_risk(
                intent, entities
            )
            
            # Create command object
            command = VoiceCommand(
                command_type=intent,
                priority=self._determine_priority(intent, entities),
                parameters=entities,
                user_id="user_123",  # From session
                timestamp=datetime.now(),
                confirmation_required=risk_score > 0.3,
                risk_score=risk_score
            )
            
            return command
            
        except Exception as e:
            logging.error(f"Voice command processing error: {e}")
            raise
    
    def _classify_intent(self, text: str) -> VoiceCommandType:
        """Classify intent from voice text"""
        patterns = self.intent_classifier
        
        if any(pattern in text for pattern in patterns["trading_patterns"]):
            return VoiceCommandType.TRADE_ORDER
        elif any(pattern in text for pattern in patterns["portfolio_patterns"]):
            return VoiceCommandType.PORTFOLIO_QUERY
        elif any(pattern in text for pattern in patterns["market_patterns"]):
            return VoiceCommandType.MARKET_ANALYSIS
        elif any(pattern in text for pattern in patterns["risk_patterns"]):
            return VoiceCommandType.RISK_MANAGEMENT
        else:
            return VoiceCommandType.HELP_REQUEST
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from voice text"""
        entities = {}
        
        # Extract trading symbols
        import re
        symbols = re.findall(r'\b[A-Z]{2,6}\b', text)
        entities["symbols"] = symbols if symbols else ["BTC"]
        
        # Extract amounts
        amounts = re.findall(r'\d+(?:\.\d+)?', text)
        entities["amounts"] = [float(a) for a in amounts] if amounts else [100]
        
        # Extract percentages
        percentages = re.findall(r'\d+%', text)
        entities["percentages"] = [float(p.rstrip('%')) for p in percentages] if percentages else [2.0]
        
        # Extract action
        if "sotib" in text or "buy" in text:
            entities["action"] = "buy"
        elif "sotaman" in text or "sell" in text:
            entities["action"] = "sell"
        else:
            entities["action"] = "query"
            
        return entities
    
    def _determine_priority(self, intent: VoiceCommandType, entities: Dict) -> VoiceCommandPriority:
        """Determine command execution priority"""
        if intent == VoiceCommandType.TRADE_ORDER:
            return VoiceCommandPriority.HIGH
        elif intent == VoiceCommandType.RISK_MANAGEMENT:
            return VoiceCommandPriority.CRITICAL
        elif intent == VoiceCommandType.PORTFOLIO_QUERY:
            return VoiceCommandPriority.NORMAL
        else:
            return VoiceCommandPriority.LOW

class RiskAssessmentEngine:
    """Real-time risk assessment for voice commands"""
    
    def __init__(self):
        self.risk_models = self._load_risk_models()
        self.market_data = MarketDataProvider()
    
    def _load_risk_models(self) -> Dict[str, Any]:
        """Load risk assessment models"""
        return {
            "volatility_threshold": 0.05,
            "volume_threshold": 1000000,
            "correlation_limit": 0.8,
            "position_size_limit": 0.1
        }
    
    async def calculate_risk(self, intent: VoiceCommandType, entities: Dict) -> float:
        """Calculate risk score for voice command"""
        try:
            risk_score = 0.0
            
            # Trade order specific risks
            if intent == VoiceCommandType.TRADE_ORDER:
                # Check symbol volatility
                symbol = entities.get("symbols", ["BTC"])[0]
                volatility = await self.market_data.get_volatility(symbol)
                risk_score += min(volatility * 2, 0.4)
                
                # Check position size
                amount = entities.get("amounts", [100])[0]
                risk_score += min(amount / 10000, 0.3)
                
                # Check market conditions
                market_stress = await self.market_data.get_market_stress()
                risk_score += market_stress * 0.2
                
            # Risk management specific risks
            elif intent == VoiceCommandType.RISK_MANAGEMENT:
                risk_score = 0.1  # Lower risk for safety measures
            
            # Ensure risk score is between 0 and 1
            return min(max(risk_score, 0.0), 1.0)
            
        except Exception as e:
            logging.error(f"Risk assessment error: {e}")
            return 0.5  # Default medium risk

class MarketDataProvider:
    """Real-time market data provider"""
    
    async def get_volatility(self, symbol: str) -> float:
        """Get current volatility for symbol"""
        # Simulated volatility data
        volatilities = {
            "BTC": 0.03,
            "ETH": 0.04,
            "BNB": 0.02,
            "USDT": 0.001
        }
        return volatilities.get(symbol, 0.05)
    
    async def get_market_stress(self) -> float:
        """Get overall market stress indicator"""
        # Simulated market stress (0-1)
        return 0.2

class VoiceInterface:
    """Advanced voice interface with speech recognition and synthesis"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        
    def setup_tts(self):
        """Setup text-to-speech engine"""
        voices = self.tts_engine.getProperty('voices')
        # Set Uzbek language voice if available
        if voices:
            self.tts_engine.setProperty('voice', voices[0].id)
        
        self.tts_engine.setProperty('rate', 150)  # Speaking speed
        self.tts_engine.setProperty('volume', 0.8)  # Volume level
    
    async def listen_for_command(self, timeout: int = 10) -> str:
        """Listen for voice command from user"""
        try:
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source)
                logging.info("Ovoz buyrug'i uchun tinglash...")
                
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout)
                
                # Convert speech to text
                voice_text = self.recognizer.recognize_google(
                    audio, language='uz-UZ'
                )
                
                logging.info(f"Recognized voice: {voice_text}")
                return voice_text
                
        except sr.WaitTimeoutError:
            logging.warning("Vaqt tugadi, ovoz signalini kutishni to'xtatish")
            return ""
        except sr.UnknownValueError:
            logging.error("Ovoz aniqlanmadi")
            return ""
        except Exception as e:
            logging.error(f"Voice recognition error: {e}")
            return ""
    
    async def speak_response(self, text: str) -> None:
        """Convert text to speech and speak"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logging.error(f"Text-to-speech error: {e}")
    
    async def confirm_command(self, command: VoiceCommand) -> bool:
        """Get user confirmation for high-risk commands"""
        confirmation_prompt = self._generate_confirmation_prompt(command)
        
        await self.speak_response(confirmation_prompt)
        
        # Listen for confirmation
        response = await self.listen_for_command(timeout=5)
        
        return "ha" in response.lower() or "yes" in response.lower()
    
    def _generate_confirmation_prompt(self, command: VoiceCommand) -> str:
        """Generate confirmation prompt for user"""
        if command.command_type == VoiceCommandType.TRADE_ORDER:
            return (f"Trade order tayyor. {command.parameters.get('action', 'buy')} "
                   f"{command.parameters.get('amount', 100)} dollar qiymatidagi "
                   f"{command.parameters.get('symbols', ['BTC'])[0]}. "
                   f"Risk balandligi: {command.risk_score:.2f}. "
                   f"Bajarishni tasdiqlaysizmi?")
        elif command.command_type == VoiceCommandType.RISK_MANAGEMENT:
            return "Risk management operatsiyasi tayyor. Tasdiqlaysizmi?"
        else:
            return "Operatsiya tayyor. Davom etamizmi?"

class TradingExecutor:
    """Execute trading commands received via voice"""
    
    def __init__(self):
        self.trading_engine = self._initialize_trading_engine()
        self.security = SecurityManager()
    
    def _initialize_trading_engine(self) -> Dict[str, Any]:
        """Initialize trading engine"""
        return {
            "exchanges": ["binance", "coinbase", "kraken"],
            "supported_pairs": ["BTC/USDT", "ETH/USDT", "BNB/USDT"],
            "min_amount": 10,
            "max_amount": 100000
        }
    
    async def execute_voice_command(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute voice command through trading system"""
        try:
            # Security check
            if not await self.security.authorize_command(command):
                return {"success": False, "error": "Security authorization failed"}
            
            # Route to appropriate executor
            if command.command_type == VoiceCommandType.TRADE_ORDER:
                return await self._execute_trade_order(command)
            elif command.command_type == VoiceCommandType.PORTFOLIO_QUERY:
                return await self._execute_portfolio_query(command)
            elif command.command_type == VoiceCommandType.MARKET_ANALYSIS:
                return await self._execute_market_analysis(command)
            else:
                return await self._execute_general_command(command)
                
        except Exception as e:
            logging.error(f"Command execution error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_trade_order(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute trade order"""
        params = command.parameters
        
        # Validate parameters
        symbol = params.get("symbols", ["BTC"])[0]
        amount = params.get("amounts", [100])[0]
        action = params.get("action", "buy")
        
        # Simulate trade execution
        execution_result = {
            "success": True,
            "order_id": f"VOICE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "symbol": symbol,
            "action": action,
            "amount": amount,
            "timestamp": datetime.now().isoformat(),
            "price": 45000.00,  # Simulated price
            "execution_time": "1.2s"
        }
        
        return execution_result
    
    async def _execute_portfolio_query(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute portfolio query"""
        return {
            "success": True,
            "data": {
                "total_value": 15420.50,
                "positions": [
                    {"symbol": "BTC", "amount": 0.25, "value": 11250.00},
                    {"symbol": "ETH", "amount": 2.1, "value": 4170.50}
                ],
                "pnl": {"daily": 156.75, "total": 2340.25}
            }
        }
    
    async def _execute_market_analysis(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute market analysis query"""
        return {
            "success": True,
            "analysis": {
                "trend": "bullish",
                "confidence": 0.75,
                "key_levels": {"support": 44000, "resistance": 46000},
                "volume": "above_average",
                "sentiment": "positive"
            }
        }
    
    async def _execute_general_command(self, command: VoiceCommand) -> Dict[str, Any]:
        """Execute general purpose commands"""
        return {
            "success": True,
            "message": f"{command.command_type.value} successfully processed",
            "timestamp": datetime.now().isoformat()
        }

class SecurityManager:
    """Enhanced security management for voice commands"""
    
    def __init__(self):
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
    async def authorize_command(self, command: VoiceCommand) -> bool:
        """Authorize voice command execution"""
        try:
            # Check command integrity
            if not self._verify_command_integrity(command):
                return False
            
            # Check user permissions
            if not await self._check_user_permissions(command.user_id):
                return False
            
            # Check risk limits
            if command.risk_score > 0.8:
                return False
            
            # Additional biometric verification could be added here
            return True
            
        except Exception as e:
            logging.error(f"Authorization error: {e}")
            return False
    
    def _verify_command_integrity(self, command: VoiceCommand) -> bool:
        """Verify command data integrity"""
        # Simple integrity check
        required_fields = ['command_type', 'parameters', 'user_id', 'timestamp']
        return all(hasattr(command, field) for field in required_fields)
    
    async def _check_user_permissions(self, user_id: str) -> bool:
        """Check user permissions for command execution"""
        # Mock permission check
        return user_id is not None and len(user_id) > 0

class AIVoiceAssistant:
    """Main AI Voice Assistant class - Innovatsion ovozli trading platform"""
    
    def __init__(self):
        self.ai_engine = AIProcessingEngine()
        self.voice_interface = VoiceInterface()
        self.trading_executor = TradingExecutor()
        self.security_manager = SecurityManager()
        self.is_running = False
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    async def start_assistant(self) -> None:
        """Start the AI Voice Assistant"""
        self.is_running = True
        self.logger.info("AI Voice Assistant ishga tushdi...")
        
        await self.speak_welcome_message()
        
        # Main interaction loop
        while self.is_running:
            try:
                await self.handle_voice_interaction()
                await asyncio.sleep(1)  # Prevent CPU overload
                
            except KeyboardInterrupt:
                self.logger.info("Assistant to'xtatildi...")
                break
            except Exception as e:
                self.logger.error(f"Interaction error: {e}")
                await self.handle_error(e)
    
    async def speak_welcome_message(self) -> None:
        """Speak welcome message"""
        welcome_text = (
            "Salom! Men Orion Starline AI Voice Assistant. "
            "Ovoz orqali trading operatsiyalarni bajarish uchun menga gapiring. "
            "Yordam kerak bo'lsa 'yordam' deb ayting."
        )
        await self.voice_interface.speak_response(welcome_text)
    
    async def handle_voice_interaction(self) -> None:
        """Handle main voice interaction loop"""
        # Listen for command
        voice_text = await self.voice_interface.listen_for_command()
        
        if not voice_text:
            return
        
        # Process voice command
        command = await self.ai_engine.process_voice_command(voice_text)
        
        # Handle confirmation if required
        if command.confirmation_required:
            confirmed = await self.voice_interface.confirm_command(command)
            if not confirmed:
                await self.voice_interface.speak_response("Operatsiya bekor qilindi.")
                return
        
        # Execute command
        result = await self.trading_executor.execute_voice_command(command)
        
        # Provide feedback
        await self.provide_execution_feedback(result, command)
    
    async def provide_execution_feedback(self, result: Dict, command: VoiceCommand) -> None:
        """Provide feedback about command execution"""
        if result["success"]:
            if command.command_type == VoiceCommandType.TRADE_ORDER:
                response = f"Order muvaffaqiyatli bajarildi. Order ID: {result.get('order_id', 'N/A')}"
            elif command.command_type == VoiceCommandType.PORTFOLIO_QUERY:
                total_value = result["data"]["total_value"]
                response = f"Portfolio qiymatingiz {total_value} dollar"
            else:
                response = "Operatsiya muvaffaqiyatli bajarildi"
        else:
            response = f"Xatolik yuz berdi: {result.get('error', 'Noma\'lum xatolik')}"
        
        await self.voice_interface.speak_response(response)
    
    async def handle_error(self, error: Exception) -> None:
        """Handle system errors gracefully"""
        error_message = (
            "Kechirasiz, texnik muammo yuz berdi. "
            "Iltimos, qaytadan urinib ko'ring yoki administrator bilan bog'laning."
        )
        await self.voice_interface.speak_response(error_message)
    
    async def stop_assistant(self) -> None:
        """Stop the AI Voice Assistant"""
        self.is_running = False
        await self.voice_interface.speak_response("AI Voice Assistant ishni to'xtatdi. Hayr!")
        self.logger.info("AI Voice Assistant to'xtatildi")

# Demo function
async def demo_voice_assistant():
    """Demo function for AI Voice Assistant"""
    assistant = AIVoiceAssistant()
    
    print("=== AI Voice Assistant Demo ===")
    print("Ovozli trading tizimini ishga tushirish...")
    
    try:
        # Simulate voice commands for demo
        demo_commands = [
            "Bitcoin sotib ol 500 dollar",
            "Portfolio holati",
            "BTC narxi qanday",
            "Stop loss qo'yish"
        ]
        
        for command_text in demo_commands:
            print(f"\nDemo command: {command_text}")
            
            # Process command
            voice_command = await assistant.ai_engine.process_voice_command(command_text)
            
            print(f"Command type: {voice_command.command_type.value}")
            print(f"Risk score: {voice_command.risk_score}")
            print(f"Parameters: {voice_command.parameters}")
            
            # Execute command
            result = await assistant.trading_executor.execute_voice_command(voice_command)
            print(f"Result: {result}")
            
            await asyncio.sleep(2)
            
    except Exception as e:
        print(f"Demo error: {e}")

if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_voice_assistant())