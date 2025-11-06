/**
 * @class Web3WalletIntegration
 * @dev Web3 wallet integration for multi-signature wallet UI
 * @author MultiSig Wallet System
 */

import Web3 from 'web3';
import { ethers } from 'ethers';
import { WalletManager } from '../../core/wallet/WalletManager';
import { SecurityManager } from '../../security/auth/SecurityManager';
import { GovernanceManager } from '../../governance/dao/GovernanceManager';
import { KeyManager } from '../../key-management/hsm/KeyManager';
import { SpendingLimits } from '../../core/limits/SpendingLimits';

export interface WalletConnection {
  provider: string;
  chainId: number;
  address: string;
  balance: string;
  connected: boolean;
}

export interface TransactionRequest {
  to: string;
  value: string;
  data?: string;
  gasLimit?: string;
  gasPrice?: string;
  description?: string;
  category?: string;
}

export interface WalletState {
  connected: boolean;
  wallet: WalletConnection | null;
  balances: Map<string, string>;
  pendingTransactions: any[];
  confirmedTransactions: any[];
  owners: any[];
  requirement: number;
  spendingLimits: any;
  securityConfig: any;
  governanceConfig: any;
}

export class Web3WalletIntegration {
  private web3: Web3;
  private provider: ethers.BrowserProvider;
  private walletManager: WalletManager | null = null;
  private securityManager: SecurityManager;
  private governanceManager: GovernanceManager;
  private keyManager: KeyManager;
  private spendingLimits: SpendingLimits;
  private state: WalletState;
  private eventListeners: Map<string, Function[]> = new Map();

  constructor(window: any) {
    // Initialize Web3
    this.web3 = new Web3(window.ethereum);
    this.provider = new ethers.BrowserProvider(window.ethereum);
    
    // Initialize managers
    this.securityManager = new SecurityManager(this.web3);
    this.governanceManager = new GovernanceManager(
      this.provider,
      '', // governance contract address
      '', // governance token address
      null as any // wallet manager (will be set later)
    );
    this.keyManager = new KeyManager(this.web3, 'encryption-key');
    this.spendingLimits = new SpendingLimits();
    
    // Initialize state
    this.state = {
      connected: false,
      wallet: null,
      balances: new Map(),
      pendingTransactions: [],
      confirmedTransactions: [],
      owners: [],
      requirement: 0,
      spendingLimits: null,
      securityConfig: null,
      governanceConfig: null
    };
    
    this.setupEventListeners();
  }

  /**
   * Connect to Web3 wallet
   */
  async connect(): Promise<WalletConnection> {
    try {
      // Request account access
      const accounts = await this.provider.send('eth_requestAccounts', []);
      const network = await this.provider.getNetwork();
      const balance = await this.provider.getBalance(accounts[0]);
      
      const wallet: WalletConnection = {
        provider: 'metamask',
        chainId: Number(network.chainId),
        address: accounts[0],
        balance: ethers.formatEther(balance),
        connected: true
      };
      
      this.state.wallet = wallet;
      this.state.connected = true;
      
      // Emit connection event
      this.emit('walletConnected', wallet);
      
      // Initialize managers with wallet
      await this.initializeManagers();
      
      console.log('Wallet connected:', wallet.address);
      return wallet;
      
    } catch (error) {
      throw new Error(`Failed to connect wallet: ${error}`);
    }
  }

  /**
   * Disconnect wallet
   */
  disconnect(): void {
    this.state = {
      connected: false,
      wallet: null,
      balances: new Map(),
      pendingTransactions: [],
      confirmedTransactions: [],
      owners: [],
      requirement: 0,
      spendingLimits: null,
      securityConfig: null,
      governanceConfig: null
    };
    
    this.emit('walletDisconnected', null);
    console.log('Wallet disconnected');
  }

  /**
   * Switch network
   */
  async switchNetwork(chainId: number): Promise<void> {
    try {
      await this.provider.send('wallet_switchEthereumChain', [
        { chainId: `0x${chainId.toString(16)}` }
      ]);
      
      const network = await this.provider.getNetwork();
      if (this.state.wallet) {
        this.state.wallet.chainId = Number(network.chainId);
      }
      
      this.emit('networkChanged', network);
      console.log('Network switched to:', chainId);
      
    } catch (error) {
      throw new Error(`Failed to switch network: ${error}`);
    }
  }

