/**
 * Multi-Signature Wallet Integration System
 * Example Usage
 * @author MultiSig Wallet System
 */

import { 
  Web3WalletIntegration, 
  MobileWallet, 
  ConfigurationManager,
  SecurityLevel,
  VoteType,
  type WalletConfig,
  type TransactionRequest,
  type SecurityConfig
} from './index';

// Example 1: Basic Web3 Wallet Setup
async function basicWalletExample() {
  console.log('=== Basic Wallet Example ===');
  
  // Initialize Web3 integration (assuming window.ethereum is available)
  const web3Integration = new Web3WalletIntegration(window);
  
  try {
    // Connect to wallet
    console.log('Connecting to wallet...');
    const wallet = await web3Integration.connect();
    console.log('Connected:', wallet.address);
    
    // Create new multi-sig wallet
    console.log('Creating multi-sig wallet...');
    const walletConfig: WalletConfig = {
      owners: [
        '0x1234567890123456789012345678901234567890',
        '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
        '0x9876543210987654321098765432109876543210'
      ],
      threshold: 2,
      dailyLimit: ethers.parseEther('1.0'),
      weeklyLimit: ethers.parseEther('10.0'),
      monthlyLimit: ethers.parseEther('50.0')
    };
    
    const walletAddress = await web3Integration.createMultiSigWallet(walletConfig);
    console.log('Multi-sig wallet created:', walletAddress);
    
    // Submit a transaction
    const txRequest: TransactionRequest = {
      to: '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
      value: '0.5',
      description: 'Test transaction'
    };
    
    console.log('Submitting transaction...');
    const txId = await web3Integration.submitTransaction(txRequest);
    console.log('Transaction submitted:', txId);
    
    // Confirm transaction
    console.log('Confirming transaction...');
    await web3Integration.confirmTransaction(txId);
    console.log('Transaction confirmed');
    
  } catch (error) {
    console.error('Error:', error);
  }
}

// Example 2: Security Configuration
async function securityExample() {
  console.log('=== Security Configuration Example ===');
  
  const configManager = new ConfigurationManager();
  
  // Configure security settings
  const securityConfig: SecurityConfig = {
    level: SecurityLevel.ENTERPRISE,
    mfa: {
      enabled: true,
      providers: ['totp', 'sms', 'push'],
      required: true
    },
    hardware: {
      required: true,
      supportedDevices: ['ledger', 'trezor']
    },
    spendingLimits: {
      daily: '0.1',
      weekly: '1.0',
      monthly: '10.0'
    },
    timeLocks: {
      transaction: 3600, // 1 hour
      configuration: 86400, // 24 hours
      emergency: 7200 // 2 hours
    },
    rateLimits: {
      transactions: {
        window: 3600,
        maxPerWindow: 5
      },
      apiCalls: {
        window: 3600,
        maxPerWindow: 50
      }
    },
    operatingHours: {
      enabled: true,
      timezone: 'UTC',
      hours: { start: 9, end: 17 },
      daysOfWeek: [1, 2, 3, 4, 5] // Mon-Fri
    }
  };
  
  // Update security configuration
  configManager.updateSecurityConfig(securityConfig);
  console.log('Security configuration updated');
  
  // Validate configuration
  const validation = configManager.validateConfig();
  console.log('Config valid:', validation.valid);
  if (!validation.valid) {
    console.log('Errors:', validation.errors);
  }
}

// Example 3: Governance Integration
async function governanceExample() {
  console.log('=== Governance Integration Example ===');
  
  const web3Integration = new Web3WalletIntegration(window);
  
  try {
    // Ensure wallet is connected
    const walletState = web3Integration.getState();
    if (!walletState.connected) {
      await web3Integration.connect();
    }
    
    // Load an existing governance-enabled wallet
    await web3Integration.loadMultiSigWallet('0xgovernance-wallet-address');
    
    // Create a governance proposal
    console.log('Creating governance proposal...');
    const proposalId = await web3Integration.createProposal({
      title: 'Update Daily Spending Limit',
      description: 'Reduce daily spending limit from 1 ETH to 0.5 ETH',
      actions: [
        {
          target: '0xsecurity-contract-address',
          value: '0',
          data: '0x-encoded-function-call-to-update-limit',
          description: 'Update spending limit configuration'
        }
      ],
      votingPeriod: 7 * 24 * 60 * 60, // 7 days
      emergency: false
    });
    
    console.log('Proposal created:', proposalId);
    
    // Cast a vote
    console.log('Casting vote...');
    await web3Integration.castVote(proposalId, VoteType.FOR, '1000');
    console.log('Vote cast successfully');
    
    // Get proposal details
    const governanceManager = web3Integration.governanceManager;
    const proposal = governanceManager.getProposal(proposalId);
    console.log('Proposal state:', proposal?.state);
    
  } catch (error) {
    console.error('Governance error:', error);
  }
}

