/**
 * @file config.ts
 * @description Configuration for Advanced Voting Systems
 * @author Advanced Voting Systems
 */

export interface VotingSystemConfig {
  [key: string]: {
    name: string;
    description: string;
    enabled: boolean;
    parameters: Record<string, any>;
    contracts: {
      address?: string;
      abi?: any[];
    };
    ui: {
      showTokensInput?: boolean;
      showConvictionInput?: boolean;
      showDelegationInfo?: boolean;
      showConditionalOptions?: boolean;
    };
  };
}

export interface NetworkConfig {
  chainId: number;
  name: string;
  rpcUrl: string;
  blockExplorer: string;
  contracts: {
    quadraticVoting?: string;
    convictionVoting?: string;
    delegatedDPoS?: string;
    holographicConsensus?: string;
    futarchyMarkets?: string;
    governanceToken?: string;
  };
}

export interface AnalyticsConfig {
  enabled: boolean;
  updateInterval: number; // milliseconds
  metricsToTrack: string[];
  biasDetectionEnabled: boolean;
  realTimeUpdates: boolean;
}

export interface NotificationConfig {
  enabled: boolean;
  channels: ('push' | 'email' | 'sms')[];
  events: {
    proposalCreated: boolean;
    voteReminder: boolean;
    proposalExecuted: boolean;
    governanceAlert: boolean;
    systemUpdate: boolean;
  };
}

export interface MobileConfig {
  biometricAuthRequired: boolean;
  offlineVotingEnabled: boolean;
  backgroundSync: boolean;
  gestureControls: boolean;
  voiceCommands: boolean;
}

export interface SecurityConfig {
  enableMultiSig: boolean;
  timeLockPeriod: number; // seconds
  emergencyPauseEnabled: boolean;
  rateLimiting: {
    enabled: boolean;
    maxRequests: number;
    windowSize: number; // seconds
  };
  encryptionEnabled: boolean;
}

// Main configuration object
export const VOTING_SYSTEMS: VotingSystemConfig = {
  simple: {
    name: 'Simple Majority Voting',
    description: 'Basic one-token-one-vote system with simple majority rule',
    enabled: true,
    parameters: {
      minQuorum: 0.1,
      supportThreshold: 0.5,
      votingPeriod: 7 * 24 * 60 * 60, // 7 days
      executionDelay: 24 * 60 * 60 // 1 day
    },
    ui: {
      showTokensInput: false,
      showConvictionInput: false,
      showDelegationInfo: false,
      showConditionalOptions: true
    }
  },
  
  quadratic: {
    name: 'Quadratic Voting',
    description: 'Voting power equals square root of tokens spent',
    enabled: true,
    parameters: {
      minQuorum: 0.15,
      supportThreshold: 0.6,
      votingPeriod: 7 * 24 * 60 * 60,
      executionDelay: 2 * 24 * 60 * 60,
      diminishingReturns: 0.8,
      maxTokensPerVote: 1000
    },
    ui: {
      showTokensInput: true,
      showConvictionInput: false,
      showDelegationInfo: false,
      showConditionalOptions: true
    }
  },
  
  conviction: {
    name: 'Conviction Voting',
    description: 'Long-term commitment determines voting influence',
    enabled: true,
    parameters: {
      minQuorum: 0.2,
      supportThreshold: 0.65,
      votingPeriod: 14 * 24 * 60 * 60, // 14 days
      executionDelay: 3 * 24 * 60 * 60,
      decayRate: 0.01, // 1% per day
      maxConviction: 100
    },
    ui: {
      showTokensInput: false,
      showConvictionInput: true,
      showDelegationInfo: true,
      showConditionalOptions: true
    }
  },
  
  delegated_dpos: {
    name: 'Delegated Proof of Stake',
    description: 'Stake-based voting with delegation capabilities',
    enabled: true,
    parameters: {
      minQuorum: 0.25,
      supportThreshold: 0.7,
      votingPeriod: 3 * 24 * 60 * 60,
      executionDelay: 12 * 60 * 60,
      minStake: 10000,
      maxValidators: 21,
      slashingThreshold: 0.5
    },
    ui: {
      showTokensInput: false,
      showConvictionInput: false,
      showDelegationInfo: true,
      showConditionalOptions: true
    }
  },
  
  holographic: {
    name: 'Holographic Consensus',
    description: 'Multi-SubDAO consensus using holographic weighting',
    enabled: true,
    parameters: {
      minQuorum: 0.3,
      supportThreshold: 0.8,
      votingPeriod: 21 * 24 * 60 * 60,
      executionDelay: 5 * 24 * 60 * 60,
      requiredSubDAOs: 3,
      consensusThreshold: 0.8
    },
    ui: {
      showTokensInput: true,
      showConvictionInput: false,
      showDelegationInfo: true,
      showConditionalOptions: true
    }
  },
  
  futarchy: {
    name: 'Futarchy Prediction Markets',
    description: 'Voting power based on prediction market accuracy',
    enabled: true,
    parameters: {
      minQuorum: 0.2,
      supportThreshold: 0.75,
      votingPeriod: 10 * 24 * 60 * 60,
      executionDelay: 24 * 60 * 60,
      predictionWeight: 0.6,
      votingWeight: 0.4
    },
    ui: {
      showTokensInput: false,
      showConvictionInput: false,
      showDelegationInfo: true,
      showConditionalOptions: true
    }
  },
  
  conditional: {
    name: 'Conditional Voting',
    description: 'Votes with if-then conditions based on other outcomes',
    enabled: true,
    parameters: {
      minQuorum: 0.1,
      supportThreshold: 0.5,
      votingPeriod: 7 * 24 * 60 * 60,
      executionDelay: 24 * 60 * 60,
      maxConditions: 5,
      conditionComplexity: 'medium'
    },
    ui: {
      showTokensInput: true,
      showConvictionInput: true,
      showDelegationInfo: true,
      showConditionalOptions: true
    }
  }
};

