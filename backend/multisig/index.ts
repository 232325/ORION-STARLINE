/**
 * Multi-Signature Wallet Integration System
 * Main Entry Point
 * @author MultiSig Wallet System
 */

export { WalletManager } from './core/wallet/WalletManager';
export { SpendingLimits } from './core/limits/SpendingLimits';

export { SecurityManager } from './security/auth/SecurityManager';

export { GovernanceManager } from './governance/dao/GovernanceManager';

export { KeyManager } from './key-management/hsm/KeyManager';

export { Web3WalletIntegration } from './interface/web3/Web3WalletIntegration';
export { default as MobileWallet } from './interface/mobile/MobileWallet';

export { ConfigurationManager, configManager } from './config/ConfigurationManager';

// Types and Interfaces
export type {
  WalletConfig,
  Transaction,
  Confirmation,
  WalletState,
  TransactionRequest
} from './interface/web3/Web3WalletIntegration';

export type {
  SecurityConfig,
  SecurityLevel,
  WhitelistEntry,
  BlacklistEntry,
  EmergencyAccess,
  SecurityAlert,
  SecurityAlertType,
  AlertSeverity
} from './security/auth/SecurityManager';

export type {
  Proposal,
  GovernanceAction,
  Vote,
  Delegation,
  VotingPower,
  GovernanceConfig,
  ProposalState,
  VoteType
} from './governance/dao/GovernanceManager';

export type {
  KeyRecord,
  KeyBackup,
  RecoveryInfo,
  SocialRecoveryConfig,
  TimeLockConfig,
  HSMConfig,
  KeyShare,
  KeyType,
  KeyStatus,
  BackupType,
  TrustLevel,
  HSMProvider,
  HSMOperation
} from './key-management/hsm/KeyManager';

export type {
  NetworkConfig,
  SecurityConfig as SecuritySettings,
  GovernanceConfig as GovernanceSettings,
  UIConfig,
  KeyManagementConfig,
  ApplicationConfig
} from './config/ConfigurationManager';

// Smart Contract ABIs and Interfaces
export * from './contracts/interfaces/IMultiSigWallet';
export * from './contracts/interfaces/ISecurityManager';
export * from './contracts/interfaces/IGovernanceManager';

// Utility functions
export { createWallet, connectWallet, validateTransaction, calculateGas } from './utils/helpers';

// Version
export const VERSION = '1.0.0';
export const NAME = 'Multi-Signature Wallet Integration System';