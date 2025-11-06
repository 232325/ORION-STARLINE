/**
 * @class WalletManager
 * @dev Multi-signature wallet management system
 * @author MultiSig Wallet System
 */

import Web3 from 'web3';
import { ethers } from 'ethers';
import { GnosisSafe } from './gnosis/GnosisSafe';
import { CustomMultiSig } from './custom/CustomMultiSig';
import { SecurityManager } from './security/SecurityManager';
import { GovernanceManager } from './governance/GovernanceManager';
import { KeyManager } from './key-management/KeyManager';
import { SpendingLimits } from './limits/SpendingLimits';

export interface WalletConfig {
  owners: string[];
  threshold: number;
  dailyLimit?: bigint;
  weeklyLimit?: bigint;
  monthlyLimit?: bigint;
  timeLock?: number;
  emergencyAccess?: string[];
  metadata?: Record<string, any>;
}

export interface Transaction {
  id: string;
  to: string;
  value: bigint;
  data: string;
  operation: number;
  submittedBy: string;
  submittedAt: number;
  confirmations: Confirmation[];
  status: TransactionStatus;
  deadline?: number;
  gasLimit?: number;
  gasPrice?: bigint;
}

export interface Confirmation {
  owner: string;
  timestamp: number;
  signature?: string;
}

export enum TransactionStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed',
  EXECUTED = 'executed',
  REJECTED = 'rejected',
  CANCELLED = 'cancelled'
}

export interface SpendingLimit {
  type: 'daily' | 'weekly' | 'monthly' | 'single';
  amount: bigint;
  used: bigint;
  resetTime: number;
}

export interface Owner {
  address: string;
  confirmed: boolean;
  lastSeen?: number;
  metadata?: Record<string, any>;
}

export class WalletManager {
  private web3: Web3;
  private provider: ethers.JsonRpcProvider;
  private signer: ethers.Signer;
  private wallet: ethers.Contract;
  private config: WalletConfig;
  private securityManager: SecurityManager;
  private governanceManager: GovernanceManager;
  private keyManager: KeyManager;
  private spendingLimits: SpendingLimits;

  constructor(
    web3Provider: Web3 | ethers.JsonRpcProvider,
    walletAddress: string,
    config: WalletConfig
  ) {
    this.web3 = web3Provider instanceof Web3 ? web3Provider : new Web3(web3Provider as any);
    this.provider = new ethers.JsonRpcProvider(web3Provider as string);
    this.signer = this.provider.getSigner();
    
    // Initialize managers
    this.securityManager = new SecurityManager(web3Provider);
    this.governanceManager = new GovernanceManager(web3Provider);
    this.keyManager = new KeyManager();
    this.spendingLimits = new SpendingLimits();
    
    this.config = config;
    this.initializeWallet(walletAddress);
  }

  private async initializeWallet(walletAddress: string): Promise<void> {
    try {
      // Check if it's a Gnosis Safe or custom multi-sig
      const isGnosisSafe = await this.checkGnosisSafe(walletAddress);
      
      if (isGnosisSafe) {
        this.wallet = new ethers.Contract(walletAddress, GnosisSafe.ABI, this.signer);
      } else {
        this.wallet = new ethers.Contract(walletAddress, CustomMultiSig.ABI, this.signer);
      }
      
      // Load wallet configuration
      await this.loadConfiguration();
      
    } catch (error) {
      throw new Error(`Failed to initialize wallet: ${error}`);
    }
  }

