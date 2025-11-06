import { useState, useEffect } from 'react';
import Card from '../ui/Card';
import Badge from '../ui/Badge';
import { TrendingUp, TrendingDown, Activity, AlertTriangle } from 'lucide-react';

interface Prediction {
    symbol: string;
    timeframe: string;
    current_price: number;
    predicted_price: number;
    predicted_direction: 'up' | 'down' | 'neutral';
    predicted_change_percentage: number;
    confidence_score: number;
    probability_up: number;
    probability_down: number;
    technical_signals: {
        rsi: number;
        macd: number;
        sma_20: number;
        sma_50: number;
    };
    market_regime: string;
    volatility_level: string;
    is_anomaly: boolean;
    anomaly_score: number;
    prediction_time: string;
}

interface MLPredictionChartProps {
    symbol: string;
    timeframes?: string[];
}

export default function MLPredictionChart({ symbol, timeframes = ['1m', '5m', '15m', '1h', '4h', '1d'] }: MLPredictionChartProps) {
    const [predictions, setPredictions] = useState<Prediction[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedTimeframe, setSelectedTimeframe] = useState('1h');

    useEffect(() => {
        fetchPredictions();
        const interval = setInterval(fetchPredictions, 60000); // Har 1 daqiqada yangilash
        return () => clearInterval(interval);
    }, [symbol]);

    const fetchPredictions = async () => {
        try {
            setLoading(true);
            const response = await fetch(
                'https://bgrmoxpwfbuqszmmeodo.supabase.co/functions/v1/ml-price-predictor-enhanced-v2',
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`
                    },
                    body: JSON.stringify({
                        symbol,
                        timeframes,
                        model_type: 'lstm_ensemble'
                    })
                }
            );

            const result = await response.json();
            if (result.data?.predictions) {
                setPredictions(result.data.predictions);
            }
        } catch (error) {
            console.error('ML prediction olishda xato:', error);
        } finally {
            setLoading(false);
        }
    };

    const selectedPrediction = predictions.find(p => p.timeframe === selectedTimeframe);

    if (loading) {
        return (
            <Card variant="elevated">
                <div className="p-6 text-center">
                    <Activity className="w-8 h-8 animate-spin mx-auto mb-2 text-blue-400" />
                    <div>ML tahminlar yuklanmoqda...</div>
                </div>
            </Card>
        );
    }

    return (
        <div className="space-y-4">
            {/* Timeframe Selector */}
            <Card variant="elevated">
                <div className="p-4">
                    <div className="flex flex-wrap gap-2">
                        {timeframes.map((tf) => (
                            <button
                                key={tf}
                                onClick={() => setSelectedTimeframe(tf)}
                                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                                    selectedTimeframe === tf
                                        ? 'bg-blue-500 text-white'
                                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                                }`}
                            >
                                {tf}
                            </button>
                        ))}
                    </div>
                </div>
            </Card>

            {/* Main Prediction Card */}
            {selectedPrediction && (
                <Card variant="elevated">
                    <div className="p-6">
                        <div className="flex items-center justify-between mb-6">
                            <div>
                                <h3 className="text-2xl font-bold">{symbol}</h3>
                                <div className="text-sm text-slate-400">
                                    {selectedTimeframe} Timeframe Tahmin
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="text-sm text-slate-400">Joriy Narx</div>
                                <div className="text-2xl font-bold">
                                    ${selectedPrediction.current_price.toFixed(2)}
                                </div>
                            </div>
                        </div>

                        {/* Prediction Result */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                            <div className={`p-6 rounded-lg ${
                                selectedPrediction.predicted_direction === 'up' 
                                    ? 'bg-green-500/10 border border-green-500/20' 
                                    : 'bg-red-500/10 border border-red-500/20'
                            }`}>
                                <div className="flex items-center justify-between mb-4">
                                    <div className="text-lg font-medium">Tahmin Narxi</div>
                                    {selectedPrediction.predicted_direction === 'up' ? (
                                        <TrendingUp className="w-8 h-8 text-green-400" />
                                    ) : (
                                        <TrendingDown className="w-8 h-8 text-red-400" />
                                    )}
                                </div>
                                <div className="text-3xl font-bold mb-2">
                                    ${selectedPrediction.predicted_price.toFixed(2)}
                                </div>
                                <div className={`text-lg ${
                                    selectedPrediction.predicted_change_percentage >= 0 
                                        ? 'text-green-400' 
                                        : 'text-red-400'
                                }`}>
                                    {selectedPrediction.predicted_change_percentage >= 0 ? '+' : ''}
                                    {selectedPrediction.predicted_change_percentage.toFixed(2)}%
                                </div>
                            </div>

                            <div className="p-6 rounded-lg bg-blue-500/10 border border-blue-500/20">
                                <div className="text-lg font-medium mb-4">Confidence Score</div>
                                <div className="relative">
                                    <div className="w-full h-4 bg-slate-800 rounded-full overflow-hidden">
                                        <div 
                                            className="h-full bg-gradient-to-r from-blue-500 to-blue-400 transition-all duration-500"
                                            style={{ width: `${selectedPrediction.confidence_score * 100}%` }}
                                        />
                                    </div>
                                    <div className="text-3xl font-bold mt-4">
                                        {(selectedPrediction.confidence_score * 100).toFixed(1)}%
                                    </div>
                                    <div className="text-sm text-slate-400 mt-1">
                                        {selectedPrediction.confidence_score >= 0.8 ? 'Yuqori' :
                                         selectedPrediction.confidence_score >= 0.6 ? 'O\'rtacha' : 'Past'}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Probabilities */}
                        <div className="grid grid-cols-2 gap-4 mb-6">
                            <div className="p-4 bg-slate-800/50 rounded-lg">
                                <div className="text-sm text-slate-400 mb-2">Up Ehtimoli</div>
                                <div className="text-2xl font-bold text-green-400">
                                    {(selectedPrediction.probability_up * 100).toFixed(1)}%
                                </div>
                            </div>
                            <div className="p-4 bg-slate-800/50 rounded-lg">
                                <div className="text-sm text-slate-400 mb-2">Down Ehtimoli</div>
                                <div className="text-2xl font-bold text-red-400">
                                    {(selectedPrediction.probability_down * 100).toFixed(1)}%
                                </div>
                            </div>
                        </div>

                        {/* Technical Signals */}
                        <div className="mb-6">
                            <h4 className="text-lg font-semibold mb-4">Texnik Signallar</h4>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <div className="p-3 bg-slate-800/50 rounded-lg">
                                    <div className="text-xs text-slate-400">RSI</div>
                                    <div className="text-lg font-semibold">
                                        {selectedPrediction.technical_signals.rsi.toFixed(1)}
                                    </div>
                                    <Badge 
                                        color={
                                            selectedPrediction.technical_signals.rsi > 70 ? 'danger' :
                                            selectedPrediction.technical_signals.rsi < 30 ? 'success' : 'default'
                                        }
                                        className="mt-1"
                                    >
                                        {selectedPrediction.technical_signals.rsi > 70 ? 'Overbought' :
                                         selectedPrediction.technical_signals.rsi < 30 ? 'Oversold' : 'Neutral'}
                                    </Badge>
                                </div>
                                <div className="p-3 bg-slate-800/50 rounded-lg">
                                    <div className="text-xs text-slate-400">MACD</div>
                                    <div className="text-lg font-semibold">
                                        {selectedPrediction.technical_signals.macd.toFixed(2)}
                                    </div>
                                </div>
                                <div className="p-3 bg-slate-800/50 rounded-lg">
                                    <div className="text-xs text-slate-400">SMA 20</div>
                                    <div className="text-lg font-semibold">
                                        ${selectedPrediction.technical_signals.sma_20.toFixed(2)}
                                    </div>
                                </div>
                                <div className="p-3 bg-slate-800/50 rounded-lg">
                                    <div className="text-xs text-slate-400">SMA 50</div>
                                    <div className="text-lg font-semibold">
                                        ${selectedPrediction.technical_signals.sma_50.toFixed(2)}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Market Analysis */}
                        <div className="grid grid-cols-2 gap-4 mb-6">
                            <div className="p-4 bg-slate-800/50 rounded-lg">
                                <div className="text-sm text-slate-400 mb-2">Market Rejim</div>
                                <Badge color="purple">{selectedPrediction.market_regime}</Badge>
                            </div>
                            <div className="p-4 bg-slate-800/50 rounded-lg">
                                <div className="text-sm text-slate-400 mb-2">Volatillik</div>
                                <Badge color={
                                    selectedPrediction.volatility_level === 'high' ? 'danger' :
                                    selectedPrediction.volatility_level === 'medium' ? 'warning' : 'success'
                                }>
                                    {selectedPrediction.volatility_level}
                                </Badge>
                            </div>
                        </div>

                        {/* Anomaly Detection */}
                        {selectedPrediction.is_anomaly && (
                            <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg flex items-start gap-3">
                                <AlertTriangle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
                                <div>
                                    <div className="font-semibold text-yellow-200">Anomaliya Aniqlandi</div>
                                    <div className="text-sm text-yellow-200/80 mt-1">
                                        Anomaliya Score: {selectedPrediction.anomaly_score.toFixed(2)} - 
                                        Narx kutilmagan harakat qilmoqda
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Timestamp */}
                        <div className="text-xs text-slate-500 mt-4">
                            Oxirgi yangilanish: {new Date(selectedPrediction.prediction_time).toLocaleString('uz-UZ')}
                        </div>
                    </div>
                </Card>
            )}

            {/* All Predictions Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                {predictions.map((pred) => (
                    <Card 
                        key={pred.timeframe}
                        variant="elevated"
                        className={`cursor-pointer transition-all ${
                            selectedTimeframe === pred.timeframe ? 'ring-2 ring-blue-500' : ''
                        }`}
                        onClick={() => setSelectedTimeframe(pred.timeframe)}
                    >
                        <div className="p-4">
                            <div className="text-sm text-slate-400 mb-2">{pred.timeframe}</div>
                            <div className={`text-lg font-bold ${
                                pred.predicted_direction === 'up' ? 'text-green-400' : 'text-red-400'
                            }`}>
                                {pred.predicted_direction === 'up' ? '+' : ''}
                                {pred.predicted_change_percentage.toFixed(2)}%
                            </div>
                            <div className="text-xs text-slate-500 mt-1">
                                {(pred.confidence_score * 100).toFixed(0)}% ishonch
                            </div>
                        </div>
                    </Card>
                ))}
            </div>
        </div>
    );
}
