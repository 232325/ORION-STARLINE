"""
Cross-Chain Relay Network
Ko'p zanjirli relay tarmoqi va xabar yetkazish tizimi
"""

import asyncio
import json
import time
import hashlib
import hmac
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import aiohttp
import websockets
from concurrent.futures import ThreadPoolExecutor

class MessageType(Enum):
    """Xabar turlari"""
    STATE_PROOF = "state_proof"
    BRIDGE_REQUEST = "bridge_request"
    BRIDGE_RESPONSE = "bridge_response"
    ORACLE_UPDATE = "oracle_update"
    VALIDATOR_SLASH = "validator_slash"
    EMERGENCY_PAUSE = "emergency_pause"
    ASSET_PRICE = "asset_price"
    LIQUIDITY_UPDATE = "liquidity_update"

class RelayStatus(Enum):
    """Relay tugun holatlari"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SYNCING = "syncing"
    ERROR = "error"

@dataclass
class RelayNode:
    """Relay tugun ma'lumotlari"""
    node_id: str
    endpoint: str
    chains_supported: List[int]
    status: RelayStatus
    last_seen: int
    reputation_score: float
    total_messages: int
    successful_relays: int
    failed_relays: int

@dataclass
class RelayMessage:
    """Relay xabari"""
    message_id: str
    message_type: MessageType
    source_chain: int
    target_chain: int
    sender: str
    recipient: str
    payload: Dict
    timestamp: int
    signature: str
    requires_acknowledgment: bool = True

@dataclass
class ProofData:
    """Cross-chain proof ma'lumotlari"""
    proof_id: str
    source_chain: int
    target_chain: int
    contract_address: str
    state_root: str
    proof_data: str  # Merkle proof
    block_number: int
    block_hash: str
    timestamp: int

