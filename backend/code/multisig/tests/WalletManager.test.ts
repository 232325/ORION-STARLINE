/**
 * @class WalletManagerTest
 * @dev Test suite for WalletManager
 * @author MultiSig Wallet System
 */

import { WalletManager, type WalletConfig } from '../core/wallet/WalletManager';
import { SpendingLimits } from '../core/limits/SpendingLimits';
import { SecurityManager } from '../security/auth/SecurityManager';
import { ethers } from 'ethers';

describe('WalletManager', () => {
  let walletManager: WalletManager;
  let mockProvider: jest.Mocked<ethers.JsonRpcProvider>;
  let mockSigner: jest.Mocked<ethers.Signer>;
  let mockWallet: jest.Mocked<ethers.Contract>;

  beforeEach(() => {
    // Setup mock provider
    mockProvider = {
      getNetwork: jest.fn().mockResolvedValue({ chainId: 1 }),
      getBalance: jest.fn().mockResolvedValue(ethers.parseEther('10')),
      getCode: jest.fn().mockResolvedValue('0x1234'),
      send: jest.fn()
    } as any;

    // Setup mock signer
    mockSigner = {
      getAddress: jest.fn().mockResolvedValue('0x1234567890123456789012345678901234567890'),
      signTransaction: jest.fn(),
      signMessage: jest.fn()
    } as any;

    // Setup mock wallet contract
    mockWallet = {
      address: '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
      isOwner: jest.fn().mockResolvedValue(true),
      submitTransaction: jest.fn().mockResolvedValue('0x1234'),
      confirmTransaction: jest.fn().mockResolvedValue(void 0),
      executeTransaction: jest.fn().mockResolvedValue('0x5678'),
      getTransactionIds: jest.fn().mockResolvedValue([]),
      transactions: jest.fn().mockReturnValue({
        to: ethers.ZeroAddress,
        value: 0n,
        data: '0x',
        operation: 0,
        executed: false,
        submittedBy: '0x1234',
        submittedAt: Math.floor(Date.now() / 1000),
        confirmations: 0
      }),
      getOwners: jest.fn().mockResolvedValue([
        '0x1234567890123456789012345678901234567890',
        '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd'
      ]),
      required: jest.fn().mockResolvedValue(2),
      addOwner: jest.fn().mockResolvedValue(void 0),
      removeOwner: jest.fn().mockResolvedValue(void 0),
      changeRequirement: jest.fn().mockResolvedValue(void 0)
    } as any;

    // Create wallet manager instance
    walletManager = new WalletManager(
      mockProvider,
      mockWallet.address,
      {
        owners: ['0x1234567890123456789012345678901234567890'],
        threshold: 1
      }
    );
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('createWallet', () => {
    it('should create a new multi-signature wallet', async () => {
      const config: WalletConfig = {
        owners: [
          '0x1234567890123456789012345678901234567890',
          '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd'
        ],
        threshold: 2,
        dailyLimit: ethers.parseEther('1'),
        weeklyLimit: ethers.parseEther('10'),
        monthlyLimit: ethers.parseEther('50')
      };

      const wallet = await WalletManager.createWallet(mockProvider, config);
      
      expect(wallet).toBeInstanceOf(WalletManager);
      expect(wallet['wallet'].address).toBeDefined();
    });

    it('should throw error for invalid threshold', async () => {
      const config: WalletConfig = {
        owners: ['0x1234567890123456789012345678901234567890'],
        threshold: 2, // Invalid: threshold > owners
        dailyLimit: ethers.parseEther('1')
      };

      await expect(
        WalletManager.createWallet(mockProvider, config)
      ).rejects.toThrow('Invalid threshold');
    });

    it('should throw error for zero threshold', async () => {
      const config: WalletConfig = {
        owners: [
          '0x1234567890123456789012345678901234567890',
          '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd'
        ],
        threshold: 0, // Invalid: threshold must be > 0
        dailyLimit: ethers.parseEther('1')
      };

      await expect(
        WalletManager.createWallet(mockProvider, config)
      ).rejects.toThrow('Invalid threshold');
    });
  });

  describe('submitTransaction', () => {
    it('should submit a valid transaction', async () => {
      const txId = await walletManager.submitTransaction(
        '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
        ethers.parseEther('0.1'),
        '0x',
        0
      );

      expect(txId).toBeDefined();
      expect(typeof txId).toBe('string');
    });

    it('should throw error for invalid transaction', async () => {
      await expect(
        walletManager.submitTransaction(
          ethers.ZeroAddress, // Invalid: zero address
          ethers.parseEther('0.1'),
          '0x',
          0
        )
      ).rejects.toThrow('Invalid destination');
    });

    it('should throw error when exceeding spending limits', async () => {
      // Mock spending limits to reject
      jest.spyOn(walletManager['spendingLimits'], 'validateTransaction')
        .mockResolvedValue(false);

      await expect(
        walletManager.submitTransaction(
          '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
          ethers.parseEther('100'), // Exceeds limits
          '0x',
          0
        )
      ).rejects.toThrow('Exceeds spending limits');
    });
  });

  describe('confirmTransaction', () => {
    it('should confirm a pending transaction', async () => {
      const txId = '0x1234567890123456789012345678901234567890';
      
      // Mock transaction exists and is pending
      mockWallet.transactions.mockReturnValue({
        to: '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
        value: ethers.parseEther('0.1'),
        data: '0x',
        operation: 0,
        executed: false,
        submittedBy: '0x1234',
        submittedAt: Math.floor(Date.now() / 1000),
        confirmations: 0
      });
      mockWallet.confirmations.mockReturnValue(false);

      await walletManager.confirmTransaction(txId);

      expect(mockWallet.confirmTransaction).toHaveBeenCalledWith(txId);
    });

    it('should throw error when transaction already confirmed', async () => {
      const txId = '0x1234567890123456789012345678901234567890';
      
      // Mock transaction already confirmed by current owner
      mockWallet.confirmations.mockReturnValue(true);

      await expect(
        walletManager.confirmTransaction(txId)
      ).rejects.toThrow('Transaction already confirmed');
    });
  });

  describe('executeTransaction', () => {
    it('should execute a transaction with sufficient confirmations', async () => {
      const txId = '0x1234567890123456789012345678901234567890';
      
      // Mock sufficient confirmations
      mockWallet.transactions.mockReturnValue({
        to: '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
        value: ethers.parseEther('0.1'),
        data: '0x',
        operation: 0,
        executed: false,
        submittedBy: '0x1234',
        submittedAt: Math.floor(Date.now() / 1000),
        confirmations: 2
      });
      mockWallet.required.mockResolvedValue(2);

      const txHash = await walletManager.executeTransaction(txId);

      expect(txHash).toBeDefined();
      expect(txHash).toBe('0x5678');
    });

    it('should throw error when not enough confirmations', async () => {
      const txId = '0x1234567890123456789012345678901234567890';
      
      // Mock insufficient confirmations
      mockWallet.transactions.mockReturnValue({
        to: '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
        value: ethers.parseEther('0.1'),
        data: '0x',
        operation: 0,
        executed: false,
        submittedBy: '0x1234',
        submittedAt: Math.floor(Date.now() / 1000),
        confirmations: 1
      });
      mockWallet.required.mockResolvedValue(2);

      await expect(
        walletManager.executeTransaction(txId)
      ).rejects.toThrow('Not enough confirmations');
    });
  });

  describe('cancelTransaction', () => {
    it('should cancel a pending transaction', async () => {
      const txId = '0x1234567890123456789012345678901234567890';
      const mockMyAddress = '0x1234567890123456789012345678901234567890';
      
      mockSigner.getAddress.mockResolvedValue(mockMyAddress);
      mockWallet.transactions.mockReturnValue({
        to: '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
        value: ethers.parseEther('0.1'),
        data: '0x',
        operation: 0,
        executed: false,
        submittedBy: mockMyAddress, // Current user submitted it
        submittedAt: Math.floor(Date.now() / 1000),
        confirmations: 0
      });

      await walletManager.cancelTransaction(txId);

      expect(mockWallet.cancelTransaction).toHaveBeenCalledWith(txId);
    });

    it('should throw error when canceling non-submitter transaction', async () => {
      const txId = '0x1234567890123456789012345678901234567890';
      const mockMyAddress = '0x1234567890123456789012345678901234567890';
      const otherUser = '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd';
      
      mockSigner.getAddress.mockResolvedValue(mockMyAddress);
      mockWallet.transactions.mockReturnValue({
        to: '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
        value: ethers.parseEther('0.1'),
        data: '0x',
        operation: 0,
        executed: false,
        submittedBy: otherUser, // Different user submitted
        submittedAt: Math.floor(Date.now() / 1000),
        confirmations: 0
      });

      await expect(
        walletManager.cancelTransaction(txId)
      ).rejects.toThrow('Insufficient permissions');
    });
  });

  describe('getBalance', () => {
    it('should return wallet balance', async () => {
      const balance = await walletManager.getBalance();
      
      expect(balance).toBe(ethers.parseEther('10'));
      expect(mockProvider.getBalance).toHaveBeenCalledWith(mockWallet.address);
    });
  });

  describe('getPendingTransactions', () => {
    it('should return list of pending transactions', async () => {
      const mockTxIds = ['0x1234', '0x5678'];
      mockWallet.getTransactionIds.mockResolvedValue(mockTxIds);

      // Mock transactions
      mockWallet.transactions
        .mockReturnValueOnce({
          to: '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
          value: ethers.parseEther('0.1'),
          data: '0x',
          operation: 0,
          executed: false,
          submittedBy: '0x1234',
          submittedAt: Math.floor(Date.now() / 1000),
          confirmations: 1
        })
        .mockReturnValueOnce({
          to: '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
          value: ethers.parseEther('0.2'),
          data: '0x',
          operation: 0,
          executed: false,
          submittedBy: '0x5678',
          submittedAt: Math.floor(Date.now() / 1000),
          confirmations: 0
        });

      const pendingTransactions = await walletManager.getPendingTransactions();

      expect(pendingTransactions).toHaveLength(2);
      expect(pendingTransactions[0].value).toBe('0.1');
      expect(pendingTransactions[1].value).toBe('0.2');
    });

    it('should return empty array when no pending transactions', async () => {
      mockWallet.getTransactionIds.mockResolvedValue([]);

      const pendingTransactions = await walletManager.getPendingTransactions();

      expect(pendingTransactions).toHaveLength(0);
    });
  });

  describe('getExecutedTransactions', () => {
    it('should return list of executed transactions', async () => {
      const mockTxIds = ['0xabcd'];
      mockWallet.getTransactionIds.mockResolvedValue(mockTxIds);

      mockWallet.transactions.mockReturnValue({
        to: '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
        value: ethers.parseEther('0.5'),
        data: '0x',
        operation: 0,
        executed: true, // Already executed
        submittedBy: '0x1234',
        submittedAt: Math.floor(Date.now() / 1000),
        confirmations: 2
      });

      const executedTransactions = await walletManager.getExecutedTransactions();

      expect(executedTransactions).toHaveLength(1);
      expect(executedTransactions[0].status).toBe('executed');
    });
  });

  describe('getOwners', () => {
    it('should return list of wallet owners', async () => {
      const owners = await walletManager.getOwners();

      expect(owners).toHaveLength(2);
      expect(owners[0].address).toBe('0x1234567890123456789012345678901234567890');
      expect(owners[1].address).toBe('0xabcdefabcdefabcdefabcdefabcdefabcdefabcd');
      expect(owners[0].confirmed).toBe(true);
      expect(owners[1].confirmed).toBe(true);
    });
  });

  describe('isOwner', () => {
    it('should return true for valid owner', async () => {
      const isOwner = await walletManager.isOwner('0x1234567890123456789012345678901234567890');
      expect(isOwner).toBe(true);
      expect(mockWallet.isOwner).toHaveBeenCalledWith('0x1234567890123456789012345678901234567890');
    });

    it('should return false for non-owner', async () => {
      mockWallet.isOwner.mockResolvedValue(false);
      
      const isOwner = await walletManager.isOwner('0x9999999999999999999999999999999999999999');
      expect(isOwner).toBe(false);
    });
  });

  describe('addOwner', () => {
    it('should add new owner to wallet', async () => {
      const newOwner = '0x9999999999999999999999999999999999999999';
      
      await walletManager.addOwner(newOwner);

      expect(mockWallet.addOwner).toHaveBeenCalledWith(newOwner);
    });
  });

  describe('removeOwner', () => {
    it('should remove owner from wallet', async () => {
      const ownerToRemove = '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd';
      
      await walletManager.removeOwner(ownerToRemove);

      expect(mockWallet.removeOwner).toHaveBeenCalledWith(ownerToRemove);
    });
  });

  describe('changeRequirement', () => {
    it('should change required confirmations', async () => {
      const newRequirement = 3;
      
      await walletManager.changeRequirement(newRequirement);

      expect(mockWallet.changeRequirement).toHaveBeenCalledWith(newRequirement);
    });
  });

  describe('activateEmergencyMode', () => {
    it('should activate emergency mode', async () => {
      // Mock security manager
      const securityManager = {
        activateEmergencyMode: jest.fn().mockResolvedValue(void 0)
      };
      
      walletManager['securityManager'] = securityManager as any;

      await walletManager.activateEmergencyMode();

      expect(securityManager.activateEmergencyMode).toHaveBeenCalled();
    });
  });
});

describe('Integration Tests', () => {
  describe('End-to-End Wallet Creation and Transaction', () => {
    it('should complete full wallet lifecycle', async () => {
      const mockProvider = {
        getNetwork: jest.fn().mockResolvedValue({ chainId: 1 }),
        getBalance: jest.fn().mockResolvedValue(ethers.parseEther('100'))
      } as any;

      const config: WalletConfig = {
        owners: [
          '0x1111111111111111111111111111111111111111',
          '0x2222222222222222222222222222222222222222',
          '0x3333333333333333333333333333333333333333'
        ],
        threshold: 2,
        dailyLimit: ethers.parseEther('5'),
        weeklyLimit: ethers.parseEther('50'),
        monthlyLimit: ethers.parseEther('200')
      };

      // Create wallet
      const wallet = await WalletManager.createWallet(mockProvider, config);
      expect(wallet).toBeInstanceOf(WalletManager);

      // Get initial balance
      const balance = await wallet.getBalance();
      expect(balance).toBe(ethers.parseEther('100'));

      // Submit transaction
      const txId = await wallet.submitTransaction(
        '0x4444444444444444444444444444444444444444',
        ethers.parseEther('1'),
        '0x',
        0
      );
      expect(txId).toBeDefined();

      // Get pending transactions
      const pending = await wallet.getPendingTransactions();
      expect(pending).toHaveLength(1);
      expect(pending[0].id).toBe(txId);

      // Get owners
      const owners = await wallet.getOwners();
      expect(owners).toHaveLength(3);
      expect(owners[0].confirmed).toBe(true);
    });
  });
});

describe('Error Handling', () => {
  it('should handle provider errors gracefully', async () => {
    const mockProvider = {
      getBalance: jest.fn().mockRejectedValue(new Error('Provider error'))
    } as any;

    const walletManager = new WalletManager(
      mockProvider,
      '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
      {
        owners: ['0x1234567890123456789012345678901234567890'],
        threshold: 1
      }
    );

    await expect(walletManager.getBalance()).rejects.toThrow('Provider error');
  });

  it('should handle invalid addresses', async () => {
    const mockProvider = {} as any;
    const walletManager = new WalletManager(
      mockProvider,
      'invalid-address', // Invalid address
      {
        owners: ['0x1234567890123456789012345678901234567890'],
        threshold: 1
      }
    );

    await expect(
      walletManager.submitTransaction(
        ethers.ZeroAddress,
        ethers.parseEther('0.1'),
        '0x',
        0
      )
    ).rejects.toThrow();
  });
});

describe('Performance Tests', () => {
  it('should handle large number of transactions efficiently', async () => {
    const startTime = Date.now();
    
    // Simulate many transaction operations
    for (let i = 0; i < 100; i++) {
      await walletManager.submitTransaction(
        '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
        ethers.parseEther('0.1'),
        '0x',
        0
      );
    }

    const endTime = Date.now();
    const duration = endTime - startTime;
    
    // Should complete within reasonable time (adjust as needed)
    expect(duration).toBeLessThan(5000); // 5 seconds
  });
});