  /**
   * Create new multi-signature wallet
   */
  async createMultiSigWallet(config: {
    owners: string[];
    threshold: number;
    dailyLimit?: string;
    weeklyLimit?: string;
    monthlyLimit?: string;
  }): Promise<string> {
    try {
      if (!this.state.connected) {
        throw new Error('Wallet not connected');
      }
      
      // Create wallet manager
      this.walletManager = await WalletManager.createWallet(
        this.web3,
        {
          owners: config.owners,
          threshold: config.threshold,
          dailyLimit: config.dailyLimit ? ethers.parseEther(config.dailyLimit) : undefined,
          weeklyLimit: config.weeklyLimit ? ethers.parseEther(config.weeklyLimit) : undefined,
          monthlyLimit: config.monthlyLimit ? ethers.parseEther(config.monthlyLimit) : undefined
        }
      );
      
      // Initialize spending limits
      this.spendingLimits.initialize(this.walletManager.wallet.address, this.provider);
      
      // Load wallet state
      await this.loadWalletState();
      
      this.emit('walletCreated', this.walletManager.wallet.address);
      return this.walletManager.wallet.address;
      
    } catch (error) {
      throw new Error(`Failed to create multi-sig wallet: ${error}`);
    }
  }

  /**
   * Load existing multi-signature wallet
   */
  async loadMultiSigWallet(walletAddress: string): Promise<void> {
    try {
      if (!this.state.connected) {
        throw new Error('Wallet not connected');
      }
      
      // Create wallet manager for existing wallet
      this.walletManager = new WalletManager(
        this.web3,
        walletAddress,
        {
          owners: [],
          threshold: 0
        }
      );
      
      // Initialize spending limits
      this.spendingLimits.initialize(walletAddress, this.provider);
      
      // Load wallet state
      await this.loadWalletState();
      
      this.emit('walletLoaded', walletAddress);
      console.log('Multi-sig wallet loaded:', walletAddress);
      
    } catch (error) {
      throw new Error(`Failed to load multi-sig wallet: ${error}`);
    }
  }

  /**
   * Submit transaction
   */
  async submitTransaction(request: TransactionRequest): Promise<string> {
    try {
      if (!this.walletManager) {
        throw new Error('Multi-sig wallet not loaded');
      }
      
      // Validate transaction
      const validation = await this.securityManager.validateTransaction(
        request.to,
        ethers.parseEther(request.value),
        request.data || '0x'
      );
      
      if (!validation.valid) {
        throw new Error(`Transaction validation failed: ${validation.reason}`);
      }
      
      // Show security warnings if any
      if (validation.warnings && validation.warnings.length > 0) {
        console.warn('Transaction security warnings:', validation.warnings);
      }
      
      // Submit transaction
      const txId = await this.walletManager.submitTransaction(
        request.to,
        ethers.parseEther(request.value),
        request.data || '0x'
      );
      
      // Record spending
      await this.spendingLimits.recordTransaction(
        txId,
        ethers.parseEther(request.value)
      );
      
      this.emit('transactionSubmitted', { txId, request });
      
      console.log('Transaction submitted:', txId);
      return txId;
      
    } catch (error) {
      throw new Error(`Failed to submit transaction: ${error}`);
    }
  }

  /**
   * Confirm transaction
   */
  async confirmTransaction(txId: string): Promise<void> {
    try {
      if (!this.walletManager) {
        throw new Error('Multi-sig wallet not loaded');
      }
      
      await this.walletManager.confirmTransaction(txId);
      this.emit('transactionConfirmed', { txId });
      
      console.log('Transaction confirmed:', txId);
      
    } catch (error) {
      throw new Error(`Failed to confirm transaction: ${error}`);
    }
  }

  /**
   * Execute transaction
   */
  async executeTransaction(txId: string): Promise<string> {
    try {
      if (!this.walletManager) {
        throw new Error('Multi-sig wallet not loaded');
      }
      
      const txHash = await this.walletManager.executeTransaction(txId);
      this.emit('transactionExecuted', { txId, txHash });
      
      console.log('Transaction executed:', txHash);
      return txHash;
      
    } catch (error) {
      throw new Error(`Failed to execute transaction: ${error}`);
    }
  }

  /**
   * Get wallet balance
   */
  async getBalance(): Promise<string> {
    try {
      if (!this.walletManager) {
        return '0';
      }
      
      const balance = await this.walletManager.getBalance();
      return ethers.formatEther(balance);
      
    } catch (error) {
      console.error('Failed to get balance:', error);
      return '0';
    }
  }

  /**
   * Get pending transactions
   */
  async getPendingTransactions(): Promise<any[]> {
    try {
      if (!this.walletManager) {
        return [];
      }
      
      const transactions = await this.walletManager.getPendingTransactions();
      
      // Format for UI
      return transactions.map(tx => ({
        id: tx.id,
        to: tx.to,
        value: ethers.formatEther(tx.value),
        submittedBy: tx.submittedBy,
        submittedAt: new Date(tx.submittedAt * 1000).toISOString(),
        confirmations: tx.confirmations.length,
        required: tx.required,
        deadline: tx.deadline ? new Date(tx.deadline * 1000).toISOString() : null
      }));
      
    } catch (error) {
      console.error('Failed to get pending transactions:', error);
      return [];
    }
  }

