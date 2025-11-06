import { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import Input from '../components/ui/Input';
import { 
  FireIcon,
  ChartBarIcon,
  ShieldCheckIcon,
  ClockIcon,
  CurrencyDollarIcon,
  BanknotesIcon,
  ArrowTrendingUpIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

interface YieldOpportunity {
  id: string;
  protocolName: string;
  poolName: string;
  chain: string;
  tokenPair: string;
  apy: number;
  tvl: number;
  riskScore: number;
  lockPeriod?: number;
  minDeposit: number;
  autoCompound: boolean;
  rewards: string[];
}

interface UserPosition {
  id: string;
  protocolName: string;
  poolName: string;
  amount: number;
  currentValue: number;
  earnedRewards: number;
  entryApy: number;
  status: string;
  createdAt: string;
}

export default function DeFiYieldFarmingPage() {
  const [opportunities, setOpportunities] = useState<YieldOpportunity[]>([]);
  const [userPositions, setUserPositions] = useState<UserPosition[]>([]);
  const [loading, setLoading] = useState(true);
  const [calculatorAmount, setCalculatorAmount] = useState('1000');
  const [calculatorPeriod, setCalculatorPeriod] = useState('30');
  const [selectedOpp, setSelectedOpp] = useState<YieldOpportunity | null>(null);
  const [projection, setProjection] = useState<any>(null);
  const [filterChain, setFilterChain] = useState('all');
  const [sortBy, setSortBy] = useState<'apy' | 'tvl' | 'risk'>('apy');

  useEffect(() => {
    fetchYieldData();
  }, [filterChain]);

  useEffect(() => {
    if (selectedOpp && calculatorAmount && calculatorPeriod) {
      calculateProjection();
    }
  }, [selectedOpp, calculatorAmount, calculatorPeriod]);

  const fetchYieldData = async () => {
    try {
      setLoading(true);

      // Fetch yield opportunities
      const oppResponse = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/defi-yield-optimizer`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
          },
          body: JSON.stringify({ 
            action: 'get_opportunities',
            chain: filterChain !== 'all' ? filterChain : undefined
          })
        }
      );

      if (oppResponse.ok) {
        const oppData = await oppResponse.json();
        if (oppData.data?.opportunities) {
          setOpportunities(oppData.data.opportunities);
        }
      }

      // Fetch user positions
      const posResponse = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/defi-yield-optimizer`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
          },
          body: JSON.stringify({ action: 'get_user_positions' })
        }
      );

      if (posResponse.ok) {
        const posData = await posResponse.json();
        if (posData.data?.positions) {
          setUserPositions(posData.data.positions);
        }
      }

    } catch (error) {
      console.error('Error fetching yield data:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateProjection = async () => {
    if (!selectedOpp) return;

    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/defi-yield-optimizer`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
          },
          body: JSON.stringify({
            action: 'calculate_projection',
            protocolId: selectedOpp.id,
            amount: parseFloat(calculatorAmount),
            period: parseInt(calculatorPeriod)
          })
        }
      );

      if (response.ok) {
        const data = await response.json();
        if (data.data) {
          setProjection(data.data);
        }
      }
    } catch (error) {
      console.error('Error calculating projection:', error);
    }
  };

  const enterPosition = async (opportunity: YieldOpportunity) => {
    const amount = prompt(`${opportunity.poolName} havuzuna yatirim miktarini girin ($):`);
    if (!amount || parseFloat(amount) < opportunity.minDeposit) {
      alert(`Minimum yatirim: $${opportunity.minDeposit}`);
      return;
    }

    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/defi-yield-optimizer`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
          },
          body: JSON.stringify({
            action: 'enter_position',
            protocolId: opportunity.id,
            amount: parseFloat(amount)
          })
        }
      );

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          alert('Yield farming pozisyonu acildi!');
          fetchYieldData();
        } else {
          alert(data.error || 'Islem basarisiz');
        }
      }
    } catch (error) {
      console.error('Error entering position:', error);
      alert('Bir hata olustu');
    }
  };

  const sortedOpportunities = [...opportunities].sort((a, b) => {
    switch (sortBy) {
      case 'apy':
        return b.apy - a.apy;
      case 'tvl':
        return b.tvl - a.tvl;
      case 'risk':
        return a.riskScore - b.riskScore;
      default:
        return 0;
    }
  });

  const getRiskBadge = (score: number) => {
    if (score <= 3) return <Badge variant="success">Dusuk Risk</Badge>;
    if (score <= 6) return <Badge variant="default">Orta Risk</Badge>;
    return <Badge variant="danger">Yuksek Risk</Badge>;
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('tr-TR', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return `${value.toFixed(2)}%`;
  };

  const totalPositionValue = userPositions.reduce((sum, pos) => sum + pos.currentValue, 0);
  const totalEarnings = userPositions.reduce((sum, pos) => sum + pos.earnedRewards, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
          Yield Farming & Optimization
        </h1>
        <p className="text-muted-foreground mt-1">
          DeFi protokollerinde otomatik yield optimization
        </p>
      </div>

      {/* User Positions Summary */}
      {userPositions.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card variant="glass">
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Toplam Yatirim</p>
                  <p className="text-2xl font-bold mt-1">{formatCurrency(totalPositionValue)}</p>
                </div>
                <div className="p-3 bg-primary/10 rounded-lg">
                  <CurrencyDollarIcon className="w-6 h-6 text-primary" />
                </div>
              </div>
            </div>
          </Card>

          <Card variant="glass">
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Toplam Kazanc</p>
                  <p className="text-2xl font-bold mt-1 text-green-500">
                    +{formatCurrency(totalEarnings)}
                  </p>
                </div>
                <div className="p-3 bg-green-500/10 rounded-lg">
                  <ArrowTrendingUpIcon className="w-6 h-6 text-green-500" />
                </div>
              </div>
            </div>
          </Card>

          <Card variant="glass">
            <div className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Aktif Pozisyonlar</p>
                  <p className="text-2xl font-bold mt-1">{userPositions.length}</p>
                </div>
                <div className="p-3 bg-orange-500/10 rounded-lg">
                  <FireIcon className="w-6 h-6 text-orange-500" />
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card variant="glass">
        <div className="p-6">
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <label className="block text-sm font-medium mb-2">Chain</label>
              <select
                value={filterChain}
                onChange={(e) => setFilterChain(e.target.value)}
                className="w-full px-4 py-2 bg-background border border-border rounded-lg"
              >
                <option value="all">Tum Chainler</option>
                <option value="Ethereum">Ethereum</option>
                <option value="BSC">BSC</option>
                <option value="Polygon">Polygon</option>
                <option value="Arbitrum">Arbitrum</option>
              </select>
            </div>

            <div className="flex-1 min-w-[200px]">
              <label className="block text-sm font-medium mb-2">Siralama</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="w-full px-4 py-2 bg-background border border-border rounded-lg"
              >
                <option value="apy">En Yuksek APY</option>
                <option value="tvl">En Yuksek TVL</option>
                <option value="risk">En Dusuk Risk</option>
              </select>
            </div>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Yield Opportunities */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="text-lg font-semibold">Yield Firsatlari</h3>
          
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3].map(i => (
                <Card key={i} variant="glass">
                  <div className="p-6 h-32 animate-pulse bg-card/50" />
                </Card>
              ))}
            </div>
          ) : sortedOpportunities.length === 0 ? (
            <Card variant="glass">
              <div className="p-12 text-center text-muted-foreground">
                <FireIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Yield firsati bulunamadi</p>
              </div>
            </Card>
          ) : (
            <div className="space-y-4">
              {sortedOpportunities.map((opp) => (
                <Card 
                  key={opp.id} 
                  variant="glass"
                  className="hover:border-primary/50 transition-colors cursor-pointer"
                  onClick={() => setSelectedOpp(opp)}
                >
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h4 className="text-lg font-semibold">{opp.protocolName}</h4>
                          <Badge variant="default" outlined>{opp.chain}</Badge>
                          {getRiskBadge(opp.riskScore)}
                        </div>
                        <p className="text-sm text-muted-foreground mb-1">{opp.poolName}</p>
                        <p className="text-xs text-muted-foreground">{opp.tokenPair}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-3xl font-bold text-green-500">
                          {formatPercent(opp.apy)}
                        </div>
                        <p className="text-xs text-muted-foreground">APY</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4 mb-4 pb-4 border-b border-border">
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">TVL</p>
                        <p className="font-medium">{formatCurrency(opp.tvl)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Min. Yatirim</p>
                        <p className="font-medium">{formatCurrency(opp.minDeposit)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Lock Period</p>
                        <p className="font-medium">
                          {opp.lockPeriod ? `${opp.lockPeriod} gun` : 'Yok'}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-sm">
                        {opp.autoCompound && (
                          <Badge variant="success" className="text-xs">
                            Auto-Compound
                          </Badge>
                        )}
                        {opp.rewards.map(reward => (
                          <Badge key={reward} variant="default" outlined className="text-xs">
                            {reward}
                          </Badge>
                        ))}
                      </div>
                      <Button size="sm" onClick={() => enterPosition(opp)}>
                        Yatirim Yap
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Yield Calculator */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Yield Hesaplayici</h3>
          
          <Card variant="glass">
            <div className="p-6">
              <div className="space-y-4">
                {selectedOpp ? (
                  <>
                    <div className="p-3 bg-primary/5 border border-primary/20 rounded-lg">
                      <p className="text-sm font-medium">{selectedOpp.protocolName}</p>
                      <p className="text-xs text-muted-foreground">{selectedOpp.poolName}</p>
                      <p className="text-lg font-bold text-green-500 mt-1">
                        {formatPercent(selectedOpp.apy)} APY
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">Yatirim Miktari ($)</label>
                      <Input
                        type="number"
                        value={calculatorAmount}
                        onChange={(e) => setCalculatorAmount(e.target.value)}
                        placeholder="1000"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">Sure (gun)</label>
                      <Input
                        type="number"
                        value={calculatorPeriod}
                        onChange={(e) => setCalculatorPeriod(e.target.value)}
                        placeholder="30"
                      />
                    </div>

                    {projection && (
                      <div className="p-4 bg-green-500/5 border border-green-500/20 rounded-lg space-y-3">
                        <h4 className="font-semibold text-green-500">Tahmini Kazanc</h4>
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-muted-foreground">Gunluk:</span>
                            <span className="font-medium text-green-500">
                              +{formatCurrency(projection.dailyEarnings || 0)}
                            </span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-muted-foreground">Aylik:</span>
                            <span className="font-medium text-green-500">
                              +{formatCurrency(projection.monthlyEarnings || 0)}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Toplam ({calculatorPeriod} gun):</span>
                            <span className="font-bold text-green-500 text-lg">
                              +{formatCurrency(projection.totalEarnings || 0)}
                            </span>
                          </div>
                        </div>
                        
                        {projection.riskAssessment && (
                          <div className="pt-3 border-t border-border">
                            <p className="text-xs text-muted-foreground mb-2">Risk Analizi:</p>
                            <div className="flex items-center gap-2">
                              {getRiskBadge(selectedOpp.riskScore)}
                              <ExclamationTriangleIcon className="w-4 h-4 text-yellow-500" />
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <ChartBarIcon className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">Bir yield firsati secin</p>
                  </div>
                )}
              </div>
            </div>
          </Card>

          {/* Tips */}
          <Card variant="glass">
            <div className="p-6">
              <h4 className="font-semibold mb-3 flex items-center gap-2">
                <ShieldCheckIcon className="w-5 h-5 text-primary" />
                Ipuclari
              </h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 bg-primary rounded-full mt-1.5" />
                  <span>Yuksek APY her zaman yuksek risk demektir</span>
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 bg-primary rounded-full mt-1.5" />
                  <span>TVL yuksek protokoller genelde daha guvenlidir</span>
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 bg-primary rounded-full mt-1.5" />
                  <span>Auto-compound kazanclarinizi arttirir</span>
                </li>
                <li className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 bg-primary rounded-full mt-1.5" />
                  <span>Lock period olan havuzlarda dikkatli olun</span>
                </li>
              </ul>
            </div>
          </Card>
        </div>
      </div>

      {/* Active Positions */}
      {userPositions.length > 0 && (
        <Card variant="glass">
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-4">Aktif Pozisyonlarim</h3>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-3 px-4 font-medium">Protokol</th>
                    <th className="text-left py-3 px-4 font-medium">Pool</th>
                    <th className="text-right py-3 px-4 font-medium">Yatirim</th>
                    <th className="text-right py-3 px-4 font-medium">Deger</th>
                    <th className="text-right py-3 px-4 font-medium">Kazanc</th>
                    <th className="text-center py-3 px-4 font-medium">APY</th>
                    <th className="text-center py-3 px-4 font-medium">Durum</th>
                  </tr>
                </thead>
                <tbody>
                  {userPositions.map((pos) => (
                    <tr key={pos.id} className="border-b border-border/50 hover:bg-accent/50">
                      <td className="py-3 px-4 font-medium">{pos.protocolName}</td>
                      <td className="py-3 px-4 text-sm text-muted-foreground">{pos.poolName}</td>
                      <td className="py-3 px-4 text-right">{formatCurrency(pos.amount)}</td>
                      <td className="py-3 px-4 text-right font-medium">{formatCurrency(pos.currentValue)}</td>
                      <td className="py-3 px-4 text-right text-green-500 font-medium">
                        +{formatCurrency(pos.earnedRewards)}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <Badge variant="success">{formatPercent(pos.entryApy)}</Badge>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <Badge variant="default" outlined={pos.status !== 'active'}>
                          {pos.status}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
