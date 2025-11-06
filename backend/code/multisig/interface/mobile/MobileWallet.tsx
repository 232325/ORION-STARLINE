/**
 * @class MobileWallet
 * @dev Mobile wallet interface for multi-signature wallets
 * @author MultiSig Wallet System
 */

import React, { useState, useEffect } from 'react';
import { Web3WalletIntegration } from '../web3/Web3WalletIntegration';
import { WalletManager } from '../../core/wallet/WalletManager';

interface MobileWalletProps {
  web3Integration: Web3WalletIntegration;
  onTransactionSubmit?: (tx: any) => void;
  onError?: (error: string) => void;
}

interface Transaction {
  id: string;
  to: string;
  value: string;
  status: 'pending' | 'confirmed' | 'executed';
  confirmations: number;
  required: number;
  submittedAt: string;
}

interface WalletState {
  connected: boolean;
  address: string;
  balance: string;
  pendingTransactions: Transaction[];
  confirmedTransactions: Transaction[];
  owners: string[];
  requirement: number;
  spendingLimits: {
    daily: { used: string; limit: string };
    weekly: { used: string; limit: string };
    monthly: { used: string; limit: string };
  };
}

const MobileWallet: React.FC<MobileWalletProps> = ({
  web3Integration,
  onTransactionSubmit,
  onError
}) => {
  const [state, setState] = useState<WalletState>({
    connected: false,
    address: '',
    balance: '0',
    pendingTransactions: [],
    confirmedTransactions: [],
    owners: [],
    requirement: 0,
    spendingLimits: {
      daily: { used: '0', limit: '0' },
      weekly: { used: '0', limit: '0' },
      monthly: { used: '0', limit: '0' }
    }
  });

  const [showSendModal, setShowSendModal] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [selectedTx, setSelectedTx] = useState<Transaction | null>(null);
  const [sendForm, setSendForm] = useState({
    to: '',
    value: '',
    description: ''
  });

  useEffect(() => {
    initializeWallet();
    setupEventListeners();
    
    return () => {
      // Cleanup
    };
  }, []);

  const initializeWallet = async () => {
    try {
      // Check if wallet is already connected
      if (web3Integration.getState().connected) {
        await loadWalletData();
      }
    } catch (error) {
      console.error('Failed to initialize wallet:', error);
      onError?.(error instanceof Error ? error.message : 'Unknown error');
    }
  };

  const setupEventListeners = () => {
    web3Integration.on('walletConnected', async () => {
      await loadWalletData();
    });

    web3Integration.on('walletDisconnected', () => {
      setState({
        connected: false,
        address: '',
        balance: '0',
        pendingTransactions: [],
        confirmedTransactions: [],
        owners: [],
        requirement: 0,
        spendingLimits: {
          daily: { used: '0', limit: '0' },
          weekly: { used: '0', limit: '0' },
          monthly: { used: '0', limit: '0' }
        }
      });
    });

    web3Integration.on('transactionSubmitted', () => {
      loadWalletData();
    });

    web3Integration.on('transactionConfirmed', () => {
      loadWalletData();
    });

    web3Integration.on('transactionExecuted', () => {
      loadWalletData();
    });
  };

  const loadWalletData = async () => {
    try {
      const walletState = web3Integration.getState();
      const [balance, pendingTx, confirmedTx, owners, spendingStatus] = await Promise.all([
        web3Integration.getBalance(),
        web3Integration.getPendingTransactions(),
        web3Integration.getConfirmedTransactions(),
        web3Integration.getOwners(),
        web3Integration.getSpendingStatus()
      ]);

      setState({
        connected: walletState.connected,
        address: walletState.wallet?.address || '',
        balance,
        pendingTransactions: pendingTx,
        confirmedTransactions: confirmedTx,
        owners: owners.map(o => o.address),
        requirement: walletState.requirement,
        spendingLimits: spendingStatus?.limits ? {
          daily: {
            used: spendingStatus.limits.daily.used.toString(),
            limit: spendingStatus.limits.daily.amount.toString()
          },
          weekly: {
            used: spendingStatus.limits.weekly.used.toString(),
            limit: spendingStatus.limits.weekly.amount.toString()
          },
          monthly: {
            used: spendingStatus.limits.monthly.used.toString(),
            limit: spendingStatus.limits.monthly.amount.toString()
          }
        } : {
          daily: { used: '0', limit: '0' },
          weekly: { used: '0', limit: '0' },
          monthly: { used: '0', limit: '0' }
        }
      });
    } catch (error) {
      console.error('Failed to load wallet data:', error);
      onError?.(error instanceof Error ? error.message : 'Failed to load data');
    }
  };

  const connectWallet = async () => {
    try {
      await web3Integration.connect();
    } catch (error) {
      console.error('Failed to connect wallet:', error);
      onError?.(error instanceof Error ? error.message : 'Failed to connect');
    }
  };

  const loadMultiSigWallet = async () => {
    const address = prompt('Enter multi-signature wallet address:');
    if (!address) return;

    try {
      await web3Integration.loadMultiSigWallet(address);
      await loadWalletData();
    } catch (error) {
      console.error('Failed to load wallet:', error);
      onError?.(error instanceof Error ? error.message : 'Failed to load wallet');
    }
  };

  const sendTransaction = async () => {
    try {
      const txId = await web3Integration.submitTransaction({
        to: sendForm.to,
        value: sendForm.value,
        description: sendForm.description
      });

      setShowSendModal(false);
      setSendForm({ to: '', value: '', description: '' });
      onTransactionSubmit?.(txId);
      
      await loadWalletData();
    } catch (error) {
      console.error('Failed to send transaction:', error);
      onError?.(error instanceof Error ? error.message : 'Failed to send transaction');
    }
  };

  const confirmTransaction = async (tx: Transaction) => {
    try {
      await web3Integration.confirmTransaction(tx.id);
      await loadWalletData();
    } catch (error) {
      console.error('Failed to confirm transaction:', error);
      onError?.(error instanceof Error ? error.message : 'Failed to confirm transaction');
    }
  };

  const executeTransaction = async (tx: Transaction) => {
    try {
      const txHash = await web3Integration.executeTransaction(tx.id);
      await loadWalletData();
    } catch (error) {
      console.error('Failed to execute transaction:', error);
      onError?.(error instanceof Error ? error.message : 'Failed to execute transaction');
    }
  };

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const formatValue = (value: string) => {
    return parseFloat(value).toFixed(4);
  };

  const getPercentage = (used: string, limit: string) => {
    const usedNum = parseFloat(used);
    const limitNum = parseFloat(limit);
    return limitNum > 0 ? (usedNum / limitNum) * 100 : 0;
  };

  if (!state.connected) {
    return (
      <div className="mobile-wallet">
        <div className="connection-screen">
          <h1>Multi-Signature Wallet</h1>
          <p>Connect your wallet to get started</p>
          
          <div className="connection-options">
            <button onClick={connectWallet} className="primary-btn">
              Connect Wallet
            </button>
            
            <div className="divider">
              <span>OR</span>
            </div>
            
            <button onClick={loadMultiSigWallet} className="secondary-btn">
              Load Existing Wallet
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mobile-wallet">
      {/* Header */}
      <div className="wallet-header">
        <div className="wallet-info">
          <h2>{formatAddress(state.address)}</h2>
          <p className="balance">{formatValue(state.balance)} ETH</p>
        </div>
        <button 
          onClick={() => setShowSettings(true)} 
          className="settings-btn"
        >
          ⚙️
        </button>
      </div>

      {/* Spending Limits */}
      <div className="spending-limits">
        <h3>Spending Limits</h3>
        <div className="limit-bars">
          <div className="limit-bar">
            <label>Daily: {formatValue(state.spendingLimits.daily.used)} / {formatValue(state.spendingLimits.daily.limit)} ETH</label>
            <div className="bar">
              <div 
                className="bar-fill" 
                style={{ width: `${getPercentage(state.spendingLimits.daily.used, state.spendingLimits.daily.limit)}%` }}
              />
            </div>
          </div>
          
          <div className="limit-bar">
            <label>Weekly: {formatValue(state.spendingLimits.weekly.used)} / {formatValue(state.spendingLimits.weekly.limit)} ETH</label>
            <div className="bar">
              <div 
                className="bar-fill" 
                style={{ width: `${getPercentage(state.spendingLimits.weekly.used, state.spendingLimits.weekly.limit)}%` }}
              />
            </div>
          </div>
          
          <div className="limit-bar">
            <label>Monthly: {formatValue(state.spendingLimits.monthly.used)} / {formatValue(state.spendingLimits.monthly.limit)} ETH</label>
            <div className="bar">
              <div 
                className="bar-fill" 
                style={{ width: `${getPercentage(state.spendingLimits.monthly.used, state.spendingLimits.monthly.limit)}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <button 
          onClick={() => setShowSendModal(true)} 
          className="action-btn primary"
        >
          Send
        </button>
        <button className="action-btn secondary">
          Receive
        </button>
        <button className="action-btn secondary">
          History
        </button>
      </div>

      {/* Transactions */}
      <div className="transactions-section">
        <div className="tabs">
          <button className="tab active">Pending ({state.pendingTransactions.length})</button>
          <button className="tab">Confirmed ({state.confirmedTransactions.length})</button>
        </div>

        <div className="transactions-list">
          {state.pendingTransactions.map(tx => (
            <div key={tx.id} className="transaction-item pending">
              <div className="tx-info">
                <p className="tx-to">{formatAddress(tx.to)}</p>
                <p className="tx-value">{formatValue(tx.value)} ETH</p>
                <p className="tx-time">{new Date(tx.submittedAt).toLocaleDateString()}</p>
              </div>
              <div className="tx-actions">
                <div className="confirmations">
                  {tx.confirmations}/{tx.required}
                </div>
                <button 
                  onClick={() => confirmTransaction(tx)} 
                  className="confirm-btn"
                >
                  Confirm
                </button>
              </div>
            </div>
          ))}

          {state.confirmedTransactions.map(tx => (
            <div key={tx.id} className="transaction-item confirmed">
              <div className="tx-info">
                <p className="tx-to">{formatAddress(tx.to)}</p>
                <p className="tx-value">{formatValue(tx.value)} ETH</p>
                <p className="tx-time">{new Date(tx.submittedAt).toLocaleDateString()}</p>
              </div>
              <div className="tx-status">
                ✓ Confirmed
              </div>
            </div>
          ))}

          {state.pendingTransactions.length === 0 && state.confirmedTransactions.length === 0 && (
            <div className="empty-state">
              <p>No transactions yet</p>
            </div>
          )}
        </div>
      </div>

      {/* Send Transaction Modal */}
      {showSendModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Send Transaction</h3>
              <button onClick={() => setShowSendModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              <input
                type="text"
                placeholder="Recipient Address"
                value={sendForm.to}
                onChange={(e) => setSendForm({...sendForm, to: e.target.value})}
              />
              <input
                type="text"
                placeholder="Amount (ETH)"
                value={sendForm.value}
                onChange={(e) => setSendForm({...sendForm, value: e.target.value})}
              />
              <textarea
                placeholder="Description (optional)"
                value={sendForm.description}
                onChange={(e) => setSendForm({...sendForm, description: e.target.value})}
              />
            </div>
            <div className="modal-actions">
              <button onClick={() => setShowSendModal(false)} className="secondary-btn">
                Cancel
              </button>
              <button onClick={sendTransaction} className="primary-btn">
                Send
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Settings Modal */}
      {showSettings && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Wallet Settings</h3>
              <button onClick={() => setShowSettings(false)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="setting-item">
                <label>Owners ({state.owners.length}):</label>
                <div className="owners-list">
                  {state.owners.map(owner => (
                    <span key={owner} className="owner-tag">
                      {formatAddress(owner)}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="setting-item">
                <label>Required Confirmations: {state.requirement}</label>
              </div>
              
              <div className="setting-item">
                <button className="secondary-btn">View Full History</button>
                <button className="secondary-btn">Export Data</button>
                <button className="danger-btn">Disconnect Wallet</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MobileWallet;