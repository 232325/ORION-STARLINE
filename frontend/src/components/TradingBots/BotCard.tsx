import { useState } from 'react';
import Card from '../ui/Card';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import { Play, Pause, StopCircle, Trash2, TrendingUp, TrendingDown, Activity, Settings } from 'lucide-react';

interface Bot {
    id: string;
    bot_name: string;
    bot_type: string;
    description: string;
    status: 'active' | 'inactive' | 'paused' | 'error';
    trading_pairs: string[];
    current_capital: number;
    initial_capital: number;
    total_trades: number;
    winning_trades: number;
    losing_trades: number;
    win_rate: number;
    total_profit: number;
    total_loss: number;
    created_at: string;
    last_active_at: string;
}

interface BotCardProps {
    bot: Bot;
    onAction: (botId: string, action: 'start' | 'stop' | 'pause' | 'delete') => void;
    onConfigure?: (bot: Bot) => void;
}

export default function BotCard({ bot, onAction, onConfigure }: BotCardProps) {
    const getBotTypeColor = (type: string) => {
        switch (type) {
            case 'conservative': return 'blue';
            case 'aggressive': return 'red';
            case 'balanced': return 'purple';
            case 'grid': return 'green';
            case 'arbitrage': return 'yellow';
            default: return 'gray';
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active': return 'success';
            case 'inactive': return 'default';
            case 'paused': return 'warning';
            case 'error': return 'danger';
            default: return 'default';
        }
    };

    const getBotTypeDescription = (type: string) => {
        switch (type) {
            case 'conservative': return 'Xavfsiz - Past risk';
            case 'aggressive': return 'Yuqori daromad - Yuqori risk';
            case 'balanced': return 'Muvozanatli - O\'rtacha risk';
            case 'grid': return 'DCA Strategiya';
            case 'arbitrage': return 'Farq Savdosi';
            default: return '';
        }
    };

    const netProfit = bot.total_profit - bot.total_loss;
    const profitPercent = bot.initial_capital > 0 
        ? ((bot.current_capital - bot.initial_capital) / bot.initial_capital) * 100 
        : 0;

    return (
        <Card variant="elevated" className="hover:shadow-lg transition-all duration-300">
            <div className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                        <h3 className="text-xl font-bold mb-2">{bot.bot_name}</h3>
                        <div className="flex items-center gap-2 flex-wrap">
                            <Badge color={getBotTypeColor(bot.bot_type) as any}>
                                {bot.bot_type}
                            </Badge>
                            <Badge color={getStatusColor(bot.status) as any}>
                                {bot.status}
                            </Badge>
                            <span className="text-xs text-slate-500">
                                {getBotTypeDescription(bot.bot_type)}
                            </span>
                        </div>
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="flex gap-2">
                        {bot.status === 'active' ? (
                            <>
                                <Button 
                                    size="sm" 
                                    variant="outline" 
                                    onClick={() => onAction(bot.id, 'pause')}
                                    title="Pauza"
                                >
                                    <Pause className="w-4 h-4" />
                                </Button>
                                <Button 
                                    size="sm" 
                                    variant="outline" 
                                    onClick={() => onAction(bot.id, 'stop')}
                                    title="To'xtatish"
                                >
                                    <StopCircle className="w-4 h-4" />
                                </Button>
                            </>
                        ) : (
                            <Button 
                                size="sm" 
                                onClick={() => onAction(bot.id, 'start')}
                                title="Boshlash"
                            >
                                <Play className="w-4 h-4" />
                            </Button>
                        )}
                        {onConfigure && (
                            <Button 
                                size="sm" 
                                variant="outline" 
                                onClick={() => onConfigure(bot)}
                                title="Sozlamalar"
                            >
                                <Settings className="w-4 h-4" />
                            </Button>
                        )}
                        <Button 
                            size="sm" 
                            variant="danger" 
                            onClick={() => onAction(bot.id, 'delete')}
                            title="O'chirish"
                        >
                            <Trash2 className="w-4 h-4" />
                        </Button>
                    </div>
                </div>

                {/* Description */}
                {bot.description && (
                    <p className="text-sm text-slate-400 mb-4 line-clamp-2">
                        {bot.description}
                    </p>
                )}

                {/* Main Metrics */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                        <div className="text-sm text-slate-400">Joriy Kapital</div>
                        <div className="text-lg font-semibold text-white">
                            ${bot.current_capital.toFixed(2)}
                        </div>
                        <div className={`text-xs ${profitPercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {profitPercent >= 0 ? '+' : ''}{profitPercent.toFixed(2)}%
                        </div>
                    </div>
                    <div>
                        <div className="text-sm text-slate-400">Daromad/Zarar</div>
                        <div className={`text-lg font-semibold flex items-center ${netProfit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {netProfit >= 0 ? (
                                <TrendingUp className="w-4 h-4 mr-1" />
                            ) : (
                                <TrendingDown className="w-4 h-4 mr-1" />
                            )}
                            ${Math.abs(netProfit).toFixed(2)}
                        </div>
                    </div>
                </div>

                {/* Performance Stats */}
                <div className="grid grid-cols-3 gap-4 mb-4 p-3 bg-slate-800/50 rounded-lg">
                    <div className="text-center">
                        <div className="text-xs text-slate-400">Jami</div>
                        <div className="text-lg font-semibold">{bot.total_trades}</div>
                    </div>
                    <div className="text-center">
                        <div className="text-xs text-slate-400">Yutgan</div>
                        <div className="text-lg font-semibold text-green-400">
                            {bot.winning_trades}
                        </div>
                    </div>
                    <div className="text-center">
                        <div className="text-xs text-slate-400">Win Rate</div>
                        <div className="text-lg font-semibold text-blue-400">
                            {bot.win_rate.toFixed(1)}%
                        </div>
                    </div>
                </div>

                {/* Trading Pairs */}
                <div className="pt-4 border-t border-slate-700">
                    <div className="text-sm text-slate-400 mb-2">Trading Pairs</div>
                    <div className="flex flex-wrap gap-2">
                        {bot.trading_pairs.slice(0, 5).map((pair, idx) => (
                            <span 
                                key={idx} 
                                className="px-2 py-1 bg-slate-800 rounded text-xs font-medium"
                            >
                                {pair}
                            </span>
                        ))}
                        {bot.trading_pairs.length > 5 && (
                            <span className="px-2 py-1 bg-slate-800 rounded text-xs font-medium text-slate-400">
                                +{bot.trading_pairs.length - 5}
                            </span>
                        )}
                    </div>
                </div>

                {/* Last Activity */}
                {bot.last_active_at && (
                    <div className="mt-4 text-xs text-slate-500 flex items-center">
                        <Activity className="w-3 h-3 mr-1" />
                        Oxirgi faollik: {new Date(bot.last_active_at).toLocaleString('uz-UZ')}
                    </div>
                )}
            </div>
        </Card>
    );
}
