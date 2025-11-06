import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';

interface Position {
  id: string;
  symbol: string;
  side: string;
  position_type: string;
  size: number;
  entry_price: number;
  current_price: number;
  unrealized_pnl: number;
  leverage: number;
  stop_loss: number;
  take_profit: number;
  status: string;
  opened_at: string;
}

export default function PositionsPage() {
  const { user } = useAuth();
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPositions();
  }, [user]);

  async function loadPositions() {
    if (!user) return;

    try {
      const { data } = await supabase
        .from('positions')
        .select('*')
        .eq('user_id', user.id)
        .order('opened_at', { ascending: false });

      setPositions(data || []);
    } catch (error) {
      console.error('Error loading positions:', error);
    } finally {
      setLoading(false);
    }
  }

  async function closePosition(positionId: string) {
    try {
      const position = positions.find(p => p.id === positionId);
      if (!position) return;

      const { data: session } = await supabase.auth.getSession();
      if (!session?.session?.access_token) {
        alert('Autentifikatsiya xatosi');
        return;
      }

      const response = await supabase.functions.invoke('close-position', {
        body: {
          positionId: positionId,
          closingPrice: position.current_price
        }
      });

      if (response.error) {
        throw response.error;
      }

      alert('Pozitsiya yopildi!');
      loadPositions();
    } catch (error: any) {
      console.error('Error closing position:', error);
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
          <h2 className="text-3xl font-bold text-white mb-2">Pozitsiyalar</h2>
          <p className="text-slate-400">Barcha trading pozitsiyalaringiz</p>
        </div>
      </div>

      <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-700/50">
              <tr>
                <th className="text-left py-4 px-6 text-slate-300 font-semibold">Symbol</th>
                <th className="text-left py-4 px-6 text-slate-300 font-semibold">Turi</th>
                <th className="text-left py-4 px-6 text-slate-300 font-semibold">Hajm</th>
                <th className="text-left py-4 px-6 text-slate-300 font-semibold">Leverage</th>
                <th className="text-left py-4 px-6 text-slate-300 font-semibold">Kirish</th>
                <th className="text-left py-4 px-6 text-slate-300 font-semibold">Joriy</th>
                <th className="text-left py-4 px-6 text-slate-300 font-semibold">Stop Loss</th>
                <th className="text-left py-4 px-6 text-slate-300 font-semibold">Take Profit</th>
                <th className="text-left py-4 px-6 text-slate-300 font-semibold">PnL</th>
                <th className="text-left py-4 px-6 text-slate-300 font-semibold">Status</th>
                <th className="text-left py-4 px-6 text-slate-300 font-semibold">Amallar</th>
              </tr>
            </thead>
            <tbody>
              {positions.length === 0 ? (
                <tr>
                  <td colSpan={11} className="text-center py-12 text-slate-400">
                    Pozitsiyalar topilmadi
                  </td>
                </tr>
              ) : (
                positions.map((position) => (
                  <tr key={position.id} className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors">
                    <td className="py-4 px-6 text-white font-medium">{position.symbol}</td>
                    <td className="py-4 px-6">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        (position.side || position.position_type) === 'long' 
                          ? 'bg-green-500/20 text-green-400' 
                          : 'bg-red-500/20 text-red-400'
                      }`}>
                        {(position.side || position.position_type)?.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-slate-300">{position.size}</td>
                    <td className="py-4 px-6 text-slate-300">{position.leverage || 1}x</td>
                    <td className="py-4 px-6 text-slate-300">${position.entry_price?.toFixed(2)}</td>
                    <td className="py-4 px-6 text-slate-300">${position.current_price?.toFixed(2)}</td>
                    <td className="py-4 px-6 text-slate-300">
                      {position.stop_loss ? `$${position.stop_loss.toFixed(2)}` : '-'}
                    </td>
                    <td className="py-4 px-6 text-slate-300">
                      {position.take_profit ? `$${position.take_profit.toFixed(2)}` : '-'}
                    </td>
                    <td className={`py-4 px-6 font-semibold ${
                      (position.unrealized_pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      ${(position.unrealized_pnl || 0).toFixed(2)}
                    </td>
                    <td className="py-4 px-6">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        position.status === 'open' 
                          ? 'bg-blue-500/20 text-blue-400' 
                          : 'bg-slate-500/20 text-slate-400'
                      }`}>
                        {(position.status || 'open').toUpperCase()}
                      </span>
                    </td>
                    <td className="py-4 px-6">
                      {position.status === 'open' && (
                        <button
                          onClick={() => closePosition(position.id)}
                          className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white text-sm font-medium rounded-lg transition-colors"
                        >
                          Yopish
                        </button>
                      )}
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
