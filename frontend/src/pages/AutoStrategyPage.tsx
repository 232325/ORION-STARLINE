import { useState } from 'react';
import { Sparkles, TrendingUp, Shield, DollarSign, Target, RefreshCw } from 'lucide-react';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';

interface Strategy {
  id: string;
  name: string;
  description: string;
  risk_level: string;
  investment_amount: number;
  expected_return: string;
  max_drawdown: string;
  win_rate: string;
  asset_allocation: any;
  backtest_results: any;
  is_active: boolean;
}

export default function AutoStrategyPage() {
  const { user } = useAuth();
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  
  const [formData, setFormData] = useState({
    risk_level: 'medium',
    investment_amount: 10000,
    timeframe: 'daily',
  });

  const generateStrategy = async () => {
    if (!user) return;

    setGenerating(true);
    try {
      const { data, error } = await supabase.functions.invoke('auto-strategy-generator', {
        body: {
          user_id: user.id,
          ...formData,
        },
      });

      if (error) throw error;
      
      setStrategies(prev => [data.strategy, ...prev]);
      alert(data.recommendation);
    } catch (error) {
      console.error('Xatolik:', error);
    } finally {
      setGenerating(false);
    }
  };

  const loadStrategies = async () => {
    if (!user) return;

    setLoading(true);
    try {
      const { data, error } = await supabase.functions.invoke('auto-strategy-generator', {
        method: 'GET',
        body: { user_id: user.id },
      });

      if (error) throw error;
      setStrategies(data.strategies || []);
    } catch (error) {
      console.error('Xatolik:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'text-green-400';
      case 'medium': return 'text-yellow-400';
      case 'high': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-violet-900 to-slate-900 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
          <Sparkles className="w-10 h-10 text-violet-400" />
          Auto Strategy Generator
        </h1>
        <p className="text-slate-400">AI tomonidan avtomatik yaratilgan trading strategiyalar</p>
      </div>

      {/* Strategy Generator Form */}
      <div className="mb-8 max-w-4xl mx-auto">
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl p-8">
          <h2 className="text-2xl font-bold text-white mb-6">Yangi strategiya yaratish</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div>
              <label className="block text-slate-400 mb-2">Xavf darajasi</label>
              <select
                value={formData.risk_level}
                onChange={(e) => setFormData({ ...formData, risk_level: e.target.value })}
                className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-violet-500"
              >
                <option value="low">Past (Konservativ)</option>
                <option value="medium">O'rtacha (Balansli)</option>
                <option value="high">Yuqori (Agressiv)</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-400 mb-2">Investitsiya miqdori ($)</label>
              <input
                type="number"
                value={formData.investment_amount}
                onChange={(e) => setFormData({ ...formData, investment_amount: Number(e.target.value) })}
                className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-violet-500"
                min="100"
                step="100"
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-2">Vaqt oralig'i</label>
              <select
                value={formData.timeframe}
                onChange={(e) => setFormData({ ...formData, timeframe: e.target.value })}
                className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-violet-500"
              >
                <option value="hourly">Soatlik</option>
                <option value="daily">Kunlik</option>
                <option value="weekly">Haftalik</option>
              </select>
            </div>
          </div>

          <button
            onClick={generateStrategy}
            disabled={generating}
            className="w-full py-4 bg-violet-600 hover:bg-violet-700 text-white rounded-lg font-bold transition-all disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {generating ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                Strategiya yaratilmoqda...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Strategiya yaratish
              </>
            )}
          </button>
        </div>
      </div>

      {/* Strategies List */}
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">Strategiyalarim</h2>
          <button
            onClick={loadStrategies}
            disabled={loading}
            className="px-6 py-3 bg-slate-800/50 hover:bg-slate-700/50 text-white rounded-lg transition-all flex items-center gap-2"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            Yangilash
          </button>
        </div>

        {strategies.length === 0 ? (
          <div className="text-center py-12 bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl">
            <Sparkles className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">Hozircha strategiyalar yo'q. Yuqorida yangi strategiya yarating!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {strategies.map((strategy) => (
              <div
                key={strategy.id}
                className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6 hover:border-violet-500/50 transition-all"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-white mb-1">{strategy.name}</h3>
                    <p className="text-slate-400 text-sm">{strategy.description}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-lg text-sm font-bold ${getRiskColor(strategy.risk_level)}`}>
                    {strategy.risk_level.toUpperCase()}
                  </span>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="p-3 bg-slate-900/50 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      <DollarSign className="w-4 h-4 text-blue-400" />
                      <p className="text-slate-400 text-xs">Investitsiya</p>
                    </div>
                    <p className="text-white font-bold">${strategy.investment_amount.toLocaleString()}</p>
                  </div>

                  <div className="p-3 bg-slate-900/50 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      <TrendingUp className="w-4 h-4 text-green-400" />
                      <p className="text-slate-400 text-xs">Kutilayotgan daromad</p>
                    </div>
                    <p className="text-green-400 font-bold">{strategy.expected_return}</p>
                  </div>

                  <div className="p-3 bg-slate-900/50 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      <Shield className="w-4 h-4 text-red-400" />
                      <p className="text-slate-400 text-xs">Max Drawdown</p>
                    </div>
                    <p className="text-red-400 font-bold">{strategy.max_drawdown}</p>
                  </div>

                  <div className="p-3 bg-slate-900/50 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      <Target className="w-4 h-4 text-yellow-400" />
                      <p className="text-slate-400 text-xs">Win Rate</p>
                    </div>
                    <p className="text-yellow-400 font-bold">{strategy.win_rate}</p>
                  </div>
                </div>

                {/* Asset Allocation */}
                <div className="mb-4">
                  <p className="text-slate-400 text-sm mb-2">Aktivlar taqsimoti:</p>
                  <div className="flex gap-2 flex-wrap">
                    {Object.entries(strategy.asset_allocation).map(([asset, percentage]) => (
                      <span
                        key={asset}
                        className="px-3 py-1 bg-violet-500/20 text-violet-400 rounded-lg text-sm font-medium"
                      >
                        {asset}: {String(percentage)}%
                      </span>
                    ))}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-3">
                  <button
                    className={`flex-1 py-3 rounded-lg font-medium transition-all ${
                      strategy.is_active
                        ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
                        : 'bg-green-500/20 text-green-400 hover:bg-green-500/30'
                    }`}
                  >
                    {strategy.is_active ? 'To\'xtatish' : 'Faollashtirish'}
                  </button>
                  <button className="px-6 py-3 bg-slate-700/50 hover:bg-slate-600/50 text-white rounded-lg transition-all">
                    Batafsil
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
