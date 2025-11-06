import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { supabase } from '../../lib/supabase';
import Card from '../ui/Card';
import Badge from '../ui/Badge';
import { Activity, TrendingUp, TrendingDown, Clock, DollarSign, BarChart3 } from 'lucide-react';

interface Trade {
    id: string;
    bot_id: string;
    bot_name: string;
    symbol: string;
    side: 'buy' | 'sell';
    entry_price: number;
    exit_price?: number;
    quantity: number;
    profit_loss?: number;
    status: 'open' | 'closed' | 'cancelled';
    opened_at: string;
    closed_at?: string;
}

interface BotActivity {
    bot_id: string;
    bot_name: string;
    status: 'active' | 'inactive';
    last_trade_time: string;
    total_profit_today: number;
    trades_today: number;
}

export default function TradingMonitor() {
    const { user } = useAuth();
    const [recentTrades, setRecentTrades] = useState<Trade[]>([]);
    const [botActivities, setBotActivities] = useState<BotActivity[]>([]);
    const [realTimeData, setRealTimeData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (user) {
            fetchTradingData();
            
            // Real-time updates har 5 soniyada
            const interval = setInterval(fetchTradingData, 5000);
            
            // Supabase Realtime subscription
            const subscription = supabase
                .channel('trading_monitor')
                .on('postgres_changes', 
                    { 
                        event: '*', 
                        schema: 'public', 
                        table: 'bot_trades' 
                    }, 
                    (payload) => {
                        console.log('Real-time update:', payload);
                        fetchTradingData();
                    }
                )
                .subscribe();

            return () => {
                clearInterval(interval);
                subscription.unsubscribe();
            };
        }
    }, [user]);

    const fetchTradingData = async () => {
        try {
            // Fetch recent trades
            const { data: trades, error: tradesError } = await supabase
                .from('bot_trades')
                .select('*')
                .eq('user_id', user?.id)
                .order('opened_at', { ascending: false })
                .limit(20);

            if (!tradesError && trades) {
                setRecentTrades(trades as Trade[]);
            }

            // Calculate bot activities
            const { data: bots, error: botsError } = await supabase
                .from('trading_bots')
                .select('*')
                .eq('user_id', user?.id)
                .eq('status', 'active');

            if (!botsError && bots) {
                const activities: BotActivity[] = bots.map((bot: any) => {
                    const botTrades = trades?.filter(t => t.bot_id === bot.id) || [];
                    const todayTrades = botTrades.filter(t => {
                        const tradeDate = new Date(t.opened_at);
                        const today = new Date();
                        return tradeDate.toDateString() === today.toDateString();
                    });
                    
                    const totalProfitToday = todayTrades
                        .filter(t => t.status === 'closed' && t.profit_loss)
                        .reduce((sum, t) => sum + (t.profit_loss || 0), 0);

                    return {
                        bot_id: bot.id,
                        bot_name: bot.bot_name,
                        status: bot.status,
                        last_trade_time: botTrades[0]?.opened_at || bot.last_active_at,
                        total_profit_today: totalProfitToday,
                        trades_today: todayTrades.length
                    };
                });

                setBotActivities(activities);
            }

            // Calculate real-time stats
            const openTrades = trades?.filter(t => t.status === 'open') || [];
            const closedTodayTrades = trades?.filter(t => {
                if (t.status !== 'closed') return false;
                const tradeDate = new Date(t.closed_at || '');
                const today = new Date();
                return tradeDate.toDateString() === today.toDateString();
            }) || [];

            const totalPnLToday = closedTodayTrades.reduce((sum, t) => sum + (t.profit_loss || 0), 0);
            const winRate = closedTodayTrades.length > 0 
                ? (closedTodayTrades.filter(t => (t.profit_loss || 0) > 0).length / closedTodayTrades.length) * 100
                : 0;

            setRealTimeData({
                openPositions: openTrades.length,
                todayTrades: closedTodayTrades.length,
                todayPnL: totalPnLToday,
                winRate: winRate
            });

        } catch (error) {
            console.error('Trading data olishda xato:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <Card variant="elevated">
                <div className="p-6 text-center">
                    <Activity className="w-8 h-8 animate-spin mx-auto mb-2 text-blue-400" />
                    <div>Trading monitor yuklanmoqda...</div>
                </div>
            </Card>
        );
    }

    return (
        <div className="space-y-6">
            {/* Real-time Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card variant="elevated">
                    <div className="p-4">
                        <div className="flex items-center justify-between mb-2">
                            <div className="text-sm text-slate-400">Ochiq Pozitsiyalar</div>
                            <Activity className="w-5 h-5 text-blue-400" />
                        </div>
                        <div className="text-2xl font-bold">
                            {realTimeData?.openPositions || 0}
                        </div>
                    </div>
                </Card>
                
                <Card variant="elevated">
                    <div className="p-4">
                        <div className="flex items-center justify-between mb-2">
                            <div className="text-sm text-slate-400">Bugungi Tradelar</div>
                            <BarChart3 className="w-5 h-5 text-purple-400" />
                        </div>
                        <div className="text-2xl font-bold">
                            {realTimeData?.todayTrades || 0}
                        </div>
                    </div>
                </Card>
                
                <Card variant="elevated">
                    <div className="p-4">
                        <div className="flex items-center justify-between mb-2">
                            <div className="text-sm text-slate-400">Bugungi P&L</div>
                            <DollarSign className="w-5 h-5 text-green-400" />
                        </div>
                        <div className={`text-2xl font-bold ${
                            (realTimeData?.todayPnL || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                        }`}>
                            ${Math.abs(realTimeData?.todayPnL || 0).toFixed(2)}
                        </div>
                    </div>
                </Card>
                
                <Card variant="elevated">
                    <div className="p-4">
                        <div className="flex items-center justify-between mb-2">
                            <div className="text-sm text-slate-400">Win Rate</div>
                            <TrendingUp className="w-5 h-5 text-blue-400" />
                        </div>
                        <div className="text-2xl font-bold text-blue-400">
                            {(realTimeData?.winRate || 0).toFixed(1)}%
                        </div>
                    </div>
                </Card>
            </div>

            {/* Bot Activities */}
            <Card variant="elevated">
                <div className="p-6">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <Activity className="w-5 h-5 text-blue-400" />
                        Bot Faoliyati
                    </h3>
                    <div className="space-y-3">
                        {botActivities.length > 0 ? (
                            botActivities.map((activity) => (
                                <div key={activity.bot_id} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                                    <div>
                                        <div className="font-semibold">{activity.bot_name}</div>
                                        <div className="text-sm text-slate-400 flex items-center gap-2 mt-1">
                                            <Clock className="w-3 h-3" />
                                            Oxirgi trade: {new Date(activity.last_trade_time).toLocaleTimeString('uz-UZ')}
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className={`font-semibold ${
                                            activity.total_profit_today >= 0 ? 'text-green-400' : 'text-red-400'
                                        }`}>
                                            ${Math.abs(activity.total_profit_today).toFixed(2)}
                                        </div>
                                        <div className="text-sm text-slate-400">
                                            {activity.trades_today} trades
                                        </div>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="text-center py-8 text-slate-400">
                                Faol botlar yo'q
                            </div>
                        )}
                    </div>
                </div>
            </Card>

            {/* Recent Trades */}
            <Card variant="elevated">
                <div className="p-6">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <BarChart3 className="w-5 h-5 text-purple-400" />
                        So'nggi Tradelar
                    </h3>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-slate-700">
                                    <th className="text-left py-3 px-2 text-sm font-medium text-slate-400">Vaqt</th>
                                    <th className="text-left py-3 px-2 text-sm font-medium text-slate-400">Bot</th>
                                    <th className="text-left py-3 px-2 text-sm font-medium text-slate-400">Symbol</th>
                                    <th className="text-left py-3 px-2 text-sm font-medium text-slate-400">Turi</th>
                                    <th className="text-left py-3 px-2 text-sm font-medium text-slate-400">Narx</th>
                                    <th className="text-left py-3 px-2 text-sm font-medium text-slate-400">Miqdor</th>
                                    <th className="text-left py-3 px-2 text-sm font-medium text-slate-400">P&L</th>
                                    <th className="text-left py-3 px-2 text-sm font-medium text-slate-400">Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {recentTrades.slice(0, 15).map((trade) => (
                                    <tr key={trade.id} className="border-b border-slate-800 hover:bg-slate-800/30">
                                        <td className="py-3 px-2 text-sm">
                                            {new Date(trade.opened_at).toLocaleTimeString('uz-UZ', { 
                                                hour: '2-digit', 
                                                minute: '2-digit' 
                                            })}
                                        </td>
                                        <td className="py-3 px-2 text-sm">{trade.bot_name}</td>
                                        <td className="py-3 px-2 text-sm font-medium">{trade.symbol}</td>
                                        <td className="py-3 px-2">
                                            <Badge color={trade.side === 'buy' ? 'success' : 'danger'}>
                                                {trade.side}
                                            </Badge>
                                        </td>
                                        <td className="py-3 px-2 text-sm">
                                            ${trade.entry_price.toFixed(2)}
                                        </td>
                                        <td className="py-3 px-2 text-sm">{trade.quantity}</td>
                                        <td className="py-3 px-2">
                                            {trade.profit_loss !== undefined ? (
                                                <div className={`font-semibold flex items-center ${
                                                    trade.profit_loss >= 0 ? 'text-green-400' : 'text-red-400'
                                                }`}>
                                                    {trade.profit_loss >= 0 ? (
                                                        <TrendingUp className="w-3 h-3 mr-1" />
                                                    ) : (
                                                        <TrendingDown className="w-3 h-3 mr-1" />
                                                    )}
                                                    ${Math.abs(trade.profit_loss).toFixed(2)}
                                                </div>
                                            ) : (
                                                <span className="text-slate-500">-</span>
                                            )}
                                        </td>
                                        <td className="py-3 px-2">
                                            <Badge 
                                                color={
                                                    trade.status === 'open' ? 'warning' :
                                                    trade.status === 'closed' ? 'success' : 'default'
                                                }
                                            >
                                                {trade.status}
                                            </Badge>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {recentTrades.length === 0 && (
                            <div className="text-center py-8 text-slate-400">
                                Hech qanday trade yo'q
                            </div>
                        )}
                    </div>
                </div>
            </Card>
        </div>
    );
}