class CrossChainRelayNetwork:
    """Cross-chain relay tarmog'i"""
    
    def __init__(self):
        self.nodes = {}
        self.message_queue = {}
        self.proof_cache = {}
        self.subscribers = {}
        self.routing_table = {}
        
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Configuration
        self.max_retries = 3
        self.message_timeout = 30  # seconds
        self.proof_validity_period = 3600  # 1 hour
        self.min_reputation_score = 0.5
        
        # Initialize relay nodes
        self._initialize_relay_nodes()
    
    def _initialize_relay_nodes(self):
        """Relay tughunlarini ishga tushirish"""
        
        self.nodes = {
            "relay_1": RelayNode(
                node_id="relay_1",
                endpoint="wss://relay1.cross-chain.io",
                chains_supported=[1, 56, 137],
                status=RelayStatus.ACTIVE,
                last_seen=int(time.time()),
                reputation_score=0.95,
                total_messages=1000,
                successful_relays=980,
                failed_relays=20
            ),
            "relay_2": RelayNode(
                node_id="relay_2",
                endpoint="wss://relay2.cross-chain.io",
                chains_supported=[1, 42161, 10],
                status=RelayStatus.ACTIVE,
                last_seen=int(time.time()),
                reputation_score=0.92,
                total_messages=850,
                successful_relays=825,
                failed_relays=25
            ),
            "relay_3": RelayNode(
                node_id="relay_3",
                endpoint="wss://relay3.cross-chain.io",
                chains_supported=[56, 137, 42161],
                status=RelayStatus.ACTIVE,
                last_seen=int(time.time()),
                reputation_score=0.88,
                total_messages=650,
                successful_relays=620,
                failed_relays=30
            ),
            "relay_backup": RelayNode(
                node_id="relay_backup",
                endpoint="wss://relay-backup.cross-chain.io",
                chains_supported=[1, 56, 137, 42161, 10],
                status=RelayStatus.ACTIVE,
                last_seen=int(time.time()),
                reputation_score=0.85,
                total_messages=300,
                successful_relays=285,
                failed_relays=15
            )
        }
        
        print(f"✅ {len(self.nodes)} relay tugun ishga tushirildi")
    
    async def register_subscriber(self, chain_id: int, callback: Callable):
        """Subscriber ro'yxatga olish"""
        
        if chain_id not in self.subscribers:
            self.subscribers[chain_id] = []
        
        self.subscribers[chain_id].append(callback)
        
        print(f"📡 Subscriber ro'yxatga olindi: Chain {chain_id}")
    
    async def relay_message(self, message: RelayMessage) -> bool:
        """Xabarni relay qilish"""
        
        try:
            # Relay tugunini tanlash
            target_node = self._select_best_relay_node(message.target_chain)
            
            if not target_node:
                self.logger.error("Mos relay tugun topilmadi")
                return False
            
            # Xabarni queue ga qo'shish
            if target_node.node_id not in self.message_queue:
                self.message_queue[target_node.node_id] = []
            
            self.message_queue[target_node.node_id].append(message)
            
            # Async relay qilish
            asyncio.create_task(self._process_message_queue(target_node.node_id))
            
            print(f"📨 Xabar relay qilindi: {message.message_id}")
            print(f"   Maqsad tugun: {target_node.node_id}")
            print(f"   Manba zanjir: {message.source_chain}")
            print(f"   Maqsad zanjir: {message.target_chain}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Relay qilishda xatolik: {e}")
            return False
    
    def _select_best_relay_node(self, target_chain: int) -> Optional[RelayNode]:
        """Eng yaxshi relay tugunni tanlash"""
        
        # Target chain'ni qo'llab-quvvatlaydigan tugunlarni filtrlash
        suitable_nodes = [
            node for node in self.nodes.values()
            if target_chain in node.chains_supported and node.status == RelayStatus.ACTIVE
        ]
        
        if not suitable_nodes:
            return None
        
        # Reputation score bo'yicha saralash
        suitable_nodes.sort(key=lambda x: x.reputation_score, reverse=True)
        
        # Success rate hisoblash
        for node in suitable_nodes:
            if node.total_messages > 0:
                success_rate = node.successful_relays / node.total_messages
                if success_rate > 0.8 and node.reputation_score > self.min_reputation_score:
                    return node
        
        # Fallback - eng yuqori reputation
        return suitable_nodes[0] if suitable_nodes else None
    
    async def _process_message_queue(self, node_id: str):
        """Xabar queue'sini qayta ishlash"""
        
        if node_id not in self.message_queue:
            return
        
        queue = self.message_queue[node_id]
        node = self.nodes[node_id]
        
        while queue:
            message = queue.pop(0)
            
            try:
                # Xabarni yuborish
                success = await self._send_message_to_node(node, message)
                
                # Statistikani yangilash
                node.total_messages += 1
                if success:
                    node.successful_relays += 1
                else:
                    node.failed_relays += 1
                    node.reputation_score = max(0.1, node.reputation_score - 0.01)
                
                node.last_seen = int(time.time())
                
                # Acknowledgment kutish
                if message.requires_acknowledgment:
                    await self._wait_for_acknowledgment(message.message_id)
                
            except Exception as e:
                self.logger.error(f"Xabar qayta ishlashda xatolik: {e}")
                node.failed_relays += 1
                node.reputation_score = max(0.1, node.reputation_score - 0.05)
    
    async def _send_message_to_node(self, node: RelayNode, message: RelayMessage) -> bool:
        """Tugunga xabar yuborish"""
        
        try:
            # Simulated WebSocket connection
            # Haqiqiy implementatsiyada websockets kutib olish kerak
            
            message_data = {
                "message_id": message.message_id,
                "message_type": message.message_type.value,
                "source_chain": message.source_chain,
                "target_chain": message.target_chain,
                "sender": message.sender,
                "recipient": message.recipient,
                "payload": message.payload,
                "timestamp": message.timestamp,
                "signature": message.signature
            }
            
            # Simulate network delay
            await asyncio.sleep(0.1)
            
            # Simulate success/failure (95% success rate)
            success = hash(message.message_id) % 100 < 95
            
            if success:
                print(f"✅ Xabar yuborildi: {node.node_id}")
            else:
                print(f"❌ Xabar yuborishda xatolik: {node.node_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Tugun bilan bog'lanishda xatolik: {e}")
            return False
    
    async def _wait_for_acknowledgment(self, message_id: str, timeout: int = 30):
        """Acknowledgment kutish"""
        
        start_time = int(time.time())
        
        while int(time.time()) - start_time < timeout:
            # Check if acknowledgment received
            # In real implementation, this would check a message store
            
            await asyncio.sleep(1)
        
        print(f"⏰ Acknowledgment kutish vaqti tugadi: {message_id}")
    
    async def verify_cross_chain_proof(self, proof: ProofData) -> bool:
        """Cross-chain proof'ni tekshirish"""
        
        try:
            # Proof ID yaratish
            proof_key = f"{proof.source_chain}_{proof.target_chain}_{proof.contract_address}"
            
            # Cache dan tekshirish
            if proof_key in self.proof_cache:
                cached_proof = self.proof_cache[proof_key]
                if int(time.time()) - cached_proof["timestamp"] < self.proof_validity_period:
                    return cached_proof["is_valid"]
            
            # Proof verification logic
            is_valid = await self._perform_proof_verification(proof)
            
            # Cache ga saqlash
            self.proof_cache[proof_key] = {
                "is_valid": is_valid,
                "timestamp": int(time.time()),
                "proof_data": proof
            }
            
            print(f"🔍 Proof tekshirildi: {is_valid}")
            
            return is_valid
            
        except Exception as e:
            self.logger.error(f"Proof verification xatolik: {e}")
            return False
    
    async def _perform_proof_verification(self, proof: ProofData) -> bool:
        """Proof verification bajarish"""
        
        try:
            # Simplified verification logic
            # Haqiqiy implementatsiyada Merkle proof verification kerak
            
            # Block number validation
            if proof.block_number < 0 or proof.block_number > 999999999:
                return False
            
            # Timestamp validation
            if proof.timestamp > int(time.time()):
                return False
            
            # Hash validation
            expected_hash = hashlib.sha256(
                f"{proof.state_root}_{proof.contract_address}_{proof.block_number}".encode()
            ).hexdigest()
            
            return proof.block_hash.startswith(expected_hash[:16])
            
        except Exception:
            return False
    
    async def send_state_proof(
        self,
        source_chain: int,
        target_chain: int,
        contract_address: str,
        state_data: Dict
    ) -> bool:
        """State proof yuborish"""
        
        try:
            # State root yaratish
            state_root = self._calculate_state_root(state_data)
            
            # Proof yaratish
            proof = ProofData(
                proof_id=f"proof_{int(time.time())}",
                source_chain=source_chain,
                target_chain=target_chain,
                contract_address=contract_address,
                state_root=state_root,
                proof_data=json.dumps(state_data),
                block_number=12345678,
                block_hash=hashlib.sha256(state_root.encode()).hexdigest(),
                timestamp=int(time.time())
            )
            
            # Relay message yaratish
            message = RelayMessage(
                message_id=f"msg_{int(time.time())}",
                message_type=MessageType.STATE_PROOF,
                source_chain=source_chain,
                target_chain=target_chain,
                sender="relay_network",
                recipient="contract",
                payload={
                    "proof": asdict(proof)
                },
                timestamp=int(time.time()),
                signature=self._sign_message(json.dumps(state_data))
            )
            
            # Relay qilish
            success = await self.relay_message(message)
            
            if success:
                print(f"✅ State proof yuborildi:")
                print(f"   Proof ID: {proof.proof_id}")
                print(f"   Source: Chain {source_chain}")
                print(f"   Target: Chain {target_chain}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"State proof yuborishda xatolik: {e}")
            return False
    
    def _calculate_state_root(self, state_data: Dict) -> str:
        """State root hisoblash"""
        data_str = json.dumps(state_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _sign_message(self, message: str) -> str:
        """Xabarni imzolash"""
        signature_key = "relay_signature_key_2025"
        signature = hmac.new(
            signature_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    async def broadcast_oracle_update(self, asset: str, price: float, source: str):
        """Oracle update tarqatish"""
        
        message = RelayMessage(
            message_id=f"oracle_{int(time.time())}",
            message_type=MessageType.ORACLE_UPDATE,
            source_chain=1,  # Ethereum
            target_chain=0,  # All chains
            sender="oracle_network",
            recipient="all",
            payload={
                "asset": asset,
                "price": price,
                "source": source,
                "timestamp": int(time.time())
            },
            timestamp=int(time.time()),
            signature=self._sign_message(f"{asset}:{price}:{source}")
        )
        
        # Barcha zanjirlar uchun broadcast
        for chain_id in [56, 137, 42161, 10]:
            message.target_chain = chain_id
            await self.relay_message(message)
        
        print(f"📡 Oracle update tarqatildi: {asset} = ${price}")
    
    async def notify_emergency_pause(self, reason: str, initiator: str):
        """Favqulodda to'xtatish haqida xabar"""
        
        message = RelayMessage(
            message_id=f"emergency_{int(time.time())}",
            message_type=MessageType.EMERGENCY_PAUSE,
            source_chain=1,
            target_chain=0,  # All chains
            sender=initiator,
            recipient="all_contracts",
            payload={
                "reason": reason,
                "initiator": initiator,
                "timestamp": int(time.time())
            },
            timestamp=int(time.time()),
            signature=self._sign_message(f"emergency:{reason}:{initiator}")
        )
        
        # Barcha zanjirlar uchun broadcast
        for chain_id in [56, 137, 42161, 10]:
            message.target_chain = chain_id
            await self.relay_message(message)
        
        print(f"🚨 Favqulodda xabar tarqatildi: {reason}")
    
    def get_network_stats(self) -> Dict:
        """Tarmoq statistikasini olish"""
        
        total_nodes = len(self.nodes)
        active_nodes = len([n for n in self.nodes.values() if n.status == RelayStatus.ACTIVE])
        
        total_messages = sum(n.total_messages for n in self.nodes.values())
        total_success = sum(n.successful_relays for n in self.nodes.values())
        total_fail = sum(n.failed_relays for n in self.nodes.values())
        
        success_rate = total_success / total_messages if total_messages > 0 else 0
        
        # Chains coverage
        supported_chains = set()
        for node in self.nodes.values():
            supported_chains.update(node.chains_supported)
        
        return {
            "total_nodes": total_nodes,
            "active_nodes": active_nodes,
            "total_messages": total_messages,
            "successful_messages": total_success,
            "failed_messages": total_fail,
            "success_rate": success_rate,
            "supported_chains": list(supported_chains),
            "message_queue_size": sum(len(queue) for queue in self.message_queue.values()),
            "proof_cache_size": len(self.proof_cache),
            "subscribers_count": sum(len(subs) for subs in self.subscribers.values())
        }
    
    def get_node_status(self) -> List[Dict]:
        """Barcha tugunlarning holati"""
        
        status_list = []
        
        for node in self.nodes.values():
            success_rate = node.successful_relays / node.total_messages if node.total_messages > 0 else 0
            
            status_list.append({
                "node_id": node.node_id,
                "endpoint": node.endpoint,
                "status": node.status.value,
                "reputation_score": node.reputation_score,
                "total_messages": node.total_messages,
                "success_rate": success_rate,
                "chains_supported": node.chains_supported,
                "last_seen": node.last_seen
            })
        
        return status_list
    
    async def health_check(self) -> Dict:
        """Tarmoq sog'lig'ini tekshirish"""
        
        health_status = {
            "overall_status": "healthy",
            "checks": {},
            "issues": []
        }
        
        # Active nodes check
        active_nodes = [n for n in self.nodes.values() if n.status == RelayStatus.ACTIVE]
        health_status["checks"]["active_nodes"] = len(active_nodes) / len(self.nodes)
        
        if health_status["checks"]["active_nodes"] < 0.8:
            health_status["issues"].append("Kam active tugun")
        
        # Message queue check
        total_queue_size = sum(len(queue) for queue in self.message_queue.values())
        if total_queue_size > 100:
            health_status["issues"].append("Katta message queue")
        
        health_status["checks"]["message_queue"] = min(1.0, 100 / max(1, total_queue_size))
        
        # Success rate check
        total_messages = sum(n.total_messages for n in self.nodes.values())
        total_success = sum(n.successful_relays for n in self.nodes.values())
        overall_success_rate = total_success / total_messages if total_messages > 0 else 1.0
        
        health_status["checks"]["success_rate"] = overall_success_rate
        
        if overall_success_rate < 0.9:
            health_status["issues"].append("Past success rate")
        
        # Overall status determination
        if len(health_status["issues"]) == 0:
            health_status["overall_status"] = "healthy"
        elif len(health_status["issues"]) <= 2:
            health_status["overall_status"] = "warning"
        else:
            health_status["overall_status"] = "critical"
        
        return health_status
    
    def clear_cache(self):
        """Cache larni tozalash"""
        
        self.proof_cache.clear()
        self.message_queue.clear()
        
        print("🧹 Relay cache tozalandi")
    
    async def add_relay_node(self, node: RelayNode):
        """Yangi relay tugun qo'shish"""
        
        self.nodes[node.node_id] = node
        
        print(f"➕ Yangi relay tugun qo'shildi: {node.node_id}")
    
    async def remove_relay_node(self, node_id: str):
        """Relay tugunni olib tashlash"""
        
        if node_id in self.nodes:
            del self.nodes[node_id]
            print(f"➖ Relay tugun olib tashlandi: {node_id}")
    
    def get_supported_chains(self) -> List[int]:
        """Qo'llab-quvvatlanadigan zanjirlarni olish"""
        
        supported_chains = set()
        for node in self.nodes.values():
            supported_chains.update(node.chains_supported)
        
        return list(supported_chains)

# Global relay network instance
relay_network = CrossChainRelayNetwork()

async def initialize_relay_network():
    """Relay tarmog'ini ishga tushirish"""
    print("🌐 Cross-Chain Relay Network ishga tushirilmoqda...")
    # Tarmoq allaqachon initialize qilingan __init__ da
    print("✅ Relay tarmog'i tayyor")

async def relay_cross_chain_message(source_chain: int, target_chain: int, payload: Dict) -> bool:
    """Cross-chain xabar relay qilish"""
    
    message = RelayMessage(
        message_id=f"msg_{int(time.time())}",
        message_type=MessageType.BRIDGE_REQUEST,
        source_chain=source_chain,
        target_chain=target_chain,
        sender="app",
        recipient="bridge_contract",
        payload=payload,
        timestamp=int(time.time()),
        signature="demo_signature"
    )
    
    return await relay_network.relay_message(message)

async def verify_proof(source_chain: int, target_chain: int, contract_address: str, state_data: Dict) -> bool:
    """Cross-chain proof verification"""
    
    proof = ProofData(
        proof_id=f"proof_{int(time.time())}",
        source_chain=source_chain,
        target_chain=target_chain,
        contract_address=contract_address,
        state_root="demo_state_root",
        proof_data=json.dumps(state_data),
        block_number=12345678,
        block_hash="demo_hash",
        timestamp=int(time.time())
    )
    
    return await relay_network.verify_cross_chain_proof(proof)