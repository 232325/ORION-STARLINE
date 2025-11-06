import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { ethers } from 'ethers';

interface Web3ContextType {
  provider: ethers.BrowserProvider | null;
  signer: ethers.Signer | null;
  account: string | null;
  chainId: number | null;
  balance: string | null;
  isConnecting: boolean;
  error: string | null;
  connectWallet: () => Promise<void>;
  disconnectWallet: () => void;
  switchChain: (chainId: number) => Promise<void>;
}

const Web3Context = createContext<Web3ContextType | undefined>(undefined);

interface Web3ProviderProps {
  children: ReactNode;
}

// Supported chains
export const SUPPORTED_CHAINS = {
  1: { name: 'Ethereum', symbol: 'ETH', rpc: 'https://eth.llamarpc.com' },
  56: { name: 'BSC', symbol: 'BNB', rpc: 'https://bsc-dataseed.binance.org' },
  137: { name: 'Polygon', symbol: 'MATIC', rpc: 'https://polygon-rpc.com' },
  42161: { name: 'Arbitrum', symbol: 'ARB', rpc: 'https://arb1.arbitrum.io/rpc' },
  10: { name: 'Optimism', symbol: 'OP', rpc: 'https://mainnet.optimism.io' },
  43114: { name: 'Avalanche', symbol: 'AVAX', rpc: 'https://api.avax.network/ext/bc/C/rpc' }
};

export function Web3Provider({ children }: Web3ProviderProps) {
  const [provider, setProvider] = useState<ethers.BrowserProvider | null>(null);
  const [signer, setSigner] = useState<ethers.Signer | null>(null);
  const [account, setAccount] = useState<string | null>(null);
  const [chainId, setChainId] = useState<number | null>(null);
  const [balance, setBalance] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Check if wallet is already connected on mount
  useEffect(() => {
    checkConnection();
    
    // Listen for account changes
    if (window.ethereum) {
      window.ethereum.on('accountsChanged', handleAccountsChanged);
      window.ethereum.on('chainChanged', handleChainChanged);
    }

    return () => {
      if (window.ethereum) {
        window.ethereum.removeListener('accountsChanged', handleAccountsChanged);
        window.ethereum.removeListener('chainChanged', handleChainChanged);
      }
    };
  }, []);

  // Update balance when account or chain changes
  useEffect(() => {
    if (account && provider) {
      updateBalance();
    }
  }, [account, chainId, provider]);

  const checkConnection = async () => {
    if (typeof window.ethereum !== 'undefined') {
      try {
        const provider = new ethers.BrowserProvider(window.ethereum);
        const accounts = await provider.listAccounts();
        
        if (accounts.length > 0) {
          const signer = await provider.getSigner();
          const address = await signer.getAddress();
          const network = await provider.getNetwork();
          
          setProvider(provider);
          setSigner(signer);
          setAccount(address);
          setChainId(Number(network.chainId));
        }
      } catch (err) {
        console.error('Error checking connection:', err);
      }
    }
  };

  const connectWallet = async () => {
    if (typeof window.ethereum === 'undefined') {
      setError('MetaMask yuklu degil. Lutfen MetaMask yukleyin.');
      return;
    }

    try {
      setIsConnecting(true);
      setError(null);

      // Request account access
      await window.ethereum.request({ method: 'eth_requestAccounts' });

      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const address = await signer.getAddress();
      const network = await provider.getNetwork();

      setProvider(provider);
      setSigner(signer);
      setAccount(address);
      setChainId(Number(network.chainId));

      // Store connection state
      localStorage.setItem('web3_connected', 'true');
    } catch (err: any) {
      console.error('Error connecting wallet:', err);
      setError(err.message || 'Cuzdan baglantisi basarisiz');
    } finally {
      setIsConnecting(false);
    }
  };

  const disconnectWallet = () => {
    setProvider(null);
    setSigner(null);
    setAccount(null);
    setChainId(null);
    setBalance(null);
    localStorage.removeItem('web3_connected');
  };

  const switchChain = async (targetChainId: number) => {
    if (!window.ethereum) {
      setError('MetaMask bulunamadi');
      return;
    }

    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: `0x${targetChainId.toString(16)}` }],
      });
    } catch (err: any) {
      // Chain doesn't exist, add it
      if (err.code === 4902) {
        const chainConfig = SUPPORTED_CHAINS[targetChainId as keyof typeof SUPPORTED_CHAINS];
        if (chainConfig) {
          try {
            await window.ethereum.request({
              method: 'wallet_addEthereumChain',
              params: [{
                chainId: `0x${targetChainId.toString(16)}`,
                chainName: chainConfig.name,
                nativeCurrency: {
                  name: chainConfig.symbol,
                  symbol: chainConfig.symbol,
                  decimals: 18
                },
                rpcUrls: [chainConfig.rpc],
              }],
            });
          } catch (addErr) {
            console.error('Error adding chain:', addErr);
            setError('Chain eklenemedi');
          }
        }
      } else {
        console.error('Error switching chain:', err);
        setError('Chain degistirilemedi');
      }
    }
  };

  const updateBalance = async () => {
    if (!account || !provider) return;

    try {
      const balance = await provider.getBalance(account);
      setBalance(ethers.formatEther(balance));
    } catch (err) {
      console.error('Error fetching balance:', err);
    }
  };

  const handleAccountsChanged = (accounts: string[]) => {
    if (accounts.length === 0) {
      disconnectWallet();
    } else {
      setAccount(accounts[0]);
    }
  };

  const handleChainChanged = () => {
    // Reload to avoid state issues
    window.location.reload();
  };

  const value: Web3ContextType = {
    provider,
    signer,
    account,
    chainId,
    balance,
    isConnecting,
    error,
    connectWallet,
    disconnectWallet,
    switchChain
  };

  return <Web3Context.Provider value={value}>{children}</Web3Context.Provider>;
}

export function useWeb3() {
  const context = useContext(Web3Context);
  if (context === undefined) {
    throw new Error('useWeb3 must be used within a Web3Provider');
  }
  return context;
}

// Utility functions
export function formatAddress(address: string): string {
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

export function getChainName(chainId: number): string {
  return SUPPORTED_CHAINS[chainId as keyof typeof SUPPORTED_CHAINS]?.name || 'Unknown';
}

export function isChainSupported(chainId: number): boolean {
  return chainId in SUPPORTED_CHAINS;
}

// TypeScript declaration for window.ethereum
declare global {
  interface Window {
    ethereum?: any;
  }
}
