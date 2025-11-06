"""
Futures & Options Trading - Leverage Management & Hedging Strategies
====================================================================

Futures va Options trading strategiyalari:
- Leverage position management
- Funding rate arbitrage
- Delta-neutral hedging
- Options strategies (covered call, protective put, straddle)
- Risk management (liquidation prevention)
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PositionSide(Enum):
    """Position yo'nalishi"""
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"


class OptionType(Enum):
    """Option turi"""
    CALL = "call"
    PUT = "put"


@dataclass
class FuturesPosition:
    """Futures pozitsiyasi"""
    symbol: str
    side: PositionSide
    entry_price: float
    size: float  # Contract size
    leverage: int
    margin: float
    liquidation_price: float
    unrealized_pnl: float = 0.0
    funding_rate: float = 0.0001  # 0.01%
    opened_at: datetime = None


@dataclass
class OptionPosition:
    """Option pozitsiyasi"""
    symbol: str
    option_type: OptionType
    strike_price: float
    expiry: datetime
    premium: float
    size: float  # Number of contracts
    current_value: float = 0.0
    delta: float = 0.0
    gamma: float = 0.0
    theta: float = 0.0
    vega: float = 0.0


class FuturesTradingStrategy:
    """
    Futures Trading Strategy
    
    Leverage bilan pozitsiya boshqaruvi, funding rate arbitrage,
    va risk management.
    """
    
    def __init__(
        self,
        max_leverage: int = 10,
        max_position_size: float = 10000.0,
        liquidation_buffer: float = 0.2  # 20% buffer
    ):
        self.max_leverage = max_leverage
        self.max_position_size = max_position_size
        self.liquidation_buffer = liquidation_buffer
        
        self.positions: List[FuturesPosition] = []
        self.closed_positions: List[Dict] = []
        
        self.total_margin = 0.0
        self.available_margin = 0.0
        self.total_pnl = 0.0
        
        logger.info(f"Futures Trading Strategy initialized")
        logger.info(f"Max leverage: {max_leverage}x, Max position: ${max_position_size:.2f}")
    
    def calculate_liquidation_price(
        self,
        entry_price: float,
        leverage: int,
        side: PositionSide
    ) -> float:
        """
        Liquidation narxini hisoblash
        
        Args:
            entry_price: Kirish narxi
            leverage: Leverage
            side: Position yo'nalishi
            
        Returns:
            Liquidation narxi
        """
        # Simplified liquidation formula
        # Long: liq_price = entry * (1 - 1/leverage + buffer)
        # Short: liq_price = entry * (1 + 1/leverage - buffer)
        
        liquidation_distance = (1 / leverage) - self.liquidation_buffer
        
        if side == PositionSide.LONG:
            liq_price = entry_price * (1 - liquidation_distance)
        else:  # SHORT
            liq_price = entry_price * (1 + liquidation_distance)
        
        return liq_price
    
    def calculate_required_margin(
        self,
        position_size: float,
        leverage: int
    ) -> float:
        """
        Kerakli margin hisoblash
        
        Args:
            position_size: Pozitsiya hajmi ($)
            leverage: Leverage
            
        Returns:
            Kerakli margin ($)
        """
        return position_size / leverage
    
    def calculate_optimal_leverage(
        self,
        volatility: float,
        risk_tolerance: float = 0.02  # 2% max loss
    ) -> int:
        """
        Optimal leverage hisoblash (volatility asosida)
        
        Args:
            volatility: Narx volatility (%)
            risk_tolerance: Risk tolerance (%)
            
        Returns:
            Optimal leverage
        """
        # Higher volatility = lower leverage
        # Formula: leverage = risk_tolerance / (volatility * safety_factor)
        safety_factor = 2.0
        
        optimal_leverage = int(risk_tolerance / (volatility / 100 * safety_factor))
        
        # Clamp to max leverage
        optimal_leverage = max(1, min(self.max_leverage, optimal_leverage))
        
        return optimal_leverage
    
    def open_position(
        self,
        symbol: str,
        side: PositionSide,
        entry_price: float,
        size: float,
        leverage: int
    ) -> Optional[FuturesPosition]:
        """
        Yangi pozitsiya ochish
        
        Args:
            symbol: Trading symbol
            side: LONG yoki SHORT
            entry_price: Kirish narxi
            size: Pozitsiya hajmi ($)
            leverage: Leverage
            
        Returns:
            Ochilgan pozitsiya yoki None
        """
        # Calculate required margin
        required_margin = self.calculate_required_margin(size, leverage)
        
        if required_margin > self.available_margin:
            logger.warning(f"Insufficient margin: required ${required_margin:.2f}, available ${self.available_margin:.2f}")
            return None
        
        # Calculate liquidation price
        liq_price = self.calculate_liquidation_price(entry_price, leverage, side)
        
        # Create position
        position = FuturesPosition(
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            size=size,
            leverage=leverage,
            margin=required_margin,
            liquidation_price=liq_price,
            opened_at=datetime.now()
        )
        
        self.positions.append(position)
        self.available_margin -= required_margin
        self.total_margin += required_margin
        
        logger.info(f"✅ Opened {side.value} position: {symbol}")
        logger.info(f"   Size: ${size:.2f}, Leverage: {leverage}x")
        logger.info(f"   Entry: ${entry_price:.2f}, Liquidation: ${liq_price:.2f}")
        logger.info(f"   Margin used: ${required_margin:.2f}")
        
        return position
    
    def update_position_pnl(
        self,
        position: FuturesPosition,
        current_price: float
    ):
        """
        Pozitsiya PnL yangilash
        
        Args:
            position: Pozitsiya
            current_price: Joriy narx
        """
        price_diff = current_price - position.entry_price
        
        if position.side == PositionSide.LONG:
            pnl = (price_diff / position.entry_price) * position.size * position.leverage
        else:  # SHORT
            pnl = -(price_diff / position.entry_price) * position.size * position.leverage
        
        position.unrealized_pnl = pnl
    
    def check_liquidation(
        self,
        position: FuturesPosition,
        current_price: float
    ) -> bool:
        """
        Liquidation tekshirish
        
        Args:
            position: Pozitsiya
            current_price: Joriy narx
            
        Returns:
            True agar liquidate qilinsa
        """
        if position.side == PositionSide.LONG:
            is_liquidated = current_price <= position.liquidation_price
        else:  # SHORT
            is_liquidated = current_price >= position.liquidation_price
        
        if is_liquidated:
            logger.warning(f"⚠️ Position LIQUIDATED: {position.symbol} {position.side.value}")
            logger.warning(f"   Liquidation price: ${position.liquidation_price:.2f}")
            logger.warning(f"   Current price: ${current_price:.2f}")
            
            # Close position with loss
            self.close_position(position, current_price, reason='liquidation')
        
        return is_liquidated
    
    def close_position(
        self,
        position: FuturesPosition,
        exit_price: float,
        reason: str = 'manual'
    ) -> Dict:
        """
        Pozitsiyani yopish
        
        Args:
            position: Yopiladigan pozitsiya
            exit_price: Chiqish narxi
            reason: Yopish sababi
            
        Returns:
            Yopilgan pozitsiya ma'lumotlari
        """
        # Calculate final PnL
        self.update_position_pnl(position, exit_price)
        final_pnl = position.unrealized_pnl
        
        # Calculate funding fees (simplified)
        # Assume funding every 8 hours
        holding_hours = (datetime.now() - position.opened_at).total_seconds() / 3600
        funding_periods = int(holding_hours / 8)
        funding_fee = position.size * position.funding_rate * funding_periods
        
        net_pnl = final_pnl - funding_fee
        
        # Return margin
        self.available_margin += position.margin
        self.total_margin -= position.margin
        
        # Update total PnL
        self.total_pnl += net_pnl
        
        # Record closed position
        closed = {
            'symbol': position.symbol,
            'side': position.side.value,
            'entry_price': position.entry_price,
            'exit_price': exit_price,
            'size': position.size,
            'leverage': position.leverage,
            'pnl': net_pnl,
            'funding_fee': funding_fee,
            'opened_at': position.opened_at,
            'closed_at': datetime.now(),
            'reason': reason
        }
        
        self.closed_positions.append(closed)
        
        # Remove from active positions
        self.positions.remove(position)
        
        logger.info(f"📊 Closed {position.side.value} position: {position.symbol}")
        logger.info(f"   Entry: ${position.entry_price:.2f}, Exit: ${exit_price:.2f}")
        logger.info(f"   PnL: ${net_pnl:.2f} (Funding: ${funding_fee:.2f})")
        logger.info(f"   Reason: {reason}")
        
        return closed
    
    def funding_rate_arbitrage(
        self,
        spot_price: float,
        futures_price: float,
        funding_rate: float,
        funding_interval_hours: int = 8
    ) -> Optional[Dict]:
        """
        Funding rate arbitrage strategiyasi
        
        Args:
            spot_price: Spot narx
            futures_price: Futures narx
            funding_rate: Funding rate (%)
            funding_interval_hours: Funding interval (soat)
            
        Returns:
            Arbitrage imkoniyati
        """
        # Calculate annualized funding rate
        periods_per_year = 365 * 24 / funding_interval_hours
        annualized_rate = funding_rate * periods_per_year * 100
        
        # Profitable if funding rate > borrowing cost + spread
        borrowing_cost = 5.0  # 5% annual
        spread = abs(futures_price - spot_price) / spot_price * 100
        
        profit_potential = annualized_rate - borrowing_cost - spread
        
        if profit_potential > 2.0:  # 2% minimum profit
            strategy = {
                'type': 'funding_arbitrage',
                'action': 'short_futures_long_spot' if funding_rate > 0 else 'long_futures_short_spot',
                'spot_price': spot_price,
                'futures_price': futures_price,
                'funding_rate': funding_rate,
                'annualized_return': profit_potential,
                'recommended_size': self.max_position_size * 0.3  # 30% of max
            }
            
            logger.info(f"🎯 Funding arbitrage opportunity found!")
            logger.info(f"   Expected annual return: {profit_potential:.2f}%")
            logger.info(f"   Action: {strategy['action']}")
            
            return strategy
        
        return None


