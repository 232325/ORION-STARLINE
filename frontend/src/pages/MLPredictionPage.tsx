import { useState } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import MLPredictionChart from '../components/TradingBots/MLPredictionChart';
import { TrendingUp, Search, Star, Clock } from 'lucide-react';

export default function MLPredictionPage() {
    const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
    const [searchQuery, setSearchQuery] = useState('');
    const [favorites, setFavorites] = useState(['AAPL', 'MSFT', 'GOOGL', 'TSLA']);

    const popularSymbols = [
        { symbol: 'AAPL', name: 'Apple Inc.' },
        { symbol: 'MSFT', name: 'Microsoft Corporation' },
        { symbol: 'GOOGL', name: 'Alphabet Inc.' },
        { symbol: 'TSLA', name: 'Tesla Inc.' },
        { symbol: 'AMZN', name: 'Amazon.com Inc.' },
        { symbol: 'META', name: 'Meta Platforms Inc.' },
        { symbol: 'NVDA', name: 'NVIDIA Corporation' },
        { symbol: 'JPM', name: 'JPMorgan Chase & Co.' },
        { symbol: 'V', name: 'Visa Inc.' },
        { symbol: 'WMT', name: 'Walmart Inc.' },
        { symbol: 'DIS', name: 'Walt Disney Company' },
        { symbol: 'NFLX', name: 'Netflix Inc.' }
    ];

    const filteredSymbols = searchQuery
        ? popularSymbols.filter(s => 
            s.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
            s.name.toLowerCase().includes(searchQuery.toLowerCase())
          )
        : popularSymbols;

    const toggleFavorite = (symbol: string) => {
        setFavorites(prev => 
            prev.includes(symbol) 
                ? prev.filter(s => s !== symbol)
                : [...prev, symbol]
        );
    };

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold flex items-center gap-3">
                    <TrendingUp className="w-8 h-8 text-purple-400" />
                    ML Price Prediction Dashboard V2
                </h1>
                <p className="text-slate-400 mt-1">
                    Real-time LSTM tahminlari Alpha Vantage market data bilan
                </p>
            </div>

            {/* Features Info */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card variant="elevated">
                    <div className="p-4">
                        <div className="flex items-center gap-3 mb-2">
                            <TrendingUp className="w-5 h-5 text-blue-400" />
                            <div className="text-sm font-medium">6 Timeframe</div>
                        </div>
                        <div className="text-xs text-slate-400">
                            1m, 5m, 15m, 1h, 4h, 1d tahminlar
                        </div>
                    </div>
                </Card>
                <Card variant="elevated">
                    <div className="p-4">
                        <div className="flex items-center gap-3 mb-2">
                            <Clock className="w-5 h-5 text-green-400" />
                            <div className="text-sm font-medium">Real-time</div>
                        </div>
                        <div className="text-xs text-slate-400">
                            Jonli market data yangilanishi
                        </div>
                    </div>
                </Card>
                <Card variant="elevated">
                    <div className="p-4">
                        <div className="flex items-center gap-3 mb-2">
                            <Badge color="purple">LSTM</Badge>
                            <div className="text-sm font-medium">ML Model</div>
                        </div>
                        <div className="text-xs text-slate-400">
                            Ensemble LSTM + Technical indicators
                        </div>
                    </div>
                </Card>
                <Card variant="elevated">
                    <div className="p-4">
                        <div className="flex items-center gap-3 mb-2">
                            <Badge color="warning">Anomaly</Badge>
                            <div className="text-sm font-medium">Detection</div>
                        </div>
                        <div className="text-xs text-slate-400">
                            Avtomatik anomaliya aniqlash
                        </div>
                    </div>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Symbol Selector */}
                <div className="lg:col-span-1 space-y-4">
                    {/* Search */}
                    <Card variant="elevated">
                        <div className="p-4">
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <input
                                    type="text"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="w-full pl-10 pr-4 py-2 rounded-lg bg-slate-800 border border-slate-700 focus:border-blue-500 outline-none"
                                    placeholder="Symbol qidirish..."
                                />
                            </div>
                        </div>
                    </Card>

                    {/* Favorites */}
                    {favorites.length > 0 && (
                        <Card variant="elevated">
                            <div className="p-4">
                                <div className="flex items-center gap-2 mb-3">
                                    <Star className="w-4 h-4 text-yellow-400" />
                                    <div className="text-sm font-medium">Sevimlilar</div>
                                </div>
                                <div className="space-y-2">
                                    {favorites.map((symbol) => (
                                        <button
                                            key={symbol}
                                            onClick={() => setSelectedSymbol(symbol)}
                                            className={`w-full px-3 py-2 rounded-lg text-left transition-all ${
                                                selectedSymbol === symbol
                                                    ? 'bg-blue-500 text-white'
                                                    : 'bg-slate-800/50 hover:bg-slate-800'
                                            }`}
                                        >
                                            <div className="font-medium">{symbol}</div>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </Card>
                    )}

                    {/* Popular Symbols */}
                    <Card variant="elevated">
                        <div className="p-4">
                            <div className="text-sm font-medium mb-3">Mashhur Symbollar</div>
                            <div className="space-y-2 max-h-96 overflow-y-auto">
                                {filteredSymbols.map((item) => (
                                    <div
                                        key={item.symbol}
                                        className={`flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all ${
                                            selectedSymbol === item.symbol
                                                ? 'bg-blue-500 text-white'
                                                : 'bg-slate-800/50 hover:bg-slate-800'
                                        }`}
                                    >
                                        <button
                                            onClick={() => setSelectedSymbol(item.symbol)}
                                            className="flex-1 text-left"
                                        >
                                            <div className="font-medium">{item.symbol}</div>
                                            <div className={`text-xs ${
                                                selectedSymbol === item.symbol ? 'text-blue-100' : 'text-slate-400'
                                            }`}>
                                                {item.name}
                                            </div>
                                        </button>
                                        <button
                                            onClick={() => toggleFavorite(item.symbol)}
                                            className="ml-2"
                                        >
                                            <Star
                                                className={`w-4 h-4 ${
                                                    favorites.includes(item.symbol)
                                                        ? 'text-yellow-400 fill-yellow-400'
                                                        : 'text-slate-500'
                                                }`}
                                            />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </Card>
                </div>

                {/* ML Predictions */}
                <div className="lg:col-span-3">
                    <MLPredictionChart 
                        symbol={selectedSymbol}
                        timeframes={['1m', '5m', '15m', '1h', '4h', '1d']}
                    />
                </div>
            </div>

            {/* Info Banner */}
            <Card variant="elevated">
                <div className="p-6">
                    <div className="flex items-start gap-4">
                        <div className="p-3 bg-purple-500/10 rounded-lg">
                            <TrendingUp className="w-6 h-6 text-purple-400" />
                        </div>
                        <div className="flex-1">
                            <h3 className="text-lg font-semibold mb-2">ML Price Predictor V2 Haqida</h3>
                            <div className="text-sm text-slate-400 space-y-2">
                                <p>
                                    Bu dashboard real-time Alpha Vantage market data asosida LSTM (Long Short-Term Memory) 
                                    neural network modelidan foydalanadi. Har bir tahmin quyidagilarni o'z ichiga oladi:
                                </p>
                                <ul className="list-disc list-inside space-y-1 ml-4">
                                    <li>6 xil timeframe (1m dan 1d gacha) bo'yicha narx tahminlari</li>
                                    <li>Confidence score - tahminning ishonch darajasi</li>
                                    <li>Texnik indikatorlar analizi (RSI, MACD, SMA, Bollinger Bands)</li>
                                    <li>Market rejim aniqlash (trending/ranging)</li>
                                    <li>Volatillik darajasi (low/medium/high)</li>
                                    <li>Anomaliya aniqlash - kutilmagan narx harakatlari</li>
                                    <li>Up/Down ehtimollik ko'rsatkichlari</li>
                                </ul>
                                <p className="mt-3">
                                    Barcha tahminlar har 1 daqiqada avtomatik yangilanadi va real trading signallari 
                                    uchun ishlatilishi mumkin.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </Card>
        </div>
    );
}