// Example 4: Mobile Interface Setup
function mobileInterfaceExample() {
  console.log('=== Mobile Interface Example ===');
  
  // This would be used in a React Native or mobile web app
  const web3Integration = new Web3WalletIntegration(window);
  
  // Mobile wallet component would be used like this:
  /*
  import MobileWallet from './interface/mobile/MobileWallet';
  
  function MobileApp() {
    const [web3Integration, setWeb3Integration] = useState(null);
    
    useEffect(() => {
      const integration = new Web3WalletIntegration(window);
      setWeb3Integration(integration);
    }, []);
    
    return (
      <MobileWallet
        web3Integration={web3Integration}
        onTransactionSubmit={(txId) => {
          console.log('Transaction submitted:', txId);
          // Handle transaction submission
        }}
        onError={(error) => {
          console.error('Transaction error:', error);
          // Handle errors
        }}
        onSecurityAlert={(alert) => {
          console.warn('Security alert:', alert);
          // Handle security alerts
        }}
        onGovernanceUpdate={(proposal) => {
          console.log('Governance update:', proposal);
          // Handle governance updates
        }}
      />
    );
  }
  */
}

// Example 5: Key Management
async function keyManagementExample() {
  console.log('=== Key Management Example ===');
  
  const { KeyManager } = await import('./key-management/hsm/KeyManager');
  
  // Initialize key manager
  const keyManager = new KeyManager(window.web3, 'encryption-key-32-chars-long');
  await keyManager.initialize();
  
  try {
    // Generate new EOA key
    console.log('Generating new EOA key...');
    const eoaKey = await keyManager.generateKey('eoa', {
      purpose: 'transaction-signing',
      network: 'ethereum'
    });
    console.log('EOA key generated:', eoaKey.id);
    
    // Create backup
    console.log('Creating key backup...');
    const backup = await keyManager.createBackup(eoaKey.id, 'file', {
      location: 'secure-storage/keys',
      encryption: true
    });
    console.log('Backup created:', backup.id);
    
    // Set up social recovery
    console.log('Setting up social recovery...');
    await keyManager.setupSocialRecovery(
      eoaKey.id,
      [
        { 
          address: '0xrecovery-contact-1', 
          publicKey: '...', 
          confirmed: true,
          addedAt: Date.now()
        },
        { 
          address: '0xrecovery-contact-2', 
          publicKey: '...', 
          confirmed: true,
          addedAt: Date.now()
        },
        { 
          address: '0xrecovery-contact-3', 
          publicKey: '...', 
          confirmed: true,
          addedAt: Date.now()
        }
      ],
      2, // threshold
      24 * 60 * 60 // 24 hours delay
    );
    console.log('Social recovery configured');
    
    // Create threshold shares
    console.log('Creating threshold shares...');
    const holders = [
      '0xholder-1',
      '0xholder-2', 
      '0xholder-3',
      '0xholder-4'
    ];
    
    const shares = await keyManager.createThresholdShares(eoaKey.id, holders, 3);
    console.log('Threshold shares created:', shares.length);
    
  } catch (error) {
    console.error('Key management error:', error);
  }
}

// Example 6: Configuration Management
async function configurationExample() {
  console.log('=== Configuration Management Example ===');
  
  // Load custom configuration
  const configManager = new ConfigurationManager({
    security: {
      level: 'high',
      spendingLimits: {
        daily: '0.5',
        weekly: '5.0',
        monthly: '20.0'
      }
    },
    governance: {
      enabled: true,
      proposal: {
        threshold: '500',
        quorumPercentage: 25,
        votingPeriod: 86400 * 5 // 5 days
      }
    },
    ui: {
      theme: 'dark',
      currency: {
        display: 'both',
        default: 'usd'
      }
    }
  });
  
  // Export configuration
  console.log('Exporting configuration...');
  const configJson = configManager.exportConfig('json');
  const configYaml = configManager.exportConfig('yaml');
  
  console.log('Config (JSON):', configJson);
  console.log('Config (YAML):', configYaml);
  
  // Update configuration at runtime
  console.log('Updating configuration...');
  configManager.updateSecurityConfig({
    level: 'enterprise',
    hardware: {
      required: true
    }
  });
  
  // Get current configuration
  const currentConfig = configManager.getConfig();
  console.log('Current security level:', currentConfig.security.level);
  
  // Validate configuration
  const validation = configManager.validateConfig();
  console.log('Configuration valid:', validation.valid);
}

