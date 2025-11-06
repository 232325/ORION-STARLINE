import { useWeb3, formatAddress, getChainName, SUPPORTED_CHAINS } from '../contexts/Web3Context';
import Button from './ui/Button';
import Badge from './ui/Badge';
import {
  WalletIcon,
  ArrowRightOnRectangleIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

export default function Web3ConnectButton() {
  const { 
    account, 
    chainId, 
    balance, 
    isConnecting, 
    error,
    connectWallet, 
    disconnectWallet,
    switchChain 
  } = useWeb3();

  const isSupported = chainId ? chainId in SUPPORTED_CHAINS : false;

  if (account) {
    return (
      <div className="flex items-center gap-3">
        {/* Chain indicator */}
        {chainId && (
          <div className="flex items-center gap-2 px-3 py-2 bg-card rounded-lg border border-border">
            {isSupported ? (
              <CheckCircleIcon className="w-4 h-4 text-green-500" />
            ) : (
              <ExclamationTriangleIcon className="w-4 h-4 text-yellow-500" />
            )}
            <span className="text-sm font-medium">
              {getChainName(chainId)}
            </span>
          </div>
        )}

        {/* Account & Balance */}
        <div className="flex items-center gap-3 px-4 py-2 bg-card rounded-lg border border-border">
          <div className="text-right">
            <p className="text-sm font-medium">{formatAddress(account)}</p>
            {balance && (
              <p className="text-xs text-muted-foreground">
                {parseFloat(balance).toFixed(4)} {chainId && SUPPORTED_CHAINS[chainId as keyof typeof SUPPORTED_CHAINS]?.symbol}
              </p>
            )}
          </div>
          <button
            onClick={disconnectWallet}
            className="p-2 hover:bg-destructive/10 rounded-lg transition-colors"
            title="Cuzdan Baglantiyi Kes"
          >
            <ArrowRightOnRectangleIcon className="w-5 h-5 text-destructive" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-end gap-2">
      <Button
        onClick={connectWallet}
        disabled={isConnecting}
        variant="primary"
        size="md"
      >
        <WalletIcon className="w-5 h-5 mr-2" />
        {isConnecting ? 'Baglaniliyor...' : 'MetaMask Bagla'}
      </Button>
      
      {error && (
        <p className="text-xs text-destructive">{error}</p>
      )}
    </div>
  );
}
