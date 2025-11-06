/**
 * @class ConfigurationManager
 * @dev Configuration management for multi-signature wallet system
 * @author MultiSig Wallet System
 */

export interface NetworkConfig {
  chainId: number;
  name: string;
  rpcUrl: string;
  blockExplorerUrl: string;
  nativeCurrency: {
    name: string;
    symbol: string;
    decimals: number;
  };
  contracts: {
    gnosisSafeFactory?: string;
    customMultiSigFactory?: string;
    securityManager?: string;
    governance?: string;
    governanceToken?: string;
  };
  gasSettings: {
    gasPrice?: number;
    gasLimitMultiplier?: number;
  };
}

export interface SecurityConfig {
  level: 'basic' | 'standard' | 'high' | 'enterprise';
  mfa: {
    enabled: boolean;
    providers: string[];
    required: boolean;
  };
  hardware: {
    enabled: boolean;
    required: boolean;
    supportedDevices: string[];
  };
  spendingLimits: {
    daily: string;
    weekly: string;
    monthly: string;
    single: string;
  };
  timeLocks: {
    transaction: number; // seconds
    configuration: number; // seconds
    emergency: number; // seconds
  };
  rateLimits: {
    transactions: {
      window: number; // seconds
      maxPerWindow: number;
    };
    apiCalls: {
      window: number; // seconds
      maxPerWindow: number;
    };
  };
  operatingHours: {
    enabled: boolean;
    timezone: string;
    hours: {
      start: number; // 0-23
      end: number; // 0-23
    };
    daysOfWeek: number[]; // 0-6, Sunday = 0
  };
  notifications: {
    enabled: boolean;
    channels: ('email' | 'sms' | 'push' | 'webhook')[];
    security: {
      enabled: boolean;
      threshold: string; // transaction value threshold
    };
    transactions: {
      enabled: boolean;
      onSubmit: boolean;
      onConfirm: boolean;
      onExecute: boolean;
    };
  };
}

export interface GovernanceConfig {
  enabled: boolean;
  tokenContract: string;
  proposal: {
    threshold: string; // minimum token balance to create proposals
    votingDelay: number; // seconds before voting starts
    votingPeriod: number; // seconds
    timeLockPeriod: number; // seconds before execution
    quorumPercentage: number; // 0-100
  };
  emergency: {
    enabled: boolean;
    specialProposalThreshold: string;
    shorterVotingPeriod: number; // seconds
    emergencyQuorumPercentage: number; // 0-100
  };
  delegation: {
    enabled: boolean;
    allowDelegation: boolean;
    allowRevocation: boolean;
    requireDelegationConfirmation: boolean;
  };
  execution: {
    automatic: boolean;
    requireTimeLock: boolean;
    maxActionsPerProposal: number;
  };
}

export interface UIConfig {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  currency: {
    display: 'eth' | 'usd' | 'both';
    default: 'eth' | 'usd';
    exchangeRate?: number;
  };
  display: {
    showConfirmations: boolean;
    showTransactionHistory: boolean;
    transactionPerPage: number;
    compactMode: boolean;
  };
  mobile: {
    responsive: boolean;
    touchOptimized: boolean;
    biometricAuth: boolean;
  };
}

export interface KeyManagementConfig {
  encryption: {
    algorithm: 'aes-256-gcm' | 'aes-256-cbc';
    keyDerivation: 'pbkdf2' | 'scrypt' | 'argon2';
    iterations: number;
    saltLength: number;
  };
  backup: {
    enabled: boolean;
    methods: ('file' | 'cloud' | 'paper' | 'multisig')[];
    automaticInterval: number; // hours
    retentionPeriod: number; // days
    encryption: boolean;
  };
  hsm: {
    enabled: boolean;
    provider: 'aws' | 'azure' | 'gcp' | 'thales';
    region?: string;
    keyUsage: ('sign' | 'generate' | 'backup')[];
  };
  recovery: {
    socialEnabled: boolean;
    thresholdRequired: number;
    timeDelay: number; // hours
    maxAttempts: number;
  };
}

