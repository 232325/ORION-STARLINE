"""
Black Swan Events Module
========================

Black swan voqealar aniqlash moduli.
"""

class BlackSwanDetector:
    """Black swan event detector"""
    
    def __init__(self):
        self.threshold_multiplier = 5.0  # 5 sigma event
        self.min_data_points = 1000
    
    def detect_black_swan_events(self, returns_data):
        """Black swan voqealarni aniqlash"""
        if len(returns_data) < self.min_data_points:
            return []
        
        mean_return = returns_data.mean()
        std_return = returns_data.std()
        threshold = mean_return + self.threshold_multiplier * std_return
        
        black_swans = returns_data[abs(returns_data) > abs(threshold)]
        
        return {
            'event_count': len(black_swans),
            'events': black_swans.index.tolist(),
            'threshold': threshold,
            'frequency': len(black_swans) / len(returns_data)
        }
    
    def calculate_event_probability(self, historical_data):
        """Event ehtimolini hisoblash"""
        return {'daily_probability': 0.001, 'annual_probability': 0.25}