// Example 7: Transaction History and Analytics
async function analyticsExample() {
  console.log('=== Analytics Example ===');
  
  const web3Integration = new Web3WalletIntegration(window);
  
  try {
    // Ensure wallet is connected
    if (!web3Integration.getState().connected) {
      await web3Integration.connect();
    }
    
    // Get transaction history with filters
    console.log('Fetching transaction history...');
    const history = await web3Integration.getTransactionHistory({
      page: 1,
      limit: 20,
      status: 'executed',
      fromDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // Last 30 days
      toDate: new Date()
    });
    
    console.log('Transaction history:', {
      total: history.total,
      page: history.page,
      totalPages: history.totalPages,
      transactions: history.transactions.length
    });
    
    // Get spending analytics
    const spendingStatus = await web3Integration.getSpendingStatus();
    if (spendingStatus) {
      console.log('Spending status:', {
        daily: spendingStatus.limits.daily,
        weekly: spendingStatus.limits.weekly,
        monthly: spendingStatus.limits.monthly
      });
    }
    
    // Export wallet data
    console.log('Exporting wallet data...');
    const exportData = await web3Integration.exportWalletData('json');
    console.log('Exported data length:', exportData.length);
    
  } catch (error) {
    console.error('Analytics error:', error);
  }
}

// Example 8: Emergency Mode
async function emergencyModeExample() {
  console.log('=== Emergency Mode Example ===');
  
  const web3Integration = new Web3WalletIntegration(window);
  
  try {
    // Load wallet
    await web3Integration.loadMultiSigWallet('0xwallet-address');
    
    // Check if emergency access is available
    const securityManager = web3Integration.securityManager;
    const hasEmergencyAccess = securityManager.hasEmergencyAccess(
      '0xemergency-contact-address'
    );
    
    if (hasEmergencyAccess) {
      console.log('Emergency access available');
      
      // Use emergency access (requires unlock time to be reached)
      // await securityManager.useEmergencyAccess(targetAddress, value, data);
      
    } else {
      console.log('No emergency access available');
    }
    
    // Get security alerts
    const alerts = securityManager.getSecurityAlerts();
    console.log('Recent security alerts:', alerts.length);
    
    // Generate security report
    const securityReport = await securityManager.generateSecurityReport();
    console.log('Security report:', {
      level: securityReport.config.level,
      stats: securityReport.stats,
      recommendations: securityReport.recommendations
    });
    
  } catch (error) {
    console.error('Emergency mode error:', error);
  }
}

// Main execution function
async function main() {
  console.log('Multi-Signature Wallet Integration System Examples\n');
  
  try {
    // Run examples
    await basicWalletExample();
    console.log('\n' + '='.repeat(50) + '\n');
    
    await securityExample();
    console.log('\n' + '='.repeat(50) + '\n');
    
    await governanceExample();
    console.log('\n' + '='.repeat(50) + '\n');
    
    await keyManagementExample();
    console.log('\n' + '='.repeat(50) + '\n');
    
    await configurationExample();
    console.log('\n' + '='.repeat(50) + '\n');
    
    await analyticsExample();
    console.log('\n' + '='.repeat(50) + '\n');
    
    await emergencyModeExample();
    console.log('\n' + '='.repeat(50) + '\n');
    
    console.log('All examples completed successfully!');
    
  } catch (error) {
    console.error('Example execution error:', error);
  }
}

// Execute examples if this file is run directly
if (require.main === module) {
  main();
}

// Export examples for use in tests or documentation
export {
  basicWalletExample,
  securityExample,
  governanceExample,
  mobileInterfaceExample,
  keyManagementExample,
  configurationExample,
  analyticsExample,
  emergencyModeExample
};