class OptionsStrategy:
    """
    Options Trading Strategies
    
    Options strategiyalari: covered call, protective put, straddle, etc.
    """
    
    def __init__(self):
        self.positions: List[OptionPosition] = []
        self.spot_positions: Dict[str, float] = {}  # Underlying asset holdings
        
        logger.info("Options Strategy initialized")
    
    def black_scholes_price(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,  # Years
        volatility: float,  # Annual volatility
        risk_free_rate: float,
        option_type: OptionType
    ) -> float:
        """
        Black-Scholes option pricing
        
        Args:
            spot_price: Joriy narx
            strike_price: Strike narx
            time_to_expiry: Muddatgacha qolgan vaqt (yil)
            volatility: Volatility (yillik %)
            risk_free_rate: Risk-free rate (%)
            option_type: CALL yoki PUT
            
        Returns:
            Option narxi
        """
        from scipy.stats import norm
        
        d1 = (np.log(spot_price / strike_price) + 
              (risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / \
             (volatility * np.sqrt(time_to_expiry))
        
        d2 = d1 - volatility * np.sqrt(time_to_expiry)
        
        if option_type == OptionType.CALL:
            price = (spot_price * norm.cdf(d1) - 
                    strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2))
        else:  # PUT
            price = (strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2) - 
                    spot_price * norm.cdf(-d1))
        
        return price
    
    def calculate_greeks(
        self,
        spot_price: float,
        strike_price: float,
        time_to_expiry: float,
        volatility: float,
        risk_free_rate: float,
        option_type: OptionType
    ) -> Dict[str, float]:
        """
        Option Greeks hisoblash (Delta, Gamma, Theta, Vega)
        
        Returns:
            Greeks qiymatlari
        """
        from scipy.stats import norm
        
        d1 = (np.log(spot_price / strike_price) + 
              (risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / \
             (volatility * np.sqrt(time_to_expiry))
        
        d2 = d1 - volatility * np.sqrt(time_to_expiry)
        
        # Delta
        if option_type == OptionType.CALL:
            delta = norm.cdf(d1)
        else:  # PUT
            delta = -norm.cdf(-d1)
        
        # Gamma (same for call and put)
        gamma = norm.pdf(d1) / (spot_price * volatility * np.sqrt(time_to_expiry))
        
        # Theta (per day)
        if option_type == OptionType.CALL:
            theta = (-(spot_price * norm.pdf(d1) * volatility) / (2 * np.sqrt(time_to_expiry)) -
                    risk_free_rate * strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)) / 365
        else:  # PUT
            theta = (-(spot_price * norm.pdf(d1) * volatility) / (2 * np.sqrt(time_to_expiry)) +
                    risk_free_rate * strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2)) / 365
        
        # Vega
        vega = spot_price * norm.pdf(d1) * np.sqrt(time_to_expiry) / 100  # Per 1% change
        
        return {
            'delta': delta,
            'gamma': gamma,
            'theta': theta,
            'vega': vega
        }
    
    def covered_call_strategy(
        self,
        symbol: str,
        spot_price: float,
        strike_price: float,
        expiry_days: int,
        spot_size: float = 1.0,
        volatility: float = 0.5
    ) -> Dict:
        """
        Covered Call strategiyasi
        
        Long stock + Short call option
        
        Returns:
            Strategiya ma'lumotlari
        """
        # Check if we have spot position
        if symbol not in self.spot_positions or self.spot_positions[symbol] < spot_size:
            logger.warning(f"Insufficient spot position for covered call")
            return None
        
        # Calculate call option price
        time_to_expiry = expiry_days / 365
        risk_free_rate = 0.05  # 5%
        
        call_price = self.black_scholes_price(
            spot_price, strike_price, time_to_expiry,
            volatility, risk_free_rate, OptionType.CALL
        )
        
        # Premium received
        premium_received = call_price * spot_size
        
        # Max profit (if price goes above strike)
        max_profit = (strike_price - spot_price) * spot_size + premium_received
        
        # Downside protection
        downside_protection = premium_received / (spot_price * spot_size) * 100
        
        strategy = {
            'type': 'covered_call',
            'symbol': symbol,
            'spot_price': spot_price,
            'strike_price': strike_price,
            'call_premium': call_price,
            'premium_received': premium_received,
            'max_profit': max_profit,
            'max_profit_pct': (max_profit / (spot_price * spot_size)) * 100,
            'downside_protection_pct': downside_protection,
            'breakeven': spot_price - call_price
        }
        
        logger.info(f"📈 Covered Call Strategy:")
        logger.info(f"   Premium received: ${premium_received:.2f}")
        logger.info(f"   Max profit: ${max_profit:.2f} ({strategy['max_profit_pct']:.2f}%)")
        logger.info(f"   Downside protection: {downside_protection:.2f}%")
        
        return strategy
    
    def protective_put_strategy(
        self,
        symbol: str,
        spot_price: float,
        strike_price: float,
        expiry_days: int,
        spot_size: float = 1.0,
        volatility: float = 0.5
    ) -> Dict:
        """
        Protective Put strategiyasi (Portfolio Insurance)
        
        Long stock + Long put option
        
        Returns:
            Strategiya ma'lumotlari
        """
        # Calculate put option price
        time_to_expiry = expiry_days / 365
        risk_free_rate = 0.05
        
        put_price = self.black_scholes_price(
            spot_price, strike_price, time_to_expiry,
            volatility, risk_free_rate, OptionType.PUT
        )
        
        # Cost of protection
        protection_cost = put_price * spot_size
        
        # Max loss (limited to strike price)
        max_loss = (spot_price - strike_price) * spot_size + protection_cost
        
        # Protection cost as % of position
        protection_cost_pct = protection_cost / (spot_price * spot_size) * 100
        
        strategy = {
            'type': 'protective_put',
            'symbol': symbol,
            'spot_price': spot_price,
            'strike_price': strike_price,
            'put_premium': put_price,
            'protection_cost': protection_cost,
            'protection_cost_pct': protection_cost_pct,
            'max_loss': max_loss,
            'max_loss_pct': (max_loss / (spot_price * spot_size)) * 100,
            'breakeven': spot_price + put_price
        }
        
        logger.info(f"🛡️ Protective Put Strategy:")
        logger.info(f"   Protection cost: ${protection_cost:.2f} ({protection_cost_pct:.2f}%)")
        logger.info(f"   Max loss: ${max_loss:.2f} ({strategy['max_loss_pct']:.2f}%)")
        
        return strategy
    
    def straddle_strategy(
        self,
        symbol: str,
        spot_price: float,
        strike_price: float,
        expiry_days: int,
        size: float = 1.0,
        volatility: float = 0.5
    ) -> Dict:
        """
        Long Straddle strategiyasi
        
        Long call + Long put (same strike)
        Volatility o'sishidan foyda olish
        
        Returns:
            Strategiya ma'lumotlari
        """
        time_to_expiry = expiry_days / 365
        risk_free_rate = 0.05
        
        # Calculate call and put prices
        call_price = self.black_scholes_price(
            spot_price, strike_price, time_to_expiry,
            volatility, risk_free_rate, OptionType.CALL
        )
        
        put_price = self.black_scholes_price(
            spot_price, strike_price, time_to_expiry,
            volatility, risk_free_rate, OptionType.PUT
        )
        
        # Total cost
        total_cost = (call_price + put_price) * size
        
        # Breakeven points
        upper_breakeven = strike_price + call_price + put_price
        lower_breakeven = strike_price - call_price - put_price
        
        # Required move for profit
        required_move_pct = ((call_price + put_price) / spot_price) * 100
        
        strategy = {
            'type': 'long_straddle',
            'symbol': symbol,
            'strike_price': strike_price,
            'call_premium': call_price,
            'put_premium': put_price,
            'total_cost': total_cost,
            'upper_breakeven': upper_breakeven,
            'lower_breakeven': lower_breakeven,
            'required_move_pct': required_move_pct,
            'max_loss': total_cost
        }
        
        logger.info(f"⚡ Long Straddle Strategy:")
        logger.info(f"   Total cost: ${total_cost:.2f}")
        logger.info(f"   Breakeven range: ${lower_breakeven:.2f} - ${upper_breakeven:.2f}")
        logger.info(f"   Required move: {required_move_pct:.2f}%")
        
        return strategy


