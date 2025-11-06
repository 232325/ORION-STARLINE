import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';
import { apiService, AISignal, QuantumAnalysis, HFTMetrics } from '../lib/api';
import {
  ChartBarIcon,
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  BoltIcon,
  SparklesIcon,
  CpuChipIcon,
  RocketLaunchIcon
} from '@heroicons/react/24/outline';

interface Stats {
  totalBalance: number;
  totalPnl: number;
  winRate: number;
  activeStrategies: number;
}

interface Position {
  id: string;
  symbol: string;
  side: string;
  position_type: string;
  size: number;
  entry_price: number;
  current_price: number;
  unrealized_pnl: number;
  status: string;
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<Stats>({
    totalBalance: 0,
    totalPnl: 0,
    winRate: 0,
    activeStrategies: 0
  });
  const [positions, setPositions] = useState<Position[]>([]);
  const [aiSignals, setAiSignals] = useState<AISignal[]>([]);
  const [quantumAnalysis, setQuantumAnalysis] = useState<QuantumAnalysis | null>(null);
  const [hftMetrics, setHftMetrics] = useState<HFTMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [backendStatus, setBackendStatus] = useState<'connected' | 'disconnected'>('disconnected');

  useEffect(() => {
    loadDashboardData();
    loadBackendData();
  }, [user]);

  async function loadBackendData() {
    try {
      // Check backend health
      const health = await apiService.healthCheck();
      if (health.status === 'healthy') {
        setBackendStatus('connected');
        
        // Load AI signals
        const signals = await apiService.getAISignals(5);
        setAiSignals(signals);
        
        // Load quantum analysis
        const quantum = await apiService.getQuantumAnalysis();
        setQuantumAnalysis(quantum);
        
        // Load HFT metrics
        const hft = await apiService.getHFTMetrics();
        setHftMetrics(hft);
      }
    } catch (error) {
      console.error('Backend connection error:', error);
      setBackendStatus('disconnected');
    }
  }