  /**
   * Create new multi-signature wallet
   */
  static async createWallet(
    provider: Web3 | ethers.JsonRpcProvider,
    config: WalletConfig
  ): Promise<WalletManager> {
    try {
      const web3 = provider instanceof Web3 ? provider : new Web3(provider as any);
      const ethersProvider = new ethers.JsonRpcProvider(provider as string);
      const signer = ethersProvider.getSigner();
      
      // Deploy appropriate wallet contract based on configuration
      let walletAddress: string;
      
      if (config.owners.length <= 50) { // Gnosis Safe limit
        const factory = new ethers.Contract(
          GnosisSafe.FACTORY_ADDRESS,
          GnosisSafe.FACTORY_ABI,
          signer
        );
        
        const tx = await factory.createSafe(
          config.owners,
          config.threshold,
          config.dailyLimit || BigInt(0),
          config.weeklyLimit || BigInt(0),
          config.monthlyLimit || BigInt(0),
          config.timeLock || 0,
          ethers.encodeBytes32String('metadata')
        );
        
        const receipt = await tx.wait();
        walletAddress = receipt.logs[0].address; // Extract from logs
      } else {
        const factory = new ethers.Contract(
          CustomMultiSig.FACTORY_ADDRESS,
          CustomMultiSig.FACTORY_ABI,
          signer
        );
        
        const tx = await factory.createSafe(
          config.owners,
          config.threshold,
          config.dailyLimit || BigInt(0),
          config.weeklyLimit || BigInt(0),
          config.monthlyLimit || BigInt(0)
        );
        
        const receipt = await tx.wait();
        walletAddress = receipt.logs[0].address; // Extract from logs
      }
      
      return new WalletManager(provider, walletAddress, config);
      
    } catch (error) {
      throw new Error(`Failed to create wallet: ${error}`);
    }
  }

  /**
   * Submit transaction for approval
   */
  async submitTransaction(
    to: string,
    value: bigint,
    data: string = '0x',
    operation: number = 0,
    deadline?: number
  ): Promise<string> {
    try {
      // Validate transaction
      await this.validateTransaction(to, value, data, operation);
      
      // Generate transaction ID
      const txId = this.generateTransactionId(to, value, data, operation);
      
      // Submit to contract
      const tx = await this.wallet.submitTransaction(to, value, data, operation, deadline);
      const receipt = await tx.wait();
      
      // Log transaction
      console.log(`Transaction submitted: ${txId}`, receipt);
      
      return txId;
      
    } catch (error) {
      throw new Error(`Failed to submit transaction: ${error}`);
    }
  }

  /**
   * Confirm transaction
   */
  async confirmTransaction(txId: string, signature?: string): Promise<void> {
    try {
      // Verify transaction exists and is pending
      const transaction = await this.getTransaction(txId);
      if (!transaction || transaction.status !== TransactionStatus.PENDING) {
        throw new Error('Transaction not found or not pending');
      }
      
      // Check if already confirmed
      const myAddress = await this.signer.getAddress();
      const alreadyConfirmed = await this.wallet.confirmations(myAddress, txId);
      if (alreadyConfirmed) {
        throw new Error('Transaction already confirmed');
      }
      
      // Confirm transaction
      const tx = await this.wallet.confirmTransaction(txId);
      await tx.wait();
      
      // Update transaction status
      await this.updateTransactionStatus(txId);
      
      console.log(`Transaction confirmed: ${txId}`);
      
    } catch (error) {
      throw new Error(`Failed to confirm transaction: ${error}`);
    }
  }

  /**
   * Execute transaction (if enough confirmations)
   */
  async executeTransaction(txId: string): Promise<string> {
    try {
      const transaction = await this.getTransaction(txId);
      if (!transaction) {
        throw new Error('Transaction not found');
      }
      
      // Check if ready to execute
      const required = await this.getRequiredConfirmations();
      const confirmed = transaction.confirmations.length;
      
      if (confirmed < required) {
        throw new Error(`Not enough confirmations. Required: ${required}, Got: ${confirmed}`);
      }
      
      // Execute transaction
      const tx = await this.wallet.executeTransaction(txId);
      const receipt = await tx.wait();
      
      // Update status
      await this.updateTransactionStatus(txId, TransactionStatus.EXECUTED);
      
      console.log(`Transaction executed: ${txId}`, receipt.hash);
      return receipt.hash;
      
    } catch (error) {
      throw new Error(`Failed to execute transaction: ${error}`);
    }
  }

