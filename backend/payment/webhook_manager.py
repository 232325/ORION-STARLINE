"""
Webhook Manager
Webhook integrations va event notifications

Xususiyatlar:
- Webhook subscription management
- Event filtering va routing
- Retry logic with exponential backoff
- Webhook verification (signatures)
- Event history va logs
- Multiple destinations support
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import hashlib
import hmac
import logging
from decimal import Decimal
import asyncio

logger = logging.getLogger(__name__)


class WebhookEvent(Enum):
    """Webhook event turlari"""
    # Trading events
    TRADE_OPENED = "trade.opened"
    TRADE_CLOSED = "trade.closed"
    TRADE_UPDATED = "trade.updated"
    TRADE_CANCELLED = "trade.cancelled"
    TRADE_PARTIALLY_FILLED = "trade.partially_filled"
    
    # Order events
    ORDER_CREATED = "order.created"
    ORDER_FILLED = "order.filled"
    ORDER_CANCELED = "order.canceled"
    ORDER_PARTIALLY_FILLED = "order.partially_filled"
    ORDER_REJECTED = "order.rejected"
    
    # Account events
    BALANCE_UPDATED = "balance.updated"
    DEPOSIT_RECEIVED = "deposit.received"
    WITHDRAWAL_COMPLETED = "withdrawal.completed"
    WITHDRAWAL_REQUESTED = "withdrawal.requested"
    ACCOUNT_VERIFIED = "account.verified"
    ACCOUNT_SUSPENDED = "account.suspended"
    
    # Alert events
    PRICE_ALERT = "price.alert"
    RISK_ALERT = "risk.alert"
    STRATEGY_ALERT = "strategy.alert"
    MARGIN_CALL = "margin.call"
    LIQUIDATION_WARNING = "liquidation.warning"
    
    # Payment events
    PAYMENT_SUCCEEDED = "payment.succeeded"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_REFUNDED = "payment.refunded"
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_UPDATED = "subscription.updated"
    SUBSCRIPTION_CANCELED = "subscription.canceled"
    
    # Metal trading events
    METAL_PRICE_UPDATED = "metal.price.updated"
    METAL_POSITION_OPENED = "metal.position.opened"
    METAL_POSITION_CLOSED = "metal.position.closed"
    METAL_DELIVERY_SCHEDULED = "metal.delivery.scheduled"
    METAL_DELIVERY_COMPLETED = "metal.delivery.completed"
    
    # Quantum trading events
    QUANTUM_STRATEGY_ACTIVATED = "quantum.strategy.activated"
    QUANTUM_ANALYSIS_COMPLETED = "quantum.analysis.completed"
    QUANTUM_OPTIMIZATION_RUN = "quantum.optimization.run"
    QUANTUM_BACKTEST_FINISHED = "quantum.backtest.finished"
    
    # HFT events
    HFT_EXECUTION_COMPLETED = "hft.execution.completed"
    LATENCY_THRESHOLD_EXCEEDED = "latency.threshold.exceeded"
    ARBITRAGE_OPPORTUNITY_DETECTED = "arbitrage.opportunity.detected"
    MARKET_MAKING_STATUS_CHANGED = "market_making.status.changed"
    
    # NFT events
    NFT_MINTED = "nft.minted"
    NFT_TRANSFERRED = "nft.transferred"
    NFT_LISTED = "nft.listed"
    NFT_SOLD = "nft.sold"
    
    # DAO governance events
    DAO_PROPOSAL_CREATED = "dao.proposal.created"
    DAO_VOTE_CAST = "dao.vote.cast"
    DAO_PROPOSAL_APPROVED = "dao.proposal.approved"
    DAO_TREASURY_TRANSACTION = "dao.treasury.transaction"
    
    # AI/ML events
    MODEL_TRAINED = "ai.model.trained"
    MODEL_PERFORMANCE_DROPPED = "ai.model.performance_dropped"
    SIGNAL_GENERATED = "ai.signal.generated"
    STRATEGY_OPTIMIZED = "ai.strategy.optimized"
    
    # Cross-chain events
    BRIDGE_TRANSACTION_INITIATED = "bridge.transaction.initiated"
    BRIDGE_TRANSACTION_COMPLETED = "bridge.transaction.completed"
    CHAIN_SWITCH_DETECTED = "chain.switch.detected"
    
    # Risk management events
    RISK_LIMIT_REACHED = "risk.limit.reached"
    DRAWDOWN_WARNING = "drawdown.warning"
    POSITION_SIZE_EXCEEDED = "position.size.exceeded"
    RISK_SCORE_CHANGED = "risk.score.changed"
    
    # Portfolio events
    PORTFOLIO_REBALANCED = "portfolio.rebalanced"
    ALLOCATION_UPDATED = "allocation.updated"
    PERFORMANCE_CALCULATED = "performance.calculated"
    
    # Market data events
    MARKET_OPENED = "market.opened"
    MARKET_CLOSED = "market.closed"
    VOLATILITY_SPIKE = "volatility.spike"
    LIQUIDITY_CHANGED = "liquidity.changed"
    
    # Economic events
    ECONOMIC_INDICATOR_UPDATED = "economic.indicator.updated"
    CYCLE_CHANGE_DETECTED = "cycle.change.detected"
    REGIME_SHIFT_DETECTED = "regime.shift.detected"
    
    # System events
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"
    SYSTEM_INFO = "system.info"
    SYSTEM_MAINTENANCE = "system.maintenance"
    API_RATE_LIMIT_EXCEEDED = "api.rate_limit.exceeded"


class WebhookStatus(Enum):
    """Webhook holati"""
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"
    FAILED = "failed"


class DeliveryStatus(Enum):
    """Delivery holati"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class WebhookSubscription:
    """Webhook subscription"""
    id: str
    user_id: str
    url: str
    events: List[WebhookEvent]
    status: WebhookStatus
    secret: str
    created_at: datetime
    description: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    retry_config: Dict[str, Any] = field(default_factory=lambda: {
        "max_retries": 3,
        "initial_delay": 1,
        "max_delay": 60,
        "backoff_multiplier": 2
    })
    failure_count: int = 0
    last_delivery_at: Optional[datetime] = None
    last_error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "url": self.url,
            "events": [e.value for e in self.events],
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "description": self.description,
            "failure_count": self.failure_count,
            "last_delivery_at": self.last_delivery_at.isoformat() if self.last_delivery_at else None,
            "last_error": self.last_error
        }