  async function loadDashboardData() {
    if (!user) return;

    try {
      // Get profile
      const { data: profile } = await supabase
        .from('profiles')
        .select('*')
        .eq('user_id', user.id)
        .maybeSingle();

      // Get positions
      const { data: positionsData } = await supabase
        .from('positions')
        .select('*')
        .eq('user_id', user.id)
        .order('opened_at', { ascending: false })
        .limit(5);

      // Get strategies
      const { data: strategiesData } = await supabase
        .from('strategies')
        .select('*')
        .eq('user_id', user.id)
        .eq('is_active', true);

      // Calculate stats
      const totalPnl = positionsData?.reduce((sum, pos) => sum + (parseFloat(pos.unrealized_pnl) || 0), 0) || 0;
      const closedPositions = positionsData?.filter(p => p.status === 'closed') || [];
      const winningPositions = closedPositions.filter(p => parseFloat(p.unrealized_pnl) > 0);
      const winRate = closedPositions.length > 0 ? (winningPositions.length / closedPositions.length) * 100 : 0;

      setStats({
        totalBalance: parseFloat(profile?.balance || '0'),
        totalPnl,
        winRate,
        activeStrategies: strategiesData?.length || 0
      });

      setPositions(positionsData || []);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
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
          <h2 className="text-3xl font-bold text-white mb-2">Dashboard</h2>
          <p className="text-slate-400">Trading statistikangizni ko'ring</p>
        </div>
        <div className="flex items-center gap-2">
          <div className={`px-3 py-1 rounded-full text-xs font-medium ${
            backendStatus === 'connected' 
              ? 'bg-green-500/20 text-green-400' 
              : 'bg-red-500/20 text-red-400'
          }`}>
            <span className="flex items-center gap-1">
              <span className={`w-2 h-2 rounded-full ${
                backendStatus === 'connected' ? 'bg-green-400' : 'bg-red-400'
              }`}></span>
              Backend {backendStatus === 'connected' ? 'Ulandi' : 'Ulanmadi'}
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-blue-600/20 rounded-lg">
              <CurrencyDollarIcon className="w-6 h-6 text-blue-400" />
            </div>
          </div>
          <p className="text-slate-400 text-sm mb-1">Umumiy Balans</p>
          <p className="text-2xl font-bold text-white">${stats.totalBalance.toLocaleString()}</p>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-green-600/20 rounded-lg">
              <ArrowTrendingUpIcon className="w-6 h-6 text-green-400" />
            </div>
          </div>
          <p className="text-slate-400 text-sm mb-1">Umumiy PnL</p>
          <p className={`text-2xl font-bold ${stats.totalPnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            ${stats.totalPnl.toFixed(2)}
          </p>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-purple-600/20 rounded-lg">
              <ChartBarIcon className="w-6 h-6 text-purple-400" />
            </div>
          </div>
          <p className="text-slate-400 text-sm mb-1">Win Rate</p>
          <p className="text-2xl font-bold text-white">{stats.winRate.toFixed(1)}%</p>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-cyan-600/20 rounded-lg">
              <BoltIcon className="w-6 h-6 text-cyan-400" />
            </div>
          </div>
          <p className="text-slate-400 text-sm mb-1">Faol Strategiyalar</p>
          <p className="text-2xl font-bold text-white">{stats.activeStrategies}</p>
        </div>
      </div>

      {/* AI & Advanced Features Section */}
      {backendStatus === 'connected' && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Quantum Analysis */}
            {quantumAnalysis && (
              <div className="bg-gradient-to-br from-purple-900/30 to-purple-800/20 backdrop-blur-xl rounded-xl border border-purple-700/50 p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-3 bg-purple-600/30 rounded-lg">
                    <SparklesIcon className="w-6 h-6 text-purple-300" />
                  </div>
                  <h3 className="text-lg font-bold text-white">Quantum Tahlil</h3>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-slate-400 text-sm">Holat:</span>
                    <span className="text-purple-300 font-medium">{quantumAnalysis.quantum_state}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400 text-sm">Coherence:</span>
                    <span className="text-purple-300 font-medium">{quantumAnalysis.coherence_time}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400 text-sm">Fidelity:</span>
                    <span className="text-purple-300 font-medium">{(quantumAnalysis.fidelity * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400 text-sm">Qubits:</span>
                    <span className="text-purple-300 font-medium">{quantumAnalysis.qbit_count}</span>
                  </div>
                </div>
              </div>
            )}

            {/* HFT Metrics */}
            {hftMetrics && (
              <div className="bg-gradient-to-br from-cyan-900/30 to-cyan-800/20 backdrop-blur-xl rounded-xl border border-cyan-700/50 p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-3 bg-cyan-600/30 rounded-lg">
                    <RocketLaunchIcon className="w-6 h-6 text-cyan-300" />
                  </div>
                  <h3 className="text-lg font-bold text-white">HFT Engine</h3>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-slate-400 text-sm">Latency:</span>
                    <span className="text-cyan-300 font-medium">{hftMetrics.latency_us}μs</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400 text-sm">TPS:</span>
                    <span className="text-cyan-300 font-medium">{hftMetrics.trades_per_second.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400 text-sm">P&L:</span>
                    <span className={`font-medium ${hftMetrics.profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      ${hftMetrics.profit_loss.toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* AI Signals Summary */}
            <div className="bg-gradient-to-br from-blue-900/30 to-blue-800/20 backdrop-blur-xl rounded-xl border border-blue-700/50 p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-blue-600/30 rounded-lg">
                  <CpuChipIcon className="w-6 h-6 text-blue-300" />
                </div>
                <h3 className="text-lg font-bold text-white">AI Signallar</h3>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-slate-400 text-sm">Jami signallar:</span>
                  <span className="text-blue-300 font-medium">{aiSignals.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400 text-sm">Buy signallar:</span>
                  <span className="text-green-400 font-medium">
                    {aiSignals.filter(s => s.signal_type === 'buy').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400 text-sm">Sell signallar:</span>
                  <span className="text-red-400 font-medium">
                    {aiSignals.filter(s => s.signal_type === 'sell').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400 text-sm">O'rtacha ishonch:</span>
                  <span className="text-blue-300 font-medium">
                    {aiSignals.length > 0 
                      ? (aiSignals.reduce((sum, s) => sum + s.confidence, 0) / aiSignals.length * 100).toFixed(0)
                      : 0}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* AI Signals Table */}
          {aiSignals.length > 0 && (
            <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
              <h3 className="text-xl font-bold text-white mb-4">AI Trading Signallari</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-700">
                      <th className="text-left py-3 px-4 text-slate-400 font-medium">Symbol</th>
                      <th className="text-left py-3 px-4 text-slate-400 font-medium">Signal</th>
                      <th className="text-left py-3 px-4 text-slate-400 font-medium">Ishonch</th>
                      <th className="text-left py-3 px-4 text-slate-400 font-medium">Narx</th>
                      <th className="text-left py-3 px-4 text-slate-400 font-medium">Vaqt</th>
                    </tr>
                  </thead>
                  <tbody>
                    {aiSignals.map((signal) => (
                      <tr key={signal.id} className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors">
                        <td className="py-3 px-4 text-white font-medium">{signal.symbol}</td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            signal.signal_type === 'buy' 
                              ? 'bg-green-500/20 text-green-400' 
                              : 'bg-red-500/20 text-red-400'
                          }`}>
                            {signal.signal_type.toUpperCase()}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <div className="w-full bg-slate-700 rounded-full h-2">
                              <div 
                                className="bg-blue-500 h-2 rounded-full"
                                style={{ width: `${signal.confidence * 100}%` }}
                              ></div>
                            </div>
                            <span className="text-slate-300 text-sm">{(signal.confidence * 100).toFixed(0)}%</span>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-slate-300">${signal.price.toLocaleString()}</td>
                        <td className="py-3 px-4 text-slate-400 text-sm">
                          {new Date(signal.created_at).toLocaleTimeString('uz-UZ')}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
        <h3 className="text-xl font-bold text-white mb-4">So'nggi Pozitsiyalar</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Symbol</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Turi</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Hajm</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Kirish narxi</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Joriy narx</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">PnL</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {positions.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-8 text-slate-400">
                    Pozitsiyalar topilmadi
                  </td>
                </tr>
              ) : (
                positions.map((position) => (
                  <tr key={position.id} className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors">
                    <td className="py-3 px-4 text-white font-medium">{position.symbol}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        (position.side || position.position_type) === 'long' 
                          ? 'bg-green-500/20 text-green-400' 
                          : 'bg-red-500/20 text-red-400'
                      }`}>
                        {position.side || position.position_type}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-300">{position.size}</td>
                    <td className="py-3 px-4 text-slate-300">${position.entry_price?.toFixed(2)}</td>
                    <td className="py-3 px-4 text-slate-300">${position.current_price?.toFixed(2)}</td>
                    <td className={`py-3 px-4 font-medium ${
                      (position.unrealized_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      ${(position.unrealized_pnl || 0).toFixed(2)}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        position.status === 'open' 
                          ? 'bg-blue-500/20 text-blue-400' 
                          : 'bg-slate-500/20 text-slate-400'
                      }`}>
                        {position.status || 'open'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