  /**
   * Cancel pending transaction
   */
  async cancelTransaction(txId: string): Promise<void> {
    try {
      const transaction = await this.getTransaction(txId);
      if (!transaction || transaction.status !== TransactionStatus.PENDING) {
        throw new Error('Transaction not found or not pending');
      }
      
      // Check permissions
      const myAddress = await this.signer.getAddress();
      if (transaction.submittedBy !== myAddress && !(await this.isOwner(myAddress))) {
        throw new Error('Insufficient permissions to cancel');
      }
      
      const tx = await this.wallet.cancelTransaction(txId);
      await tx.wait();
      
      await this.updateTransactionStatus(txId, TransactionStatus.CANCELLED);
      
      console.log(`Transaction cancelled: ${txId}`);
      
    } catch (error) {
      throw new Error(`Failed to cancel transaction: ${error}`);
    }
  }

  /**
   * Get wallet balance
   */
  async getBalance(): Promise<bigint> {
    try {
      return await this.provider.getBalance(this.wallet.address);
    } catch (error) {
      throw new Error(`Failed to get balance: ${error}`);
    }
  }

  /**
   * Get transaction details
   */
  async getTransaction(txId: string): Promise<Transaction | null> {
    try {
      const tx = await this.wallet.transactions(txId);
      
      if (tx.to === ethers.ZeroAddress) {
        return null; // Transaction doesn't exist
      }
      
      const confirmations = await this.getTransactionConfirmations(txId);
      const status = await this.getTransactionStatus(txId);
      
      return {
        id: txId,
        to: tx.to,
        value: tx.value,
        data: tx.data,
        operation: tx.operation,
        submittedBy: tx.submitter,
        submittedAt: tx.submittedAt,
        confirmations,
        status,
        deadline: tx.deadline
      };
      
    } catch (error) {
      throw new Error(`Failed to get transaction: ${error}`);
    }
  }

  /**
   * Get pending transactions
   */
  async getPendingTransactions(): Promise<Transaction[]> {
    try {
      const txIds = await this.wallet.getTransactionIds(true, false);
      const transactions: Transaction[] = [];
      
      for (const txId of txIds) {
        const tx = await this.getTransaction(txId);
        if (tx) {
          transactions.push(tx);
        }
      }
      
      return transactions;
      
    } catch (error) {
      throw new Error(`Failed to get pending transactions: ${error}`);
    }
  }

  /**
   * Get executed transactions
   */
  async getExecutedTransactions(): Promise<Transaction[]> {
    try {
      const txIds = await this.wallet.getTransactionIds(false, true);
      const transactions: Transaction[] = [];
      
      for (const txId of txIds) {
        const tx = await this.getTransaction(txId);
        if (tx) {
          transactions.push(tx);
        }
      }
      
      return transactions;
      
    } catch (error) {
      throw new Error(`Failed to get executed transactions: ${error}`);
    }
  }

  /**
   * Get wallet owners
   */
  async getOwners(): Promise<Owner[]> {
    try {
      const owners = await this.wallet.getOwners();
      const ownerList: Owner[] = [];
      
      for (const owner of owners) {
        const confirmed = await this.wallet.isOwner(owner);
        ownerList.push({
          address: owner,
          confirmed
        });
      }
      
      return ownerList;
      
    } catch (error) {
      throw new Error(`Failed to get owners: ${error}`);
    }
  }

  /**
   * Check if address is owner
   */
  async isOwner(address: string): Promise<boolean> {
    try {
      return await this.wallet.isOwner(address);
    } catch (error) {
      throw new Error(`Failed to check ownership: ${error}`);
    }
  }

  /**
   * Add new owner
   */
  async addOwner(address: string): Promise<string> {
    try {
      const tx = await this.wallet.addOwner(address);
      const receipt = await tx.wait();
      
      console.log(`Owner added: ${address}`, receipt.hash);
      return receipt.hash;
      
    } catch (error) {
      throw new Error(`Failed to add owner: ${error}`);
    }
  }

