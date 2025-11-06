import { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { 
  SparklesIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ChartBarIcon,
  LightBulbIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

interface Prediction {
  symbol: string;
  current_price: number;
  predictions: {
    days_ahead: number;
    predicted_price: number;
    confidence: number;
    lower_bound: number;
    upper_bound: number;
  }[];
  accuracy: number;
  model: string;
}

interface TrendAnalysis {
  symbol: string;
  trend: 'bullish' | 'bearish' | 'neutral';
  sma_20: number;
  sma_50: number;
  rsi: number;
  macd: number;
  signal_strength: number;
}

interface TradingSignal {
  symbol: string;
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  entry_price: number;
  target_price: number;
  stop_loss: number;
  reasoning: string[];
}

interface Anomaly {
  timestamp: string;
  symbol: string;
  type: 'spike' | 'drop' | 'unusual_volume' | 'pattern';
  severity: number;
  description: string;
}

export default function AIMarketPredictorPage() {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [trends, setTrends] = useState<TrendAnalysis[]>([]);
  const [signals, setSignals] = useState<TradingSignal[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [predictionDays, setPredictionDays] = useState(7);

  useEffect(() => {
    fetchPredictions();
  }, [selectedSymbol]);

  const fetchPredictions = async () => {
    try {
      setLoading(true);

      // LSTM Price Prediction
      const predictionResponse = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/ai-market-predictor`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`
          },
          body: JSON.stringify({
            action: 'predict_price',
            symbol: selectedSymbol,
            days_ahead: predictionDays
          })
        }
      );

      const predictionData = await predictionResponse.json();
      if (predictionData.data) {
        setPredictions([predictionData.data]);
      }

      // Trend Analysis
      const trendResponse = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/ai-market-predictor`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`
          },
          body: JSON.stringify({
            action: 'analyze_trend',
            symbol: selectedSymbol
          })
        }
      );

      const trendData = await trendResponse.json();
      if (trendData.data) {
        setTrends([trendData.data]);
      }

      // Trading Signals
      const signalResponse = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/ai-market-predictor`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`
          },
          body: JSON.stringify({
            action: 'generate_signals',
            symbols: [selectedSymbol, 'MSFT', 'GOOGL']
          })
        }
      );

      const signalData = await signalResponse.json();
      if (signalData.data) {
        setSignals(signalData.data);
      }

      // Anomaly Detection
      const anomalyResponse = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/ai-market-predictor`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`
          },
          body: JSON.stringify({
            action: 'detect_anomalies',
            symbol: selectedSymbol,
            window: 30
          })
        }
      );

      const anomalyData = await anomalyResponse.json();
      if (anomalyData.data && anomalyData.data.anomalies) {
        setAnomalies(anomalyData.data.anomalies);
      }

    } catch (error) {
      console.error('AI tahmin verileri yüklenirken hata:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'bullish':
        return <ArrowTrendingUpIcon className="h-6 w-6 text-green-400" />;
      case 'bearish':
        return <ArrowTrendingDownIcon className="h-6 w-6 text-red-400" />;
      default:
        return <ChartBarIcon className="h-6 w-6 text-yellow-400" />;
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'bullish': return 'text-green-400';
      case 'bearish': return 'text-red-400';
      default: return 'text-yellow-400';
    }
  };

  const getSignalBadge = (signal: string): 'success' | 'danger' | 'warning' => {
    switch (signal) {
      case 'BUY': return 'success';
      case 'SELL': return 'danger';
      default: return 'warning';
    }
  };

  const formatPrice = (price: number) => {
    return `$${price.toFixed(2)}`;
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-slate-700 rounded w-1/4"></div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-64 bg-slate-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <SparklesIcon className="h-8 w-8 text-purple-400" />
            AI Market Tahmini
          </h1>
          <p className="text-slate-400 mt-2">
            LSTM tabanlı fiyat tahmini ve akıllı işlem sinyalleri
          </p>
        </div>
        <div className="flex gap-3">
          <select
            value={selectedSymbol}
            onChange={(e) => setSelectedSymbol(e.target.value)}
            className="px-4 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white"
          >
            <option value="AAPL">AAPL</option>
            <option value="MSFT">MSFT</option>
            <option value="GOOGL">GOOGL</option>
            <option value="TSLA">TSLA</option>
            <option value="NVDA">NVDA</option>
          </select>
          <Button onClick={fetchPredictions} disabled={loading}>
            Yenile
          </Button>
        </div>
      </div>

      {/* Price Predictions */}
      {predictions.length > 0 && (
        <Card variant="glass" className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
              <ChartBarIcon className="h-6 w-6 text-blue-400" />
              Fiyat Tahmini - {predictions[0].symbol}
            </h2>
            <Badge variant="neutral">
              Model Doğruluğu: {predictions[0].accuracy.toFixed(1)}%
            </Badge>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="p-4 bg-slate-800/50 rounded-lg">
              <p className="text-sm text-slate-400">Mevcut Fiyat</p>
              <p className="text-2xl font-bold text-white mt-1">
                {formatPrice(predictions[0].current_price)}
              </p>
            </div>
            {predictions[0].predictions.slice(0, 3).map((pred, index) => (
              <div key={index} className="p-4 bg-slate-800/50 rounded-lg">
                <p className="text-sm text-slate-400">{pred.days_ahead} Gün Sonrası</p>
                <p className={`text-2xl font-bold mt-1 ${
                  pred.predicted_price > predictions[0].current_price ? 'text-green-400' : 'text-red-400'
                }`}>
                  {formatPrice(pred.predicted_price)}
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  Güven: {(pred.confidence * 100).toFixed(0)}%
                </p>
              </div>
            ))}
          </div>

          <div className="space-y-3">
            {predictions[0].predictions.map((pred, index) => (
              <div key={index} className="p-4 bg-slate-800/50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white font-medium">{pred.days_ahead} Gün Sonrası</span>
                  <Badge variant={pred.confidence >= 0.8 ? 'success' : pred.confidence >= 0.6 ? 'warning' : 'danger'}>
                    %{(pred.confidence * 100).toFixed(0)} Güven
                  </Badge>
                </div>
                <div className="flex items-center gap-4 text-sm">
                  <div className="flex-1">
                    <span className="text-slate-400">Tahmin: </span>
                    <span className={`font-bold ${
                      pred.predicted_price > predictions[0].current_price ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {formatPrice(pred.predicted_price)}
                    </span>
                  </div>
                  <div className="flex-1">
                    <span className="text-slate-400">Aralık: </span>
                    <span className="text-blue-400">
                      {formatPrice(pred.lower_bound)} - {formatPrice(pred.upper_bound)}
                    </span>
                  </div>
                  <div className="flex-1">
                    <span className="text-slate-400">Değişim: </span>
                    <span className={
                      pred.predicted_price > predictions[0].current_price ? 'text-green-400' : 'text-red-400'
                    }>
                      {((pred.predicted_price - predictions[0].current_price) / predictions[0].current_price * 100).toFixed(2)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Trend Analysis */}
      {trends.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card variant="glass" className="p-6">
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              {getTrendIcon(trends[0].trend)}
              Trend Analizi
            </h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Genel Trend</span>
                <Badge variant={trends[0].trend === 'bullish' ? 'success' : trends[0].trend === 'bearish' ? 'danger' : 'warning'}>
                  {trends[0].trend.toUpperCase()}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">SMA 20</span>
                <span className="text-white font-medium">{formatPrice(trends[0].sma_20)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">SMA 50</span>
                <span className="text-white font-medium">{formatPrice(trends[0].sma_50)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">RSI</span>
                <span className={`font-medium ${
                  trends[0].rsi > 70 ? 'text-red-400' :
                  trends[0].rsi < 30 ? 'text-green-400' : 'text-yellow-400'
                }`}>
                  {trends[0].rsi.toFixed(2)}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">MACD</span>
                <span className={trends[0].macd >= 0 ? 'text-green-400' : 'text-red-400'}>
                  {trends[0].macd.toFixed(2)}
                </span>
              </div>
              <div className="mt-4 pt-4 border-t border-slate-700">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Sinyal Gücü</span>
                  <span className="text-blue-400 font-bold text-lg">
                    {trends[0].signal_strength.toFixed(0)}/100
                  </span>
                </div>
                <div className="mt-2 w-full bg-slate-700 rounded-full h-2">
                  <div 
                    className="h-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-500"
                    style={{ width: `${trends[0].signal_strength}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </Card>

          {/* Trading Signals */}
          <Card variant="glass" className="p-6">
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <LightBulbIcon className="h-6 w-6 text-yellow-400" />
              İşlem Sinyalleri
            </h2>
            <div className="space-y-3">
              {signals.map((signal, index) => (
                <div key={index} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-white font-semibold">{signal.symbol}</span>
                      <Badge variant={getSignalBadge(signal.signal)}>
                        {signal.signal}
                      </Badge>
                    </div>
                    <span className="text-slate-400 text-sm">
                      Güven: {(signal.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="grid grid-cols-3 gap-3 text-sm mb-3">
                    <div>
                      <p className="text-slate-400">Giriş</p>
                      <p className="text-blue-400 font-medium">{formatPrice(signal.entry_price)}</p>
                    </div>
                    <div>
                      <p className="text-slate-400">Hedef</p>
                      <p className="text-green-400 font-medium">{formatPrice(signal.target_price)}</p>
                    </div>
                    <div>
                      <p className="text-slate-400">Stop-Loss</p>
                      <p className="text-red-400 font-medium">{formatPrice(signal.stop_loss)}</p>
                    </div>
                  </div>
                  <div className="text-xs text-slate-400">
                    <p className="font-semibold mb-1">Analiz:</p>
                    <ul className="space-y-1">
                      {signal.reasoning.map((reason, i) => (
                        <li key={i}>• {reason}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Anomaly Detection */}
      {anomalies.length > 0 && (
        <Card variant="glass" className="p-6">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
            <ExclamationTriangleIcon className="h-6 w-6 text-orange-400" />
            Anomali Tespiti
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {anomalies.map((anomaly, index) => (
              <div key={index} className="p-4 bg-slate-800/50 rounded-lg border border-orange-600/30">
                <div className="flex items-start justify-between mb-2">
                  <Badge variant={anomaly.severity > 7 ? 'danger' : 'warning'}>
                    {anomaly.type.replace('_', ' ').toUpperCase()}
                  </Badge>
                  <span className="text-xs text-slate-400">
                    {new Date(anomaly.timestamp).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-sm text-slate-300 mb-2">{anomaly.description}</p>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400">Önem:</span>
                  <div className="flex-1 bg-slate-700 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        anomaly.severity > 7 ? 'bg-red-500' : 'bg-orange-500'
                      }`}
                      style={{ width: `${anomaly.severity * 10}%` }}
                    ></div>
                  </div>
                  <span className="text-xs text-orange-400">{anomaly.severity}/10</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
