import { useState, useEffect } from 'react';
import { Twitter, MessageCircle, TrendingUp, Activity, BarChart3 } from 'lucide-react';
import { supabase } from '../lib/supabase';

interface SentimentData {
  symbol: string;
  twitter_sentiment: number;
  reddit_sentiment: number;
  overall_sentiment: string;
  fear_greed_index: number;
  volume: number;
  signal: string;
  created_at: string;
}

export default function SocialSentimentPage() {
  const [sentimentData, setSentimentData] = useState<SentimentData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSymbol, setSelectedSymbol] = useState('BTC');

  useEffect(() => {
    fetchSentiment();
  }, [selectedSymbol]);

  const fetchSentiment = async () => {
    try {
      setLoading(true);
      const { data, error } = await supabase.functions.invoke('social-sentiment-analysis', {
        method: 'GET',
      });

      if (error) throw error;
      setSentimentData(data.sentiment_data || []);
    } catch (error) {
      console.error('Xatolik:', error);
    } finally {
      setLoading(false);
    }
  };

  const currentData = sentimentData.find(d => d.symbol === selectedSymbol) || sentimentData[0];

  const getSentimentColor = (value: number) => {
    if (value >= 70) return 'text-green-400';
    if (value >= 40) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getFearGreedColor = (index: number) => {
    if (index >= 75) return 'bg-green-500';
    if (index >= 55) return 'bg-blue-500';
    if (index >= 45) return 'bg-yellow-500';
    if (index >= 25) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getFearGreedLabel = (index: number) => {
    if (index >= 75) return 'Haddan tashqari ochko\'zlik';
    if (index >= 55) return 'Ochko\'zlik';
    if (index >= 45) return 'Neytral';
    if (index >= 25) return 'Qo\'rquv';
    return 'Haddan tashqari qo\'rquv';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">Social Sentiment Analysis</h1>
        <p className="text-slate-400">Ijtimoiy tarmoqlar kayfiyati tahlili</p>
      </div>

      {/* Symbol Selector */}
      <div className="mb-6 flex gap-3">
        {['BTC', 'ETH', 'BNB', 'SOL', 'ADA'].map(symbol => (
          <button
            key={symbol}
            onClick={() => setSelectedSymbol(symbol)}
            className={`px-6 py-3 rounded-lg font-bold transition-all ${
              selectedSymbol === symbol
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/50'
                : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700/50'
            }`}
          >
            {symbol}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-center py-12">
          <Activity className="w-12 h-12 text-purple-400 animate-pulse mx-auto mb-4" />
          <p className="text-slate-400">Yuklanmoqda...</p>
        </div>
      ) : currentData ? (
        <div className="space-y-6">
          {/* Fear & Greed Index */}
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
              <BarChart3 className="w-8 h-8 text-purple-400" />
              Fear & Greed Index
            </h2>
            <div className="flex items-center gap-8">
              <div className="flex-1">
                <div className="relative h-8 bg-slate-700/50 rounded-full overflow-hidden">
                  <div
                    className={`absolute h-full transition-all ${getFearGreedColor(currentData.fear_greed_index)}`}
                    style={{ width: `${currentData.fear_greed_index}%` }}
                  />
                </div>
                <div className="flex justify-between mt-3 text-sm text-slate-400">
                  <span>Qo'rquv</span>
                  <span>Neytral</span>
                  <span>Ochko'zlik</span>
                </div>
              </div>
              <div className="text-center">
                <div className="text-6xl font-bold text-white mb-2">{currentData.fear_greed_index}</div>
                <div className={`text-lg font-semibold ${getSentimentColor(currentData.fear_greed_index)}`}>
                  {getFearGreedLabel(currentData.fear_greed_index)}
                </div>
              </div>
            </div>
          </div>

          {/* Sentiment Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Twitter Sentiment */}
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-blue-500/20 rounded-lg">
                  <Twitter className="w-8 h-8 text-blue-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">Twitter Sentiment</h3>
                  <p className="text-slate-400 text-sm">So'nggi 24 soat</p>
                </div>
              </div>
              <div className="text-center">
                <div className={`text-6xl font-bold mb-3 ${getSentimentColor(currentData.twitter_sentiment)}`}>
                  {currentData.twitter_sentiment.toFixed(1)}%
                </div>
                <div className="w-full bg-slate-700/30 rounded-full h-4">
                  <div
                    className="bg-blue-500 h-4 rounded-full transition-all"
                    style={{ width: `${currentData.twitter_sentiment}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Reddit Sentiment */}
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-orange-500/20 rounded-lg">
                  <MessageCircle className="w-8 h-8 text-orange-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">Reddit Sentiment</h3>
                  <p className="text-slate-400 text-sm">So'nggi 24 soat</p>
                </div>
              </div>
              <div className="text-center">
                <div className={`text-6xl font-bold mb-3 ${getSentimentColor(currentData.reddit_sentiment)}`}>
                  {currentData.reddit_sentiment.toFixed(1)}%
                </div>
                <div className="w-full bg-slate-700/30 rounded-full h-4">
                  <div
                    className="bg-orange-500 h-4 rounded-full transition-all"
                    style={{ width: `${currentData.reddit_sentiment}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Overall Analysis */}
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
              <TrendingUp className="w-8 h-8 text-purple-400" />
              Umumiy tahlil
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-6 bg-slate-900/50 rounded-lg">
                <p className="text-slate-400 mb-2">Umumiy kayfiyat</p>
                <p className={`text-3xl font-bold ${currentData.overall_sentiment === 'BULLISH' ? 'text-green-400' : currentData.overall_sentiment === 'BEARISH' ? 'text-red-400' : 'text-yellow-400'}`}>
                  {currentData.overall_sentiment}
                </p>
              </div>
              <div className="text-center p-6 bg-slate-900/50 rounded-lg">
                <p className="text-slate-400 mb-2">Trading signal</p>
                <p className={`text-3xl font-bold ${currentData.signal === 'BUY' ? 'text-green-400' : currentData.signal === 'SELL' ? 'text-red-400' : 'text-yellow-400'}`}>
                  {currentData.signal}
                </p>
              </div>
              <div className="text-center p-6 bg-slate-900/50 rounded-lg">
                <p className="text-slate-400 mb-2">Faollik hajmi</p>
                <p className="text-3xl font-bold text-purple-400">{currentData.volume.toLocaleString()}</p>
              </div>
            </div>
          </div>

          {/* Historical Data */}
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
            <h2 className="text-xl font-bold text-white mb-4">Tarixiy ma'lumotlar</h2>
            <div className="space-y-3">
              {sentimentData.slice(0, 5).map((data, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg">
                  <div className="flex items-center gap-4">
                    <span className="text-white font-mono font-bold">{data.symbol}</span>
                    <span className={`px-3 py-1 rounded-lg text-sm font-medium ${data.signal === 'BUY' ? 'bg-green-500/20 text-green-400' : data.signal === 'SELL' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                      {data.signal}
                    </span>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <p className="text-xs text-slate-400">Fear & Greed</p>
                      <p className={`font-bold ${getSentimentColor(data.fear_greed_index)}`}>{data.fear_greed_index}</p>
                    </div>
                    <div className="text-slate-400 text-sm">
                      {new Date(data.created_at).toLocaleTimeString('uz')}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-slate-400">Ma'lumot topilmadi</p>
        </div>
      )}
    </div>
  );
}