  /**
   * Remove owner
   */
  async removeOwner(address: string): Promise<string> {
    try {
      const tx = await this.wallet.removeOwner(address);
      const receipt = await tx.wait();
      
      console.log(`Owner removed: ${address}`, receipt.hash);
      return receipt.hash;
      
    } catch (error) {
      throw new Error(`Failed to remove owner: ${error}`);
    }
  }

  /**
   * Change required confirmations
   */
  async changeRequirement(required: number): Promise<string> {
    try {
      const tx = await this.wallet.changeRequirement(required);
      const receipt = await tx.wait();
      
      console.log(`Requirement changed to: ${required}`, receipt.hash);
      return receipt.hash;
      
    } catch (error) {
      throw new Error(`Failed to change requirement: ${error}`);
    }
  }

  /**
   * Activate emergency mode
   */
  async activateEmergencyMode(): Promise<void> {
    try {
      const tx = await this.securityManager.activateEmergencyMode(this.wallet.address);
      await tx.wait();
      
      console.log('Emergency mode activated');
      
    } catch (error) {
      throw new Error(`Failed to activate emergency mode: ${error}`);
    }
  }

  /**
   * Private helper methods
   */
  private async checkGnosisSafe(walletAddress: string): Promise<boolean> {
    try {
      // Check if contract implements Gnosis Safe interface
      const code = await this.provider.getCode(walletAddress);
      return code !== '0x' && code.length > 2;
    } catch {
      return false;
    }
  }

  private async validateTransaction(
    to: string,
    value: bigint,
    data: string,
    operation: number
  ): Promise<void> {
    // Check spending limits
    const validLimits = await this.spendingLimits.validateTransaction(
      this.wallet.address,
      value
    );
    if (!validLimits) {
      throw new Error('Transaction exceeds spending limits');
    }
    
    // Check security restrictions
    const securityValid = await this.securityManager.validateTransaction(
      this.wallet.address,
      to,
      value,
      data
    );
    if (!securityValid.valid) {
      throw new Error(`Security validation failed: ${securityValid.reason}`);
    }
    
    // Check balance
    const balance = await this.getBalance();
    if (balance < value) {
      throw new Error('Insufficient balance');
    }
  }

  private generateTransactionId(
    to: string,
    value: bigint,
    data: string,
    operation: number
  ): string {
    const timestamp = Date.now();
    return ethers.solidityPackedKeccak256(
      ['address', 'uint256', 'bytes', 'uint8', 'uint256'],
      [to, value, data, operation, timestamp]
    );
  }

  private async loadConfiguration(): Promise<void> {
    // Load security configuration
    await this.securityManager.loadConfig(this.wallet.address);
    
    // Load governance configuration
    await this.governanceManager.loadConfig(this.wallet.address);
    
    // Initialize spending limits tracking
    await this.spendingLimits.loadHistory(this.wallet.address);
  }

  private async getRequiredConfirmations(): Promise<number> {
    return await this.wallet.required();
  }

  private async getTransactionConfirmations(txId: string): Promise<Confirmation[]> {
    // Implementation would depend on specific contract structure
    // This is a simplified version
    return [];
  }

  private async getTransactionStatus(txId: string): Promise<TransactionStatus> {
    const tx = await this.wallet.transactions(txId);
    if (tx.executed) {
      return TransactionStatus.EXECUTED;
    } else if (tx.confirmations >= await this.getRequiredConfirmations()) {
      return TransactionStatus.CONFIRMED;
    } else {
      return TransactionStatus.PENDING;
    }
  }

  private async updateTransactionStatus(
    txId: string,
    status?: TransactionStatus
  ): Promise<void> {
    // Update local state or notify listeners
    // This would typically trigger events for UI updates
  }
}