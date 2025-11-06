/**
 * @file MobileTypes.ts
 * @description Mobile-specific type definitions
 * @author Advanced Voting Systems
 */

export enum VotingSystem {
  SIMPLE = 'simple',
  QUADRATIC = 'quadratic',
  CONVICTION = 'conviction',
  DELEGATED_DPOS = 'delegated_dpos',
  HOLOGRAPHIC = 'holographic',
  FUTARCHY = 'futarchy',
  CONDITIONAL = 'conditional'
}

export interface Proposal {
  id: string;
  title: string;
  description: string;
  proposer: string;
  createdAt: number;
  currentStage: string;
  votingEndTime: number;
  category: 'treasury' | 'governance' | 'technical' | 'social' | 'emergency';
  priority: 'low' | 'medium' | 'high' | 'critical';
  votingSystem: VotingSystem;
  status: 'active' | 'completed' | 'cancelled';
  userVote?: number;
  tags?: string[];
  estimatedTime?: number;
}

export interface MobileVote {
  proposalId: string;
  choice: number;
  timestamp: number;
  platform: 'mobile' | 'web';
  biometricVerified: boolean;
  metadata?: {
    tokensSpent?: string;
    conditionalStatement?: string;
    location?: LocationData;
  };
}

export interface LocationData {
  latitude: number;
  longitude: number;
  accuracy: number;
  timestamp: number;
}

export interface BiometricData {
  verified: boolean;
  method: 'fingerprint' | 'face' | 'voice' | 'pattern';
  confidence: number;
  timestamp: number;
}

export interface WalletConnection {
  address: string;
  chainId: number;
  provider: string;
  isConnected: boolean;
  balance: string;
}

export interface NotificationData {
  id: string;
  type: 'voting_reminder' | 'proposal_created' | 'proposal_executed' | 'governance_alert' | 'system_update';
  title: string;
  message: string;
  timestamp: number;
  read: boolean;
  proposalId?: string;
  actionUrl?: string;
}

export interface VotingHistoryEntry {
  id: string;
  proposalId: string;
  proposalTitle: string;
  choice: number;
  timestamp: number;
  system: VotingSystem;
  outcome: 'passed' | 'failed' | 'pending';
  impact?: string;
}

export interface VotingPowerMobile {
  basePower: number;
  reputationMultiplier: number;
  timeWeightedBonus: number;
  delegationBonus: number;
  totalPower: number;
}

export interface UserProfile {
  address: string;
  username?: string;
  avatar?: string;
  reputationScore: number;
  participationRate: number;
  votingHistory: VotingHistoryEntry[];
  lastActive: number;
  preferences: UserPreferences;
}

export interface UserPreferences {
  notifications: {
    pushEnabled: boolean;
    emailEnabled: boolean;
    votingReminders: boolean;
    proposalUpdates: boolean;
    governanceAlerts: boolean;
  };
  voting: {
    defaultSystem: VotingSystem;
    autoVote: boolean;
    abstainOnUnclear: boolean;
  };
  privacy: {
    showVotingHistory: boolean;
    showReputationScore: boolean;
  };
}

export interface DAOInfo {
  id: string;
  name: string;
  description: string;
  logo?: string;
  website?: string;
  governanceToken: string;
  totalMembers: number;
  activeProposals: number;
  governanceHealth: {
    score: number;
    grade: 'A' | 'B' | 'C' | 'D' | 'F';
    status: string;
  };
}

export interface GovernanceHealth {
  overallScore: number;
  participationRate: number;
  decentralizationScore: number;
  effectivenessScore: number;
  biasDetection: {
    sentimentBias: number;
    participationBias: number;
    votingBias: number;
  };
  recommendations: string[];
}

export interface ProposalAnalytics {
  engagement: number;
  participation: number;
  sentiment: number;
  velocity: number;
  reach: number;
}

export interface VotingResult {
  proposalId: string;
  finalDecision: number;
  totalVotes: number;
  participationRate: number;
  supportPercentage: number;
  againstPercentage: number;
  abstainPercentage: number;
  executed: boolean;
  executionTime?: number;
}