  /**
   * Get confirmed transactions
   */
  async getConfirmedTransactions(): Promise<any[]> {
    try {
      if (!this.walletManager) {
        return [];
      }
      
      const transactions = await this.walletManager.getExecutedTransactions();
      
      // Format for UI
      return transactions.map(tx => ({
        id: tx.id,
        to: tx.to,
        value: ethers.formatEther(tx.value),
        submittedBy: tx.submittedBy,
        submittedAt: new Date(tx.submittedAt * 1000).toISOString(),
        executedAt: new Date().toISOString(),
        confirmations: tx.confirmations.length
      }));
      
    } catch (error) {
      console.error('Failed to get confirmed transactions:', error);
      return [];
    }
  }

  /**
   * Get wallet owners
   */
  async getOwners(): Promise<any[]> {
    try {
      if (!this.walletManager) {
        return [];
      }
      
      return await this.walletManager.getOwners();
      
    } catch (error) {
      console.error('Failed to get owners:', error);
      return [];
    }
  }

  /**
   * Get spending status
   */
  async getSpendingStatus(): Promise<any> {
    try {
      if (!this.walletManager) {
        return null;
      }
      
      return await this.spendingLimits.getSpendingStatus(this.walletManager.wallet.address);
      
    } catch (error) {
      console.error('Failed to get spending status:', error);
      return null;
    }
  }

  /**
   * Get security configuration
   */
  getSecurityConfig(): any {
    return this.securityManager.getSecurityConfig();
  }

  /**
   * Update security level
   */
  async updateSecurityLevel(level: string): Promise<void> {
    try {
      await this.securityManager.updateSecurityLevel(level as any);
      this.emit('securityConfigUpdated', level);
      console.log('Security level updated:', level);
      
    } catch (error) {
      throw new Error(`Failed to update security level: ${error}`);
    }
  }

  /**
   * Create governance proposal
   */
  async createProposal(proposal: {
    title: string;
    description: string;
    actions: any[];
    votingPeriod?: number;
    emergency?: boolean;
  }): Promise<string> {
    try {
      if (!this.governanceManager) {
        throw new Error('Governance manager not initialized');
      }
      
      const proposalId = await this.governanceManager.createProposal(
        proposal.title,
        proposal.description,
        proposal.actions,
        proposal.votingPeriod,
        proposal.emergency
      );
      
      this.emit('proposalCreated', { proposalId, proposal });
      console.log('Proposal created:', proposalId);
      return proposalId;
      
    } catch (error) {
      throw new Error(`Failed to create proposal: ${error}`);
    }
  }

  /**
   * Cast vote on proposal
   */
  async castVote(proposalId: string, support: number, weight?: string): Promise<void> {
    try {
      if (!this.governanceManager) {
        throw new Error('Governance manager not initialized');
      }
      
      await this.governanceManager.castVote(
        proposalId,
        support,
        weight ? ethers.parseEther(weight) : undefined
      );
      
      this.emit('voteCast', { proposalId, support });
      console.log('Vote cast:', proposalId, support);
      
    } catch (error) {
      throw new Error(`Failed to cast vote: ${error}`);
    }
  }

  /**
   * Get current state
   */
  getState(): WalletState {
    return { ...this.state };
  }