export interface ApplicationConfig {
  name: string;
  version: string;
  environment: 'development' | 'staging' | 'production';
  networks: {
    [chainId: number]: NetworkConfig;
  };
  security: SecurityConfig;
  governance: GovernanceConfig;
  ui: UIConfig;
  keyManagement: KeyManagementConfig;
  logging: {
    level: 'debug' | 'info' | 'warn' | 'error';
    enableFileLogging: boolean;
    enableConsoleLogging: boolean;
    enableRemoteLogging: boolean;
    maxLogFiles: number;
    maxLogSize: number; // MB
  };
  analytics: {
    enabled: boolean;
    trackingId?: string;
    anonymized: boolean;
  };
  features: {
    beta: string[];
    experimental: string[];
    deprecated: string[];
  };
}

export class ConfigurationManager {
  private config: ApplicationConfig;
  private defaultConfig: ApplicationConfig;
  private networkConfig: Map<number, NetworkConfig> = new Map();
  private customConfig: Partial<ApplicationConfig> = {};

  constructor(customConfig?: Partial<ApplicationConfig>) {
    this.customConfig = customConfig || {};
    this.defaultConfig = this.getDefaultConfig();
    this.config = this.mergeConfigs(this.defaultConfig, this.customConfig);
    this.initializeNetworkConfigs();
  }

  /**
   * Get current configuration
   */
  getConfig(): ApplicationConfig {
    return { ...this.config };
  }

  /**
   * Get network configuration by chain ID
   */
  getNetworkConfig(chainId: number): NetworkConfig | null {
    return this.networkConfig.get(chainId) || null;
  }

  /**
   * Get all supported networks
   */
  getSupportedNetworks(): NetworkConfig[] {
    return Array.from(this.networkConfig.values());
  }

  /**
   * Get security configuration
   */
  getSecurityConfig(): SecurityConfig {
    return { ...this.config.security };
  }

  /**
   * Get governance configuration
   */
  getGovernanceConfig(): GovernanceConfig {
    return { ...this.config.governance };
  }

  /**
   * Get UI configuration
   */
  getUIConfig(): UIConfig {
    return { ...this.config.ui };
  }

  /**
   * Get key management configuration
   */
  getKeyManagementConfig(): KeyManagementConfig {
    return { ...this.config.keyManagement };
  }

  /**
   * Update security configuration
   */
  updateSecurityConfig(updates: Partial<SecurityConfig>): void {
    this.config.security = { ...this.config.security, ...updates };
  }

  /**
   * Update governance configuration
   */
  updateGovernanceConfig(updates: Partial<GovernanceConfig>): void {
    this.config.governance = { ...this.config.governance, ...updates };
  }

  /**
   * Update UI configuration
   */
  updateUIConfig(updates: Partial<UIConfig>): void {
    this.config.ui = { ...this.config.ui, ...updates };
  }

  /**
   * Add custom network configuration
   */
  addNetworkConfig(config: NetworkConfig): void {
    this.networkConfig.set(config.chainId, config);
    this.config.networks[config.chainId] = config;
  }

