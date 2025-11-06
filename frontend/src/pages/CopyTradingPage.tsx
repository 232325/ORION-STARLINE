import { useEffect, useState } from 'react';
import { 
  UserGroupIcon, 
  TrophyIcon,
  ArrowTrendingUpIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

interface Trader {
  id: string;
  display_name: string;
  avatar_url: string;
  total_followers: number;
  total_profit: number;
  win_rate: number;
  sharpe_ratio: number;
  max_drawdown: number;
  total_trades: number;
  is_verified: boolean;
  commission_rate: number;
  risk_score: number;
}

export default function CopyTradingPage() {
  const [traders, setTraders] = useState<Trader[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('total_profit');

  useEffect(() => {
    loadTraders();
  }, [sortBy]);

  async function loadTraders() {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/copy-trading-leaderboard?sort_by=${sortBy}`,
        {
          headers: {
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`
          }
        }
      );
      const data = await response.json();
      setTraders(data.traders || []);
    } catch (error) {
      console.error('Error loading traders:', error);
    } finally {
      setLoading(false);
    }
  }

  const getRiskBadge = (score: number) => {
    if (score <= 2) return { label: 'Kam', color: 'green' };
    if (score <= 4) return { label: "O'rta", color: 'yellow' };
    return { label: 'Yuqori', color: 'red' };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white">Yuklanmoqda...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Copy Trading Pro</h2>
        <p className="text-slate-400">Professional treyderlardan strategiya nusxalash</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-blue-600/20 rounded-lg">
              <UserGroupIcon className="w-6 h-6 text-blue-400" />
            </div>
            <h3 className="text-lg font-bold text-white">Jami Treyderlar</h3>
          </div>
          <p className="text-3xl font-bold text-white">{traders.length}</p>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-green-600/20 rounded-lg">
              <ArrowTrendingUpIcon className="w-6 h-6 text-green-400" />
            </div>
            <h3 className="text-lg font-bold text-white">O'rtacha Win Rate</h3>
          </div>
          <p className="text-3xl font-bold text-green-400">
            {traders.length > 0 
              ? (traders.reduce((sum, t) => sum + t.win_rate, 0) / traders.length).toFixed(1)
              : 0}%
          </p>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-purple-600/20 rounded-lg">
              <TrophyIcon className="w-6 h-6 text-purple-400" />
            </div>
            <h3 className="text-lg font-bold text-white">Jami Followerlar</h3>
          </div>
          <p className="text-3xl font-bold text-white">
            {traders.reduce((sum, t) => sum + t.total_followers, 0).toLocaleString()}
          </p>
        </div>
      </div>

      {/* Traders List */}
      <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-white">Top Treyderlar</h3>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600"
          >
            <option value="total_profit">Foyda bo'yicha</option>
            <option value="win_rate">Win rate bo'yicha</option>
            <option value="followers">Followerlar bo'yicha</option>
          </select>
        </div>

        <div className="space-y-4">
          {traders.map((trader, index) => {
            const risk = getRiskBadge(trader.risk_score);
            return (
              <div
                key={trader.id}
                className="bg-slate-700/30 rounded-xl p-6 border border-slate-600 hover:border-blue-500 transition-colors"
              >
                <div className="flex items-start gap-4">
                  <div className="relative">
                    <img
                      src={trader.avatar_url}
                      alt={trader.display_name}
                      className="w-16 h-16 rounded-full"
                    />
                    {index < 3 && (
                      <div className="absolute -top-2 -right-2 w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center text-sm font-bold">
                        {index + 1}
                      </div>
                    )}
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="text-lg font-bold text-white">{trader.display_name}</h4>
                      {trader.is_verified && (
                        <CheckCircleIcon className="w-5 h-5 text-blue-400" />
                      )}
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                      <div>
                        <p className="text-slate-400 text-sm">Foyda</p>
                        <p className="text-green-400 font-bold">${trader.total_profit.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-slate-400 text-sm">Win Rate</p>
                        <p className="text-white font-bold">{trader.win_rate.toFixed(1)}%</p>
                      </div>
                      <div>
                        <p className="text-slate-400 text-sm">Sharpe Ratio</p>
                        <p className="text-white font-bold">{trader.sharpe_ratio.toFixed(2)}</p>
                      </div>
                      <div>
                        <p className="text-slate-400 text-sm">Followerlar</p>
                        <p className="text-white font-bold">{trader.total_followers.toLocaleString()}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium bg-${risk.color}-500/20 text-${risk.color}-400`}>
                        Risk: {risk.label}
                      </span>
                      <span className="text-slate-400 text-sm">
                        Komissiya: {trader.commission_rate}%
                      </span>
                      <span className="text-slate-400 text-sm">
                        {trader.total_trades} ta trade
                      </span>
                    </div>
                  </div>

                  <button className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors">
                    Copy
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
