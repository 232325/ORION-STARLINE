import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../lib/supabase';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { Plus, Play, Pause, StopCircle, Trash2, TrendingUp, TrendingDown, Activity } from 'lucide-react';

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

export default function AIBotsPage() {
    const { user } = useAuth();
    const [bots, setBots] = useState<Bot[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [formData, setFormData] = useState({
        bot_name: '',
        bot_type: 'conservative',
        description: '',
        initial_capital: 10000,
        max_daily_trades: 10,
        max_position_size: 1000,
        trading_pairs: ['AAPL', 'MSFT', 'GOOGL'],
        risk_percentage: 2.0,
        stop_loss_percentage: 2.0,
        take_profit_percentage: 5.0
    });

    useEffect(() => {
        if (user) {
            fetchBots();
        }
    }, [user]);

    const fetchBots = async () => {
        try {
            setLoading(true);
            const { data, error } = await supabase.functions.invoke('ai-bot-manager', {
                body: {
                    action: 'get_all',
                    user_id: user?.id
                }
            });

            if (error) throw error;
            
            if (data?.data?.bots) {
                setBots(data.data.bots);
            }
        } catch (error) {
            console.error('Error fetching bots:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateBot = async () => {
        try {
            const { data, error } = await supabase.functions.invoke('ai-bot-manager', {
                body: {
                    action: 'create',
                    user_id: user?.id,
                    bot_data: formData
                }
            });

            if (error) throw error;

            setShowCreateForm(false);
            fetchBots();
            
            // Reset form
            setFormData({
                bot_name: '',
                bot_type: 'conservative',
                description: '',
                initial_capital: 10000,
                max_daily_trades: 10,
                max_position_size: 1000,
                trading_pairs: ['AAPL', 'MSFT', 'GOOGL'],
                risk_percentage: 2.0,
                stop_loss_percentage: 2.0,
                take_profit_percentage: 5.0
            });
        } catch (error) {
            console.error('Error creating bot:', error);
            alert('Bot olusturulurken hata olustu');
        }
    };

    const handleBotAction = async (botId: string, action: 'start' | 'stop' | 'pause' | 'delete') => {
        try {
            const { error } = await supabase.functions.invoke('ai-bot-manager', {
                body: {
                    action,
                    bot_id: botId,
                    user_id: user?.id
                }
            });

            if (error) throw error;
            
            fetchBots();
        } catch (error) {
            console.error(`Error ${action} bot:`, error);
            alert(`Bot ${action} isleminde hata olustu`);
        }
    };

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

    if (loading) {
        return (
            <div className="p-6">
                <div className="text-center py-12">
                    <div className="text-xl">Yuklanmoqda...</div>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">AI Trading Botlar</h1>
                    <p className="text-slate-400 mt-1">24/7 avtomatik trading botlarni boshqaring</p>
                </div>
                <Button onClick={() => setShowCreateForm(true)}>
                    <Plus className="w-5 h-5 mr-2" />
                    Yangi Bot
                </Button>
            </div>

            {/* Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <Card variant="elevated">
                    <div className="p-6">
                        <div className="text-sm text-slate-400">Jami Botlar</div>
                        <div className="text-3xl font-bold mt-2">{bots.length}</div>
                    </div>
                </Card>
                <Card variant="elevated">
                    <div className="p-6">
                        <div className="text-sm text-slate-400">Aktiv Botlar</div>
                        <div className="text-3xl font-bold mt-2 text-green-400">
                            {bots.filter(b => b.status === 'active').length}
                        </div>
                    </div>
                </Card>
                <Card variant="elevated">
                    <div className="p-6">
                        <div className="text-sm text-slate-400">Jami Daromad</div>
                        <div className="text-3xl font-bold mt-2 text-green-400">
                            ${bots.reduce((acc, b) => acc + (b.total_profit - b.total_loss), 0).toFixed(2)}
                        </div>
                    </div>
                </Card>
                <Card variant="elevated">
                    <div className="p-6">
                        <div className="text-sm text-slate-400">O'rtacha Win Rate</div>
                        <div className="text-3xl font-bold mt-2 text-blue-400">
                            {bots.length > 0 ? (bots.reduce((acc, b) => acc + b.win_rate, 0) / bots.length).toFixed(1) : 0}%
                        </div>
                    </div>
                </Card>
            </div>

            {/* Create Bot Form */}
            {showCreateForm && (
                <Card variant="elevated">
                    <div className="p-6">
                        <h2 className="text-xl font-bold mb-6">Yangi Bot Yaratish</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm font-medium mb-2">Bot Nomi</label>
                                <input
                                    type="text"
                                    value={formData.bot_name}
                                    onChange={(e) => setFormData({ ...formData, bot_name: e.target.value })}
                                    className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 focus:border-blue-500 outline-none"
                                    placeholder="Masalan: Conservative AAPL Bot"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-2">Bot Turi</label>
                                <select
                                    value={formData.bot_type}
                                    onChange={(e) => setFormData({ ...formData, bot_type: e.target.value })}
                                    className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 focus:border-blue-500 outline-none"
                                >
                                    <option value="conservative">Conservative - Xavfsiz</option>
                                    <option value="aggressive">Aggressive - Yuqori Daromad</option>
                                    <option value="balanced">Balanced - Muvozanatli</option>
                                    <option value="grid">Grid - DCA Strategiya</option>
                                    <option value="arbitrage">Arbitrage - Farq Savdosi</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-2">Boshlang'ich Kapital ($)</label>
                                <input
                                    type="number"
                                    value={formData.initial_capital}
                                    onChange={(e) => setFormData({ ...formData, initial_capital: parseFloat(e.target.value) })}
                                    className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 focus:border-blue-500 outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-2">Kunlik Maks. Tradelar</label>
                                <input
                                    type="number"
                                    value={formData.max_daily_trades}
                                    onChange={(e) => setFormData({ ...formData, max_daily_trades: parseInt(e.target.value) })}
                                    className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 focus:border-blue-500 outline-none"
                                />
                            </div>
                            <div className="md:col-span-2">
                                <label className="block text-sm font-medium mb-2">Tavsif</label>
                                <textarea
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 focus:border-blue-500 outline-none"
                                    rows={3}
                                    placeholder="Bot haqida qisqacha ma'lumot..."
                                />
                            </div>
                        </div>
                        <div className="flex gap-4 mt-6">
                            <Button onClick={handleCreateBot}>Bot Yaratish</Button>
                            <Button variant="outline" onClick={() => setShowCreateForm(false)}>Bekor Qilish</Button>
                        </div>
                    </div>
                </Card>
            )}

            {/* Bots List */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {bots.map((bot) => (
                    <Card key={bot.id} variant="elevated">
                        <div className="p-6">
                            <div className="flex items-start justify-between mb-4">
                                <div>
                                    <h3 className="text-xl font-bold">{bot.bot_name}</h3>
                                    <div className="flex items-center gap-2 mt-2">
                                        <Badge color={getBotTypeColor(bot.bot_type)}>
                                            {bot.bot_type}
                                        </Badge>
                                        <Badge color={getStatusColor(bot.status)}>
                                            {bot.status}
                                        </Badge>
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    {bot.status === 'active' ? (
                                        <>
                                            <Button size="sm" variant="outline" onClick={() => handleBotAction(bot.id, 'pause')}>
                                                <Pause className="w-4 h-4" />
                                            </Button>
                                            <Button size="sm" variant="outline" onClick={() => handleBotAction(bot.id, 'stop')}>
                                                <StopCircle className="w-4 h-4" />
                                            </Button>
                                        </>
                                    ) : (
                                        <Button size="sm" onClick={() => handleBotAction(bot.id, 'start')}>
                                            <Play className="w-4 h-4" />
                                        </Button>
                                    )}
                                    <Button size="sm" variant="danger" onClick={() => handleBotAction(bot.id, 'delete')}>
                                        <Trash2 className="w-4 h-4" />
                                    </Button>
                                </div>
                            </div>

                            {bot.description && (
                                <p className="text-sm text-slate-400 mb-4">{bot.description}</p>
                            )}

                            <div className="grid grid-cols-2 gap-4 mb-4">
                                <div>
                                    <div className="text-sm text-slate-400">Kapital</div>
                                    <div className="text-lg font-semibold">
                                        ${bot.current_capital.toFixed(2)}
                                    </div>
                                </div>
                                <div>
                                    <div className="text-sm text-slate-400">Daromad</div>
                                    <div className={`text-lg font-semibold flex items-center ${(bot.total_profit - bot.total_loss) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                        {(bot.total_profit - bot.total_loss) >= 0 ? (
                                            <TrendingUp className="w-4 h-4 mr-1" />
                                        ) : (
                                            <TrendingDown className="w-4 h-4 mr-1" />
                                        )}
                                        ${(bot.total_profit - bot.total_loss).toFixed(2)}
                                    </div>
                                </div>
                                <div>
                                    <div className="text-sm text-slate-400">Tradelar</div>
                                    <div className="text-lg font-semibold">{bot.total_trades}</div>
                                </div>
                                <div>
                                    <div className="text-sm text-slate-400">Win Rate</div>
                                    <div className="text-lg font-semibold text-blue-400">{bot.win_rate.toFixed(1)}%</div>
                                </div>
                            </div>

                            <div className="pt-4 border-t border-slate-700">
                                <div className="text-sm text-slate-400 mb-2">Trading Pairs</div>
                                <div className="flex flex-wrap gap-2">
                                    {bot.trading_pairs.map((pair, idx) => (
                                        <span key={idx} className="px-2 py-1 bg-slate-800 rounded text-xs">
                                            {pair}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            {bot.last_active_at && (
                                <div className="mt-4 text-xs text-slate-500 flex items-center">
                                    <Activity className="w-3 h-3 mr-1" />
                                    Oxirgi faollik: {new Date(bot.last_active_at).toLocaleString('uz-UZ')}
                                </div>
                            )}
                        </div>
                    </Card>
                ))}
            </div>

            {bots.length === 0 && !showCreateForm && (
                <Card variant="elevated">
                    <div className="p-12 text-center">
                        <div className="text-xl font-medium mb-2">Hech qanday bot yo'q</div>
                        <div className="text-slate-400 mb-6">
                            Birinchi AI trading botingizni yarating va 24/7 avtomatik savdo qiling
                        </div>
                        <Button onClick={() => setShowCreateForm(true)}>
                            <Plus className="w-5 h-5 mr-2" />
                            Yangi Bot Yaratish
                        </Button>
                    </div>
                </Card>
            )}
        </div>
    );
}
