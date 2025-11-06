import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Target, Brain, AlertCircle } from 'lucide-react';
import { supabase } from '../lib/supabase';

interface Prediction {
  id: string;
  symbol: string;
  current_price: number;
  predicted_price: number;
  price_change_percentage: number;
  direction: string;
  confidence_score: number;
  support_levels: number[];
  resistance_levels: number[];
  key_indicators: any;
  sentiment_score: number;
  factors: string[];
  risk_assessment: string;
  created_at: string;
}

export default function MarketPredictionsPage() {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState('BTC');

  useEffect(() => {
    loadPredictions();
  }, []);

  const loadPredictions = async () => {
    setLoading(true);
    try {
      const { data, error } = await supabase.functions.invoke('market-predictions', {
        method: 'GET',
      });

      if (error) throw error;
      setPredictions(data.predictions || []);
    } catch (error) {
      console.error('Xatolik:', error);
    } finally {
      setLoading(false);
    }
  };

  const generatePrediction = async () => {
    setLoading(true);
    try {
      const { data, error } = await supabase.functions.invoke('market-predictions', {
        body: { symbol: selectedSymbol, timeframe: '24h' },
      });

      if (error) throw error;
      setPredictions(prev => [data.prediction, ...prev]);
    } catch (error) {
      console.error('Xatolik:', error);
    } finally {
      setLoading(false);
    }
  };

  const currentPrediction = predictions.find(p => p.symbol === selectedSymbol) || predictions[0];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-cyan-900 to-slate-900 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
          <Brain className="w-10 h-10 text-cyan-400" />
          Market Predictions
        </h1>
        <p className="text-slate-400">AI asosida bozor bashoratlari va narx taxminlari</p>
      </div>

      {/* Controls */}
      <div className="mb-6 flex gap-3">
        {['BTC', 'ETH', 'BNB', 'SOL', 'ADA'].map(symbol => (
          <button
            key={symbol}
            onClick={() => setSelectedSymbol(symbol)}
            className={`px-6 py-3 rounded-lg font-bold transition-all ${
              selectedSymbol === symbol
                ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-500/50'
                : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700/50'
            }`}
          >
            {symbol}
          </button>
        ))}
        <button
          onClick={generatePrediction}
          disabled={loading}
          className="ml-auto px-6 py-3 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-all disabled:opacity-50"
        >
          Yangi bashorat
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <Brain className="w-12 h-12 text-cyan-400 animate-pulse mx-auto mb-4" />
          <p className="text-slate-400">Tahlil qilinmoqda...</p>
        </div>
      ) : currentPrediction ? (
        <div className="space-y-6">
          {/* Main Prediction Card */}
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl p-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Left: Price Info */}
              <div>
                <div className="flex items-center gap-3 mb-6">
                  <h2 className="text-3xl font-bold text-white">{currentPrediction.symbol}</h2>
                  {currentPrediction.direction === 'UP' ? (
                    <TrendingUp className="w-8 h-8 text-green-400" />
                  ) : (
                    <TrendingDown className="w-8 h-8 text-red-400" />
                  )}
                </div>

                <div className="space-y-4">
                  <div>
                    <p className="text-slate-400 text-sm mb-1">Joriy narx</p>
                    <p className="text-4xl font-bold text-white">
                      ${currentPrediction.current_price.toLocaleString()}
                    </p>
                  </div>

                  <div>
                    <p className="text-slate-400 text-sm mb-1">Bashorat qilingan narx (24h)</p>
                    <p className={`text-4xl font-bold ${
                      currentPrediction.direction === 'UP' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      ${currentPrediction.predicted_price.toLocaleString()}
                    </p>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className={`px-6 py-3 rounded-xl ${
                      currentPrediction.direction === 'UP'
                        ? 'bg-green-500/20 text-green-400'
                        : 'bg-red-500/20 text-red-400'
                    }`}>
                      <p className="text-sm">O'zgarish</p>
                      <p className="text-2xl font-bold">
                        {currentPrediction.price_change_percentage > 0 ? '+' : ''}
                        {currentPrediction.price_change_percentage}%
                      </p>
                    </div>

                    <div className="px-6 py-3 bg-cyan-500/20 text-cyan-400 rounded-xl">
                      <p className="text-sm">Ishonch</p>
                      <p className="text-2xl font-bold">{currentPrediction.confidence_score}%</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right: Confidence Gauge */}
              <div className="flex items-center justify-center">
                <div className="relative w-64 h-64">
                  <svg viewBox="0 0 100 100" className="transform -rotate-90">
                    <circle
                      cx="50"
                      cy="50"
                      r="40"
                      fill="none"
                      stroke="rgb(51, 65, 85)"
                      strokeWidth="8"
                    />
                    <circle
                      cx="50"
                      cy="50"
                      r="40"
                      fill="none"
                      stroke="rgb(34, 211, 238)"
                      strokeWidth="8"
                      strokeDasharray={`${(currentPrediction.confidence_score / 100) * 251.2} 251.2`}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center flex-col">
                    <p className="text-5xl font-bold text-white">{currentPrediction.confidence_score}%</p>
                    <p className="text-slate-400 text-sm">Ishonch darajasi</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Support & Resistance Levels */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Target className="w-6 h-6 text-green-400" />
                Support darajalari
              </h3>
              <div className="space-y-3">
                {currentPrediction.support_levels.map((level, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
                    <span className="text-slate-400">S{index + 1}</span>
                    <span className="text-green-400 font-bold">${level.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Target className="w-6 h-6 text-red-400" />
                Resistance darajalari
              </h3>
              <div className="space-y-3">
                {currentPrediction.resistance_levels.map((level, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                    <span className="text-slate-400">R{index + 1}</span>
                    <span className="text-red-400 font-bold">${level.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Key Factors */}
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
            <h3 className="text-xl font-bold text-white mb-4">Asosiy omillar</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {currentPrediction.factors.map((factor, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-slate-900/50 rounded-lg">
                  <AlertCircle className="w-5 h-5 text-cyan-400 mt-0.5" />
                  <p className="text-slate-300 text-sm">{factor}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Risk Assessment */}
          <div className={`border rounded-xl p-6 ${
            currentPrediction.risk_assessment === 'Low'
              ? 'bg-green-500/10 border-green-500/30'
              : currentPrediction.risk_assessment === 'Medium'
              ? 'bg-yellow-500/10 border-yellow-500/30'
              : 'bg-red-500/10 border-red-500/30'
          }`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-300 mb-1">Xavf baholash</p>
                <p className={`text-3xl font-bold ${
                  currentPrediction.risk_assessment === 'Low'
                    ? 'text-green-400'
                    : currentPrediction.risk_assessment === 'Medium'
                    ? 'text-yellow-400'
                    : 'text-red-400'
                }`}>
                  {currentPrediction.risk_assessment}
                </p>
              </div>
              <AlertCircle className={`w-12 h-12 ${
                currentPrediction.risk_assessment === 'Low'
                  ? 'text-green-400'
                  : currentPrediction.risk_assessment === 'Medium'
                  ? 'text-yellow-400'
                  : 'text-red-400'
              }`} />
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-slate-400">Bashorat yo'q. Yuqorida yangi bashorat yarating.</p>
        </div>
      )}
    </div>
  );
}