@dataclass
class WebhookDelivery:
    """Webhook delivery attempt"""
    id: str
    subscription_id: str
    event_type: WebhookEvent
    payload: Dict[str, Any]
    status: DeliveryStatus
    created_at: datetime
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "subscription_id": self.subscription_id,
            "event_type": self.event_type.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "response_code": self.response_code,
            "error_message": self.error_message,
            "retry_count": self.retry_count
        }


@dataclass
class WebhookEvent:
    """Webhook event data"""
    id: str
    type: WebhookEvent
    timestamp: datetime
    data: Dict[str, Any]
    user_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "user_id": self.user_id
        }


class WebhookManager:
    """
    Webhook Manager
    
    Webhook subscriptions, event routing, delivery management
    """
    
    def __init__(self):
        self.subscriptions: Dict[str, WebhookSubscription] = {}
        self.deliveries: Dict[str, WebhookDelivery] = {}
        self.event_history: List[WebhookEvent] = []
        
        # Event handlers (for internal processing)
        self.event_handlers: Dict[WebhookEvent, List[Callable]] = {}
        
        logger.info("WebhookManager initialized")
    
    async def create_subscription(
        self,
        user_id: str,
        url: str,
        events: List[WebhookEvent],
        description: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> WebhookSubscription:
        """
        Webhook subscription yaratish
        
        Args:
            user_id: Foydalanuvchi ID
            url: Webhook URL
            events: Subscribe qilinadigan eventlar
            description: Tavsif
            headers: Qo'shimcha HTTP headerlar
        
        Returns:
            WebhookSubscription obyekti
        """
        import uuid
        import secrets
        
        # Generate secret for signature verification
        secret = secrets.token_urlsafe(32)
        
        subscription = WebhookSubscription(
            id=f"webhook_{uuid.uuid4().hex[:16]}",
            user_id=user_id,
            url=url,
            events=events,
            status=WebhookStatus.ACTIVE,
            secret=secret,
            created_at=datetime.now(),
            description=description,
            headers=headers or {}
        )
        
        self.subscriptions[subscription.id] = subscription
        
        logger.info(f"Webhook subscription created: {subscription.id} - URL: {url}")
        
        return subscription
    
    async def update_subscription(
        self,
        subscription_id: str,
        url: Optional[str] = None,
        events: Optional[List[WebhookEvent]] = None,
        status: Optional[WebhookStatus] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> WebhookSubscription:
        """Subscription yangilash"""
        if subscription_id not in self.subscriptions:
            raise ValueError(f"Subscription not found: {subscription_id}")
        
        subscription = self.subscriptions[subscription_id]
        
        if url:
            subscription.url = url
        if events:
            subscription.events = events
        if status:
            subscription.status = status
        if headers:
            subscription.headers = headers
        
        logger.info(f"Webhook subscription updated: {subscription_id}")
        
        return subscription
    
    async def delete_subscription(self, subscription_id: str) -> bool:
        """Subscription o'chirish"""
        if subscription_id not in self.subscriptions:
            raise ValueError(f"Subscription not found: {subscription_id}")
        
        del self.subscriptions[subscription_id]
        
        logger.info(f"Webhook subscription deleted: {subscription_id}")
        
        return True
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """
        Webhook signature yaratish (HMAC-SHA256)
        
        Args:
            payload: JSON payload string
            secret: Shared secret
        
        Returns:
            Signature string
        """
        signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    async def trigger_event(
        self,
        event_type: WebhookEvent,
        data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> List[WebhookDelivery]:
        """
        Event trigger qilish va webhook yuborish
        
        Args:
            event_type: Event turi
            data: Event ma'lumotlari
            user_id: Foydalanuvchi ID (optional, filter uchun)
        
        Returns:
            WebhookDelivery obyektlari ro'yxati
        """
        import uuid
        
        # Create event record
        event = WebhookEvent(
            id=f"event_{uuid.uuid4().hex[:16]}",
            type=event_type,
            timestamp=datetime.now(),
            data=data,
            user_id=user_id
        )
        
        self.event_history.append(event)
        
        # Find matching subscriptions
        matching_subs = [
            sub for sub in self.subscriptions.values()
            if (sub.status == WebhookStatus.ACTIVE and
                event_type in sub.events and
                (user_id is None or sub.user_id == user_id))
        ]
        
        # Trigger internal handlers
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    await handler(event.to_dict())
                except Exception as e:
                    logger.error(f"Event handler error: {e}")
        
        # Send webhooks
        deliveries = []
        for subscription in matching_subs:
            delivery = await self._send_webhook(subscription, event)
            deliveries.append(delivery)
        
        logger.info(f"Event triggered: {event_type.value} - {len(deliveries)} webhooks sent")
        
        return deliveries
    
    async def _send_webhook(
        self,
        subscription: WebhookSubscription,
        event: WebhookEvent
    ) -> WebhookDelivery:
        """
        Webhook yuborish
        
        Args:
            subscription: WebhookSubscription
            event: WebhookEvent
        
        Returns:
            WebhookDelivery obyekti
        """
        import uuid
        
        # Prepare payload
        payload = {
            "event": event.to_dict(),
            "subscription_id": subscription.id
        }
        
        payload_str = json.dumps(payload, default=str)
        
        # Generate signature
        signature = self._generate_signature(payload_str, subscription.secret)
        
        # Create delivery record
        delivery = WebhookDelivery(
            id=f"delivery_{uuid.uuid4().hex[:16]}",
            subscription_id=subscription.id,
            event_type=event.type,
            payload=payload,
            status=DeliveryStatus.PENDING,
            created_at=datetime.now()
        )
        
        self.deliveries[delivery.id] = delivery
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": event.type.value,
            "X-Webhook-Delivery-ID": delivery.id,
            **subscription.headers
        }
        
        # Simulate sending (in real implementation, use aiohttp)
        try:
            delivery.status = DeliveryStatus.SENT
            delivery.sent_at = datetime.now()
            
            # Simulate HTTP request
            # In real implementation:
            # async with aiohttp.ClientSession() as session:
            #     async with session.post(subscription.url, json=payload, headers=headers) as response:
            #         delivery.response_code = response.status
            #         delivery.response_body = await response.text()
            
            # Simulate success
            delivery.status = DeliveryStatus.DELIVERED
            delivery.delivered_at = datetime.now()
            delivery.response_code = 200
            
            # Update subscription
            subscription.last_delivery_at = datetime.now()
            subscription.failure_count = 0
            
        except Exception as e:
            delivery.status = DeliveryStatus.FAILED
            delivery.error_message = str(e)
            
            # Update subscription
            subscription.failure_count += 1
            subscription.last_error = str(e)
            
            # Schedule retry
            if delivery.retry_count < subscription.retry_config["max_retries"]:
                await self._schedule_retry(delivery, subscription)
            else:
                # Too many failures - disable subscription
                if subscription.failure_count >= 10:
                    subscription.status = WebhookStatus.DISABLED
                    logger.warning(f"Subscription disabled due to failures: {subscription.id}")
        
        return delivery
    
    async def _schedule_retry(
        self,
        delivery: WebhookDelivery,
        subscription: WebhookSubscription
    ):
        """Retry schedule qilish (exponential backoff)"""
        delivery.retry_count += 1
        delivery.status = DeliveryStatus.RETRYING
        
        # Calculate delay
        config = subscription.retry_config
        delay = min(
            config["initial_delay"] * (config["backoff_multiplier"] ** (delivery.retry_count - 1)),
            config["max_delay"]
        )
        
        logger.info(f"Scheduling retry {delivery.retry_count} for delivery {delivery.id} in {delay}s")
        
        # Schedule retry with delay
        asyncio.create_task(self._delayed_retry(delivery, subscription, delay))
    
    async def _delayed_retry(
        self,
        delivery: WebhookDelivery,
        subscription: WebhookSubscription,
        delay: float
    ):
        """Delayed retry"""
        await asyncio.sleep(delay)
        if delivery.status == DeliveryStatus.RETRYING:  # Still valid
            await self._retry_delivery(delivery, subscription)
    
    async def _retry_delivery(
        self,
        delivery: WebhookDelivery,
        subscription: WebhookSubscription
    ):
        """Delivery-ni qayta urinish"""
        logger.info(f"Retrying delivery {delivery.id} (attempt {delivery.retry_count + 1})")
        
        # Reset status for retry
        delivery.status = DeliveryStatus.PENDING
        delivery.sent_at = None
        delivery.delivered_at = None
        delivery.response_code = None
        delivery.response_body = None
        delivery.error_message = None
        
        # Re-prepare payload (same as original)
        event_data = delivery.payload["event"]
        event = WebhookEvent(
            id=event_data["id"],
            type=WebhookEvent(event_data["type"]),
            timestamp=datetime.fromisoformat(event_data["timestamp"]),
            data=event_data["data"],
            user_id=event_data.get("user_id")
        )
        
        # Re-prepare payload
        payload = {
            "event": event.to_dict(),
            "subscription_id": subscription.id
        }
        
        payload_str = json.dumps(payload, default=str)
        delivery.payload = payload
        
        # Generate signature again
        signature = self._generate_signature(payload_str, subscription.secret)
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": event.type.value,
            "X-Webhook-Delivery-ID": delivery.id,
            "X-Retry-Attempt": str(delivery.retry_count),
            **subscription.headers
        }
        
        # Try sending again
        try:
            delivery.status = DeliveryStatus.SENT
            delivery.sent_at = datetime.now()
            
            # Simulate HTTP request with retry
            # In real implementation:
            # async with aiohttp.ClientSession() as session:
            #     timeout = aiohttp.ClientTimeout(total=30)
            #     async with session.post(
            #         subscription.url, 
            #         json=payload, 
            #         headers=headers,
            #         timeout=timeout
            #     ) as response:
            #         delivery.response_code = response.status
            #         delivery.response_body = await response.text()
            
            # Simulate improved success rate for retries
            success_probability = min(0.3 + (delivery.retry_count * 0.2), 0.8)
            import random
            if random.random() < success_probability:
                # Success
                delivery.status = DeliveryStatus.DELIVERED
                delivery.delivered_at = datetime.now()
                delivery.response_code = 200
                
                # Update subscription
                subscription.last_delivery_at = datetime.now()
                subscription.failure_count = 0
                subscription.last_error = None
                
                logger.info(f"Retry successful for delivery {delivery.id}")
            else:
                raise Exception("Simulated retry failure")
            
        except Exception as e:
            delivery.status = DeliveryStatus.FAILED
            delivery.error_message = str(e)
            
            # Update subscription
            subscription.failure_count += 1
            subscription.last_error = f"Retry {delivery.retry_count}: {str(e)}"
            
            # Schedule another retry if under limit
            if delivery.retry_count < subscription.retry_config["max_retries"]:
                await self._schedule_retry(delivery, subscription)
            else:
                # Max retries reached - mark as permanently failed
                if subscription.failure_count >= 10:
                    subscription.status = WebhookStatus.DISABLED
                    logger.warning(f"Subscription disabled due to retry failures: {subscription.id}")
        
        return delivery
    
    async def get_subscription(self, subscription_id: str) -> Optional[WebhookSubscription]:
        """Subscription olish"""
        return self.subscriptions.get(subscription_id)
    
    async def get_user_subscriptions(self, user_id: str) -> List[WebhookSubscription]:
        """Foydalanuvchi subscription-larini olish"""
        return [
            sub for sub in self.subscriptions.values()
            if sub.user_id == user_id
        ]
    
    async def get_delivery(self, delivery_id: str) -> Optional[WebhookDelivery]:
        """Delivery ma'lumotlarini olish"""
        return self.deliveries.get(delivery_id)
    
    async def get_subscription_deliveries(
        self,
        subscription_id: str,
        status: Optional[DeliveryStatus] = None,
        limit: int = 100
    ) -> List[WebhookDelivery]:
        """Subscription uchun delivery tarixini olish"""
        deliveries = [
            d for d in self.deliveries.values()
            if d.subscription_id == subscription_id
        ]
        
        if status:
            deliveries = [d for d in deliveries if d.status == status]
        
        # Sort by created_at descending
        deliveries.sort(key=lambda x: x.created_at, reverse=True)
        
        return deliveries[:limit]
    
    async def get_event_history(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[WebhookEvent] = None,
        limit: int = 100
    ) -> List[WebhookEvent]:
        """Event tarixini olish"""
        events = self.event_history
        
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        
        if event_type:
            events = [e for e in events if e.type == event_type]
        
        # Sort by timestamp descending
        events.sort(key=lambda x: x.timestamp, reverse=True)
        
        return events[:limit]
    
    async def test_webhook(self, subscription_id: str) -> WebhookDelivery:
        """
        Webhook test qilish
        
        Args:
            subscription_id: Subscription ID
        
        Returns:
            Test delivery
        """
        if subscription_id not in self.subscriptions:
            raise ValueError(f"Subscription not found: {subscription_id}")
        
        subscription = self.subscriptions[subscription_id]
        
        # Create test event
        import uuid
        test_event = WebhookEvent(
            id=f"test_{uuid.uuid4().hex[:8]}",
            type=WebhookEvent.SYSTEM_INFO,
            timestamp=datetime.now(),
            data={
                "message": "This is a test webhook",
                "subscription_id": subscription_id
            },
            user_id=subscription.user_id
        )
        
        # Send webhook
        delivery = await self._send_webhook(subscription, test_event)
        
        logger.info(f"Test webhook sent: {subscription_id}")
        
        return delivery
    
    def register_handler(
        self,
        event_type: WebhookEvent,
        handler: Callable
    ):
        """
        Internal event handler qo'shish
        
        Args:
            event_type: Event turi
            handler: Handler funksiyasi (async)
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        
        logger.info(f"Event handler registered: {event_type.value}")
    
    async def retry_failed_deliveries(
        self,
        subscription_id: Optional[str] = None,
        max_retry_attempts: int = 3
    ) -> List[WebhookDelivery]:
        """
        Failed deliverylarni qayta urinish
        
        Args:
            subscription_id: Faqat shu subscription uchun (optional)
            max_retry_attempts: Maksimal retry urinishlari
        
        Returns:
            Retry qilingan deliverylar
        """
        failed = [
            d for d in self.deliveries.values()
            if d.status == DeliveryStatus.FAILED and
            d.retry_count < max_retry_attempts and
            (subscription_id is None or d.subscription_id == subscription_id)
        ]
        
        retried = []
        for delivery in failed:
            subscription = self.subscriptions.get(delivery.subscription_id)
            if subscription and subscription.status == WebhookStatus.ACTIVE:
                await self._retry_delivery(delivery, subscription)
                retried.append(delivery)
        
        logger.info(f"Retried {len(retried)} failed deliveries for {subscription_id or 'all subscriptions'}")
        
        return retried
    
    async def get_failed_deliveries(
        self,
        subscription_id: Optional[str] = None,
        days: int = 7
    ) -> List[WebhookDelivery]:
        """
        Failed deliverylarni olish
        
        Args:
            subscription_id: Subscription ID (optional)
            days: So'nggi necha kunlik failed deliverylar
        
        Returns:
            Failed deliverylar ro'yxati
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        failed = [
            d for d in self.deliveries.values()
            if d.status == DeliveryStatus.FAILED and
            d.created_at >= cutoff_date and
            (subscription_id is None or d.subscription_id == subscription_id)
        ]
        
        # Sort by created_at descending
        failed.sort(key=lambda x: x.created_at, reverse=True)
        
        return failed
    
    async def mark_delivery_as_permanently_failed(
        self,
        delivery_id: str,
        reason: str
    ) -> bool:
        """
        Delivery-ni doimiy ravishda failed deb belgilash
        
        Args:
            delivery_id: Delivery ID
            reason: Sabab
        
        Returns:
            True agar muvaffaqiyatli bo'lsa
        """
        if delivery_id not in self.deliveries:
            return False
        
        delivery = self.deliveries[delivery_id]
        delivery.status = DeliveryStatus.FAILED
        delivery.error_message = f"Permanently failed: {reason}"
        
        # Update subscription failure count
        subscription = self.subscriptions.get(delivery.subscription_id)
        if subscription:
            subscription.failure_count += 1
            subscription.last_error = reason
            
            # Disable if too many failures
            if subscription.failure_count >= 10:
                subscription.status = WebhookStatus.DISABLED
        
        logger.warning(f"Delivery {delivery_id} marked as permanently failed: {reason}")
        
        return True
    
    async def bulk_retry_deliveries(
        self,
        delivery_ids: List[str],
        parallel: bool = True
    ) -> Dict[str, WebhookDelivery]:
        """
        Ko'plab deliverylarni parallel ravishda retry qilish
        
        Args:
            delivery_ids: Delivery IDlar ro'yxati
            parallel: Parallel processing qilish
        
        Returns:
            Retry natijalari dict tarzida
        """
        results = {}
        valid_deliveries = []
        
        # Filter valid failed deliveries
        for delivery_id in delivery_ids:
            delivery = self.deliveries.get(delivery_id)
            if delivery and delivery.status == DeliveryStatus.FAILED:
                subscription = self.subscriptions.get(delivery.subscription_id)
                if subscription and subscription.status == WebhookStatus.ACTIVE:
                    valid_deliveries.append((delivery, subscription))
        
        logger.info(f"Starting bulk retry for {len(valid_deliveries)} deliveries")
        
        if parallel:
            # Parallel retry
            import asyncio
            tasks = []
            for delivery, subscription in valid_deliveries:
                task = asyncio.create_task(self._retry_delivery(delivery, subscription))
                tasks.append((delivery.id, task))
            
            for delivery_id, task in tasks:
                try:
                    result = await task
                    results[delivery_id] = result
                except Exception as e:
                    logger.error(f"Bulk retry failed for {delivery_id}: {e}")
                    results[delivery_id] = None
        else:
            # Sequential retry
            for delivery, subscription in valid_deliveries:
                try:
                    result = await self._retry_delivery(delivery, subscription)
                    results[delivery.id] = result
                except Exception as e:
                    logger.error(f"Retry failed for {delivery.id}: {e}")
                    results[delivery.id] = None
        
        successful_retries = sum(1 for r in results.values() if r and r.status == DeliveryStatus.DELIVERED)
        logger.info(f"Bulk retry completed: {successful_retries}/{len(results)} successful")
        
        return results
    
    async def cleanup_old_deliveries(self, days: int = 30) -> int:
        """
        Eski deliverylarni tozalash
        
        Args:
            days: Necha kunlik deliverylarni saqlash
        
        Returns:
            O'chirilgan deliverylar soni
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Find old deliveries (only PENDING, SENT, DELIVERED)
        old_deliveries = [
            delivery_id for delivery_id, delivery in self.deliveries.items()
            if delivery.created_at < cutoff_date and
            delivery.status in [DeliveryStatus.DELIVERED, DeliveryStatus.FAILED]
        ]
        
        # Remove old deliveries
        for delivery_id in old_deliveries:
            del self.deliveries[delivery_id]
        
        logger.info(f"Cleaned up {len(old_deliveries)} old deliveries older than {days} days")
        
        return len(old_deliveries)
    
    def get_retry_statistics(self) -> Dict[str, Any]:
        """
        Retry statistikasini olish
        
        Returns:
            Retry statistikasi
        """
        total_deliveries = len(self.deliveries)
        retry_deliveries = sum(1 for d in self.deliveries.values() if d.retry_count > 0)
        permanently_failed = sum(
            1 for d in self.deliveries.values()
            if d.status == DeliveryStatus.FAILED and d.retry_count >= 3
        )
        
        # Retry success rate
        retried_and_successful = sum(
            1 for d in self.deliveries.values()
            if d.retry_count > 0 and d.status == DeliveryStatus.DELIVERED
        )
        retry_success_rate = (
            (retried_and_successful / retry_deliveries * 100)
            if retry_deliveries > 0 else 0
        )
        
        # Average retry count
        avg_retry_count = sum(d.retry_count for d in self.deliveries.values()) / total_deliveries if total_deliveries > 0 else 0
        
        # Most common errors
        error_counts = {}
        for delivery in self.deliveries.values():
            if delivery.error_message:
                error_type = delivery.error_message.split(":")[0] if ":" in delivery.error_message else delivery.error_message
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        return {
            "total_deliveries": total_deliveries,
            "retry_deliveries": retry_deliveries,
            "retried_and_successful": retried_and_successful,
            "permanently_failed": permanently_failed,
            "retry_success_rate": f"{retry_success_rate:.2f}%",
            "average_retry_count": f"{avg_retry_count:.2f}",
            "error_distribution": dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Webhook statistikasi"""
        total_deliveries = len(self.deliveries)
        
        delivered = sum(
            1 for d in self.deliveries.values()
            if d.status == DeliveryStatus.DELIVERED
        )
        
        failed = sum(
            1 for d in self.deliveries.values()
            if d.status == DeliveryStatus.FAILED
        )
        
        retrying = sum(
            1 for d in self.deliveries.values()
            if d.status == DeliveryStatus.RETRYING
        )
        
        pending = sum(
            1 for d in self.deliveries.values()
            if d.status == DeliveryStatus.PENDING
        )
        
        sent = sum(
            1 for d in self.deliveries.values()
            if d.status == DeliveryStatus.SENT
        )
        
        # Success rate
        success_rate = (delivered / total_deliveries * 100) if total_deliveries > 0 else 0
        
        # By event type
        by_event_type = {}
        for delivery in self.deliveries.values():
            event_type = delivery.event_type.value
            by_event_type[event_type] = by_event_type.get(event_type, 0) + 1
        
        # Subscription status distribution
        subscription_stats = {}
        for status in WebhookStatus:
            subscription_stats[status.value] = sum(
                1 for s in self.subscriptions.values() if s.status == status
            )
        
        # Active subscriptions
        active_subs = sum(
            1 for s in self.subscriptions.values()
            if s.status == WebhookStatus.ACTIVE
        )
        
        # Top event types by frequency
        top_events = dict(sorted(by_event_type.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Recent activity (last 24 hours)
        recent_deliveries = [
            d for d in self.deliveries.values()
            if d.created_at >= datetime.now() - timedelta(hours=24)
        ]
        
        # Failure reasons
        failure_reasons = {}
        for delivery in self.deliveries.values():
            if delivery.status == DeliveryStatus.FAILED and delivery.error_message:
                reason = delivery.error_message[:100]  # First 100 chars
                failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
        
        return {
            "total_subscriptions": len(self.subscriptions),
            "active_subscriptions": active_subs,
            "subscription_status_distribution": subscription_stats,
            "total_deliveries": total_deliveries,
            "delivered": delivered,
            "failed": failed,
            "retrying": retrying,
            "pending": pending,
            "sent": sent,
            "success_rate": f"{success_rate:.2f}%",
            "recent_deliveries_24h": len(recent_deliveries),
            "total_events": len(self.event_history),
            "deliveries_by_event_type": by_event_type,
            "top_event_types": top_events,
            "failure_reasons": dict(sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True)[:5]),
            "supported_events": [e.value for e in WebhookEvent],
            "retry_statistics": self.get_retry_statistics()
        }


# Example usage va testing
async def demo_webhook_manager():
    """
    Webhook Manager demo
    """
    manager = WebhookManager()
    
    # Subscription yaratish
    subscription = await manager.create_subscription(
        user_id="user123",
        url="https://example.com/webhook",
        events=[
            WebhookEvent.TRADE_OPENED,
            WebhookEvent.PRICE_ALERT,
            WebhookEvent.METAL_PRICE_UPDATED,
            WebhookEvent.QUANTUM_STRATEGY_ACTIVATED
        ],
        description="Trading alerts webhook"
    )
    
    print(f"Subscription created: {subscription.id}")
    
    # Event trigger qilish
    deliveries = await manager.trigger_event(
        event_type=WebhookEvent.TRADE_OPENED,
        data={
            "trade_id": "trade_123",
            "symbol": "EUR/USD",
            "side": "buy",
            "quantity": 1000,
            "price": 1.0950
        },
        user_id="user123"
    )
    
    print(f"Event triggered, {len(deliveries)} webhooks sent")
    
    # Test webhook
    test_delivery = await manager.test_webhook(subscription.id)
    print(f"Test webhook: {test_delivery.status.value}")
    
    # Statistics
    stats = manager.get_statistics()
    print(f"Success rate: {stats['success_rate']}")
    print(f"Total subscriptions: {stats['total_subscriptions']}")
    
    # Retry failed deliveries
    retried = await manager.retry_failed_deliveries(subscription.id)
    print(f"Retried {len(retried)} deliveries")


if __name__ == "__main__":
    asyncio.run(demo_webhook_manager())