export interface BatchVoteRequest {
  proposals: {
    id: string;
    choice: number;
  }[];
  metadata?: {
    tokensToSpend?: Record<string, string>;
    conditionalStatements?: Record<string, string>;
  };
}

export interface BatchVoteResult {
  successful: number;
  failed: number;
  results: Array<{
    proposalId: string;
    success: boolean;
    transactionHash?: string;
    error?: string;
  }>;
}

export interface VotingSession {
  id: string;
  proposalIds: string[];
  startTime: number;
  endTime: number;
  active: boolean;
  userVotes: Map<string, number>;
}

export interface OfflineVoting {
  enabled: boolean;
  syncStatus: 'synced' | 'pending' | 'failed';
  unsyncedVotes: MobileVote[];
  lastSync: number;
}

export interface VoiceCommand {
  command: string;
  parameters: Record<string, any>;
  confidence: number;
  timestamp: number;
}

export interface GestureControl {
  type: 'swipe' | 'tap' | 'pinch' | 'rotate';
  direction?: 'up' | 'down' | 'left' | 'right';
  position: { x: number; y: number };
  timestamp: number;
}

export interface AccessibilityFeature {
  type: 'screen_reader' | 'high_contrast' | 'large_text' | 'voice_navigation';
  enabled: boolean;
  settings: Record<string, any>;
}

export interface SecuritySettings {
  biometricAuth: boolean;
  requireBiometricForVote: boolean;
  autoLockTimeout: number; // minutes
  enableVPNCheck: boolean;
  deviceBinding: boolean;
}

export interface AppSettings {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  currency: string;
  timezone: string;
  dataUsage: 'wifi_only' | 'cellular' | 'both';
  analytics: {
    enabled: boolean;
    shareUsage: boolean;
  };
  security: SecuritySettings;
  accessibility: AccessibilityFeature[];
}

export interface DeviceInfo {
  deviceId: string;
  platform: 'ios' | 'android';
  osVersion: string;
  appVersion: string;
  screenSize: {
    width: number;
    height: number;
  };
  capabilities: {
    biometricAuth: boolean;
    faceID: boolean;
    fingerprint: boolean;
    voiceCommands: boolean;
  };
}

export interface NetworkStatus {
  connected: boolean;
  type: 'wifi' | 'cellular' | 'none';
  quality: 'excellent' | 'good' | 'poor';
  latency?: number;
}

export interface TransactionData {
  hash: string;
  status: 'pending' | 'confirmed' | 'failed';
  blockNumber?: number;
  gasUsed?: number;
  timestamp: number;
  from: string;
  to: string;
  value: string;
  method: string;
  parameters: any[];
}

export interface ErrorReport {
  id: string;
  error: string;
  stack?: string;
  deviceInfo: DeviceInfo;
  userAction?: string;
  timestamp: number;
  reported: boolean;
}

export interface FeedbackData {
  type: 'bug_report' | 'feature_request' | 'general_feedback';
  title: string;
  description: string;
  email?: string;
  attachments?: string[];
  timestamp: number;
}

export interface AnalyticsEvent {
  event: string;
  properties: Record<string, any>;
  timestamp: number;
  userId?: string;
  sessionId: string;
}

export interface CacheData {
  key: string;
  data: any;
  timestamp: number;
  ttl: number; // Time to live in milliseconds
}

export interface SyncStatus {
  lastSync: number;
  pendingActions: number;
  syncErrors: string[];
  autoSync: boolean;
}

export interface ExportData {
  type: 'voting_history' | 'proposal_data' | 'analytics';
  format: 'json' | 'csv' | 'pdf';
  data: any;
  generatedAt: number;
}

export interface ImportData {
  type: 'wallet' | 'voting_preferences' | 'proposals';
  data: any;
  validated: boolean;
  errors: string[];
}

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: number;
  pagination?: {
    page: number;
    limit: number;
    total: number;
  };
}