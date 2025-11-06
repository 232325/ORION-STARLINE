import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWeb3 } from '../contexts/Web3Context';
import Web3ConnectButton from '../components/Web3ConnectButton';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { 
  CurrencyDollarIcon,
  ArrowsRightLeftIcon,
  ChartBarIcon,
  WalletIcon,
  BanknotesIcon,
  SparklesIcon,
  LinkIcon,
  FireIcon
} from '@heroicons/react/24/outline';

interface ProtocolSummary {
  name: string;
  tvl: number;
  apy: number;
  type: string;
  userBalance?: number;
}

interface ChainBalance {
  chain: string;
  balance: number;
  tokens: { symbol: string; amount: number; value: number }[];
}

interface ArbitrageOpportunity {
  id: string;
  token: string;
  profit: number;
  source: string;
  destination: string;
}

export default function DeFiDashboardPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [totalValue, setTotalValue] = useState(0);
  const [chainBalances, setChainBalances] = useState<ChainBalance[]>([]);
  const [protocols, setProtocols] = useState<ProtocolSummary[]>([]);
  const [arbitrageOps, setArbitrageOps] = useState<ArbitrageOpportunity[]>([]);
  const [yieldPositions, setYieldPositions] = useState<any[]>([]);

  useEffect(() => {
    fetchDeFiOverview();
  }, []);

  const fetchDeFiOverview = async () => {
    try {
      setLoading(true);

      // Fetch multi-chain balances
      const walletResponse = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/defi-wallet-manager`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
          },
          body: JSON.stringify({ action: 'get_balances' })
        }
      );

      if (walletResponse.ok) {
        const walletData = await walletResponse.json();
        if (walletData.data) {
          setChainBalances(walletData.data.balances || []);
          setTotalValue(walletData.data.totalValue || 0);
        }
      }

      // Fetch DeFi protocols
      const protocolResponse = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/defi-protocol-aggregator`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
          },
          body: JSON.stringify({ action: 'get_protocols' })
        }
      );

      if (protocolResponse.ok) {
        const protocolData = await protocolResponse.json();
        if (protocolData.data) {
          setProtocols(protocolData.data.protocols || []);
        }
      }

      // Fetch arbitrage opportunities
      const arbResponse = await fetch(
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

      if (arbResponse.ok) {
        const arbData = await arbResponse.json();
        if (arbData.data) {
          setArbitrageOps(arbData.data.opportunities || []);
        }
      }

      // Fetch yield positions
      const yieldResponse = await fetch(
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

      if (yieldResponse.ok) {
        const yieldData = await yieldResponse.json();
        if (yieldData.data) {
          setYieldPositions(yieldData.data.positions || []);
        }
      }

    } catch (error) {
      console.error('Error fetching DeFi overview:', error);
    } finally {
      setLoading(false);
    }
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
            DeFi 2.0 Dashboard
          </h1>
          <p className="text-muted-foreground mt-1">
            Cross-chain DeFi protokolleri ve yield optimization
          </p>
        </div>
        <Web3ConnectButton />
      </div>

      {/* Portfolio Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card variant="glass">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Toplam Portfoy</p>
                <p className="text-2xl font-bold mt-1">
                  {formatCurrency(totalValue)}
                </p>
              </div>
              <div className="p-3 bg-primary/10 rounded-lg">
                <WalletIcon className="w-6 h-6 text-primary" />
              </div>
            </div>
          </div>
        </Card>

        <Card variant="glass">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Aktif Yield Pozisyonlari</p>
                <p className="text-2xl font-bold mt-1">{yieldPositions.length}</p>
              </div>
              <div className="p-3 bg-green-500/10 rounded-lg">
                <ChartBarIcon className="w-6 h-6 text-green-500" />
              </div>
            </div>
          </div>
        </Card>

        <Card variant="glass">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Arbitraj Firsatlari</p>
                <p className="text-2xl font-bold mt-1">{arbitrageOps.length}</p>
              </div>
              <div className="p-3 bg-orange-500/10 rounded-lg">
                <SparklesIcon className="w-6 h-6 text-orange-500" />
              </div>
            </div>
          </div>
        </Card>

        <Card variant="glass">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Baglantilar</p>
                <p className="text-2xl font-bold mt-1">{chainBalances.length}</p>
              </div>
              <div className="p-3 bg-purple-500/10 rounded-lg">
                <LinkIcon className="w-6 h-6 text-purple-500" />
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card variant="glass">
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Hizli Islemler</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <Button 
              variant="outline" 
              className="h-auto py-4 flex-col"
              onClick={() => navigate('/defi/bridge')}
            >
              <ArrowsRightLeftIcon className="w-6 h-6 mb-2" />
              <span>Cross-Chain Bridge</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-auto py-4 flex-col"
              onClick={() => navigate('/defi/yield')}
            >
              <FireIcon className="w-6 h-6 mb-2" />
              <span>Yield Farming</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-auto py-4 flex-col"
              onClick={() => navigate('/defi/arbitrage')}
            >
              <SparklesIcon className="w-6 h-6 mb-2" />
              <span>Arbitrage</span>
            </Button>
            <Button 
              variant="outline" 
              className="h-auto py-4 flex-col"
              onClick={() => navigate('/defi/trading')}
            >
              <CurrencyDollarIcon className="w-6 h-6 mb-2" />
              <span>DeFi Trading</span>
            </Button>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chain Balances */}
        <Card variant="glass">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Multi-Chain Bakiyeler</h3>
              <Button size="sm" variant="ghost" onClick={() => navigate('/defi/wallet')}>
                Tum Cuzdanlar
              </Button>
            </div>
            
            {loading ? (
              <div className="space-y-3">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-16 bg-card/50 rounded-lg animate-pulse" />
                ))}
              </div>
            ) : chainBalances.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <WalletIcon className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Henuz cuzdan baglantisi yok</p>
                <Button size="sm" variant="outline" className="mt-3" onClick={() => navigate('/defi/wallet')}>
                  Cuzdan Bagla
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {chainBalances.map((chain, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 bg-card/50 rounded-lg hover:bg-card/70 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                        <LinkIcon className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium">{chain.chain}</p>
                        <p className="text-sm text-muted-foreground">
                          {chain.tokens.length} token
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold">{formatCurrency(chain.balance)}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>

        {/* Top Yield Opportunities */}
        <Card variant="glass">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">En Iyi Yield Firsatlari</h3>
              <Button size="sm" variant="ghost" onClick={() => navigate('/defi/yield')}>
                Tum Firsatlar
              </Button>
            </div>
            
            {loading ? (
              <div className="space-y-3">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-16 bg-card/50 rounded-lg animate-pulse" />
                ))}
              </div>
            ) : protocols.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <ChartBarIcon className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Yield firsatlari yukleniyor...</p>
              </div>
            ) : (
              <div className="space-y-3">
                {protocols.slice(0, 5).map((protocol, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 bg-card/50 rounded-lg hover:bg-card/70 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-green-500/10 rounded-full flex items-center justify-center">
                        <BanknotesIcon className="w-5 h-5 text-green-500" />
                      </div>
                      <div>
                        <p className="font-medium">{protocol.name}</p>
                        <p className="text-sm text-muted-foreground capitalize">{protocol.type}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant="success">
                        {formatPercent(protocol.apy)} APY
                      </Badge>
                      <p className="text-xs text-muted-foreground mt-1">
                        TVL: {formatCurrency(protocol.tvl)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Arbitrage Opportunities */}
      {arbitrageOps.length > 0 && (
        <Card variant="glass">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Aktif Arbitraj Firsatlari</h3>
              <Button size="sm" variant="ghost" onClick={() => navigate('/defi/arbitrage')}>
                Tum Firsatlar
              </Button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {arbitrageOps.slice(0, 3).map((opp) => (
                <div key={opp.id} className="p-4 bg-card/50 rounded-lg border border-primary/20">
                  <div className="flex items-center justify-between mb-3">
                    <Badge variant="default">{opp.token}</Badge>
                    <Badge variant="success">+{formatPercent(opp.profit)}</Badge>
                  </div>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Kaynak:</span>
                      <span className="font-medium">{opp.source}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Hedef:</span>
                      <span className="font-medium">{opp.destination}</span>
                    </div>
                  </div>
                  <Button size="sm" className="w-full mt-3">
                    Islem Yap
                  </Button>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
