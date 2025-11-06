import { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { 
  UserGroupIcon, 
  TrophyIcon, 
  ChartBarIcon,
  ArrowTrendingUpIcon,
  UserPlusIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

interface Trader {
  user_id: string;
  display_name: string;
  bio: string;
  total_trades: number;
  win_rate: number;
  avg_profit: number;
  followers_count: number;
  reputation_score: number;
  is_verified: boolean;
  trading_style: string;
}

interface LeaderboardEntry {
  rank: number;
  trader: Trader;
  period_profit: number;
  period_trades: number;
}

interface CopyTradeConfig {
  trader_id: string;
  mode: 'full' | 'partial' | 'manual';
  copy_percentage: number;
  max_position_size: number;
  stop_loss_percentage: number;
}

export default function SocialTradingPage() {
  const [topTraders, setTopTraders] = useState<Trader[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [following, setFollowing] = useState<Set<string>>(new Set());
  const [copying, setCopying] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState<'daily' | 'weekly' | 'monthly'>('weekly');

  useEffect(() => {
    fetchSocialTradingData();
  }, [selectedPeriod]);

  const fetchSocialTradingData = async () => {
    try {
      setLoading(true);
      
      // Fetch top traders
      const tradersResponse = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/social-trading-manager`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`
          },
          body: JSON.stringify({
            action: 'get_top_traders',
            limit: 10
          })
        }
      );
      
      const tradersData = await tradersResponse.json();
      if (tradersData.data) {
        setTopTraders(tradersData.data);
      }

      // Fetch leaderboard
      const leaderboardResponse = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/social-trading-manager`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`
          },
          body: JSON.stringify({
            action: 'get_leaderboard',
            period: selectedPeriod,
            limit: 20
          })
        }
      );
      
      const leaderboardData = await leaderboardResponse.json();
      if (leaderboardData.data) {
        setLeaderboard(leaderboardData.data);
      }

    } catch (error) {
      console.error('Sosyal trading verileri yüklenirken hata:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFollow = async (traderId: string) => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/social-trading-manager`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`
          },
          body: JSON.stringify({
            action: 'follow_trader',
            trader_id: traderId
          })
        }
      );
      
      const data = await response.json();
      if (data.success) {
        setFollowing(prev => new Set([...prev, traderId]));
      }
    } catch (error) {
      console.error('Trader takip hatası:', error);
    }
  };

  const handleCopyTrade = async (traderId: string) => {
    const config: CopyTradeConfig = {
      trader_id: traderId,
      mode: 'partial',
      copy_percentage: 50,
      max_position_size: 1000,
      stop_loss_percentage: 5
    };

    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/social-trading-manager`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`
          },
          body: JSON.stringify({
            action: 'start_copy_trading',
            ...config
          })
        }
      );
      
      const data = await response.json();
      if (data.success) {
        setCopying(prev => new Set([...prev, traderId]));
      }
    } catch (error) {
      console.error('Copy trading başlatma hatası:', error);
    }
  };

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-slate-700 rounded w-1/4"></div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map(i => (
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
            <UserGroupIcon className="h-8 w-8 text-blue-400" />
            Sosyal Trading
          </h1>
          <p className="text-slate-400 mt-2">
            Başarılı traderleri takip edin ve işlemlerini kopyalayın
          </p>
        </div>
        
        {/* Period Selector */}
        <div className="flex gap-2">
          {(['daily', 'weekly', 'monthly'] as const).map(period => (
            <Button
              key={period}
              variant={selectedPeriod === period ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setSelectedPeriod(period)}
            >
              {period === 'daily' ? 'Günlük' : period === 'weekly' ? 'Haftalık' : 'Aylık'}
            </Button>
          ))}
        </div>
      </div>

      {/* Top Traders Grid */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <TrophyIcon className="h-6 w-6 text-yellow-400" />
          En İyi Traderlar
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {topTraders.map(trader => (
            <Card key={trader.user_id} variant="glass" className="p-6">
              <div className="space-y-4">
                {/* Trader Header */}
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold text-lg">
                      {trader.display_name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-white">{trader.display_name}</h3>
                        {trader.is_verified && (
                          <CheckCircleIcon className="h-5 w-5 text-blue-400" />
                        )}
                      </div>
                      <Badge variant="neutral" className="text-xs mt-1">
                        {trader.trading_style || 'Genel'}
                      </Badge>
                    </div>
                  </div>
                </div>

                {/* Bio */}
                <p className="text-sm text-slate-400 line-clamp-2">
                  {trader.bio || 'Deneyimli trader'}
                </p>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-slate-800/50 rounded-lg p-3">
                    <div className="text-xs text-slate-400">Kazanma Oranı</div>
                    <div className={`text-lg font-bold ${trader.win_rate >= 60 ? 'text-green-400' : 'text-yellow-400'}`}>
                      {trader.win_rate.toFixed(1)}%
                    </div>
                  </div>
                  <div className="bg-slate-800/50 rounded-lg p-3">
                    <div className="text-xs text-slate-400">Ort. Kar</div>
                    <div className="text-lg font-bold text-blue-400">
                      {formatPercent(trader.avg_profit)}
                    </div>
                  </div>
                  <div className="bg-slate-800/50 rounded-lg p-3">
                    <div className="text-xs text-slate-400">İşlem Sayısı</div>
                    <div className="text-lg font-bold text-white">
                      {trader.total_trades}
                    </div>
                  </div>
                  <div className="bg-slate-800/50 rounded-lg p-3">
                    <div className="text-xs text-slate-400">Takipçi</div>
                    <div className="text-lg font-bold text-purple-400">
                      {trader.followers_count}
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <Button
                    variant={following.has(trader.user_id) ? 'secondary' : 'outline'}
                    size="sm"
                    className="flex-1"
                    onClick={() => handleFollow(trader.user_id)}
                    disabled={following.has(trader.user_id)}
                  >
                    <UserPlusIcon className="h-4 w-4 mr-2" />
                    {following.has(trader.user_id) ? 'Takip Ediliyor' : 'Takip Et'}
                  </Button>
                  <Button
                    variant={copying.has(trader.user_id) ? 'secondary' : 'primary'}
                    size="sm"
                    className="flex-1"
                    onClick={() => handleCopyTrade(trader.user_id)}
                    disabled={copying.has(trader.user_id)}
                  >
                    <ChartBarIcon className="h-4 w-4 mr-2" />
                    {copying.has(trader.user_id) ? 'Kopyalanıyor' : 'Kopyala'}
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Leaderboard */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <ArrowTrendingUpIcon className="h-6 w-6 text-green-400" />
          Liderlik Tablosu - {selectedPeriod === 'daily' ? 'Günlük' : selectedPeriod === 'weekly' ? 'Haftalık' : 'Aylık'}
        </h2>
        
        <Card variant="glass" className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-800/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    Sıra
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    Trader
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    Kar/Zarar
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    İşlem Sayısı
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    Kazanma Oranı
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">
                    İşlem
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {leaderboard.map((entry) => (
                  <tr key={entry.trader.user_id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {entry.rank <= 3 ? (
                          <TrophyIcon className={`h-6 w-6 ${
                            entry.rank === 1 ? 'text-yellow-400' :
                            entry.rank === 2 ? 'text-slate-300' :
                            'text-orange-400'
                          }`} />
                        ) : (
                          <span className="text-slate-400 font-medium">#{entry.rank}</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <span className="text-white font-medium">{entry.trader.display_name}</span>
                        {entry.trader.is_verified && (
                          <CheckCircleIcon className="h-4 w-4 text-blue-400" />
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`font-bold ${
                        entry.period_profit >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {formatPercent(entry.period_profit)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-slate-300">
                      {entry.period_trades}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-blue-400 font-medium">
                        {entry.trader.win_rate.toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => handleCopyTrade(entry.trader.user_id)}
                        disabled={copying.has(entry.trader.user_id)}
                      >
                        {copying.has(entry.trader.user_id) ? 'Kopyalanıyor' : 'Kopyala'}
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
}
