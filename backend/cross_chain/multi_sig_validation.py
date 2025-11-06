"""
Multi-Signature Validation System
Cross-chain asset management uchun multi-sig xavfsizlik tizimi
"""

import asyncio
import hashlib
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import hmac

class SignatureStatus(Enum):
    """Imzolash holatlari"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class ActionType(Enum):
    """Harakat turlari"""
    BRIDGE_INITIATE = "bridge_initiate"
    BRIDGE_COMPLETE = "bridge_complete"
    BRIDGE_CANCEL = "bridge_cancel"
    PAUSE_SYSTEM = "pause_system"
    UNPAUSE_SYSTEM = "unpause_system"
    UPDATE_ORACLE = "update_oracle"
    SLASH_VALIDATOR = "slash_validator"
    EMERGENCY_WITHDRAW = "emergency_withdraw"

@dataclass
class MultiSigTransaction:
    """Multi-sig tranzaksiya ma'lumotlari"""
    tx_id: str
    action_type: ActionType
    initiator: str
    parameters: Dict
    required_signatures: int
    signatures: List[Dict]  # [{"signer": "0x...", "signature": "0x...", "timestamp": 123456}]
    status: SignatureStatus
    created_at: int
    expires_at: int
    executed_at: Optional[int] = None

@dataclass
class ValidatorInfo:
    """Validator ma'lumotlari"""
    address: str
    stake_amount: int
    is_active: bool
    reputation_score: float
    last_active: int
    slashing_history: List[Dict]