  /**
   * Validate configuration
   */
  validateConfig(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Validate security configuration
    if (this.config.security.level && !['basic', 'standard', 'high', 'enterprise'].includes(this.config.security.level)) {
      errors.push('Invalid security level');
    }

    // Validate spending limits
    if (this.config.security.spendingLimits) {
      const limits = this.config.security.spendingLimits;
      if (parseFloat(limits.daily) < 0 || parseFloat(limits.weekly) < 0 || parseFloat(limits.monthly) < 0) {
        errors.push('Spending limits cannot be negative');
      }
    }

    // Validate operating hours
    if (this.config.security.operatingHours.enabled) {
      const hours = this.config.security.operatingHours.hours;
      if (hours.start < 0 || hours.start > 23 || hours.end < 0 || hours.end > 23) {
        errors.push('Operating hours must be between 0 and 23');
      }
    }

    // Validate governance configuration
    if (this.config.governance.enabled) {
      if (this.config.governance.proposal.quorumPercentage < 0 || 
          this.config.governance.proposal.quorumPercentage > 100) {
        errors.push('Quorum percentage must be between 0 and 100');
      }
    }

    // Validate time locks
    if (this.config.security.timeLocks.emergency < this.config.security.timeLocks.transaction) {
      errors.push('Emergency time lock cannot be shorter than transaction time lock');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Reset to default configuration
   */
  resetToDefaults(): void {
    this.config = { ...this.defaultConfig };
    this.initializeNetworkConfigs();
  }

  /**
   * Export configuration
   */
  exportConfig(format: 'json' | 'yaml' = 'json'): string {
    if (format === 'yaml') {
      return this.convertToYAML(this.config);
    } else {
      return JSON.stringify(this.config, null, 2);
    }
  }

  /**
   * Import configuration
   */
  importConfig(configData: string, format: 'json' | 'yaml' = 'json'): void {
    try {
      let importedConfig: Partial<ApplicationConfig>;
      
      if (format === 'yaml') {
        importedConfig = this.parseYAML(configData);
      } else {
        importedConfig = JSON.parse(configData);
      }
      
      // Validate imported configuration
      this.config = this.mergeConfigs(this.defaultConfig, importedConfig);
      const validation = this.validateConfig();
      
      if (!validation.valid) {
        throw new Error(`Configuration validation failed: ${validation.errors.join(', ')}`);
      }
      
      this.initializeNetworkConfigs();
      
    } catch (error) {
      throw new Error(`Failed to import configuration: ${error}`);
    }
  }

  /**
   * Get environment-specific configuration
   */
  getEnvironmentConfig(): Partial<ApplicationConfig> {
    switch (this.config.environment) {
      case 'development':
        return {
          logging: {
            ...this.config.logging,
            level: 'debug',
            enableConsoleLogging: true
          },
          analytics: {
            enabled: false
          }
        };
        
      case 'staging':
        return {
          logging: {
            ...this.config.logging,
            level: 'info',
            enableRemoteLogging: true
          },
          analytics: {
            enabled: true,
            anonymized: true
          }
        };
        
      case 'production':
        return {
          logging: {
            ...this.config.logging,
            level: 'warn',
            enableConsoleLogging: false,
            enableRemoteLogging: true
          },
          analytics: {
            enabled: true,
            anonymized: false
          },
          security: {
            ...this.config.security,
            level: 'high'
          }
        };
        
      default:
        return {};
    }
  }

  /**
   * Private helper methods
   */
  private getDefaultConfig(): ApplicationConfig {
    return {
      name: 'Multi-Signature Wallet',
      version: '1.0.0',
      environment: 'development',
      networks: {
        1: {
          chainId: 1,
          name: 'Ethereum Mainnet',
          rpcUrl: 'https://mainnet.infura.io/v3/YOUR_INFURA_KEY',
          blockExplorerUrl: 'https://etherscan.io',
          nativeCurrency: {
            name: 'Ether',
            symbol: 'ETH',
            decimals: 18
          },
          gasSettings: {
            gasPrice: 20,
            gasLimitMultiplier: 1.2
          }
        },
        5: {
          chainId: 5,
          name: 'Goerli Testnet',
          rpcUrl: 'https://goerli.infura.io/v3/YOUR_INFURA_KEY',
          blockExplorerUrl: 'https://goerli.etherscan.io',
          nativeCurrency: {
            name: 'Goerli Ether',
            symbol: 'ETH',
            decimals: 18
          },
          gasSettings: {
            gasPrice: 1,
            gasLimitMultiplier: 1.5
          }
        },
        137: {
          chainId: 137,
          name: 'Polygon Mainnet',
          rpcUrl: 'https://polygon-rpc.com',
          blockExplorerUrl: 'https://polygonscan.com',
          nativeCurrency: {
            name: 'MATIC',
            symbol: 'MATIC',
            decimals: 18
          },
          gasSettings: {
            gasPrice: 30,
            gasLimitMultiplier: 1.1
          }
        }
      },
      security: {
        level: 'standard',
        mfa: {
          enabled: true,
          providers: ['totp', 'sms', 'email'],
          required: false
        },
        hardware: {
          enabled: true,
          required: false,
          supportedDevices: ['ledger', 'trezor', 'keepkey']
        },
        spendingLimits: {
          daily: '1.0',
          weekly: '10.0',
          monthly: '50.0',
          single: '0.5'
        },
        timeLocks: {
          transaction: 3600, // 1 hour
          configuration: 86400, // 24 hours
          emergency: 7200 // 2 hours
        },
        rateLimits: {
          transactions: {
            window: 3600,
            maxPerWindow: 10
          },
          apiCalls: {
            window: 3600,
            maxPerWindow: 100
          }
        },
        operatingHours: {
          enabled: false,
          timezone: 'UTC',
          hours: {
            start: 9,
            end: 17
          },
          daysOfWeek: [1, 2, 3, 4, 5] // Monday to Friday
        },
        notifications: {
          enabled: true,
          channels: ['email', 'push'],
          security: {
            enabled: true,
            threshold: '0.1'
          },
          transactions: {
            enabled: true,
            onSubmit: false,
            onConfirm: true,
            onExecute: true
          }
        }
      },
      governance: {
        enabled: false,
        tokenContract: '',
        proposal: {
          threshold: '1000',
          votingDelay: 3600,
          votingPeriod: 604800,
          timeLockPeriod: 86400,
          quorumPercentage: 20
        },
        emergency: {
          enabled: false,
          specialProposalThreshold: '500',
          shorterVotingPeriod: 86400,
          emergencyQuorumPercentage: 30
        },
        delegation: {
          enabled: true,
          allowDelegation: true,
          allowRevocation: true,
          requireDelegationConfirmation: true
        },
        execution: {
          automatic: false,
          requireTimeLock: true,
          maxActionsPerProposal: 10
        }
      },
      ui: {
        theme: 'light',
        language: 'en',
        currency: {
          display: 'eth',
          default: 'eth',
          exchangeRate: 2000
        },
        display: {
          showConfirmations: true,
          showTransactionHistory: true,
          transactionPerPage: 10,
          compactMode: false
        },
        mobile: {
          responsive: true,
          touchOptimized: true,
          biometricAuth: false
        }
      },
      keyManagement: {
        encryption: {
          algorithm: 'aes-256-gcm',
          keyDerivation: 'scrypt',
          iterations: 100000,
          saltLength: 32
        },
        backup: {
          enabled: true,
          methods: ['file', 'cloud'],
          automaticInterval: 24,
          retentionPeriod: 90,
          encryption: true
        },
        hsm: {
          enabled: false,
          provider: 'aws',
          region: 'us-east-1',
          keyUsage: ['sign', 'generate']
        },
        recovery: {
          socialEnabled: true,
          thresholdRequired: 3,
          timeDelay: 24,
          maxAttempts: 3
        }
      },
      logging: {
        level: 'info',
        enableFileLogging: true,
        enableConsoleLogging: true,
        enableRemoteLogging: false,
        maxLogFiles: 10,
        maxLogSize: 10
      },
      analytics: {
        enabled: false,
        anonymized: true
      },
      features: {
        beta: ['governance'],
        experimental: ['social-recovery'],
        deprecated: []
      }
    };
  }

  private mergeConfigs(defaultConfig: ApplicationConfig, customConfig: Partial<ApplicationConfig>): ApplicationConfig {
    const merged = { ...defaultConfig };
    
    // Deep merge custom configuration
    for (const [key, value] of Object.entries(customConfig)) {
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        merged[key as keyof ApplicationConfig] = {
          ...merged[key as keyof ApplicationConfig],
          ...value
        };
      } else {
        merged[key as keyof ApplicationConfig] = value as any;
      }
    }
    
    return merged;
  }

  private initializeNetworkConfigs(): void {
    this.networkConfig.clear();
    
    for (const [chainId, network] of Object.entries(this.config.networks)) {
      this.networkConfig.set(Number(chainId), network);
    }
  }

  private convertToYAML(config: ApplicationConfig): string {
    // Simple YAML conversion - in production, use a proper YAML library
    return JSON.stringify(config, null, 2); // Fallback to JSON for now
  }

  private parseYAML(yamlData: string): Partial<ApplicationConfig> {
    // Simple YAML parsing - in production, use a proper YAML library
    return JSON.parse(yamlData); // Fallback to JSON for now
  }
}

// Export singleton instance
export const configManager = new ConfigurationManager();