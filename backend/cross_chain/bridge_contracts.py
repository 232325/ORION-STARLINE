"""
Cross-Chain Bridge Contracts
Ko'p zanjirli ko'prik tizimi uchun smart contract'lar
"""

import json
import asyncio
from typing import Dict, List, Optional
from web3 import Web3
from eth_account import Account
from dataclasses import dataclass
import time

@dataclass
class BridgeTransaction:
    """Ko'prik tranzaksiyasi ma'lumotlari"""
    tx_hash: str
    source_chain: str
    target_chain: str
    token_address: str
    amount: int
    recipient: str
    timestamp: int
    status: str  # 'pending', 'confirmed', 'completed', 'failed'
    proof_data: Optional[bytes] = None

class CrossChainBridge:
    """Asosiy ko'prik smart contract'i"""
    
    def __init__(self, chain_type: str, private_key: str):
        self.chain_type = chain_type
        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self.w3 = None
        self.contract = None
        self.initialized = False
    
    async def initialize(self):
        """Bridge contract'ni ishga tushirish"""
        try:
            # Web3 bog'lanish
            rpc_url = self._get_rpc_url()
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            # Contract ABIs va manzillarini yuklash
            self.contract = self._load_contract()
            
            # Manzilni tekshirish
            if not self.w3.is_connected():
                raise ConnectionError(f"{self.chain_type} zanjiriga bog'lanishda xatolik")
            
            self.initialized = True
            print(f"✅ {self.chain_type} bridge muvaffaqiyatli ishga tushirildi")
            
        except Exception as e:
            print(f"❌ {self.chain_type} bridge ishga tushirishda xatolik: {e}")
            raise
    
    def _get_rpc_url(self) -> str:
        """RPC URL olish"""
        rpc_urls = {
            "ethereum": "https://mainnet.infura.io/v3/",
            "bsc": "https://bsc-dataseed.binance.org/",
            "polygon": "https://polygon-rpc.com/",
            "arbitrum": "https://arb1.arbitrum.io/rpc",
            "optimism": "https://mainnet.optimism.io"
        }
        return rpc_urls.get(self.chain_type, "")
    
    def _load_contract(self):
        """Contract ABI va manzilni yuklash"""
        # Contract ABI (qisqartirilgan versiyasi)
        bridge_abi = [
            {
                "inputs": [
                    {"internalType": "address", "name": "token", "type": "address"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"},
                    {"internalType": "address", "name": "recipient", "type": "address"},
                    {"internalType": "uint256", "name": "targetChain", "type": "uint256"}
                ],
                "name": "bridgeTokens",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "address", "name": "token", "type": "address"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"},
                    {"internalType": "address", "name": "recipient", "type": "address"}
                ],
                "name": "mintWrappedTokens",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "pause",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "unpause",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "internalType": "address", "name": "token", "type": "address"},
                    {"indexed": True, "internalType": "address", "name": "from", "type": "address"},
                    {"indexed": True, "internalType": "address", "name": "to", "type": "address"},
                    {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"},
                    {"indexed": False, "internalType": "uint256", "name": "targetChain", "type": "uint256"}
                ],
                "name": "TokensBridged",
                "type": "event"
            }
        ]
        
        # Contract manzili (test uchun)
        contract_address = "0x742d35Cc6a12F8C71EdBD49E1a5d3f76E32C2c7d"
        
        return self.w3.eth.contract(address=contract_address, abi=bridge_abi)
    
    async def bridge_tokens(
        self,
        token_address: str,
        amount: int,
        recipient: str,
        target_chain_id: int
    ) -> str:
        """Tokenlarni boshqa zanjirga ko'chirish"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Bridge contract method
            bridge_function = self.contract.functions.bridgeTokens(
                token_address,
                amount,
                recipient,
                target_chain_id
            )
            
            # Gas estimate
            gas_estimate = bridge_function.estimate_gas({
                'from': self.account.address
            })
            
            # Transaction qurish
            transaction = bridge_function.build_transaction({
                'from': self.account.address,
                'gas': gas_estimate,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Tranzaksiyani imzolash va yuborish
            signed_txn = self.account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Tranzaksiya hashini qaytarish
            tx_hash_hex = self.w3.to_hex(tx_hash)
            
            print(f"✅ Bridge tranzaksiyasi yuborildi: {tx_hash_hex}")
            
            return tx_hash_hex
            
        except Exception as e:
            print(f"❌ Bridge tranzaksiyasida xatolik: {e}")
            raise
    
    async def mint_wrapped_tokens(
        self,
        token_address: str,
        amount: int,
        recipient: str
    ) -> str:
        """Wrapped token mint qilish (target chain)"""
        if not self.initialized:
            await self.initialize()
        
        try:
            mint_function = self.contract.functions.mintWrappedTokens(
                token_address,
                amount,
                recipient
            )
            
            gas_estimate = mint_function.estimate_gas({
                'from': self.account.address
            })
            
            transaction = mint_function.build_transaction({
                'from': self.account.address,
                'gas': gas_estimate,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            signed_txn = self.account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            tx_hash_hex = self.w3.to_hex(tx_hash)
            
            print(f"✅ Wrapped tokens minted: {tx_hash_hex}")
            
            return tx_hash_hex
            
        except Exception as e:
            print(f"❌ Mint tranzaksiyasida xatolik: {e}")
            raise
    
    async def get_transaction_status(self, tx_hash: str) -> Dict:
        """Tranzaksiya holatini tekshirish"""
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            if receipt is None:
                return {"status": "pending", "block_number": None}
            
            return {
                "status": "confirmed" if receipt.status == 1 else "failed",
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "logs": [log.dict() for log in receipt.logs]
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def pause_bridge(self) -> str:
        """Bridge'ni to'xtatib qo'yish (favqulodda)"""
        if not self.initialized:
            await self.initialize()
        
        try:
            pause_function = self.contract.functions.pause()
            
            transaction = pause_function.build_transaction({
                'from': self.account.address,
                'gas': 50000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            signed_txn = self.account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return self.w3.to_hex(tx_hash)
            
        except Exception as e:
            print(f"❌ Pause tranzaksiyasida xatolik: {e}")
            raise
    
    async def unpause_bridge(self) -> str:
        """Bridge'ni qayta ishga tushirish"""
        if not self.initialized:
            await self.initialize()
        
        try:
            unpause_function = self.contract.functions.unpause()
            
            transaction = unpause_function.build_transaction({
                'from': self.account.address,
                'gas': 50000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            signed_txn = self.account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return self.w3.to_hex(tx_hash)
            
        except Exception as e:
            print(f"❌ Unpause tranzaksiyasida xatolik: {e}")
            raise

class EthereumBSCBridge:
    """Ethereum-BSC ko'prik implementatsiyasi"""
    
    def __init__(self, private_key: str):
        self.eth_bridge = CrossChainBridge("ethereum", private_key)
        self.bsc_bridge = CrossChainBridge("bsc", private_key)
    
    async def initialize_both(self):
        """Ikkala bridge'ni ham ishga tushirish"""
        await asyncio.gather(
            self.eth_bridge.initialize(),
            self.bsc_bridge.initialize()
        )
    
    async def bridge_eth_to_bsc(
        self,
        amount: int,
        recipient: str
    ) -> BridgeTransaction:
        """ETH ni BSC ga ko'chirish"""
        # Ethereum da tokenlarni lock qilish
        eth_tx = await self.eth_bridge.bridge_tokens(
            token_address="0x0000000000000000000000000000000000000000",  # ETH
            amount=amount,
            recipient=recipient,
            target_chain_id=56  # BSC
        )
        
        # BSC da wrapped ETH mint qilish
        bsc_tx = await self.bsc_bridge.mint_wrapped_tokens(
            token_address="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",  # WETH
            amount=amount,
            recipient=recipient
        )
        
        return BridgeTransaction(
            tx_hash=eth_tx,
            source_chain="ethereum",
            target_chain="bsc",
            token_address="ETH",
            amount=amount,
            recipient=recipient,
            timestamp=int(time.time()),
            status="pending"
        )
    
    async def bridge_tokens_eth_to_bsc(
        self,
        token_address: str,
        amount: int,
        recipient: str
    ) -> BridgeTransaction:
        """Tokenlarni Ethereum dan BSC ga ko'chirish"""
        eth_tx = await self.eth_bridge.bridge_tokens(
            token_address=token_address,
            amount=amount,
            recipient=recipient,
            target_chain_id=56
        )
        
        return BridgeTransaction(
            tx_hash=eth_tx,
            source_chain="ethereum",
            target_chain="bsc",
            token_address=token_address,
            amount=amount,
            recipient=recipient,
            timestamp=int(time.time()),
            status="pending"
        )

class EthereumPolygonBridge:
    """Ethereum-Polygon ko'prik implementatsiyasi"""
    
    def __init__(self, private_key: str):
        self.eth_bridge = CrossChainBridge("ethereum", private_key)
        self.polygon_bridge = CrossChainBridge("polygon", private_key)
    
    async def initialize_both(self):
        """Ikkala bridge'ni ham ishga tushirish"""
        await asyncio.gather(
            self.eth_bridge.initialize(),
            self.polygon_bridge.initialize()
        )
    
    async def bridge_eth_to_polygon(
        self,
        amount: int,
        recipient: str
    ) -> BridgeTransaction:
        """ETH ni Polygon ga ko'chirish"""
        eth_tx = await self.eth_bridge.bridge_tokens(
            token_address="0x0000000000000000000000000000000000000000",
            amount=amount,
            recipient=recipient,
            target_chain_id=137  # Polygon
        )
        
        polygon_tx = await self.polygon_bridge.mint_wrapped_tokens(
            token_address="0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",  # WETH
            amount=amount,
            recipient=recipient
        )
        
        return BridgeTransaction(
            tx_hash=eth_tx,
            source_chain="ethereum",
            target_chain="polygon",
            token_address="ETH",
            amount=amount,
            recipient=recipient,
            timestamp=int(time.time()),
            status="pending"
        )

class MultiHopBridge:
    """Multi-hop bridging xususiyati"""
    
    def __init__(self, bridges: Dict[str, CrossChainBridge]):
        self.bridges = bridges
    
    async def multi_hop_bridge(
        self,
        source_chain: str,
        target_chain: str,
        token_address: str,
        amount: int,
        recipient: str,
        intermediate_chains: List[str]
    ) -> List[BridgeTransaction]:
        """Multi-hop bridging (ko'p oraliq zanjir orqali)"""
        
        transactions = []
        current_chain = source_chain
        remaining_amount = amount
        
        for intermediate_chain in intermediate_chains:
            # Current chain dan intermediate ga
            bridge = self.bridges[current_chain]
            
            if current_chain == "ethereum" and intermediate_chain == "bsc":
                tx = await bridge.bridge_tokens(token_address, remaining_amount, recipient, 56)
            elif current_chain == "ethereum" and intermediate_chain == "polygon":
                tx = await bridge.bridge_tokens(token_address, remaining_amount, recipient, 137)
            elif current_chain == "bsc" and intermediate_chain == "polygon":
                tx = await bridge.bridge_tokens(token_address, remaining_amount, recipient, 137)
            # ... boshqa kombinatsiyalar
            
            transactions.append(BridgeTransaction(
                tx_hash=tx,
                source_chain=current_chain,
                target_chain=intermediate_chain,
                token_address=token_address,
                amount=remaining_amount,
                recipient=recipient,
                timestamp=int(time.time()),
                status="pending"
            ))
            
            current_chain = intermediate_chain
        
        # Final hop to target chain
        final_bridge = self.bridges[current_chain]
        target_chain_id = {
            "bsc": 56,
            "polygon": 137,
            "arbitrum": 42161,
            "optimism": 10
        }.get(target_chain, 56)
        
        final_tx = await final_bridge.bridge_tokens(
            token_address,
            remaining_amount,
            recipient,
            target_chain_id
        )
        
        transactions.append(BridgeTransaction(
            tx_hash=final_tx,
            source_chain=current_chain,
            target_chain=target_chain,
            token_address=token_address,
            amount=remaining_amount,
            recipient=recipient,
            timestamp=int(time.time()),
            status="pending"
        ))
        
        return transactions

class AtomicSwapBridge:
    """Atomic swap protocol implementatsiyasi"""
    
    def __init__(self):
        self.swap_contracts = {}
    
    async def initiate_atomic_swap(
        self,
        source_chain: str,
        target_chain: str,
        token_a: str,
        token_b: str,
        amount_a: int,
        min_amount_b: int,
        recipient: str,
        timeout_blocks: int
    ) -> str:
        """Atomic swap boshlash"""
        
        # Atomic swap contract yaratish
        swap_data = {
            "token_a": token_a,
            "token_b": token_b,
            "amount_a": amount_a,
            "min_amount_b": min_amount_b,
            "recipient": recipient,
            "timeout_blocks": timeout_blocks,
            "initiator": "0x...",  # Your address
            "status": "initiated"
        }
        
        # Save swap data for tracking
        swap_id = f"swap_{int(time.time())}"
        self.swap_contracts[swap_id] = swap_data
        
        print(f"🔄 Atomic swap boshlandi: {swap_id}")
        
        return swap_id
    
    async def complete_atomic_swap(self, swap_id: str) -> bool:
        """Atomic swap tugallash"""
        
        if swap_id not in self.swap_contracts:
            raise ValueError("Swap topilmadi")
        
        swap_data = self.swap_contracts[swap_id]
        
        if swap_data["status"] != "initiated":
            raise ValueError("Swap holati noto'g'ri")
        
        # Swap completion logic
        print(f"✅ Atomic swap tugallandi: {swap_id}")
        
        swap_data["status"] = "completed"
        swap_data["completion_time"] = int(time.time())
        
        return True
    
    async def cancel_atomic_swap(self, swap_id: str) -> bool:
        """Atomic swap bekor qilish"""
        
        if swap_id not in self.swap_contracts:
            raise ValueError("Swap topilmadi")
        
        swap_data = self.swap_contracts[swap_id]
        
        if swap_data["status"] != "initiated":
            raise ValueError("Swap bekor qilinmaydi")
        
        print(f"❌ Atomic swap bekor qilindi: {swap_id}")
        
        swap_data["status"] = "cancelled"
        swap_data["cancellation_time"] = int(time.time())
        
        return True