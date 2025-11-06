import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';
import { BoltIcon, StopIcon, PlayIcon } from '@heroicons/react/24/outline';

interface Strategy {
  id: string;
  name: string;
  description: string;
  algorithm_type: string;
  parameters: any;
  is_active: boolean;
  performance_metrics: any;
  created_at: string;
}

export default function StrategiesPage() {
  const { user } = useAuth();
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStrategies();
  }, [user]);

  async function loadStrategies() {
    if (!user) return;

    try {
      const { data } = await supabase
        .from('strategies')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false });

      setStrategies(data || []);
    } catch (error) {
      console.error('Error loading strategies:', error);
    } finally {
      setLoading(false);
    }
  }

  async function toggleStrategy(strategyId: string, currentStatus: boolean) {
    try {
      const { data: session } = await supabase.auth.getSession();
      if (!session?.session?.access_token) {
        alert('Autentifikatsiya xatosi');
        return;
      }

      const response = await supabase.functions.invoke('manage-strategy', {
        body: {
          strategyId: strategyId,
          action: currentStatus ? 'stop' : 'start'
        }
      });

      if (response.error) {
        throw response.error;
      }

      alert(`Strategiya ${currentStatus ? 'to\'xtatildi' : 'ishga tushirildi'}!`);
      loadStrategies();
    } catch (error: any) {
      console.error('Error toggling strategy:', error);
      alert('Xatolik: ' + error.message);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white">Yuklanmoqda...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Trading Strategiyalar</h2>
          <p className="text-slate-400">Algoritmik trading strategiyalaringizni boshqaring</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {strategies.length === 0 ? (
          <div className="col-span-full text-center py-12 text-slate-400">
            Strategiyalar topilmadi
          </div>
        ) : (
          strategies.map((strategy) => (
            <div
              key={strategy.id}
              className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6 hover:border-slate-600 transition-all"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-blue-600/20 rounded-lg">
                    <BoltIcon className="w-6 h-6 text-blue-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">{strategy.name}</h3>
                    <p className="text-sm text-slate-400">{strategy.algorithm_type}</p>
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  strategy.is_active
                    ? 'bg-green-500/20 text-green-400'
                    : 'bg-slate-500/20 text-slate-400'
                }`}>
                  {strategy.is_active ? 'ACTIVE' : 'STOPPED'}
                </span>
              </div>

              <p className="text-slate-300 text-sm mb-4 line-clamp-2">
                {strategy.description || 'Tavsif mavjud emas'}
              </p>

              {strategy.performance_metrics && (
                <div className="grid grid-cols-2 gap-3 mb-4 p-3 bg-slate-700/30 rounded-lg">
                  <div>
                    <p className="text-xs text-slate-400 mb-1">Win Rate</p>
                    <p className="text-lg font-semibold text-white">
                      {strategy.performance_metrics.win_rate || 0}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 mb-1">Total PnL</p>
                    <p className={`text-lg font-semibold ${
                      (strategy.performance_metrics.total_pnl || 0) >= 0
                        ? 'text-green-400'
                        : 'text-red-400'
                    }`}>
                      ${strategy.performance_metrics.total_pnl || 0}
                    </p>
                  </div>
                </div>
              )}

              <div className="flex items-center space-x-3">
                <button
                  onClick={() => toggleStrategy(strategy.id, strategy.is_active)}
                  className={`flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all ${
                    strategy.is_active
                      ? 'bg-red-600 hover:bg-red-500 text-white'
                      : 'bg-green-600 hover:bg-green-500 text-white'
                  }`}
                >
                  {strategy.is_active ? (
                    <>
                      <StopIcon className="w-5 h-5" />
                      <span>To'xtatish</span>
                    </>
                  ) : (
                    <>
                      <PlayIcon className="w-5 h-5" />
                      <span>Ishga tushirish</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
