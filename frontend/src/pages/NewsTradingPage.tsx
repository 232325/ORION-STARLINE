import { useState, useEffect } from 'react';
import { Newspaper, TrendingUp, TrendingDown, AlertCircle, RefreshCw } from 'lucide-react';
import { supabase } from '../lib/supabase';

interface NewsSignal {
  id: string;
  title: string;
  source: string;
  sentiment: string;
  symbol: string;
  signal: string;
  confidence: number;
  published_at: string;
  created_at: string;
}

export default function NewsTradingPage() {
  const [signals, setSignals] = useState<NewsSignal[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState('all');

  useEffect(() => {
    fetchSignals();
  }, [activeFilter]);

  const fetchSignals = async () => {
    try {
      setLoading(true);
      const { data, error } = await supabase.functions.invoke('news-trading-bot', {
        method: 'GET',
      });

      if (error) throw error;
      setSignals(data.signals || []);
    } catch (error) {
      console.error('Xatolik:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredSignals = signals.filter(signal => {
    if (activeFilter === 'all') return true;
    if (activeFilter === 'buy') return signal.signal === 'BUY';
    if (activeFilter === 'sell') return signal.signal === 'SELL';
    return true;
  });

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'POSITIVE': return 'text-green-400';
      case 'NEGATIVE': return 'text-red-400';
      default: return 'text-yellow-400';
    }
  };

  const getSignalBadge = (signal: string) => {
    const colors = {
      BUY: 'bg-green-500/20 text-green-400 border-green-500/30',
      SELL: 'bg-red-500/20 text-red-400 border-red-500/30',
      HOLD: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    };
    return colors[signal as keyof typeof colors] || colors.HOLD;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">News Trading Bot</h1>
            <p className="text-slate-400">Yangiliklar asosida avtomatik trading signallari</p>
          </div>
          <button
            onClick={fetchSignals}
            disabled={loading}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            Yangilash
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Jami signallar</p>
                <p className="text-3xl font-bold text-white mt-1">{signals.length}</p>
              </div>
              <Newspaper className="w-10 h-10 text-blue-400" />
            </div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">BUY signallari</p>
                <p className="text-3xl font-bold text-green-400 mt-1">
                  {signals.filter(s => s.signal === 'BUY').length}
                </p>
              </div>
              <TrendingUp className="w-10 h-10 text-green-400" />
            </div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">SELL signallari</p>
                <p className="text-3xl font-bold text-red-400 mt-1">
                  {signals.filter(s => s.signal === 'SELL').length}
                </p>
              </div>
              <TrendingDown className="w-10 h-10 text-red-400" />
            </div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">O'rtacha ishonch</p>
                <p className="text-3xl font-bold text-blue-400 mt-1">
                  {signals.length > 0
                    ? Math.round(signals.reduce((sum, s) => sum + s.confidence, 0) / signals.length)
                    : 0}%
                </p>
              </div>
              <AlertCircle className="w-10 h-10 text-blue-400" />
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-3">
          {['all', 'buy', 'sell'].map(filter => (
            <button
              key={filter}
              onClick={() => setActiveFilter(filter)}
              className={`px-6 py-2 rounded-lg font-medium transition-all ${
                activeFilter === filter
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700/50'
              }`}
            >
              {filter === 'all' ? 'Barchasi' : filter === 'buy' ? 'BUY' : 'SELL'}
            </button>
          ))}
        </div>
      </div>

      {/* Signals List */}
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-12">
            <RefreshCw className="w-12 h-12 text-blue-400 animate-spin mx-auto mb-4" />
            <p className="text-slate-400">Yuklanmoqda...</p>
          </div>
        ) : filteredSignals.length === 0 ? (
          <div className="text-center py-12 bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl">
            <Newspaper className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">Hozircha signallar yo'q</p>
          </div>
        ) : (
          filteredSignals.map(signal => (
            <div
              key={signal.id}
              className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6 hover:border-blue-500/50 transition-all"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`px-3 py-1 rounded-lg border text-sm font-medium ${getSignalBadge(signal.signal)}`}>
                      {signal.signal}
                    </span>
                    <span className="text-blue-400 font-mono font-bold">{signal.symbol}</span>
                    <span className={`text-sm font-medium ${getSentimentColor(signal.sentiment)}`}>
                      {signal.sentiment}
                    </span>
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-2">{signal.title}</h3>
                  <div className="flex items-center gap-4 text-sm text-slate-400">
                    <span>{signal.source}</span>
                    <span>•</span>
                    <span>{new Date(signal.published_at).toLocaleString('uz')}</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-slate-400 mb-1">Ishonch darajasi</div>
                  <div className="text-2xl font-bold text-white">{signal.confidence}%</div>
                </div>
              </div>

              <div className="w-full bg-slate-700/30 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full transition-all"
                  style={{ width: `${signal.confidence}%` }}
                />
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
