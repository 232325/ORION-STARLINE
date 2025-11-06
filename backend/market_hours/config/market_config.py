"""
Market Hours Configuration
Tizim uchun barcha bozor vaqtlari sozlamalari
"""

from datetime import time, datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum

class MarketType(Enum):
    FOREX = "forex"
    METALS = "metals"
    NEWS = "news"

class SessionType(Enum):
    ASIAN = "asian"
    EUROPEAN = "european"
    AMERICAN = "american"
    OVERLAP = "overlap"

class MetalMarket(Enum):
    LME = "lme"
    COMEX = "comex"
    SHFE = "shfe"

# Forex Session Configuration
FOREX_SESSIONS = {
    SessionType.ASIAN: {
        "name": "Asian (Tokyo)",
        "start_time": time(0, 0),  # 00:00 GMT
        "end_time": time(9, 0),    # 09:00 GMT
        "timezone": "Asia/Tokyo",
        "primary_currencies": ["JPY", "AUD", "NZD", "SGD", "HKD"],
        "volatility_multiplier": 1.2,
        "characteristics": "quiet, range-bound"
    },
    SessionType.EUROPEAN: {
        "name": "European (London)",
        "start_time": time(8, 0),  # 08:00 GMT
        "end_time": time(17, 0),   # 17:00 GMT
        "timezone": "Europe/London",
        "primary_currencies": ["EUR", "GBP", "CHF", "SEK", "NOK"],
        "volatility_multiplier": 1.8,
        "characteristics": "most active, high volume"
    },
    SessionType.AMERICAN: {
        "name": "American (New York)",
        "start_time": time(13, 0), # 13:00 GMT
        "end_time": time(22, 0),   # 22:00 GMT
        "timezone": "America/New_York",
        "primary_currencies": ["USD", "CAD", "MXN"],
        "volatility_multiplier": 1.6,
        "characteristics": "high impact news, sharp moves"
    }
}

# Session Overlap Configuration
SESSION_OVERLAPS = {
    "european_asian": {
        "start_time": time(8, 0),  # 08:00 GMT
        "end_time": time(9, 0),    # 09:00 GMT
        "characteristics": "transition period, liquidity building",
        "volatility_multiplier": 1.4
    },
    "european_american": {
        "start_time": time(13, 0), # 13:00 GMT
        "end_time": time(17, 0),   # 17:00 GMT
        "characteristics": "highest volatility, maximum liquidity",
        "volatility_multiplier": 2.2
    },
    "asian_american": {
        "start_time": time(21, 0), # 21:00 GMT
        "end_time": time(22, 0),   # 22:00 GMT
        "characteristics": "late NY session, Asian pre-open",
        "volatility_multiplier": 1.3
    }
}

# Metal Markets Configuration
METAL_MARKETS = {
    MetalMarket.LME: {
        "name": "London Metal Exchange",
        "trading_hours": {
            "morning": {
                "start_time": time(7, 30),  # 07:30 GMT
                "end_time": time(11, 0),    # 11:00 GMT
                "type": "ring_trading"
            },
            "afternoon": {
                "start_time": time(12, 0),  # 12:00 GMT
                "end_time": time(15, 0),    # 15:00 GMT
                "type": "ring_trading"
            },
            "lme_select": {
                "start_time": time(16, 0),  # 16:00 GMT
                "end_time": time(19, 0),    # 19:00 GMT
                "type": "electronic"
            }
        },
        "instruments": ["copper", "aluminum", "lead", "zinc", "nickel", "tin"],
        "weekend_trading": True,
        "lunch_break": {
            "start_time": time(11, 0),  # 11:00 GMT
            "end_time": time(12, 0),    # 12:00 GMT
            "duration_minutes": 60
        }
    },
    MetalMarket.COMEX: {
        "name": "COMEX (Precious Metals)",
        "trading_hours": {
            "pre_market": {
                "start_time": time(17, 0),  # 17:00 GMT (prev day)
                "end_time": time(8, 30),    # 08:30 GMT
                "type": "electronic"
            },
            "regular": {
                "start_time": time(8, 30),  # 08:30 GMT
                "end_time": time(17, 0),    # 17:00 GMT
                "type": "electronic"
            },
            "closing": {
                "start_time": time(17, 0),  # 17:00 GMT
                "end_time": time(17, 30),   # 17:30 GMT
                "type": "closing"
            }
        },
        "instruments": ["gold", "silver", "platinum", "palladium"],
        "weekend_trading": True,
        "maintenance_break": {
            "start_time": time(17, 30), # 17:30 GMT
            "end_time": time(18, 0),    # 18:00 GMT
            "duration_minutes": 30
        }
    },
    MetalMarket.SHFE: {
        "name": "Shanghai Futures Exchange",
        "trading_hours": {
            "morning_session": {
                "start_time": time(1, 30),  # 01:30 GMT (9:30 CST)
                "end_time": time(3, 0),     # 03:00 GMT (11:00 CST)
                "type": "physical"
            },
            "afternoon_session": {
                "start_time": time(7, 0),   # 07:00 GMT (15:00 CST)
                "end_time": time(8, 0),     # 08:00 GMT (16:00 CST)
                "type": "physical"
            }
        },
        "instruments": ["copper", "aluminum", "zinc", "lead", "nickel"],
        "weekend_trading": False
    }
}

