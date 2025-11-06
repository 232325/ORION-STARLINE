import { useState } from 'react';
import Card from '../ui/Card';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import { Sparkles, TrendingUp, Target, Shield, BarChart3, Loader } from 'lucide-react';

interface Strategy {
    id: string;
    strategy_name: string;
    description: string;
    strategy_type: string;
    entry_rules: any;
    exit_rules: any;
    risk_rules: any;
    backtest_profit: number;
    backtest_trades: number;
    backtest_win_rate: number;
    created_at: string;
}

interface StrategyGeneratorProps {
    userId?: string;
    botId?: string;
    onStrategyCreated?: (strategy: Strategy) => void;
}

export default function StrategyGenerator({ userId, botId, onStrategyCreated }: StrategyGeneratorProps) {
    const [prompt, setPrompt] = useState('');
    const [strategyType, setStrategyType] = useState('trend_following');
    const [instruments, setInstruments] = useState(['AAPL', 'MSFT', 'GOOGL']);
    const [timeframe, setTimeframe] = useState('1h');
    const [generating, setGenerating] = useState(false);
    const [generatedStrategy, setGeneratedStrategy] = useState<Strategy | null>(null);
    const [backtestResults, setBacktestResults] = useState<any>(null);

    const handleGenerate = async () => {
        if (!prompt.trim()) {
            alert('Iltimos, strategiya tavsifini kiriting');
            return;
        }

        try {
            setGenerating(true);
            const response = await fetch(
                'https://bgrmoxpwfbuqszmmeodo.supabase.co/functions/v1/gpt4-strategy-generator-v2',
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`
                    },
                    body: JSON.stringify({
                        prompt,
                        user_id: userId,
                        bot_id: botId,
                        strategy_type: strategyType,
                        timeframe,
                        instruments
                    })
                }
            );

            const result = await response.json();
            
            if (result.data?.strategy) {
                setGeneratedStrategy(result.data.strategy);
                setBacktestResults(result.data.backtest_results);
                if (onStrategyCreated) {
                    onStrategyCreated(result.data.strategy);
                }
            } else if (result.error) {
                throw new Error(result.error.message);
            }
        } catch (error) {
            console.error('Strategiya yaratishda xato:', error);
            alert('Strategiya yaratilmadi. Qaytadan urinib ko\'ring.');
        } finally {
            setGenerating(false);
        }
    };

    const strategyTemplates = [
        {
            type: 'trend_following',
            title: 'Trend Following',
            description: 'Moving averages va momentum asosida trend ta\'qib qilish',
            icon: TrendingUp
        },
        {
            type: 'mean_reversion',
            title: 'Mean Reversion',
            description: 'Narx o\'rtachaga qaytish strategiyasi',
            icon: Target
        },
        {
            type: 'breakout',
            title: 'Breakout Trading',
            description: 'Qo\'llab-quvvatlash/qarshilik darajalarini buzish',
            icon: BarChart3
        },
        {
            type: 'risk_managed',
            title: 'Risk Managed',
            description: 'Yuqori risk boshqaruvi bilan strategiya',
            icon: Shield
        }
    ];

    return (
        <div className="space-y-6">
            {/* Strategy Input */}
            <Card variant="elevated">
                <div className="p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <Sparkles className="w-6 h-6 text-purple-400" />
                        <h3 className="text-xl font-bold">GPT-4 Strategy Generator V2</h3>
                        <Badge color="purple">AI-Powered</Badge>
                    </div>

                    {/* Prompt Input */}
                    <div className="mb-6">
                        <label className="block text-sm font-medium mb-2">
                            Strategiya Tavsifi
                        </label>
                        <textarea
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            className="w-full px-4 py-3 rounded-lg bg-slate-800 border border-slate-700 focus:border-purple-500 outline-none resize-none"
                            rows={4}
                            placeholder="Masalan: AAPL uchun RSI va MACD asosida trend-following strategiya yarating. RSI 30 dan past bo'lganda va MACD signal chizig'ini kesib o'tganda kirish. Take profit 5%, stop loss 2%."
                        />
                        <div className="text-xs text-slate-400 mt-2">
                            Tabiiy tilda strategiyangizni tasvirlang. GPT-4 uni professional trading strategiyasiga aylantiradi.
                        </div>
                    </div>

                    {/* Strategy Type */}
                    <div className="mb-6">
                        <label className="block text-sm font-medium mb-3">
                            Strategiya Turi
                        </label>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                            {strategyTemplates.map((template) => {
                                const Icon = template.icon;
                                return (
                                    <button
                                        key={template.type}
                                        onClick={() => setStrategyType(template.type)}
                                        className={`p-4 rounded-lg border-2 transition-all text-left ${
                                            strategyType === template.type
                                                ? 'border-purple-500 bg-purple-500/10'
                                                : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
                                        }`}
                                    >
                                        <Icon className={`w-5 h-5 mb-2 ${
                                            strategyType === template.type ? 'text-purple-400' : 'text-slate-400'
                                        }`} />
                                        <div className="font-medium text-sm mb-1">{template.title}</div>
                                        <div className="text-xs text-slate-400">{template.description}</div>
                                    </button>
                                );
                            })}
                        </div>
                    </div>

                    {/* Configuration */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                        <div>
                            <label className="block text-sm font-medium mb-2">
                                Timeframe
                            </label>
                            <select
                                value={timeframe}
                                onChange={(e) => setTimeframe(e.target.value)}
                                className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 focus:border-purple-500 outline-none"
                            >
                                <option value="1m">1 Daqiqa</option>
                                <option value="5m">5 Daqiqa</option>
                                <option value="15m">15 Daqiqa</option>
                                <option value="1h">1 Soat</option>
                                <option value="4h">4 Soat</option>
                                <option value="1d">1 Kun</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">
                                Instrumentlar (vergul bilan ajrating)
                            </label>
                            <input
                                type="text"
                                value={instruments.join(', ')}
                                onChange={(e) => setInstruments(e.target.value.split(',').map(s => s.trim()))}
                                className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 focus:border-purple-500 outline-none"
                                placeholder="AAPL, MSFT, GOOGL"
                            />
                        </div>
                    </div>

                    {/* Generate Button */}
                    <Button
                        onClick={handleGenerate}
                        disabled={generating || !prompt.trim()}
                        className="w-full"
                    >
                        {generating ? (
                            <>
                                <Loader className="w-5 h-5 mr-2 animate-spin" />
                                GPT-4 strategiya yaratmoqda...
                            </>
                        ) : (
                            <>
                                <Sparkles className="w-5 h-5 mr-2" />
                                Strategiya Yaratish
                            </>
                        )}
                    </Button>
                </div>
            </Card>

            {/* Generated Strategy */}
            {generatedStrategy && (
                <Card variant="elevated">
                    <div className="p-6">
                        <div className="flex items-center justify-between mb-6">
                            <div>
                                <h3 className="text-xl font-bold">{generatedStrategy.strategy_name}</h3>
                                <div className="flex items-center gap-2 mt-2">
                                    <Badge color="purple">{generatedStrategy.strategy_type}</Badge>
                                    <Badge color="success">Yaratildi</Badge>
                                </div>
                            </div>
                        </div>

                        {/* Description */}
                        <div className="mb-6">
                            <div className="text-sm text-slate-400 mb-2">Tavsif</div>
                            <div className="p-4 bg-slate-800/50 rounded-lg">
                                {generatedStrategy.description}
                            </div>
                        </div>

                        {/* Rules */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                            <div>
                                <div className="text-sm font-medium mb-3">Entry Rules</div>
                                <div className="p-4 bg-slate-800/50 rounded-lg space-y-2">
                                    {Object.entries(generatedStrategy.entry_rules || {}).map(([key, value]) => (
                                        <div key={key} className="text-sm">
                                            <span className="text-slate-400">{key}:</span>
                                            <span className="ml-2">{String(value)}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            <div>
                                <div className="text-sm font-medium mb-3">Exit Rules</div>
                                <div className="p-4 bg-slate-800/50 rounded-lg space-y-2">
                                    {Object.entries(generatedStrategy.exit_rules || {}).map(([key, value]) => (
                                        <div key={key} className="text-sm">
                                            <span className="text-slate-400">{key}:</span>
                                            <span className="ml-2">{String(value)}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            <div>
                                <div className="text-sm font-medium mb-3">Risk Rules</div>
                                <div className="p-4 bg-slate-800/50 rounded-lg space-y-2">
                                    {Object.entries(generatedStrategy.risk_rules || {}).map(([key, value]) => (
                                        <div key={key} className="text-sm">
                                            <span className="text-slate-400">{key}:</span>
                                            <span className="ml-2">{String(value)}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* Backtest Results */}
                        {backtestResults && (
                            <div>
                                <div className="text-lg font-semibold mb-4">Backtest Natijalari</div>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <div className="p-4 bg-slate-800/50 rounded-lg">
                                        <div className="text-sm text-slate-400">Jami Tradelar</div>
                                        <div className="text-2xl font-bold mt-1">
                                            {backtestResults.total_trades}
                                        </div>
                                    </div>
                                    <div className="p-4 bg-slate-800/50 rounded-lg">
                                        <div className="text-sm text-slate-400">Win Rate</div>
                                        <div className="text-2xl font-bold text-blue-400 mt-1">
                                            {backtestResults.win_rate.toFixed(1)}%
                                        </div>
                                    </div>
                                    <div className="p-4 bg-slate-800/50 rounded-lg">
                                        <div className="text-sm text-slate-400">Net Profit</div>
                                        <div className={`text-2xl font-bold mt-1 ${
                                            backtestResults.net_profit >= 0 ? 'text-green-400' : 'text-red-400'
                                        }`}>
                                            ${backtestResults.net_profit.toFixed(2)}
                                        </div>
                                    </div>
                                    <div className="p-4 bg-slate-800/50 rounded-lg">
                                        <div className="text-sm text-slate-400">Sharpe Ratio</div>
                                        <div className="text-2xl font-bold text-purple-400 mt-1">
                                            {backtestResults.sharpe_ratio.toFixed(2)}
                                        </div>
                                    </div>
                                    <div className="p-4 bg-slate-800/50 rounded-lg">
                                        <div className="text-sm text-slate-400">Max Drawdown</div>
                                        <div className="text-2xl font-bold text-red-400 mt-1">
                                            {backtestResults.max_drawdown.toFixed(2)}%
                                        </div>
                                    </div>
                                    <div className="p-4 bg-slate-800/50 rounded-lg">
                                        <div className="text-sm text-slate-400">Winning Trades</div>
                                        <div className="text-2xl font-bold text-green-400 mt-1">
                                            {backtestResults.winning_trades}
                                        </div>
                                    </div>
                                    <div className="p-4 bg-slate-800/50 rounded-lg">
                                        <div className="text-sm text-slate-400">Losing Trades</div>
                                        <div className="text-2xl font-bold text-red-400 mt-1">
                                            {backtestResults.losing_trades}
                                        </div>
                                    </div>
                                    <div className="p-4 bg-slate-800/50 rounded-lg">
                                        <div className="text-sm text-slate-400">Profit Factor</div>
                                        <div className="text-2xl font-bold mt-1">
                                            {(backtestResults.winning_trades / Math.max(backtestResults.losing_trades, 1)).toFixed(2)}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div className="text-xs text-slate-500 mt-6">
                            Yaratilgan: {new Date(generatedStrategy.created_at).toLocaleString('uz-UZ')}
                        </div>
                    </div>
                </Card>
            )}
        </div>
    );
}