# Example usage
def main():
    """Test futures and options strategies"""
    
    # Futures strategy
    print("="*60)
    print("FUTURES TRADING STRATEGY TEST")
    print("="*60)
    
    futures_strategy = FuturesTradingStrategy(
        max_leverage=10,
        max_position_size=10000
    )
    
    futures_strategy.available_margin = 5000  # $5000 margin
    
    # Open long position
    position = futures_strategy.open_position(
        symbol='BTC/USDT',
        side=PositionSide.LONG,
        entry_price=45000,
        size=5000,
        leverage=5
    )
    
    # Simulate price movement
    current_price = 46000
    futures_strategy.update_position_pnl(position, current_price)
    print(f"\nCurrent PnL: ${position.unrealized_pnl:.2f}")
    
    # Close position
    futures_strategy.close_position(position, current_price)
    
    # Options strategy
    print("\n" + "="*60)
    print("OPTIONS STRATEGY TEST")
    print("="*60)
    
    options_strategy = OptionsStrategy()
    options_strategy.spot_positions['BTC'] = 1.0  # Hold 1 BTC
    
    # Covered Call
    covered_call = options_strategy.covered_call_strategy(
        symbol='BTC',
        spot_price=45000,
        strike_price=48000,
        expiry_days=30,
        spot_size=1.0,
        volatility=0.8
    )
    
    # Protective Put
    protective_put = options_strategy.protective_put_strategy(
        symbol='BTC',
        spot_price=45000,
        strike_price=43000,
        expiry_days=30,
        spot_size=1.0,
        volatility=0.8
    )
    
    # Straddle
    straddle = options_strategy.straddle_strategy(
        symbol='BTC',
        spot_price=45000,
        strike_price=45000,
        expiry_days=30,
        size=1.0,
        volatility=0.8
    )


if __name__ == '__main__':
    main()