# News Events Classification
NEWS_IMPACT_LEVELS = {
    "HIGH": {
        "multiplier": 2.0,
        "events": [
            "central_bank_rate_decision",
            "employment_report",
            "gdp_release",
            "inflation_data",
            "fomc_meeting"
        ]
    },
    "MEDIUM": {
        "multiplier": 1.5,
        "events": [
            "retail_sales",
            "industrial_production",
            "trade_balance",
            "manufacturing_pmi",
            "consumer_confidence"
        ]
    },
    "LOW": {
        "multiplier": 1.1,
        "events": [
            "building_permits",
            "consumer_sentiment",
            "business_inventories",
            "factory_orders",
            "durable_goods"
        ]
    }
}

# Central Bank Events
CENTRAL_BANK_EVENTS = {
    "FED": {
        "name": "Federal Reserve",
        "meeting_frequency": "8_times_per_year",
        "decision_time": time(18, 0),  # 18:00 GMT (14:00 EST)
        "press_conference_time": time(18, 30),  # 18:30 GMT
        "impact_asset_classes": ["USD", "GOLD", "TREASURIES", "STOCKS"]
    },
    "ECB": {
        "name": "European Central Bank",
        "meeting_frequency": "every_6_weeks",
        "decision_time": time(12, 0),  # 12:00 GMT
        "press_conference_time": time(12, 30),  # 12:30 GMT
        "impact_asset_classes": ["EUR", "GOLD", "EURO_BONDS"]
    },
    "BOE": {
        "name": "Bank of England",
        "meeting_frequency": "monthly",
        "decision_time": time(12, 0),  # 12:00 GMT
        "press_conference_time": time(12, 30),  # 12:30 GMT
        "impact_asset_classes": ["GBP", "GILTS"]
    },
    "BOJ": {
        "name": "Bank of Japan",
        "meeting_frequency": "monthly",
        "decision_time": time(6, 0),  # 06:00 GMT
        "impact_asset_classes": ["JPY", "NIKKEI", "JGB"]
    }
}

# Inventory Reporting Schedule
INVENTORY_REPORTING = {
    "LME": {
        "daily_stocks": {
            "time": time(8, 0),  # 08:00 GMT
            "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
        },
        "weekly_position": {
            "time": time(15, 0), # 15:00 GMT
            "day": "friday"
        }
    },
    "COMEX": {
        "commitment_of_traders": {
            "time": time(14, 30), # 14:30 GMT
            "day": "friday"
        },
        "gold_silver_inventories": {
            "time": time(21, 0), # 21:00 GMT
            "days": ["tuesday", "thursday"]
        }
    }
}

# Market Holidays (major financial centers)
MARKET_HOLIDAYS = {
    "2025": {
        "new_years_day": ["2025-01-01"],
        "good_friday": ["2025-04-18"],
        "easter_monday": ["2025-04-21"],
        "labour_day": ["2025-05-01"],
        "christmas": ["2025-12-25"],
        "boxing_day": ["2025-12-26"],
        "thanksgiving_us": ["2025-11-27"],
        "independence_day_us": ["2025-07-04"],
        "memorial_day_us": ["2025-05-26"],
        "presidents_day_us": ["2025-02-17"],
        "veterans_day_us": ["2025-11-11"],
        "chinese_new_year": ["2025-01-29", "2025-01-30", "2025-01-31"],
        "golden_week_jp": ["2025-05-03", "2025-05-04", "2025-05-05"],
        "autumn_festival_jp": ["2025-10-14"]
    }
}

# Volatility Patterns by Time of Day
VOLATILITY_PATTERNS = {
    "forex": {
        "00:00-02:00": 0.8,    # Low Asian open
        "02:00-04:00": 0.6,    # Quiet Asian
        "04:00-06:00": 0.7,    # Asian preparation
        "06:00-08:00": 1.2,    # Pre-European
        "08:00-10:00": 1.8,    # European open
        "10:00-12:00": 2.0,    # European peak
        "12:00-14:00": 1.9,    # European close
        "14:00-16:00": 2.2,    # Overlap peak
        "16:00-18:00": 1.8,    # American open
        "18:00-20:00": 1.5,    # American active
        "20:00-22:00": 1.3,    # American fade
        "22:00-24:00": 0.9     # Late session
    },
    "metals": {
        "07:30-11:00": 1.5,    # LME morning ring
        "11:00-12:00": 0.5,    # LME lunch break
        "12:00-15:00": 1.8,    # LME afternoon ring
        "15:00-16:00": 1.0,    # LME transition
        "16:00-19:00": 1.6,    # LME Select
        "17:00-08:30": 1.2,    # COMEX pre-market + regular
        "08:30-17:00": 2.0,    # COMEX regular hours
        "17:00-17:30": 1.5     # COMEX closing
    }
}

# Time Zone Constants
TIMEZONES = {
    "GMT": "Etc/GMT",
    "EST": "America/New_York",
    "PST": "America/Los_Angeles",
    "BST": "Europe/London",
    "CET": "Europe/Berlin",
    "JST": "Asia/Tokyo",
    "CST": "Asia/Shanghai"
}