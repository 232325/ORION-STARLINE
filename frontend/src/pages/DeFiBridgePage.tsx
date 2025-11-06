import { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import Input from '../components/ui/Input';
import { 
  ArrowsRightLeftIcon,
  ArrowDownIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  LinkIcon
} from '@heroicons/react/24/outline';

interface BridgeTransaction {
  id: string;
  sourceChain: string;
  destinationChain: string;
  token: string;
  amount: number;
  status: string;
  fee: number;
  estimatedTime: number;
  createdAt: string;
}

interface ChainInfo {
  name: string;
  symbol: string;
  logo?: string;
}

const SUPPORTED_CHAINS: ChainInfo[] = [
  { name: 'Ethereum', symbol: 'ETH' },
  { name: 'BSC', symbol: 'BSC' },
  { name: 'Polygon', symbol: 'MATIC' },
  { name: 'Arbitrum', symbol: 'ARB' },
  { name: 'Optimism', symbol: 'OP' }
];

const BRIDGE_PROTOCOLS = ['Hop Protocol', 'Across', 'Multichain', 'Stargate'];

export default function DeFiBridgePage() {
  const [sourceChain, setSourceChain] = useState('Ethereum');
  const [destinationChain, setDestinationChain] = useState('BSC');
  const [tokenSymbol, setTokenSymbol] = useState('USDC');
  const [amount, setAmount] = useState('');
  const [bridgeProtocol, setBridgeProtocol] = useState('Hop Protocol');
  const [loading, setLoading] = useState(false);
  const [estimating, setEstimating] = useState(false);
  const [transactions, setTransactions] = useState<BridgeTransaction[]>([]);
  const [estimate, setEstimate] = useState<any>(null);

  useEffect(() => {
    fetchBridgeHistory();
  }, []);

  useEffect(() => {
    if (amount && parseFloat(amount) > 0) {
      estimateBridge();
    }
  }, [sourceChain, destinationChain, tokenSymbol, amount, bridgeProtocol]);

  const fetchBridgeHistory = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/defi-bridge-manager`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
          },
          body: JSON.stringify({ action: 'get_history' })
        }
      );

      if (response.ok) {
        const data = await response.json();
        if (data.data?.transactions) {
          setTransactions(data.data.transactions);
        }
      }
    } catch (error) {
      console.error('Error fetching bridge history:', error);
    }
  };

  const estimateBridge = async () => {
    try {
      setEstimating(true);
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/defi-bridge-manager`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
          },
          body: JSON.stringify({
            action: 'estimate_bridge',
            sourceChain,
            destinationChain,
            tokenSymbol,
            amount: parseFloat(amount),
            bridgeProtocol
          })
        }
      );

      if (response.ok) {
        const data = await response.json();
        if (data.data) {
          setEstimate(data.data);
        }
      }
    } catch (error) {
      console.error('Error estimating bridge:', error);
    } finally {
      setEstimating(false);
    }
  };

  const handleBridge = async () => {
    if (!amount || parseFloat(amount) <= 0) {
      alert('Gecerli bir miktar girin');
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/defi-bridge-manager`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
          },
          body: JSON.stringify({
            action: 'initiate_bridge',
            sourceChain,
            destinationChain,
            tokenSymbol,
            amount: parseFloat(amount),
            bridgeProtocol
          })
        }
      );

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          alert('Bridge islemi baslatildi!');
          setAmount('');
          fetchBridgeHistory();
        } else {
          alert(data.error || 'Bridge islemi basarisiz');
        }
      }
    } catch (error) {
      console.error('Error bridging:', error);
      alert('Bir hata olustu');
    } finally {
      setLoading(false);
    }
  };

  const swapChains = () => {
    const temp = sourceChain;
    setSourceChain(destinationChain);
    setDestinationChain(temp);
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, any> = {
      pending: { variant: 'default', icon: ClockIcon },
      processing: { variant: 'default', icon: ClockIcon },
      completed: { variant: 'success', icon: CheckCircleIcon },
      failed: { variant: 'destructive', icon: ExclamationTriangleIcon }
    };

    const config = variants[status] || variants.pending;
    const Icon = config.icon;

    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="w-3 h-3" />
        {status}
      </Badge>
    );
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('tr-TR', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 6
    }).format(value);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
          Cross-Chain Bridge
        </h1>
        <p className="text-muted-foreground mt-1">
          Varliklari blockchainler arasi transfer edin
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Bridge Interface */}
        <div className="lg:col-span-2">
          <Card variant="glass">
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-6">Transfer Detaylari</h3>

              {/* Source Chain */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Kaynak Chain</label>
                  <select
                    value={sourceChain}
                    onChange={(e) => setSourceChain(e.target.value)}
                    className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  >
                    {SUPPORTED_CHAINS.map(chain => (
                      <option key={chain.name} value={chain.name}>
                        {chain.name} ({chain.symbol})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Swap Button */}
                <div className="flex justify-center -my-2">
                  <button
                    onClick={swapChains}
                    className="p-2 bg-card border border-border rounded-full hover:bg-accent transition-colors"
                  >
                    <ArrowDownIcon className="w-5 h-5" />
                  </button>
                </div>

                {/* Destination Chain */}
                <div>
                  <label className="block text-sm font-medium mb-2">Hedef Chain</label>
                  <select
                    value={destinationChain}
                    onChange={(e) => setDestinationChain(e.target.value)}
                    className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  >
                    {SUPPORTED_CHAINS.map(chain => (
                      <option key={chain.name} value={chain.name}>
                        {chain.name} ({chain.symbol})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Token and Amount */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Token</label>
                    <Input
                      value={tokenSymbol}
                      onChange={(e) => setTokenSymbol(e.target.value.toUpperCase())}
                      placeholder="USDC"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Miktar</label>
                    <Input
                      type="number"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                      placeholder="0.00"
                      step="0.000001"
                    />
                  </div>
                </div>

                {/* Bridge Protocol */}
                <div>
                  <label className="block text-sm font-medium mb-2">Bridge Protokolu</label>
                  <select
                    value={bridgeProtocol}
                    onChange={(e) => setBridgeProtocol(e.target.value)}
                    className="w-full px-4 py-3 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                  >
                    {BRIDGE_PROTOCOLS.map(protocol => (
                      <option key={protocol} value={protocol}>{protocol}</option>
                    ))}
                  </select>
                </div>

                {/* Estimate */}
                {estimate && (
                  <div className="p-4 bg-primary/5 border border-primary/20 rounded-lg space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Bridge Ucreti:</span>
                      <span className="font-medium">{formatCurrency(estimate.fee || 0)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Tahmini Sure:</span>
                      <span className="font-medium">{estimate.estimatedTime || 5} dakika</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Alacaginiz Miktar:</span>
                      <span className="font-medium">
                        ~{(parseFloat(amount) - (estimate.fee || 0)).toFixed(6)} {tokenSymbol}
                      </span>
                    </div>
                  </div>
                )}

                {/* Bridge Button */}
                <Button
                  onClick={handleBridge}
                  disabled={loading || estimating || !amount || parseFloat(amount) <= 0}
                  className="w-full"
                  size="lg"
                >
                  {loading ? 'Isleniyor...' : estimating ? 'Hesaplaniyor...' : (
                    <>
                      <ArrowsRightLeftIcon className="w-5 h-5 mr-2" />
                      Bridge Islemi Baslat
                    </>
                  )}
                </Button>
              </div>
            </div>
          </Card>
        </div>

        {/* Info Cards */}
        <div className="space-y-4">
          <Card variant="glass">
            <div className="p-6">
              <h4 className="font-semibold mb-3 flex items-center gap-2">
                <LinkIcon className="w-5 h-5 text-primary" />
                Desteklenen Chainler
              </h4>
              <div className="space-y-2">
                {SUPPORTED_CHAINS.map(chain => (
                  <div key={chain.name} className="flex items-center gap-2 text-sm">
                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                    <span>{chain.name}</span>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          <Card variant="glass">
            <div className="p-6">
              <h4 className="font-semibold mb-3">Bridge Ucretleri</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Minimum:</span>
                  <span>$0.50</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Ortalama:</span>
                  <span>$2-5</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Maksimum:</span>
                  <span>0.3%</span>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Transaction History */}
      <Card variant="glass">
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Transfer Gecmisi</h3>
          
          {transactions.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <ArrowsRightLeftIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Henuz bridge islemi yapilmadi</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-3 px-4 font-medium">Tarih</th>
                    <th className="text-left py-3 px-4 font-medium">Route</th>
                    <th className="text-left py-3 px-4 font-medium">Token</th>
                    <th className="text-right py-3 px-4 font-medium">Miktar</th>
                    <th className="text-right py-3 px-4 font-medium">Ucret</th>
                    <th className="text-center py-3 px-4 font-medium">Durum</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((tx) => (
                    <tr key={tx.id} className="border-b border-border/50 hover:bg-accent/50 transition-colors">
                      <td className="py-3 px-4 text-sm">
                        {new Date(tx.createdAt).toLocaleDateString('tr-TR')}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2 text-sm">
                          <span>{tx.sourceChain}</span>
                          <ArrowsRightLeftIcon className="w-4 h-4 text-muted-foreground" />
                          <span>{tx.destinationChain}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4 font-medium text-sm">{tx.token}</td>
                      <td className="py-3 px-4 text-right font-medium">
                        {tx.amount.toFixed(6)}
                      </td>
                      <td className="py-3 px-4 text-right text-sm text-muted-foreground">
                        {formatCurrency(tx.fee)}
                      </td>
                      <td className="py-3 px-4 text-center">
                        {getStatusBadge(tx.status)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
