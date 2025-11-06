import { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { 
  SparklesIcon,
  BoltIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

interface ArbitrageOpportunity {
  id: string;
  tokenSymbol: string;
  sourceChain: string;
  sourceDex: string;
  sourcePrice: number;
  destinationChain: string;
  destinationDex: string;
  destinationPrice: number;
  priceDifference: number;
  estimatedProfit: number;
  totalFees: number;
  netProfit: number;
  riskLevel: string;
  liquidityScore: number;
  expiresAt: string;
}

export default function DeFiArbitragePage() {
  const [opportunities, setOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    fetchOpportunities();
    
    if (autoRefresh) {
      const interval = setInterval(fetchOpportunities, 10000); // 10 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const fetchOpportunities = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/defi-arbitrage-scanner`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
          },
          body: JSON.stringify({ action: 'scan_opportunities' })
        }
      );

      if (response.ok) {
        const data = await response.json();
        if (data.data?.opportunities) {
          setOpportunities(data.data.opportunities);
        }
      }
    } catch (error) {
      console.error('Error fetching arbitrage opportunities:', error);
    } finally {
      setLoading(false);
    }
  };

  const executeArbitrage = async (opp: ArbitrageOpportunity) => {
    if (!confirm(`Bu arbitraj firsatini kullanmak istiyor musunuz?\nTahmini kar: $${opp.netProfit.toFixed(2)}`)) {
      return;
    }

    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/defi-arbitrage-scanner`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
          },
          body: JSON.stringify({
            action: 'execute_arbitrage',
            opportunityId: opp.id
          })
        }
      );

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          alert('Arbitraj islemi baslatildi!');
          fetchOpportunities();
        } else {
          alert(data.error || 'Islem basarisiz');
        }
      }
    } catch (error) {
      console.error('Error executing arbitrage:', error);
      alert('Bir hata olustu');
    }
  };

  const getRiskBadge = (level: string) => {
    const variants: Record<string, any> = {
      low: { variant: 'success', label: 'Dusuk' },
      medium: { variant: 'default', label: 'Orta' },
      high: { variant: 'destructive', label: 'Yuksek' }
    };
    const config = variants[level] || variants.medium;
    return <Badge variant={config.variant}>{config.label} Risk</Badge>;
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

  const timeRemaining = (expiresAt: string) => {
    const diff = new Date(expiresAt).getTime() - Date.now();
    const minutes = Math.floor(diff / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
            DeFi Arbitrage Scanner
          </h1>
          <p className="text-muted-foreground mt-1">
            Cross-chain ve cross-DEX arbitraj firsatlari
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded"
            />
            Otomatik Yenileme
          </label>
          <Button onClick={fetchOpportunities} disabled={loading}>
            <BoltIcon className="w-5 h-5 mr-2" />
            Yenile
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card variant="glass">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Aktif Firsatlar</p>
                <p className="text-2xl font-bold mt-1">{opportunities.length}</p>
              </div>
              <div className="p-3 bg-primary/10 rounded-lg">
                <SparklesIcon className="w-6 h-6 text-primary" />
              </div>
            </div>
          </div>
        </Card>

        <Card variant="glass">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">En Yuksek Kar</p>
                <p className="text-2xl font-bold mt-1 text-green-500">
                  {opportunities.length > 0 
                    ? formatCurrency(Math.max(...opportunities.map(o => o.netProfit)))
                    : '$0.00'
                  }
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
                <p className="text-sm text-muted-foreground">Ortalama ROI</p>
                <p className="text-2xl font-bold mt-1">
                  {opportunities.length > 0
                    ? formatPercent(
                        opportunities.reduce((sum, o) => sum + o.priceDifference, 0) / opportunities.length
                      )
                    : '0.00%'
                  }
                </p>
              </div>
              <div className="p-3 bg-orange-500/10 rounded-lg">
                <ChartBarIcon className="w-6 h-6 text-orange-500" />
              </div>
            </div>
          </div>
        </Card>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map(i => (
            <Card key={i} variant="glass">
              <div className="p-6 h-48 animate-pulse bg-card/50" />
            </Card>
          ))}
        </div>
      ) : opportunities.length === 0 ? (
        <Card variant="glass">
          <div className="p-12 text-center text-muted-foreground">
            <SparklesIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>Su anda aktif arbitraj firsati bulunamadi</p>
            <p className="text-sm mt-2">Scanner her 10 saniyede bir otomatik tarama yapacak</p>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {opportunities.map((opp) => (
            <Card key={opp.id} variant="glass" className="hover:border-primary/50 transition-colors">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="text-xl font-bold">{opp.tokenSymbol}</h3>
                      {getRiskBadge(opp.riskLevel)}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <ClockIcon className="w-4 h-4" />
                      <span>Expires in {timeRemaining(opp.expiresAt)}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-green-500">
                      +{formatPercent(opp.priceDifference)}
                    </div>
                    <p className="text-xs text-muted-foreground">ROI</p>
                  </div>
                </div>

                <div className="space-y-3 mb-4">
                  <div className="flex items-center justify-between p-3 bg-card/50 rounded-lg">
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">Kaynak</p>
                      <p className="font-medium text-sm">{opp.sourceChain}</p>
                      <p className="text-xs text-muted-foreground">{opp.sourceDex}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-muted-foreground mb-1">Fiyat</p>
                      <p className="font-medium">{formatCurrency(opp.sourcePrice)}</p>
                    </div>
                  </div>

                  <div className="flex items-center justify-center">
                    <div className="p-2 bg-primary/10 rounded-full">
                      <ArrowTrendingUpIcon className="w-4 h-4 text-primary" />
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-card/50 rounded-lg">
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">Hedef</p>
                      <p className="font-medium text-sm">{opp.destinationChain}</p>
                      <p className="text-xs text-muted-foreground">{opp.destinationDex}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-muted-foreground mb-1">Fiyat</p>
                      <p className="font-medium">{formatCurrency(opp.destinationPrice)}</p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2 mb-4 pb-4 border-b border-border">
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Kar</p>
                    <p className="font-medium text-sm text-green-500">
                      {formatCurrency(opp.estimatedProfit)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Ucretler</p>
                    <p className="font-medium text-sm text-red-500">
                      -{formatCurrency(opp.totalFees)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Net Kar</p>
                    <p className="font-bold text-sm text-green-500">
                      {formatCurrency(opp.netProfit)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="text-sm">
                    <span className="text-muted-foreground">Likidite: </span>
                    <Badge variant="default" outlined className="text-xs">
                      {opp.liquidityScore.toFixed(1)}/10
                    </Badge>
                  </div>
                  <Button 
                    size="sm" 
                    onClick={() => executeArbitrage(opp)}
                    disabled={opp.netProfit <= 0}
                  >
                    <BoltIcon className="w-4 h-4 mr-1" />
                    Yukle
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