class MultiSigValidator:
    """Multi-sig validator boshqaruvchisi"""
    
    def __init__(self, threshold: int = 3, timeout_hours: int = 24):
        self.threshold = threshold
        self.timeout_seconds = timeout_hours * 3600
        self.validators = self._load_validators()
        self.pending_transactions = {}
        self.completed_transactions = {}
        self.emergency_actions = []
    
    def _load_validators(self) -> List[ValidatorInfo]:
        """Validatorlar ro'yxatini yuklash"""
        return [
            ValidatorInfo(
                address="0x742d35Cc6a12F8C71EdBD49E1a5d3f76E32C2c7d",
                stake_amount=1000000,  # 1M tokens
                is_active=True,
                reputation_score=0.95,
                last_active=int(time.time()),
                slashing_history=[]
            ),
            ValidatorInfo(
                address="0x8ba1f109551bD432803012645Hac136c23E3d441",
                stake_amount=800000,
                is_active=True,
                reputation_score=0.90,
                last_active=int(time.time()),
                slashing_history=[]
            ),
            ValidatorInfo(
                address="0x7B8F0579Cc7A9cD4c0A1C8d4E1C3a2B4d5E6F7A8",
                stake_amount=750000,
                is_active=True,
                reputation_score=0.88,
                last_active=int(time.time()),
                slashing_history=[]
            ),
            ValidatorInfo(
                address="0x9c4F5D2B8e4A3F6d9A1C7e3F5B2d8A9E6F3c7B2A5",
                stake_amount=600000,
                is_active=True,
                reputation_score=0.92,
                last_active=int(time.time()),
                slashing_history=[]
            ),
            ValidatorInfo(
                address="0x2d8E4a6F3b9c7D5E1A8b3F6c2D5E9A4F7b8C3D6E9",
                stake_amount=500000,
                is_active=True,
                reputation_score=0.85,
                last_active=int(time.time()),
                slashing_history=[]
            )
        ]
    
    def generate_tx_id(self, action_type: ActionType, initiator: str, parameters: Dict) -> str:
        """Tranzaksiya ID yaratish"""
        data = f"{action_type.value}_{initiator}_{json.dumps(parameters, sort_keys=True)}_{int(time.time())}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_signature(self, message: str, signature: str, signer_address: str) -> bool:
        """Imzolashni tekshirish"""
        # Simplified signature verification
        # Haqiqiy implementatsiyada cryptographic verification kerak
        try:
            # ECDSA signature verification logic
            signature_bytes = bytes.fromhex(signature[2:])
            
            # Hash message
            message_hash = hashlib.sha256(message.encode()).digest()
            
            # Simplified verification (real implementation needed)
            expected_hash = hashlib.sha256(f"{signer_address}_{message}".encode()).digest()
            
            return True  # Placeholder
            
        except Exception:
            return False
    
    def sign_message(self, private_key: str, message: str) -> str:
        """Xabarni imzolash"""
        try:
            # Simplified signing
            message_hash = hashlib.sha256(message.encode()).digest()
            # Real implementation would use ECDSA signing
            signature_hex = f"0x{message_hash.hexdigest()}"
            return signature_hex
            
        except Exception as e:
            raise ValueError(f"Imzolashda xatolik: {e}")
    
    async def initiate_transaction(
        self,
        action_type: ActionType,
        initiator: str,
        parameters: Dict,
        private_key: str
    ) -> str:
        """Tranzaksiyani boshlash"""
        
        # Tranzaksiya ID yaratish
        tx_id = self.generate_tx_id(action_type, initiator, parameters)
        
        # Tranzaksiya yaratish
        transaction = MultiSigTransaction(
            tx_id=tx_id,
            action_type=action_type,
            initiator=initiator,
            parameters=parameters,
            required_signatures=self.threshold,
            signatures=[],
            status=SignatureStatus.PENDING,
            created_at=int(time.time()),
            expires_at=int(time.time()) + self.timeout_seconds
        )
        
        # Boshlang'ich imzolash (initiator tomonidan)
        message = self._create_message_to_sign(transaction)
        initiator_signature = self.sign_message(private_key, message)
        
        # Initiator imzosini qo'shish
        transaction.signatures.append({
            "signer": initiator,
            "signature": initiator_signature,
            "timestamp": int(time.time())
        })
        
        self.pending_transactions[tx_id] = transaction
        
        print(f"✅ Multi-sig tranzaksiya boshlandi: {tx_id}")
        print(f"   Harakat: {action_type.value}")
        print(f"   Talab etilgan imzolar: {self.threshold}")
        
        return tx_id
    
    def _create_message_to_sign(self, transaction: MultiSigTransaction) -> str:
        """Imzolanadigan xabar yaratish"""
        message_data = {
            "tx_id": transaction.tx_id,
            "action_type": transaction.action_type.value,
            "initiator": transaction.initiator,
            "parameters": transaction.parameters,
            "created_at": transaction.created_at
        }
        return json.dumps(message_data, sort_keys=True)
    
    async def add_signature(
        self,
        tx_id: str,
        validator_address: str,
        signature: str
    ) -> bool:
        """Validator imzosini qo'shish"""
        
        if tx_id not in self.pending_transactions:
            raise ValueError("Tranzaksiya topilmadi")
        
        transaction = self.pending_transactions[tx_id]
        
        if transaction.status != SignatureStatus.PENDING:
            raise ValueError("Tranzaksiya holati noto'g'ri")
        
        if int(time.time()) > transaction.expires_at:
            transaction.status = SignatureStatus.EXPIRED
            return False
        
        # Validator mavjudligini tekshirish
        validator = next((v for v in self.validators if v.address == validator_address), None)
        if not validator or not validator.is_active:
            raise ValueError("Validator topilmadi yoki faol emas")
        
        # Imzolash holatini tekshirish
        existing_signature = next(
            (s for s in transaction.signatures if s["signer"] == validator_address),
            None
        )
        if existing_signature:
            raise ValueError("Validator allaqachon imzolagan")
        
        # Xabarni tekshirish
        message = self._create_message_to_sign(transaction)
        if not self.verify_signature(message, signature, validator_address):
            raise ValueError("Imzoga e'lon noto'g'ri")
        
        # Imzoni qo'shish
        transaction.signatures.append({
            "signer": validator_address,
            "signature": signature,
            "timestamp": int(time.time())
        })
        
        # Validator faolligini yangilash
        validator.last_active = int(time.time())
        
        print(f"✅ Imzо qo'shildi: {validator_address}")
        print(f"   Imzolar soni: {len(transaction.signatures)}/{transaction.required_signatures}")
        
        # Kerakli imzolar to'planganini tekshirish
        if len(transaction.signatures) >= transaction.required_signatures:
            await self._execute_transaction(transaction)
        
        return True
    
    async def _execute_transaction(self, transaction: MultiSigTransaction):
        """Tranzaksiyani bajarish"""
        try:
            transaction.status = SignatureStatus.APPROVED
            transaction.executed_at = int(time.time())
            
            # Tranzaksiyani bajarish
            await self._perform_action(transaction)
            
            # Completed ga ko'chirish
            self.completed_transactions[transaction.tx_id] = transaction
            del self.pending_transactions[transaction.tx_id]
            
            print(f"✅ Tranzaksiya bajarildi: {transaction.tx_id}")
            
        except Exception as e:
            transaction.status = SignatureStatus.REJECTED
            print(f"❌ Tranzaksiyani bajarishda xatolik: {e}")
    
    async def _perform_action(self, transaction: MultiSigTransaction):
        """Harakatni bajarish"""
        action_type = transaction.action_type
        
        if action_type == ActionType.BRIDGE_INITIATE:
            await self._handle_bridge_initiate(transaction)
        elif action_type == ActionType.PAUSE_SYSTEM:
            await self._handle_pause_system(transaction)
        elif action_type == ActionType.UNPAUSE_SYSTEM:
            await self._handle_unpause_system(transaction)
        elif action_type == ActionType.SLASH_VALIDATOR:
            await self._handle_slash_validator(transaction)
        elif action_type == ActionType.EMERGENCY_WITHDRAW:
            await self._handle_emergency_withdraw(transaction)
        else:
            print(f"⚠️ Noma'lum harakat turi: {action_type.value}")
    
    async def _handle_bridge_initiate(self, transaction: MultiSigTransaction):
        """Bridge boshlash harakati"""
        params = transaction.parameters
        print(f"🌉 Bridge boshlanyapti:")
        print(f"   Token: {params.get('token_address')}")
        print(f"   Miqdor: {params.get('amount')}")
        print(f"   Manzil: {params.get('recipient')}")
        
        # Bridge logic here
        await asyncio.sleep(0.1)  # Simulated processing
    
    async def _handle_pause_system(self, transaction: MultiSigTransaction):
        """Tizimni to'xtatish"""
        print("⏸️ Tizim to'xtatildi (emergency)")
        
        self.emergency_actions.append({
            "type": "pause",
            "timestamp": int(time.time()),
            "transaction_id": transaction.tx_id
        })
        
        await asyncio.sleep(0.1)
    
    async def _handle_unpause_system(self, transaction: MultiSigTransaction):
        """Tizimni qayta ishga tushirish"""
        print("▶️ Tizim qayta ishga tushirildi")
        
        self.emergency_actions.append({
            "type": "unpause",
            "timestamp": int(time.time()),
            "transaction_id": transaction.tx_id
        })
        
        await asyncio.sleep(0.1)
    
    async def _handle_slash_validator(self, transaction: MultiSigTransaction):
        """Validator jazolash"""
        validator_address = transaction.parameters.get("validator_address")
        amount = transaction.parameters.get("amount", 0)
        
        print(f"⚔️ Validator jazolanyapti: {validator_address}")
        print(f"   Jarima miqdori: {amount}")
        
        # Validator topish va jazolash
        validator = next((v for v in self.validators if v.address == validator_address), None)
        if validator:
            validator.stake_amount -= amount
            validator.slashing_history.append({
                "amount": amount,
                "timestamp": int(time.time()),
                "reason": transaction.parameters.get("reason")
            })
        
        await asyncio.sleep(0.1)
    
    async def _handle_emergency_withdraw(self, transaction: MultiSigTransaction):
        """Favqulodda mablag' yechib olish"""
        amount = transaction.parameters.get("amount", 0)
        recipient = transaction.parameters.get("recipient")
        
        print(f"🚨 Favqulodda mablag' yechib olinmoqda:")
        print(f"   Miqdor: {amount}")
        print(f"   Oluvchi: {recipient}")
        
        await asyncio.sleep(0.1)
    
    def get_transaction_status(self, tx_id: str) -> Dict:
        """Tranzaksiya holatini olish"""
        
        # Pending transactionlarni tekshirish
        if tx_id in self.pending_transactions:
            tx = self.pending_transactions[tx_id]
            return {
                "status": tx.status.value,
                "signatures": len(tx.signatures),
                "required": tx.required_signatures,
                "expires_at": tx.expires_at,
                "created_at": tx.created_at
            }
        
        # Completed transactionlarni tekshirish
        if tx_id in self.completed_transactions:
            tx = self.completed_transactions[tx_id]
            return {
                "status": tx.status.value,
                "signatures": len(tx.signatures),
                "executed_at": tx.executed_at,
                "created_at": tx.created_at
            }
        
        return {"error": "Tranzaksiya topilmadi"}
    
    async def cancel_transaction(self, tx_id: str, reason: str = "") -> bool:
        """Tranzaksiyani bekor qilish"""
        
        if tx_id not in self.pending_transactions:
            return False
        
        tx = self.pending_transactions[tx_id]
        tx.status = SignatureStatus.CANCELLED
        
        print(f"❌ Tranzaksiya bekor qilindi: {tx_id}")
        print(f"   Sabab: {reason}")
        
        return True
    
    def get_active_validators(self) -> List[ValidatorInfo]:
        """Faol validatorlarni olish"""
        return [v for v in self.validators if v.is_active]
    
    def add_validator(self, validator: ValidatorInfo) -> bool:
        """Yangi validator qo'shish"""
        
        # Takrorlanishni tekshirish
        if any(v.address == validator.address for v in self.validators):
            return False
        
        self.validators.append(validator)
        print(f"✅ Yangi validator qo'shildi: {validator.address}")
        
        return True
    
    def remove_validator(self, validator_address: str) -> bool:
        """Validatorni olib tashlash"""
        
        validator = next((v for v in self.validators if v.address == validator_address), None)
        if validator:
            self.validators.remove(validator)
            print(f"❌ Validator olib tashlandi: {validator_address}")
            return True
        
        return False
    
    def get_system_stats(self) -> Dict:
        """Tizim statistikasini olish"""
        
        total_validators = len(self.validators)
        active_validators = len(self.get_active_validators())
        pending_txs = len(self.pending_transactions)
        completed_txs = len(self.completed_transactions)
        
        total_stake = sum(v.stake_amount for v in self.validators)
        avg_reputation = sum(v.reputation_score for v in self.validators) / total_validators
        
        return {
            "total_validators": total_validators,
            "active_validators": active_validators,
            "pending_transactions": pending_txs,
            "completed_transactions": completed_txs,
            "total_stake": total_stake,
            "average_reputation": avg_reputation,
            "emergency_actions": len(self.emergency_actions)
        }

