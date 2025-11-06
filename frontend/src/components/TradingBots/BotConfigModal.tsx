import { useState, useEffect } from 'react';
import Card from '../ui/Card';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import { X, Save, AlertCircle } from 'lucide-react';

interface Bot {
    id: string;
    bot_name: string;
    bot_type: string;
    description: string;
    status: string;
    trading_pairs: string[];
    current_capital: number;
    initial_capital: number;
}

interface BotConfigModalProps {
    bot: Bot | null;
    isOpen: boolean;
    onClose: () => void;
    onSave: (botId: string, config: any) => Promise<void>;
}

export default function BotConfigModal({ bot, isOpen, onClose, onSave }: BotConfigModalProps) {
    const [config, setConfig] = useState({
        max_daily_trades: 10,
        max_position_size: 1000,
        risk_percentage: 2.0,
        stop_loss_percentage: 2.0,
        take_profit_percentage: 5.0,
        trailing_stop_enabled: true,
        trailing_stop_percentage: 1.0,
        max_concurrent_positions: 3,
        use_ml_predictions: true,
        use_gpt4_strategy: false,
        timeframe: '1h',
        min_confidence_score: 0.7
    });

    const [saving, setSaving] = useState(false);

    useEffect(() => {
        if (bot && isOpen) {
            // Bot konfiguratsiyasini yuklash (database dan)
            // Hozircha default qiymatlar
        }
    }, [bot, isOpen]);

    if (!isOpen || !bot) return null;

    const handleSave = async () => {
        try {
            setSaving(true);
            await onSave(bot.id, config);
            onClose();
        } catch (error) {
            console.error('Konfiguratsiya saqlashda xato:', error);
            alert('Konfiguratsiya saqlanmadi. Qaytadan urinib ko\'ring.');
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <Card variant="elevated" className="w-full max-w-3xl max-h-[90vh] overflow-y-auto">
                <div className="p-6">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h2 className="text-2xl font-bold">{bot.bot_name} - Sozlamalar</h2>
                            <div className="flex items-center gap-2 mt-2">
                                <Badge color="blue">{bot.bot_type}</Badge>
                                <Badge color="default">{bot.status}</Badge>
                            </div>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
                        >
                            <X className="w-6 h-6" />
                        </button>
                    </div>

                    {/* Warning */}
                    <div className="mb-6 p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
                        <div className="text-sm text-yellow-200">
                            <strong>Diqqat:</strong> Bot faol holda bo'lsa, o'zgarishlar keyingi trade'dan boshlab qo'llaniladi.
                        </div>
                    </div>

                    {/* Configuration Form */}
                    <div className="space-y-6">
                        {/* Trading Limits */}
                        <div>
                            <h3 className="text-lg font-semibold mb-4">Trading Limitleri</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-2">
                                        Kunlik Maksimal Trade Soni
                                    </label>
                                    <input
                                        type="number"
                                        value={config.max_daily_trades}
                                        onChange={(e) => setConfig({ ...config, max_daily_trades: parseInt(e.target.value) })}
                                        className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 focus:border-blue-500 outline-none"
                                        min="1"
                                        max="100"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-2">
                                        Maksimal Pozitsiya Hajmi ($)
                                    </label>
                                    <input
                                        type="number"
                                        value={config.max_position_size}
                                        onChange={(e) => setConfig({ ...config, max_position_size: parseFloat(e.target.value) })}
                                        className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 focus:border-blue-500 outline-none"
                                        min="100"
                                        step="100"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-2">
                                        Maksimal Bir Vaqtdagi Pozitsiyalar
                                    </label>
                                    <input
                                        type="number"
                                        value={config.max_concurrent_positions}
                                        onChange={(e) => setConfig({ ...config, max_concurrent_positions: parseInt(e.target.value) })}
                                        className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 focus:border-blue-500 outline-none"
                                        min="1"
                                        max="10"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-2">
                                        Timeframe
                                    </label>
                                    <select
                                        value={config.timeframe}
                                        onChange={(e) => setConfig({ ...config, timeframe: e.target.value })}
                                        className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 focus:border-blue-500 outline-none"
                                    >
                                        <option value="1m">1 Daqiqa</option>
                                        <option value="5m">5 Daqiqa</option>
                                        <option value="15m">15 Daqiqa</option>
                                        <option value="1h">1 Soat</option>
                                        <option value="4h">4 Soat</option>
                                        <option value="1d">1 Kun</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        {/* Risk Management */}
                        <div>
                            <h3 className="text-lg font-semibold mb-4">Risk Management</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-2">
                                        Risk Foizi (% per trade)
                                    </label>
                                    <input
                                        type="number"
                                        value={config.risk_percentage}
                                        onChange={(e) => setConfig({ ...config, risk_percentage: parseFloat(e.target.value) })}
                                        className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 focus:border-blue-500 outline-none"
                                        min="0.1"
                                        max="10"
                                        step="0.1"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-2">
                                        Stop Loss (%)
                                    </label>
                                    <input
                                        type="number"
                                        value={config.stop_loss_percentage}
                                        onChange={(e) => setConfig({ ...config, stop_loss_percentage: parseFloat(e.target.value) })}
                                        className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 focus:border-blue-500 outline-none"
                                        min="0.5"
                                        max="20"
                                        step="0.1"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-2">
                                        Take Profit (%)
                                    </label>
                                    <input
                                        type="number"
                                        value={config.take_profit_percentage}
                                        onChange={(e) => setConfig({ ...config, take_profit_percentage: parseFloat(e.target.value) })}
                                        className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 focus:border-blue-500 outline-none"
                                        min="1"
                                        max="50"
                                        step="0.5"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-2">
                                        Trailing Stop (%)
                                    </label>
                                    <input
                                        type="number"
                                        value={config.trailing_stop_percentage}
                                        onChange={(e) => setConfig({ ...config, trailing_stop_percentage: parseFloat(e.target.value) })}
                                        className="w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 focus:border-blue-500 outline-none"
                                        min="0.1"
                                        max="10"
                                        step="0.1"
                                        disabled={!config.trailing_stop_enabled}
                                    />
                                </div>
                            </div>
                        </div>

                        {/* AI Features */}
                        <div>
                            <h3 className="text-lg font-semibold mb-4">AI Xususiyatlari</h3>
                            <div className="space-y-4">
                                <label className="flex items-center gap-3 p-4 bg-slate-800/50 rounded-lg cursor-pointer hover:bg-slate-800 transition-colors">
                                    <input
                                        type="checkbox"
                                        checked={config.trailing_stop_enabled}
                                        onChange={(e) => setConfig({ ...config, trailing_stop_enabled: e.target.checked })}
                                        className="w-5 h-5 rounded border-slate-600"
                                    />
                                    <div>
                                        <div className="font-medium">Trailing Stop</div>
                                        <div className="text-sm text-slate-400">
                                            Avtomatik trailing stop yoqish
                                        </div>
                                    </div>
                                </label>
                                <label className="flex items-center gap-3 p-4 bg-slate-800/50 rounded-lg cursor-pointer hover:bg-slate-800 transition-colors">
                                    <input
                                        type="checkbox"
                                        checked={config.use_ml_predictions}
                                        onChange={(e) => setConfig({ ...config, use_ml_predictions: e.target.checked })}
                                        className="w-5 h-5 rounded border-slate-600"
                                    />
                                    <div>
                                        <div className="font-medium">ML Price Predictions V2</div>
                                        <div className="text-sm text-slate-400">
                                            ML tahminlaridan foydalanish (Alpha Vantage + LSTM)
                                        </div>
                                    </div>
                                </label>
                                <label className="flex items-center gap-3 p-4 bg-slate-800/50 rounded-lg cursor-pointer hover:bg-slate-800 transition-colors">
                                    <input
                                        type="checkbox"
                                        checked={config.use_gpt4_strategy}
                                        onChange={(e) => setConfig({ ...config, use_gpt4_strategy: e.target.checked })}
                                        className="w-5 h-5 rounded border-slate-600"
                                    />
                                    <div>
                                        <div className="font-medium">GPT-4 Strategy Generator V2</div>
                                        <div className="text-sm text-slate-400">
                                            GPT-4 tavsiyalaridan foydalanish
                                        </div>
                                    </div>
                                </label>
                                {config.use_ml_predictions && (
                                    <div className="ml-8">
                                        <label className="block text-sm font-medium mb-2">
                                            Minimal Confidence Score
                                        </label>
                                        <input
                                            type="range"
                                            value={config.min_confidence_score}
                                            onChange={(e) => setConfig({ ...config, min_confidence_score: parseFloat(e.target.value) })}
                                            className="w-full"
                                            min="0.5"
                                            max="0.95"
                                            step="0.05"
                                        />
                                        <div className="text-sm text-slate-400 mt-1">
                                            {(config.min_confidence_score * 100).toFixed(0)}% - Faqat yuqori ishonchli signallar
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-4 mt-8">
                        <Button onClick={handleSave} disabled={saving}>
                            <Save className="w-5 h-5 mr-2" />
                            {saving ? 'Saqlanmoqda...' : 'Saqlash'}
                        </Button>
                        <Button variant="outline" onClick={onClose} disabled={saving}>
                            Bekor Qilish
                        </Button>
                    </div>
                </div>
            </Card>
        </div>
    );
}