  /**
   * Subscribe to events
   */
  on(event: string, callback: Function): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event)!.push(callback);
  }

  /**
   * Unsubscribe from events
   */
  off(event: string, callback: Function): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  /**
   * Get transaction history with filtering and pagination
   */
  async getTransactionHistory(options: {
    page?: number;
    limit?: number;
    status?: 'pending' | 'confirmed' | 'executed';
    fromDate?: Date;
    toDate?: Date;
    category?: string;
  } = {}): Promise<{
    transactions: any[];
    total: number;
    page: number;
    totalPages: number;
  }> {
    try {
      if (!this.walletManager) {
        return { transactions: [], total: 0, page: 1, totalPages: 0 };
      }

      let allTransactions = [];
      
      // Get transactions based on status
      switch (options.status) {
        case 'pending':
          allTransactions = await this.walletManager.getPendingTransactions();
          break;
        case 'executed':
          allTransactions = await this.walletManager.getExecutedTransactions();
          break;
        default:
          const pending = await this.walletManager.getPendingTransactions();
          const executed = await this.walletManager.getExecutedTransactions();
          allTransactions = [...pending, ...executed];
      }

      // Apply date filters
      if (options.fromDate || options.toDate) {
        allTransactions = allTransactions.filter(tx => {
          const txDate = new Date(tx.submittedAt * 1000);
          if (options.fromDate && txDate < options.fromDate) return false;
          if (options.toDate && txDate > options.toDate) return false;
          return true;
        });
      }

      // Apply category filter (if implemented)
      if (options.category) {
        // Filter by category logic would go here
      }

      // Sort by date (newest first)
      allTransactions.sort((a, b) => b.submittedAt - a.submittedAt);

      // Pagination
      const page = options.page || 1;
      const limit = options.limit || 10;
      const total = allTransactions.length;
      const startIndex = (page - 1) * limit;
      const endIndex = startIndex + limit;
      const paginatedTransactions = allTransactions.slice(startIndex, endIndex);

      // Format for UI
      const formattedTransactions = paginatedTransactions.map(tx => ({
        id: tx.id,
        to: tx.to,
        value: ethers.formatEther(tx.value),
        submittedBy: tx.submittedBy,
        submittedAt: new Date(tx.submittedAt * 1000).toISOString(),
        status: tx.status,
        confirmations: tx.confirmations.length,
        required: tx.required,
        deadline: tx.deadline ? new Date(tx.deadline * 1000).toISOString() : null
      }));

      return {
        transactions: formattedTransactions,
        total,
        page,
        totalPages: Math.ceil(total / limit)
      };

    } catch (error) {
      console.error('Failed to get transaction history:', error);
      return { transactions: [], total: 0, page: 1, totalPages: 0 };
    }
  }

  /**
   * Export wallet data
   */
  async exportWalletData(format: 'json' | 'csv' = 'json'): Promise<string> {
    try {
      const data = {
        wallet: this.state.wallet,
        owners: await this.getOwners(),
        pendingTransactions: await this.getPendingTransactions(),
        confirmedTransactions: await this.getConfirmedTransactions(),
        spendingStatus: await this.getSpendingStatus(),
        securityConfig: this.getSecurityConfig(),
        exportedAt: new Date().toISOString()
      };

      if (format === 'csv') {
        // Convert to CSV format
        return this.convertToCSV(data);
      } else {
        return JSON.stringify(data, null, 2);
      }

    } catch (error) {
      throw new Error(`Failed to export wallet data: ${error}`);
    }
  }

  /**
   * Private helper methods
   */
  private async initializeManagers(): Promise<void> {
    if (!this.state.wallet) return;

    // Initialize key manager
    await this.keyManager.initialize();

    // Set up security manager
    // await this.securityManager.initialize();

    // Initialize governance if wallet is set
    // This would be done after wallet creation/loading
  }

  private async loadWalletState(): Promise<void> {
    if (!this.walletManager) return;

    try {
      // Load wallet data
      const [owners, pending, confirmed, balance] = await Promise.all([
        this.getOwners(),
        this.getPendingTransactions(),
        this.getConfirmedTransactions(),
        this.getBalance()
      ]);

      this.state.owners = owners;
      this.state.pendingTransactions = pending;
      this.state.confirmedTransactions = confirmed;
      this.state.balances.set('ETH', balance);

      // Load spending limits
      this.state.spendingLimits = await this.getSpendingStatus();

      // Load security config
      this.state.securityConfig = this.getSecurityConfig();

      this.emit('walletStateLoaded', this.state);

    } catch (error) {
      console.error('Failed to load wallet state:', error);
      throw error;
    }
  }

  private setupEventListeners(): void {
    // Listen to MetaMask events
    if (window.ethereum) {
      window.ethereum.on('accountsChanged', (accounts: string[]) => {
        if (accounts.length === 0) {
          this.disconnect();
        } else {
          // Account changed
          window.location.reload();
        }
      });

      window.ethereum.on('chainChanged', () => {
        // Chain changed
        window.location.reload();
      });
    }
  }

  private emit(event: string, data: any): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Event listener error for ${event}:`, error);
        }
      });
    }
  }

  private convertToCSV(data: any): string {
    // Simple CSV conversion for transaction data
    const transactions = [
      ...data.pendingTransactions,
      ...data.confirmedTransactions
    ];

    if (transactions.length === 0) {
      return 'No transactions to export';
    }

    const headers = ['ID', 'To', 'Value', 'Status', 'Submitted By', 'Submitted At', 'Confirmations'];
    const rows = transactions.map((tx: any) => [
      tx.id,
      tx.to,
      tx.value,
      tx.status || 'pending',
      tx.submittedBy,
      tx.submittedAt,
      tx.confirmations || 0
    ]);

    return [headers, ...rows]
      .map(row => row.map(cell => `"${cell}"`).join(','))
      .join('\n');
  }
}