class EmergencyProtocol:
    """Favqulodda protokollar"""
    
    def __init__(self, multi_sig: MultiSigValidator):
        self.multi_sig = multi_sig
        self.emergency_conditions = {
            "bridge_failure_rate": 0.05,
            "gas_price_spike": 5.0,
            "validator_offline_ratio": 0.3,
            "slashing_threshold": 0.01
        }
    
    async def check_emergency_conditions(self) -> Dict:
        """Favqulodda shartlarni tekshirish"""
        alerts = []
        
        # Bridge failure rate check
        # Simulated check
        if 0.06 > self.emergency_conditions["bridge_failure_rate"]:
            alerts.append({
                "type": "high_failure_rate",
                "message": "Bridge failure rate juda yuqori",
                "severity": "critical"
            })
        
        # Gas price spike check
        # Simulated check
        if 6.0 > self.emergency_conditions["gas_price_spike"]:
            alerts.append({
                "type": "gas_price_spike",
                "message": "Gas narxlari juda ko'p ko'tarildi",
                "severity": "warning"
            })
        
        # Validator offline ratio check
        active_validators = self.multi_sig.get_active_validators()
        total_validators = len(self.multi_sig.validators)
        
        if len(active_validators) / total_validators < (1 - self.emergency_conditions["validator_offline_ratio"]):
            alerts.append({
                "type": "validator_offline",
                "message": "Ko'p validatorlar offline",
                "severity": "warning"
            })
        
        return {"alerts": alerts, "needs_emergency": len([a for a in alerts if a["severity"] == "critical"]) > 0}
    
    async def initiate_emergency_pause(self, reason: str) -> str:
        """Favqulodda to'xtatish boshlash"""
        
        # Emergency pause transaction yaratish
        tx_id = await self.multi_sig.initiate_transaction(
            action_type=ActionType.PAUSE_SYSTEM,
            initiator="emergency_protocol",
            parameters={"reason": reason},
            private_key="emergency_key"
        )
        
        print(f"🚨 Favqulodda to'xtatish boshlаndi: {reason}")
        print(f"   Tranzaksiya ID: {tx_id}")
        
        return tx_id
    
    async def emergency_withdraw_funds(self, amount: int, recipient: str, reason: str) -> str:
        """Favqulodda mablag' yechib olish"""
        
        tx_id = await self.multi_sig.initiate_transaction(
            action_type=ActionType.EMERGENCY_WITHDRAW,
            initiator="emergency_protocol",
            parameters={
                "amount": amount,
                "recipient": recipient,
                "reason": reason
            },
            private_key="emergency_key"
        )
        
        print(f"🚨 Favqulodda mablag' yechib olish: {amount} -> {recipient}")
        print(f"   Sabab: {reason}")
        
        return tx_id