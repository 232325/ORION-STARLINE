import { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { 
  WalletIcon,
  LinkIcon,
  CheckCircleIcon,
  XCircleIcon,
  PlusIcon,
  TrashIcon
} from '@heroicons/react/24/outline';

interface Wallet {
  id: string;
  chain: string;
  address: string;
  walletType: string;
  isPrimary: boolean;
  balanceUsd: number;
  lastSync: string;
  tokens: { symbol: string; amount: number; value: number }[];
}

const SUPPORTED_CHAINS = [
  'Ethereum',
  'BSC',
  'Polygon',
  'Arbitrum',
  'Optimism',
  'Avalanche'
];

export default function DeFiWalletPage() {
  const [wallets, setWallets] = useState<Wallet[]>([]);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [selectedChain, setSelectedChain] = useState('Ethereum');
  const [walletAddress, setWalletAddress] = useState('');

  useEffect(() => {
    fetchWallets();
  }, []);

  const fetchWallets = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/defi-wallet-manager`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
          },
          body: JSON.stringify({ action: 'get_wallets' })
        }
      );

      if (response.ok) {
        const data = await response.json();
        if (data.data?.wallets) {
          setWallets(data.data.wallets);
        }
      }
    } catch (error) {
      console.error('Error fetching wallets:', error);
    } finally {
      setLoading(false);
    }
  };

  const connectWallet = async () => {
    if (!walletAddress || walletAddress.length < 20) {
      alert('Gecerli bir wallet adresi girin');
      return;
    }

    try {
      setConnecting(true);
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/defi-wallet-manager`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
          },
          body: JSON.stringify({
            action: 'connect_wallet',
            chain: selectedChain,
            address: walletAddress,
            walletType: 'MetaMask'
          })
        }
      );

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          alert('Wallet basariyla baglandi!');
          setWalletAddress('');
          fetchWallets();
        } else {
          alert(data.error || 'Baglanti basarisiz');
        }
      }
    } catch (error) {
      console.error('Error connecting wallet:', error);
      alert('Bir hata olustu');
    } finally {
      setConnecting(false);
    }
  };

  const disconnectWallet = async (walletId: string) => {
    if (!confirm('Bu cüzdani ayirmak istediginizden emin misiniz?')) {
      return;
    }

    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/defi-wallet-manager`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
          },
          body: JSON.stringify({
            action: 'disconnect_wallet',
            walletId
          })
        }
      );

      if (response.ok) {
        fetchWallets();
      }
    } catch (error) {
      console.error('Error disconnecting wallet:', error);
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

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const totalBalance = wallets.reduce((sum, w) => sum + w.balanceUsd, 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
          Multi-Chain Wallet
        </h1>
        <p className="text-muted-foreground mt-1">
          Tum chainlerdeki cuzdanlarinizi tek yerden yonetin
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card variant="glass">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Toplam Bakiye</p>
                <p className="text-2xl font-bold mt-1">{formatCurrency(totalBalance)}</p>
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
                <p className="text-sm text-muted-foreground">Bagli Cuzdanlar</p>
                <p className="text-2xl font-bold mt-1">{wallets.length}</p>
              </div>
              <div className="p-3 bg-green-500/10 rounded-lg">
                <CheckCircleIcon className="w-6 h-6 text-green-500" />
              </div>
            </div>
          </div>
        </Card>

        <Card variant="glass">
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Desteklenen Chainler</p>
                <p className="text-2xl font-bold mt-1">{SUPPORTED_CHAINS.length}</p>
              </div>
              <div className="p-3 bg-purple-500/10 rounded-lg">
                <LinkIcon className="w-6 h-6 text-purple-500" />
              </div>
            </div>
          </div>
        </Card>
      </div>

      <Card variant="glass">
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Yeni Cuzdan Bagla</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Chain</label>
              <select
                value={selectedChain}
                onChange={(e) => setSelectedChain(e.target.value)}
                className="w-full px-4 py-3 bg-background border border-border rounded-lg"
              >
                {SUPPORTED_CHAINS.map(chain => (
                  <option key={chain} value={chain}>{chain}</option>
                ))}
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-2">Wallet Adresi</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={walletAddress}
                  onChange={(e) => setWalletAddress(e.target.value)}
                  placeholder="0x..."
                  className="flex-1 px-4 py-3 bg-background border border-border rounded-lg"
                />
                <Button onClick={connectWallet} disabled={connecting}>
                  <PlusIcon className="w-5 h-5 mr-2" />
                  {connecting ? 'Baglaniyor...' : 'Bagla'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <Card key={i} variant="glass">
              <div className="p-6 h-32 animate-pulse bg-card/50" />
            </Card>
          ))}
        </div>
      ) : wallets.length === 0 ? (
        <Card variant="glass">
          <div className="p-12 text-center text-muted-foreground">
            <WalletIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>Henuz bagli cuzdan yok</p>
            <p className="text-sm mt-2">Yukaridaki formu kullanarak cuzdan baglayabilirsiniz</p>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {wallets.map((wallet) => (
            <Card key={wallet.id} variant="glass">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="p-3 bg-primary/10 rounded-lg">
                      <WalletIcon className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-semibold">{wallet.chain}</h4>
                        {wallet.isPrimary && (
                          <Badge variant="default" className="text-xs">Primary</Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground font-mono">
                        {formatAddress(wallet.address)}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => disconnectWallet(wallet.id)}
                    className="p-2 hover:bg-destructive/10 rounded-lg transition-colors"
                  >
                    <TrashIcon className="w-5 h-5 text-destructive" />
                  </button>
                </div>

                <div className="mb-4 pb-4 border-b border-border">
                  <p className="text-2xl font-bold">{formatCurrency(wallet.balanceUsd)}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Son guncelleme: {new Date(wallet.lastSync).toLocaleString('tr-TR')}
                  </p>
                </div>

                {wallet.tokens && wallet.tokens.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium mb-2">Tokenlar:</p>
                    {wallet.tokens.slice(0, 3).map((token, idx) => (
                      <div key={idx} className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">{token.symbol}</span>
                        <div className="text-right">
                          <p className="font-medium">{token.amount.toFixed(4)}</p>
                          <p className="text-xs text-muted-foreground">
                            {formatCurrency(token.value)}
                          </p>
                        </div>
                      </div>
                    ))}
                    {wallet.tokens.length > 3 && (
                      <p className="text-xs text-muted-foreground text-center pt-2">
                        +{wallet.tokens.length - 3} token daha
                      </p>
                    )}
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
