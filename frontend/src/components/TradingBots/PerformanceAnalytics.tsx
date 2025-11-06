import { useState, useEffect } from 'react';
import Card from '../ui/Card';
import Badge from '../ui/Badge';
import { TrendingUp, TrendingDown, DollarSign, Activity, BarChart3, PieChart } from 'lucide-react';

interface PerformanceData {
    totalProfit: number;
    totalTrades: number;
    winRate: number;
    avgProfit: number;
    avgLoss: number;
    bestTrade: number;
    worstTrade: number;
    profitFactor: number;
    sharpeRatio: number;
    maxDrawdown: number;
    dailyReturns: { date: string; profit: number }[];
    tradingPairs: { pair: string; trades: number; profit: number }[];
}

interface PerformanceAnalyticsProps {
    botId?: string;
    userId?: string;
}

export default function PerformanceAnalytics({ botId, userId }: PerformanceAnalyticsProps) {
    const [performanceData, setPerformanceData] = useState<PerformanceData | null>(null);
    const [loading, setLoading] = useState(true);
    const [timeRange, setTimeRange] = useState('7d');

    useEffect(() => {
        fetchPerformanceData();
    }, [botId, userId, timeRange]);

    const fetchPerformanceData = async () => {
        try {
            setLoading(true);
            
            // Real Supabase Edge Function dan ma'lumot olish
            const response = await fetch(
                'https://bgrmoxpwfbuqszmmeodo.supabase.co/functions/v1/performance-analytics',
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`
                    },
                    body: JSON.stringify({
                        user_id: userId,
                        bot_id: botId,
                        time_range: timeRange
                    })
                }
            );

            if (!response.ok) {
                throw new Error('Performance data olishda xato');
            }

            const result = await response.json();
            
            if (result.data) {
                setPerformanceData(result.data);
            } else {
                // Agar ma'lumot bo'lmasa, default qiymatlar
                setPerformanceData({
                    totalProfit: 0,
                    totalTrades: 0,
                    winRate: 0,
                    avgProfit: 0,
                    avgLoss: 0,
                    bestTrade: 0,
                    worstTrade: 0,
                    profitFactor: 0,
                    sharpeRatio: 0,
                    maxDrawdown: 0,
                    dailyReturns: [],
                    tradingPairs: []
                });
            }
        } catch (error) {
            console.error('Performance data olishda xato:', error);
            // Fallback demo data
            setPerformanceData({
                totalProfit: 0,
                totalTrades: 0,
                winRate: 0,
                avgProfit: 0,
                avgLoss: 0,
                bestTrade: 0,
                worstTrade: 0,
                profitFactor: 0,
                sharpeRatio: 0,
                maxDrawdown: 0,
                dailyReturns: [],
                tradingPairs: []
            });
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <Card variant="elevated">
                <div className="p-6 text-center">
                    <Activity className="w-8 h-8 animate-spin mx-auto mb-2 text-blue-400" />
                    <div>Performance analytics yuklanmoqda...</div>
                </div>
            </Card>
        );
    }

    if (!performanceData) return null;

    return (
        <div className="space-y-6">
            {/* Time Range Selector */}
            <Card variant="elevated">
                <div className="p-4">
                    <div className="flex gap-2">
                        {['24h', '7d', '30d', '90d', 'all'].map((range) => (
                            <button
                                key={range}
                                onClick={() => setTimeRange(range)}
                                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                                    timeRange === range
                                        ? 'bg-blue-500 text-white'
                                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                                }`}
                            >
                                {range === '24h' ? '24 Soat' :
                                 range === '7d' ? '7 Kun' :
                                 range === '30d' ? '30 Kun' :
                                 range === '90d' ? '90 Kun' : 'Barchasi'}
                            </button>
                        ))}
                    </div>
                </div>
            </Card>

            {/* Key Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card variant="elevated">
                    <div className="p-4">
                        <div className="flex items-center justify-between mb-2">
                            <div className="text-sm text-slate-400">Jami Foyda</div>
                            <DollarSign className="w-5 h-5 text-green-400" />
                        </div>
                        <div className="text-2xl font-bold text-green-400">
                            ${performanceData.totalProfit.toFixed(2)}
                        </div>
                        <div className="text-xs text-slate-500 mt-1">
                            {performanceData.totalTrades} trades
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
                            {performanceData.winRate.toFixed(1)}%
                        </div>
                        <div className="text-xs text-slate-500 mt-1">
                            Yuqori natija
                        </div>
                    </div>
                </Card>

                <Card variant="elevated">
                    <div className="p-4">
                        <div className="flex items-center justify-between mb-2">
                            <div className="text-sm text-slate-400">Profit Factor</div>
                            <BarChart3 className="w-5 h-5 text-purple-400" />
                        </div>
                        <div className="text-2xl font-bold text-purple-400">
                            {performanceData.profitFactor.toFixed(2)}
                        </div>
                        <div className="text-xs text-slate-500 mt-1">
                            {performanceData.profitFactor > 2 ? 'A\'lo' : 'Yaxshi'}
                        </div>
                    </div>
                </Card>

                <Card variant="elevated">
                    <div className="p-4">
                        <div className="flex items-center justify-between mb-2">
                            <div className="text-sm text-slate-400">Sharpe Ratio</div>
                            <Activity className="w-5 h-5 text-yellow-400" />
                        </div>
                        <div className="text-2xl font-bold text-yellow-400">
                            {performanceData.sharpeRatio.toFixed(2)}
                        </div>
                        <div className="text-xs text-slate-500 mt-1">
                            Risk-adjusted return
                        </div>
                    </div>
                </Card>
            </div>

            {/* Detailed Metrics */}
            <Card variant="elevated">
                <div className="p-6">
                    <h3 className="text-lg font-semibold mb-4">Batafsil Metrikalar</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                        <div className="p-4 bg-slate-800/50 rounded-lg">
                            <div className="text-sm text-slate-400 mb-1">O'rtacha Foyda</div>
                            <div className="text-xl font-semibold text-green-400">
                                ${performanceData.avgProfit.toFixed(2)}
                            </div>
                        </div>
                        <div className="p-4 bg-slate-800/50 rounded-lg">
                            <div className="text-sm text-slate-400 mb-1">O'rtacha Zarar</div>
                            <div className="text-xl font-semibold text-red-400">
                                ${Math.abs(performanceData.avgLoss).toFixed(2)}
                            </div>
                        </div>
                        <div className="p-4 bg-slate-800/50 rounded-lg">
                            <div className="text-sm text-slate-400 mb-1">Eng Yaxshi Trade</div>
                            <div className="text-xl font-semibold text-green-400">
                                ${performanceData.bestTrade.toFixed(2)}
                            </div>
                        </div>
                        <div className="p-4 bg-slate-800/50 rounded-lg">
                            <div className="text-sm text-slate-400 mb-1">Eng Yomon Trade</div>
                            <div className="text-xl font-semibold text-red-400">
                                ${Math.abs(performanceData.worstTrade).toFixed(2)}
                            </div>
                        </div>
                        <div className="p-4 bg-slate-800/50 rounded-lg">
                            <div className="text-sm text-slate-400 mb-1">Max Drawdown</div>
                            <div className="text-xl font-semibold text-red-400">
                                {performanceData.maxDrawdown.toFixed(2)}%
                            </div>
                        </div>
                        <div className="p-4 bg-slate-800/50 rounded-lg">
                            <div className="text-sm text-slate-400 mb-1">Risk/Reward</div>
                            <div className="text-xl font-semibold">
                                1:{(performanceData.avgProfit / Math.abs(performanceData.avgLoss)).toFixed(2)}
                            </div>
                        </div>
                        <div className="p-4 bg-slate-800/50 rounded-lg">
                            <div className="text-sm text-slate-400 mb-1">Jami Tradelar</div>
                            <div className="text-xl font-semibold">
                                {performanceData.totalTrades}
                            </div>
                        </div>
                        <div className="p-4 bg-slate-800/50 rounded-lg">
                            <div className="text-sm text-slate-400 mb-1">O'rtacha Kunlik</div>
                            <div className="text-xl font-semibold text-green-400">
                                ${(performanceData.totalProfit / 30).toFixed(2)}
                            </div>
                        </div>
                    </div>
                </div>
            </Card>

            {/* Trading Pairs Performance */}
            <Card variant="elevated">
                <div className="p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <PieChart className="w-5 h-5 text-blue-400" />
                        <h3 className="text-lg font-semibold">Trading Pairs Performance</h3>
                    </div>
                    <div className="space-y-3">
                        {performanceData.tradingPairs.map((pair) => {
                            const profitPercent = (pair.profit / performanceData.totalProfit) * 100;
                            return (
                                <div key={pair.pair} className="p-4 bg-slate-800/50 rounded-lg">
                                    <div className="flex items-center justify-between mb-2">
                                        <div className="flex items-center gap-3">
                                            <Badge color="blue">{pair.pair}</Badge>
                                            <span className="text-sm text-slate-400">
                                                {pair.trades} trades
                                            </span>
                                        </div>
                                        <div className="text-right">
                                            <div className="font-semibold text-green-400">
                                                ${pair.profit.toFixed(2)}
                                            </div>
                                            <div className="text-xs text-slate-400">
                                                {profitPercent.toFixed(1)}% of total
                                            </div>
                                        </div>
                                    </div>
                                    <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
                                        <div 
                                            className="h-full bg-gradient-to-r from-green-500 to-green-400"
                                            style={{ width: `${profitPercent}%` }}
                                        />
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </Card>

            {/* Daily Returns Chart (Simplified) */}
            <Card variant="elevated">
                <div className="p-6">
                    <h3 className="text-lg font-semibold mb-4">Kunlik Daromad</h3>
                    <div className="h-64 flex items-end justify-between gap-1">
                        {performanceData.dailyReturns.slice(-30).map((day, index) => {
                            const maxProfit = Math.max(...performanceData.dailyReturns.map(d => Math.abs(d.profit)));
                            const height = (Math.abs(day.profit) / maxProfit) * 100;
                            return (
                                <div key={index} className="flex-1 flex flex-col items-center justify-end">
                                    <div 
                                        className={`w-full ${day.profit >= 0 ? 'bg-green-500' : 'bg-red-500'} rounded-t transition-all hover:opacity-80`}
                                        style={{ height: `${height}%`, minHeight: '2px' }}
                                        title={`${day.date}: $${day.profit.toFixed(2)}`}
                                    />
                                </div>
                            );
                        })}
                    </div>
                    <div className="flex justify-between mt-2 text-xs text-slate-500">
                        <span>{performanceData.dailyReturns[0]?.date}</span>
                        <span>{performanceData.dailyReturns[performanceData.dailyReturns.length - 1]?.date}</span>
                    </div>
                </div>
            </Card>
        </div>
    );
}