export const NETWORKS: NetworkConfig[] = [
  {
    chainId: 1, // Ethereum Mainnet
    name: 'Ethereum',
    rpcUrl: 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID',
    blockExplorer: 'https://etherscan.io',
    contracts: {
      quadraticVoting: '0x...',
      convictionVoting: '0x...',
      delegatedDPoS: '0x...',
      holographicConsensus: '0x...',
      futarchyMarkets: '0x...',
      governanceToken: '0x...'
    }
  },
  {
    chainId: 137, // Polygon
    name: 'Polygon',
    rpcUrl: 'https://polygon-rpc.com',
    blockExplorer: 'https://polygonscan.com',
    contracts: {
      quadraticVoting: '0x...',
      convictionVoting: '0x...',
      delegatedDPoS: '0x...',
      holographicConsensus: '0x...',
      futarchyMarkets: '0x...',
      governanceToken: '0x...'
    }
  },
  {
    chainId: 56, // BSC
    name: 'BSC',
    rpcUrl: 'https://bsc-dataseed.binance.org',
    blockExplorer: 'https://bscscan.com',
    contracts: {
      governanceToken: '0x...'
    }
  }
];

export const ANALYTICS: AnalyticsConfig = {
  enabled: true,
  updateInterval: 30000, // 30 seconds
  metricsToTrack: [
    'participation_rate',
    'governance_concentration',
    'proposal_success_rate',
    'bias_detection',
    'democratic_health'
  ],
  biasDetectionEnabled: true,
  realTimeUpdates: true
};

export const NOTIFICATIONS: NotificationConfig = {
  enabled: true,
  channels: ['push', 'email'],
  events: {
    proposalCreated: true,
    voteReminder: true,
    proposalExecuted: true,
    governanceAlert: true,
    systemUpdate: false
  }
};

export const MOBILE: MobileConfig = {
  biometricAuthRequired: true,
  offlineVotingEnabled: false, // For security reasons
  backgroundSync: true,
  gestureControls: true,
  voiceCommands: false
};

export const SECURITY: SecurityConfig = {
  enableMultiSig: true,
  timeLockPeriod: 24 * 60 * 60, // 24 hours
  emergencyPauseEnabled: true,
  rateLimiting: {
    enabled: true,
    maxRequests: 100,
    windowSize: 60 // 1 minute
  },
  encryptionEnabled: true
};

export const UI: Record<string, any> = {
  theme: {
    primary: '#4F46E5',
    secondary: '#7C3AED',
    success: '#10B981',
    warning: '#F59E0B',
    danger: '#EF4444',
    background: '#F9FAFB',
    surface: '#FFFFFF',
    text: '#1F2937',
    textSecondary: '#6B7280'
  },
  breakpoints: {
    mobile: '640px',
    tablet: '768px',
    desktop: '1024px',
    wide: '1280px'
  },
  animations: {
    enabled: true,
    duration: 300,
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
  }
};

export const API: Record<string, any> = {
  endpoints: {
    proposals: '/api/proposals',
    votes: '/api/votes',
    analytics: '/api/analytics',
    users: '/api/users',
    notifications: '/api/notifications'
  },
  rateLimits: {
    default: 100, // requests per hour
    voting: 10, // votes per hour
    proposals: 5 // proposals per day
  },
  cache: {
    ttl: 300, // 5 minutes
    enabled: true
  }
};

export const CONSTANTS = {
  MAX_PROPOSALS_PER_USER: 10,
  MAX_AMENDMENTS_PER_PROPOSAL: 5,
  MIN_PROPOSAL_DESCRIPTION_LENGTH: 50,
  MAX_PROPOSAL_DESCRIPTION_LENGTH: 2000,
  DEFAULT_PAGE_SIZE: 20,
  MAX_SEARCH_RESULTS: 100,
  VOTING_POWER_DECIMALS: 2,
  TOKEN_DECIMALS: 18
};

// Validation rules
export const VALIDATION = {
  proposal: {
    title: {
      minLength: 5,
      maxLength: 100,
      pattern: /^[a-zA-Z0-9\s\-_]+$/
    },
    description: {
      minLength: 50,
      maxLength: 2000
    },
    tags: {
      maxCount: 10,
      maxLength: 20
    }
  },
  vote: {
    maxTokensPerVote: 10000,
    maxConditionalStatements: 5
  },
  user: {
    minReputation: 0,
    maxReputation: 1000
  }
};

export const FEATURES = {
  BATCH_VOTING: true,
  CONDITIONAL_VOTING: true,
  OFFLINE_MODE: false,
  VOICE_COMMANDS: false,
  BIOMETRIC_AUTH: true,
  CROSS_CHAIN: false,
  NFT_VOTING: false,
  DAO_COLLABORATION: true
};

export function getNetworkConfig(chainId: number): NetworkConfig | undefined {
  return NETWORKS.find(network => network.chainId === chainId);
}

export function getVotingSystemConfig(systemName: string): VotingSystemConfig[string] | undefined {
  return VOTING_SYSTEMS[systemName];
}

export function isFeatureEnabled(featureName: keyof typeof FEATURES): boolean {
  return FEATURES[featureName];
}