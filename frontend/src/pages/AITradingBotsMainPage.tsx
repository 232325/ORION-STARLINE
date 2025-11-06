import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../lib/supabase';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import BotCard from '../components/TradingBots/BotCard';
import BotConfigModal from '../components/TradingBots/BotConfigModal';
import TradingMonitor from '../components/TradingBots/TradingMonitor';
import PerformanceAnalytics from '../components/TradingBots/PerformanceAnalytics';
import StrategyGenerator from '../components/TradingBots/StrategyGenerator';
import { Plus, Activity, Bot, Sparkles, BarChart3, TrendingUp } from 'lucide-react';

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

export default function AITradingBotsMainPage() {
    const { user } = useAuth();
    const [bots, setBots] = useState<Bot[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [selectedBot, setSelectedBot] = useState<Bot | null>(null);
    const [showConfigModal, setShowConfigModal] = useState(false);
    const [activeTab, setActiveTab] = useState<'dashboard' | 'monitor' | 'analytics' | 'strategy'>('dashboard');
    
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
            console.error('Botlarni olishda xato:', error);
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
            console.error('Bot yaratishda xato:', error);
            alert('Bot yaratilmadi. Qaytadan urinib ko\'ring.');
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
            console.error(`Bot ${action} xatosi:`, error);
            alert(`Bot ${action} bajarilmadi. Qaytadan urinib ko\'ring.`);
        }
    };

    const handleConfigureBot = (bot: Bot) => {
        setSelectedBot(bot);
        setShowConfigModal(true);
    };

    const handleSaveConfig = async (botId: string, config: any) => {
        try {
            const { error } = await supabase.functions.invoke('ai-bot-manager', {
                body: {
                    action: 'update_config',
                    bot_id: botId,
                    user_id: user?.id,
                    config
                }
            });

            if (error) throw error;
            
            fetchBots();
        } catch (error) {
            console.error('Konfiguratsiya saqlashda xato:', error);
            throw error;
        }
    };

    const getBotTypeDescription = (type: string) => {
        switch (type) {
            case 'conservative': return { title: 'Conservative Bot', desc: 'Xavfsiz - Past risk, barqaror daromad', color: 'blue' };
            case 'aggressive': return { title: 'Aggressive Bot', desc: 'Yuqori daromad - Yuqori risk', color: 'red' };
            case 'balanced': return { title: 'Balanced Bot', desc: 'Muvozanatli - O\'rtacha risk', color: 'purple' };
            case 'grid': return { title: 'Grid Bot', desc: 'DCA Strategiya - Dollar-cost averaging', color: 'green' };
            case 'arbitrage': return { title: 'Arbitrage Bot', desc: 'Farq Savdosi - Cross-exchange imkoniyatlari', color: 'yellow' };
            default: return { title: 'Custom Bot', desc: 'Maxsus sozlangan', color: 'gray' };
        }
    };

    const tabs = [
        { id: 'dashboard' as const, name: 'Dashboard', icon: Activity },
        { id: 'monitor' as const, name: 'Live Monitor', icon: Bot },
        { id: 'analytics' as const, name: 'Analytics', icon: BarChart3 },
        { id: 'strategy' as const, name: 'GPT-4 Strategy', icon: Sparkles }
    ];

    if (loading) {
        return (
            <div className="p-6">
                <div className="text-center py-12">
                    <Activity className="w-12 h-12 animate-spin mx-auto mb-4 text-blue-400" />
                    <div className="text-xl">Yuklanmoqda...</div>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <Bot className="w-8 h-8 text-blue-400" />
                        AI Trading Bots Dashboard
                    </h1>
                    <p className="text-slate-400 mt-1">
                        V2 ML Price Predictor & GPT-4 Strategy Generator bilan 24/7 avtomatik trading
                    </p>
                </div>
                <Button onClick={() => setShowCreateForm(true)} size="lg">
                    <Plus className="w-5 h-5 mr-2" />
                    Yangi Bot
                </Button>
            </div>

            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <Card variant="elevated">
                    <div className="p-4">
                        <div className="text-sm text-slate-400">Jami Botlar</div>
                        <div className="text-3xl font-bold mt-2">{bots.length}</div>
                    </div>
                </Card>
                <Card variant="elevated">
                    <div className="p-4">
                        <div className="text-sm text-slate-400">Aktiv Botlar</div>
                        <div className="text-3xl font-bold mt-2 text-green-400">
                            {bots.filter(b => b.status === 'active').length}
                        </div>
                    </div>
                </Card>
                <Card variant="elevated">
                    <div className="p-4">
                        <div className="text-sm text-slate-400">Jami Daromad</div>
                        <div className="text-3xl font-bold mt-2 text-green-400">
                            ${bots.reduce((acc, b) => acc + (b.total_profit - b.total_loss), 0).toFixed(2)}
                        </div>
                    </div>
                </Card>
                <Card variant="elevated">
                    <div className="p-4">
                        <div className="text-sm text-slate-400">O'rtacha Win Rate</div>
                        <div className="text-3xl font-bold mt-2 text-blue-400">
                            {bots.length > 0 ? (bots.reduce((acc, b) => acc + b.win_rate, 0) / bots.length).toFixed(1) : 0}%
                        </div>
                    </div>
                </Card>
                <Card variant="elevated">
                    <div className="p-4">
                        <div className="text-sm text-slate-400">Jami Tradelar</div>
                        <div className="text-3xl font-bold mt-2 text-purple-400">
                            {bots.reduce((acc, b) => acc + b.total_trades, 0)}
                        </div>
                    </div>
                </Card>
            </div>

            {/* Tabs */}
            <Card variant="elevated">
                <div className="p-2">
                    <div className="flex gap-2">
                        {tabs.map((tab) => {
                            const Icon = tab.icon;
                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
                                        activeTab === tab.id
                                            ? 'bg-blue-500 text-white'
                                            : 'bg-slate-800/50 text-slate-300 hover:bg-slate-800'
                                    }`}
                                >
                                    <Icon className="w-5 h-5" />
                                    {tab.name}
                                </button>
                            );
                        })}
                    </div>
                </div>
            </Card>

            {/* Tab Content */}
            {activeTab === 'dashboard' && (
                <>
                    {/* Create Bot Form */}
                    {showCreateForm && (
                        <Card variant="elevated">
                            <div className="p-6">
                                <h2 className="text-xl font-bold mb-6">Yangi AI Trading Bot Yaratish</h2>
                                
                                {/* Bot Type Selection */}
                                <div className="mb-6">
                                    <label className="block text-sm font-medium mb-3">Bot Turini Tanlang</label>
                                    <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                                        {['conservative', 'aggressive', 'balanced', 'grid', 'arbitrage'].map((type) => {
                                            const info = getBotTypeDescription(type);
                                            return (
                                                <button
                                                    key={type}
                                                    onClick={() => setFormData({ ...formData, bot_type: type })}
                                                    className={`p-4 rounded-lg border-2 transition-all text-left ${
                                                        formData.bot_type === type
                                                            ? 'border-blue-500 bg-blue-500/10'
                                                            : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
                                                    }`}
                                                >
                                                    <Badge color={info.color as any} className="mb-2">{info.title}</Badge>
                                                    <div className="text-xs text-slate-400 mt-2">{info.desc}</div>
                                                </button>
                                            );
                                        })}
                                    </div>
                                </div>

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
                                        <label className="block text-sm font-medium mb-2">Boshlang'ich Kapital ($)</label>
                                        <input
                                            type="number"
                                            value={formData.initial_capital}
                                            onChange={(e) => setFormData({ ...formData, initial_capital: parseFloat(e.target.value) })}
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

                    {/* Bots Grid */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {bots.map((bot) => (
                            <BotCard
                                key={bot.id}
                                bot={bot}
                                onAction={handleBotAction}
                                onConfigure={handleConfigureBot}
                            />
                        ))}
                    </div>

                    {bots.length === 0 && !showCreateForm && (
                        <Card variant="elevated">
                            <div className="p-12 text-center">
                                <Bot className="w-16 h-16 mx-auto mb-4 text-slate-600" />
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
                </>
            )}

            {activeTab === 'monitor' && <TradingMonitor />}
            {activeTab === 'analytics' && <PerformanceAnalytics userId={user?.id} />}
            {activeTab === 'strategy' && <StrategyGenerator userId={user?.id} />}

            {/* Config Modal */}
            <BotConfigModal
                bot={selectedBot}
                isOpen={showConfigModal}
                onClose={() => {
                    setShowConfigModal(false);
                    setSelectedBot(null);
                }}
                onSave={handleSaveConfig}
            />
        </div>
    );
}
