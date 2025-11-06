import { useState, useEffect } from 'react';
import { Shield, AlertTriangle, TrendingDown, Activity, DollarSign, BarChart2 } from 'lucide-react';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';

interface RiskData {
  portfolio_value: number;
  var_95: number;
  var_99: number;
  sharpe_ratio: number;
  max_drawdown: number;
  volatility: number;
  risk_level: string;
}

export default function RiskAnalyticsPage() {
  const { user } = useAuth();
  const [riskData, setRiskData] = useState<RiskData | null>(null);
  const [loading, setLoading] = useState(false);

  const calculateRisk = async () => {
    if (!user) return;

    try {
      setLoading(true);
      const { data, error } = await supabase.functions.invoke('risk-analytics', {
        body: { user_id: user.id },
      });

      if (error) throw error;
      setRiskData(data.risk_analysis);
    } catch (error) {
      console.error('Xatolik:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    calculateRisk();
  }, [user]);

  const getRiskColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'low': return 'text-green-400';
      case 'medium': return 'text-yellow-400';
      case 'high': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  const getRiskBg = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'low': return 'bg-green-500/20 border-green-500/30';
      case 'medium': return 'bg-yellow-500/20 border-yellow-500/30';
      case 'high': return 'bg-red-500/20 border-red-500/30';
      default: return 'bg-slate-500/20 border-slate-500/30';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-red-900 to-slate-900 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
          <Shield className="w-10 h-10 text-red-400" />
          Risk Analytics
        </h1>
        <p className="text-slate-400">Portfolio xavf tahlili va boshqaruv</p>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <Activity className="w-12 h-12 text-red-400 animate-pulse mx-auto mb-4" />
          <p className="text-slate-400">Tahlil qilinmoqda...</p>
        </div>
      ) : riskData ? (
        <div className="space-y-6">
          {/* Risk Level Card */}
          <div className={`border rounded-2xl p-8 ${getRiskBg(riskData.risk_level)}`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-300 text-lg mb-2">Umumiy xavf darajasi</p>
                <p className={`text-6xl font-bold ${getRiskColor(riskData.risk_level)}`}>
                  {riskData.risk_level?.toUpperCase()}
                </p>
              </div>
              <AlertTriangle className={`w-24 h-24 ${getRiskColor(riskData.risk_level)} opacity-50`} />
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Portfolio Value */}
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-blue-500/20 rounded-lg">
                  <DollarSign className="w-6 h-6 text-blue-400" />
                </div>
                <p className="text-slate-400">Portfolio qiymati</p>
              </div>
              <p className="text-3xl font-bold text-white">
                ${riskData.portfolio_value.toLocaleString()}
              </p>
            </div>

            {/* Sharpe Ratio */}
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-green-500/20 rounded-lg">
                  <TrendingDown className="w-6 h-6 text-green-400" />
                </div>
                <p className="text-slate-400">Sharpe Ratio</p>
              </div>
              <p className="text-3xl font-bold text-white">
                {riskData.sharpe_ratio.toFixed(2)}
              </p>
              <p className="text-sm text-slate-500 mt-2">
                {riskData.sharpe_ratio > 2 ? 'Ajoyib' : riskData.sharpe_ratio > 1 ? 'Yaxshi' : 'Zaif'}
              </p>
            </div>

            {/* Volatility */}
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-purple-500/20 rounded-lg">
                  <Activity className="w-6 h-6 text-purple-400" />
                </div>
                <p className="text-slate-400">Volatillik</p>
              </div>
              <p className="text-3xl font-bold text-white">
                {(riskData.volatility * 100).toFixed(2)}%
              </p>
            </div>
          </div>

          {/* Value at Risk (VaR) */}
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
              <BarChart2 className="w-8 h-8 text-red-400" />
              Value at Risk (VaR)
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-6 bg-slate-900/50 rounded-lg">
                <div className="flex items-center justify-between mb-4">
                  <p className="text-slate-400">95% ishonch darajasi</p>
                  <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-lg text-sm font-medium">
                    95% VaR
                  </span>
                </div>
                <p className="text-4xl font-bold text-yellow-400 mb-2">
                  ${Math.abs(riskData.var_95).toLocaleString()}
                </p>
                <p className="text-sm text-slate-400">
                  Bir kunlik maksimal yo'qotish (95% ehtimol)
                </p>
              </div>

              <div className="p-6 bg-slate-900/50 rounded-lg">
                <div className="flex items-center justify-between mb-4">
                  <p className="text-slate-400">99% ishonch darajasi</p>
                  <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-lg text-sm font-medium">
                    99% VaR
                  </span>
                </div>
                <p className="text-4xl font-bold text-red-400 mb-2">
                  ${Math.abs(riskData.var_99).toLocaleString()}
                </p>
                <p className="text-sm text-slate-400">
                  Bir kunlik maksimal yo'qotish (99% ehtimol)
                </p>
              </div>
            </div>
          </div>

          {/* Max Drawdown */}
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">Maksimal Drawdown</h2>
            <div className="flex items-center gap-6">
              <div className="flex-1">
                <p className="text-6xl font-bold text-red-400 mb-2">
                  {(riskData.max_drawdown * 100).toFixed(2)}%
                </p>
                <p className="text-slate-400">
                  Eng katta qiymat pasayishi tarixda
                </p>
              </div>
              <div className="w-64 h-64">
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
                    stroke="rgb(239, 68, 68)"
                    strokeWidth="8"
                    strokeDasharray={`${Math.abs(riskData.max_drawdown) * 251.2} 251.2`}
                    strokeLinecap="round"
                  />
                </svg>
              </div>
            </div>
          </div>

          {/* Recommendations */}
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">Tavsiyalar</h2>
            <div className="space-y-4">
              {riskData.risk_level === 'high' && (
                <>
                  <div className="flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                    <AlertTriangle className="w-6 h-6 text-red-400 mt-1" />
                    <div>
                      <p className="text-white font-semibold mb-1">Yuqori xavf aniqlandi</p>
                      <p className="text-slate-400 text-sm">
                        Portfoliongizni diversifikatsiya qiling va positsiya hajmlarini kamaytiring
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                    <Shield className="w-6 h-6 text-yellow-400 mt-1" />
                    <div>
                      <p className="text-white font-semibold mb-1">Stop-loss o'rnating</p>
                      <p className="text-slate-400 text-sm">
                        Barcha positsiyalar uchun stop-loss chegaralarini belgilang
                      </p>
                    </div>
                  </div>
                </>
              )}
              {riskData.sharpe_ratio < 1 && (
                <div className="flex items-start gap-3 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                  <BarChart2 className="w-6 h-6 text-blue-400 mt-1" />
                  <div>
                    <p className="text-white font-semibold mb-1">Daromad/Xavf nisbati yaxshilashga muhtoj</p>
                    <p className="text-slate-400 text-sm">
                      Past Sharpe ratio - strategiyangizni qayta ko'rib chiqing
                    </p>
                  </div>
                </div>
              )}
              {riskData.volatility > 0.3 && (
                <div className="flex items-start gap-3 p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                  <Activity className="w-6 h-6 text-purple-400 mt-1" />
                  <div>
                    <p className="text-white font-semibold mb-1">Yuqori volatillik</p>
                    <p className="text-slate-400 text-sm">
                      Barqaror aktivlar qo'shib, volatillikni kamaytirishni o'ylab ko'ring
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-12">
          <Shield className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400">Risk tahlili uchun ma'lumot yo'q</p>
          <button
            onClick={calculateRisk}
            className="mt-4 px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-all"
          >
            Tahlil qilish
          </button>
        </div>
      )}
    </div>
  );
}
