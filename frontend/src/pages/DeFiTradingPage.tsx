import { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { 
  CurrencyDollarIcon,
  ArrowsRightLeftIcon,
  ChartPieIcon,
  SparklesIcon,
  BanknotesIcon,
  FireIcon
} from '@heroicons/react/24/outline';

interface DEXPrice {
  dex: string;
  price: number;
  liquidity: number;
  volume_24h: number;
}

interface SwapRoute {
  path: string[];
  expected_output: number;
  price_impact: number;
  gas_estimate: number;
  dex: string;
}

interface YieldOpportunity {
  protocol: string;
  pool: string;
  apy: number;
  tvl: number;
  rewards: string[];
  risk_score: number;
}

interface StakingOption {
  protocol: string;
  token: string;
  apy: number;
  lock_period: number;
  min_stake: number;
  total_staked: number;
}

export default function DeFiTradingPage() {
  const [dexPrices, setDexPrices] = useState<DEXPrice[]>([]);
  const [swapRoutes, setSwapRoutes] = useState<SwapRoute[]>([]);
  const [yieldOpportunities, setYieldOpportunities] = useState<YieldOpportunity[]>([]);
  const [stakingOptions, setStakingOptions] = useState<StakingOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [swapAmount, setSwapAmount] = useState('1.0');
  const [selectedPair, setSelectedPair] = useState('ETH/USDC');

  useEffect(() => {
    fetchDeFiData();
  }, []);

  const fetchDeFiData = async () => {
    try {
      setLoading(true);

      // DEX prices
      const pricesResponse = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/defi-trading-manager`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`
          },
          body: JSON.stringify({
            action: 'get_dex_prices',
            pair: 'ETH/USDC'
          })
        }
      );

      const pricesData = await pricesResponse.json();
      if (pricesData.data) {
        setDexPrices(pricesData.data);
      }

      // Yield farming opportunities
      const yieldResponse = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/defi-trading-manager`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`
          },
          body: JSON.stringify({
            action: 'calculate_yield_farming',
            token_a: 'ETH',
            token_b: 'USDC',
            amount: 10000
          })
        }
      );

      const yieldData = await yieldResponse.json();
      if (yieldData.data) {
        setYieldOpportunities(yieldData.data.opportunities || []);
      }

      // Staking options
      const stakingResponse = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/defi-trading-manager`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`
          },
          body: JSON.stringify({
            action: 'get_staking_opportunities',
            token: 'ETH'
          })
        }
      );

      const stakingData = await stakingResponse.json();
      if (stakingData.data) {
        setStakingOptions(stakingData.data);
      }

    } catch (error) {
      console.error('DeFi verileri yüklenirken hata:', error);
    } finally {
      setLoading(false);
    }
  };

  const findBestRoute = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/defi-trading-manager`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`
          },
          body: JSON.stringify({
            action: 'find_best_swap_route',
            token_in: 'ETH',
            token_out: 'USDC',
            amount_in: parseFloat(swapAmount)
          })
        }
      );

      const data = await response.json();
      if (data.data && data.data.routes) {
        setSwapRoutes(data.data.routes);
      }
    } catch (error) {
      console.error('Swap route bulunamadı:', error);
    }
  };

  const formatNumber = (value: number) => {
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `$${(value / 1e3).toFixed(2)}K`;
    return `$${value.toFixed(2)}`;
  };

  const getRiskColor = (score: number) => {
    if (score <= 3) return 'text-green-400';
    if (score <= 6) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getRiskBadge = (score: number): 'success' | 'warning' | 'danger' => {
    if (score <= 3) return 'success';
    if (score <= 6) return 'warning';
    return 'danger';
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-slate-700 rounded w-1/4"></div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-64 bg-slate-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <SparklesIcon className="h-8 w-8 text-purple-400" />
            DeFi Trading
          </h1>
          <p className="text-slate-400 mt-2">
            Merkezi olmayan finans protokolleri ve getiri fırsatları
          </p>
        </div>
        <Button onClick={fetchDeFiData} disabled={loading}>
          Yenile
        </Button>
      </div>

      {/* DEX Price Comparison */}
      <Card variant="glass" className="p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <ArrowsRightLeftIcon className="h-6 w-6 text-blue-400" />
          DEX Fiyat Karşılaştırması - {selectedPair}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {dexPrices.map((dex) => (
            <div key={dex.dex} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-white">{dex.dex}</h3>
                <Badge variant="neutral">{dex.dex === 'Uniswap' ? 'V3' : 'V2'}</Badge>
              </div>
              <div className="space-y-2">
                <div>
                  <p className="text-xs text-slate-400">Fiyat</p>
                  <p className="text-lg font-bold text-green-400">{formatNumber(dex.price)}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-400">Likidite</p>
                  <p className="text-sm text-blue-400">{formatNumber(dex.liquidity)}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-400">24h Hacim</p>
                  <p className="text-sm text-purple-400">{formatNumber(dex.volume_24h)}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Swap Route Finder */}
      <Card variant="glass" className="p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <CurrencyDollarIcon className="h-6 w-6 text-green-400" />
          En İyi Swap Rotası
        </h2>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="text-sm text-slate-400 mb-2 block">Miktar</label>
            <input
              type="number"
              value={swapAmount}
              onChange={(e) => setSwapAmount(e.target.value)}
              className="w-full px-4 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white"
              placeholder="1.0"
            />
          </div>
          <div>
            <label className="text-sm text-slate-400 mb-2 block">Pair</label>
            <select
              value={selectedPair}
              onChange={(e) => setSelectedPair(e.target.value)}
              className="w-full px-4 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white"
            >
              <option value="ETH/USDC">ETH/USDC</option>
              <option value="BTC/USDT">BTC/USDT</option>
              <option value="BNB/BUSD">BNB/BUSD</option>
            </select>
          </div>
          <div className="flex items-end">
            <Button onClick={findBestRoute} className="w-full">
              Rota Bul
            </Button>
          </div>
        </div>

        {swapRoutes.length > 0 && (
          <div className="space-y-3">
            {swapRoutes.map((route, index) => (
              <div key={index} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Badge variant={index === 0 ? 'success' : 'neutral'}>
                      {index === 0 ? 'En İyi' : `#${index + 1}`}
                    </Badge>
                    <span className="text-white font-medium">{route.dex}</span>
                  </div>
                  <span className="text-green-400 font-bold">
                    {route.expected_output.toFixed(4)} USDC
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-slate-400">Rota</p>
                    <p className="text-white">{route.path.join(' → ')}</p>
                  </div>
                  <div>
                    <p className="text-slate-400">Fiyat Etkisi</p>
                    <p className={route.price_impact < 1 ? 'text-green-400' : 'text-yellow-400'}>
                      {route.price_impact.toFixed(2)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-slate-400">Gas (tahmini)</p>
                    <p className="text-blue-400">{formatNumber(route.gas_estimate)}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Yield Farming Opportunities */}
      <Card variant="glass" className="p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <ChartPieIcon className="h-6 w-6 text-yellow-400" />
          Yield Farming Fırsatları
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {yieldOpportunities.map((opp, index) => (
            <div key={index} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-white">{opp.protocol}</h3>
                  <p className="text-sm text-slate-400">{opp.pool}</p>
                </div>
                <Badge variant={getRiskBadge(opp.risk_score)}>
                  Risk: {opp.risk_score}/10
                </Badge>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-slate-400">APY</span>
                  <span className="text-green-400 font-bold text-lg">{opp.apy.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">TVL</span>
                  <span className="text-blue-400">{formatNumber(opp.tvl)}</span>
                </div>
                <div>
                  <p className="text-slate-400 text-sm mb-1">Ödüller:</p>
                  <div className="flex flex-wrap gap-1">
                    {opp.rewards.map((reward, i) => (
                      <Badge key={i} variant="neutral" className="text-xs">
                        {reward}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
              <Button className="w-full mt-3" size="sm">
                Pool'a Katıl
              </Button>
            </div>
          ))}
        </div>
      </Card>

      {/* Staking Opportunities */}
      <Card variant="glass" className="p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <BanknotesIcon className="h-6 w-6 text-purple-400" />
          Staking Fırsatları
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-800/50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase">
                  Protokol
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase">
                  Token
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase">
                  APY
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase">
                  Kilit Süresi
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase">
                  Min. Stake
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase">
                  Toplam Stake
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-slate-400 uppercase">
                  İşlem
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {stakingOptions.map((option, index) => (
                <tr key={index} className="hover:bg-slate-800/30">
                  <td className="px-4 py-4 text-white font-medium">{option.protocol}</td>
                  <td className="px-4 py-4">
                    <Badge variant="neutral">{option.token}</Badge>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-green-400 font-bold">{option.apy.toFixed(2)}%</span>
                  </td>
                  <td className="px-4 py-4 text-slate-300">
                    {option.lock_period === 0 ? 'Esnek' : `${option.lock_period} gün`}
                  </td>
                  <td className="px-4 py-4 text-slate-300">
                    {option.min_stake} {option.token}
                  </td>
                  <td className="px-4 py-4 text-blue-400">
                    {formatNumber(option.total_staked)}
                  </td>
                  <td className="px-4 py-4 text-right">
                    <Button size="sm" variant="primary">
                      Stake Et
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
