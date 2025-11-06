import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../lib/supabase';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { Sparkles, TrendingUp, Shield, Zap, Target } from 'lucide-react';

interface Strategy {
    id: string;
    strategy_name: string;
    description: string;
    strategy_type: string;
    status: string;
    entry_rules: any;
    exit_rules: any;
    risk_rules: any;
    created_at: string;
}

interface BacktestResults {
    total_trades: number;
    winning_trades: number;
    losing_trades: number;
    win_rate: string;
    net_profit: string;
    sharpe_ratio: string;
    max_drawdown: string;
}

export default function StrategyBuilderPage() {
    const { user } = useAuth();
    const [prompt, setPrompt] = useState('');
    const [loading, setLoading] = useState(false);
    const [generatedStrategy, setGeneratedStrategy] = useState<Strategy | null>(null);
    const [backtestResults, setBacktestResults] = useState<BacktestResults | null>(null);
    const [gptAnalysis, setGptAnalysis] = useState('');

    const examplePrompts = [
        "Konservativ trend-following strategiyasi yarating. RSI va MACD indikatorlaridan foydalaning",
        "Scalping strategiyasi kerak. 5 minutlik timeframe'da ishlaydi",
        "Mean reversion strategiyasi. Bollinger Bands va volatilite'dan foydalaning",
        "Breakout strategiyasi. Volume spike va price action pattern'lari",
        "Grid trading strategiyasi. Dollar-cost averaging bilan"
    ];

    const handleGenerateStrategy = async () => {
        if (!prompt.trim()) {
            alert('Iltimos, strategiya tavsifini kiriting');
            return;
        }

        try {
            setLoading(true);
            setGeneratedStrategy(null);
            setBacktestResults(null);
            setGptAnalysis('');

            const { data, error } = await supabase.functions.invoke('gpt4-strategy-generator', {
                body: {
                    prompt,
                    user_id: user?.id,
                    strategy_type: 'custom',
                    timeframe: '1h'
                }
            });

            if (error) throw error;

            if (data?.data) {
                setGeneratedStrategy(data.data.strategy);
                setBacktestResults(data.data.backtest_results);
                setGptAnalysis(data.data.gpt_analysis);
            }
        } catch (error) {
            console.error('Error generating strategy:', error);
            alert('Strategiya yaratishda xatolik yuz berdi');
        } finally {
            setLoading(false);
        }
    };

    const strategyTypeIcons = {
        conservative: <Shield className="w-5 h-5" />,
        aggressive: <Zap className="w-5 h-5" />,
        balanced: <Target className="w-5 h-5" />,
        custom: <Sparkles className="w-5 h-5" />
    };

    return (
        <div className="p-6 space-y-6">
            <div>
                <h1 className="text-3xl font-bold flex items-center">
                    <Sparkles className="w-8 h-8 mr-3 text-purple-400" />
                    GPT-4 Strategiya Yaratuvchi
                </h1>
                <p className="text-slate-400 mt-1">Sun'iy intellekt yordamida trading strategiyalarini yarating</p>
            </div>

            {/* Strategy Generator */}
            <Card variant="elevated">
                <div className="p-6 space-y-6">
                    <div>
                        <label className="block text-sm font-medium mb-2">
                            Strategiya Tavsifi
                        </label>
                        <textarea
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            className="w-full px-4 py-3 rounded-lg bg-slate-800 border border-slate-700 focus:border-purple-500 outline-none"
                            rows={4}
                            placeholder="Qanday trading strategiyasi kerakligini tavsiflab bering. Masalan: indikatorlar, timeframe, risk management, market sharoitlari..."
                        />
                    </div>

                    <div>
                        <div className="text-sm text-slate-400 mb-3">Misol so'rovlar:</div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {examplePrompts.map((example, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => setPrompt(example)}
                                    className="text-left p-3 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-purple-500 transition-colors text-sm"
                                >
                                    {example}
                                </button>
                            ))}
                        </div>
                    </div>

                    <Button
                        onClick={handleGenerateStrategy}
                        disabled={loading || !prompt.trim()}
                        className="w-full"
                    >
                        {loading ? (
                            <>
                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                                Strategiya yaratilmoqda...
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
                <div className="space-y-6">
                    {/* Strategy Overview */}
                    <Card variant="gradient">
                        <div className="p-6">
                            <div className="flex items-start justify-between mb-4">
                                <div>
                                    <h2 className="text-2xl font-bold mb-2">{generatedStrategy.strategy_name}</h2>
                                    {generatedStrategy.description && (
                                        <p className="text-slate-300">{generatedStrategy.description}</p>
                                    )}
                                </div>
                                <Badge color="purple">
                                    GPT-4 Generated
                                </Badge>
                            </div>

                            {backtestResults && (
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                                    <div className="bg-slate-800/50 rounded-lg p-4">
                                        <div className="text-sm text-slate-400">Jami Tradelar</div>
                                        <div className="text-2xl font-bold mt-1">{backtestResults.total_trades}</div>
                                    </div>
                                    <div className="bg-slate-800/50 rounded-lg p-4">
                                        <div className="text-sm text-slate-400">Win Rate</div>
                                        <div className="text-2xl font-bold mt-1 text-green-400">{backtestResults.win_rate}%</div>
                                    </div>
                                    <div className="bg-slate-800/50 rounded-lg p-4">
                                        <div className="text-sm text-slate-400">Net Profit</div>
                                        <div className="text-2xl font-bold mt-1 text-green-400">${backtestResults.net_profit}</div>
                                    </div>
                                    <div className="bg-slate-800/50 rounded-lg p-4">
                                        <div className="text-sm text-slate-400">Sharpe Ratio</div>
                                        <div className="text-2xl font-bold mt-1 text-blue-400">{backtestResults.sharpe_ratio}</div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </Card>

                    {/* GPT Analysis */}
                    {gptAnalysis && (
                        <Card variant="elevated">
                            <div className="p-6">
                                <h3 className="text-xl font-bold mb-4 flex items-center">
                                    <Sparkles className="w-5 h-5 mr-2 text-purple-400" />
                                    AI Tahlil
                                </h3>
                                <div className="prose prose-invert max-w-none">
                                    <pre className="whitespace-pre-wrap text-sm bg-slate-800 rounded-lg p-4 overflow-x-auto">
                                        {gptAnalysis}
                                    </pre>
                                </div>
                            </div>
                        </Card>
                    )}

                    {/* Strategy Details */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Entry Rules */}
                        <Card variant="elevated">
                            <div className="p-6">
                                <h3 className="text-lg font-bold mb-4 flex items-center text-green-400">
                                    <TrendingUp className="w-5 h-5 mr-2" />
                                    Kirish Qoidalari
                                </h3>
                                {generatedStrategy.entry_rules && Object.keys(generatedStrategy.entry_rules).length > 0 ? (
                                    <div className="space-y-2 text-sm">
                                        {Object.entries(generatedStrategy.entry_rules).map(([key, value]) => (
                                            <div key={key} className="flex justify-between">
                                                <span className="text-slate-400">{key}:</span>
                                                <span className="font-medium">{String(value)}</span>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-sm text-slate-400">
                                        Kirish qoidalari GPT tahlilida keltirilgan
                                    </div>
                                )}
                            </div>
                        </Card>

                        {/* Exit Rules */}
                        <Card variant="elevated">
                            <div className="p-6">
                                <h3 className="text-lg font-bold mb-4 flex items-center text-red-400">
                                    <TrendingUp className="w-5 h-5 mr-2 rotate-180" />
                                    Chiqish Qoidalari
                                </h3>
                                {generatedStrategy.exit_rules && Object.keys(generatedStrategy.exit_rules).length > 0 ? (
                                    <div className="space-y-2 text-sm">
                                        {Object.entries(generatedStrategy.exit_rules).map(([key, value]) => (
                                            <div key={key} className="flex justify-between">
                                                <span className="text-slate-400">{key}:</span>
                                                <span className="font-medium">{String(value)}</span>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-sm text-slate-400">
                                        Chiqish qoidalari GPT tahlilida keltirilgan
                                    </div>
                                )}
                            </div>
                        </Card>

                        {/* Risk Rules */}
                        <Card variant="elevated">
                            <div className="p-6">
                                <h3 className="text-lg font-bold mb-4 flex items-center text-yellow-400">
                                    <Shield className="w-5 h-5 mr-2" />
                                    Risk Management
                                </h3>
                                {generatedStrategy.risk_rules && Object.keys(generatedStrategy.risk_rules).length > 0 ? (
                                    <div className="space-y-2 text-sm">
                                        {Object.entries(generatedStrategy.risk_rules).map(([key, value]) => (
                                            <div key={key} className="flex justify-between">
                                                <span className="text-slate-400">{key}:</span>
                                                <span className="font-medium">{String(value)}</span>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-sm text-slate-400">
                                        Risk qoidalari GPT tahlilida keltirilgan
                                    </div>
                                )}
                            </div>
                        </Card>
                    </div>

                    {/* Actions */}
                    <Card variant="elevated">
                        <div className="p-6 flex items-center justify-between">
                            <div>
                                <h3 className="font-bold">Strategiyani qo'llash</h3>
                                <p className="text-sm text-slate-400 mt-1">
                                    Bu strategiyani AI botlaringizda ishlatish uchun saqlang
                                </p>
                            </div>
                            <div className="flex gap-3">
                                <Button variant="outline">Tahrirlash</Button>
                                <Button>Botga Qo'shish</Button>
                            </div>
                        </div>
                    </Card>
                </div>
            )}

            {/* Info Cards */}
            {!generatedStrategy && !loading && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card variant="elevated">
                        <div className="p-6">
                            <div className="w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center mb-4">
                                <Sparkles className="w-6 h-6 text-purple-400" />
                            </div>
                            <h3 className="font-bold mb-2">AI-Powered</h3>
                            <p className="text-sm text-slate-400">
                                GPT-4 Turbo yordamida professional trading strategiyalarini yarating
                            </p>
                        </div>
                    </Card>
                    <Card variant="elevated">
                        <div className="p-6">
                            <div className="w-12 h-12 rounded-lg bg-green-500/20 flex items-center justify-center mb-4">
                                <Target className="w-6 h-6 text-green-400" />
                            </div>
                            <h3 className="font-bold mb-2">Backtesting</h3>
                            <p className="text-sm text-slate-400">
                                Har bir strategiya avtomatik backtesting orqali sinab ko'riladi
                            </p>
                        </div>
                    </Card>
                    <Card variant="elevated">
                        <div className="p-6">
                            <div className="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center mb-4">
                                <Shield className="w-6 h-6 text-blue-400" />
                            </div>
                            <h3 className="font-bold mb-2">Risk Management</h3>
                            <p className="text-sm text-slate-400">
                                Har bir strategiya risk management qoidalari bilan keladi
                            </p>
                        </div>
                    </Card>
                </div>
            )}
        </div>
    );
}
