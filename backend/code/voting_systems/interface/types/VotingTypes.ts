/**
 * @file VotingTypes.ts
 * @description Type definitions for Advanced Voting Systems
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
  
  // Lifecycle
  currentStage: ProposalStage;
  stages: ProposalStageInfo[];
  submittedForVoting: boolean;
  votingStarted: boolean;
  executed: boolean;
  rejected: boolean;
  
  // Metadata
  category: ProposalCategory;
  priority: Priority;
  tags: string[];
  attachments: string[];
  relatedProposals: string[];
  
  // Discussion
  discussionOpen: boolean;
  comments: Comment[];
  amendments: Amendment[];
  
  // Voting
  votingSystem: VotingSystem;
  votingPower: VotingPower;
  voteSettings: VoteSettings;
  votes: Map<string, Vote>;
  
  // Results
  result: ProposalResult;
  executionDetails?: ExecutionDetails;
}

export interface VotingPower {
  basePower: number;
  reputationMultiplier: number;
  timeWeightedBonus: number;
  delegationBonus: number;
  convictionLevel: number;
  totalPower: number;
}

export interface Vote {
  voter: string;
  choice: number; // -1, 0, 1
  timestamp: number;
  system: VotingSystem;
  weight: number;
  delegated: boolean;
  metadata?: VoteMetadata;
}

export interface VoteMetadata {
  tokensSpent?: bigint;
  conditionalStatement?: string;
  timeWeightedPower?: number;
  reputationBonus?: number;
  delegationSource?: string;
  convictionLevel?: number;
  marketPrediction?: number;
  biometricVerified?: boolean;
  platform?: string;
}

export interface ProposalStageInfo {
  stage: ProposalStage;
  startTime: number;
  endTime?: number;
  status: StageStatus;
  requirements: StageRequirement[];
  description: string;
}

export interface StageRequirement {
  type: 'min_support' | 'quorum' | 'discussion' | 'stake' | 'reputation' | 'amendment_approval';
  threshold: number;
  current?: number;
  met: boolean;
}

export interface Comment {
  id: string;
  author: string;
  content: string;
  timestamp: number;
  replies: Comment[];
  likes: string[];
  weight: number;
  isOfficial: boolean;
}

export interface Amendment {
  id: string;
  proposer: string;
  description: string;
  changes: AmendmentChange[];
  status: AmendmentStatus;
  votes: Map<string, number>;
  createdAt: number;
}

export interface AmendmentChange {
  type: 'add' | 'remove' | 'modify';
  section: string;
  oldContent?: string;
  newContent: string;
}

export interface VoteSettings {
  minQuorum: number;
  supportThreshold: number;
  votingPeriod: number;
  executionDelay: number;
  conditionalRules?: ConditionalRule[];
  batchVote?: BatchVoteSettings;
}

export interface ConditionalRule {
  condition: string;
  weight: number;
  expiry?: number;
}

export interface BatchVoteSettings {
  enabled: boolean;
  groupSize: number;
  minParticipation: number;
  timeWindow: number;
}

export interface ProposalResult {
  finalDecision: number;
  totalVotes: number;
  weightedVotes: number;
  participationRate: number;
  quorumMet: boolean;
  supportThresholdMet: boolean;
  systemBreakdown: Map<VotingSystem, SystemResult>;
}

export interface SystemResult {
  votes: number;
  yesVotes: number;
  noVotes: number;
  abstainVotes: number;
  weightedScore: number;
  participation: number;
}

export interface ExecutionDetails {
  executedAt: number;
  executor: string;
  gasUsed: number;
  transactions: string[];
  effects: ExecutionEffect[];
  errors?: string[];
}

export interface ExecutionEffect {
  type: 'parameter_change' | 'fund_transfer' | 'contract_call' | 'role_assignment';
  target: string;
  value: any;
  timestamp: number;
}

export enum ProposalStage {
  DRAFT = 'draft',
  DISCUSSION = 'discussion',
  AMENDMENT = 'amendment',
  READY_FOR_VOTING = 'ready_for_voting',
  VOTING = 'voting',
  EXECUTABLE = 'executable',
  EXECUTED = 'executed',
  REJECTED = 'rejected',
  CANCELLED = 'cancelled'
}

export enum ProposalCategory {
  GOVERNANCE = 'governance',
  TREASURY = 'treasury',
  TECHNICAL = 'technical',
  SOCIAL = 'social',
  EMERGENCY = 'emergency'
}

export enum Priority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum StageStatus {
  PENDING = 'pending',
  ACTIVE = 'active',
  COMPLETED = 'completed',
  SKIPPED = 'skipped'
}

export enum AmendmentStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  MERGED = 'merged'
}

// Web3 specific types
export interface WalletConnection {
  address: string;
  chainId: number;
  provider: string;
  isConnected: boolean;
  balance: string;
}

export interface ContractCall {
  contractAddress: string;
  functionName: string;
  parameters: any[];
  value?: string;
  gasEstimate?: number;
}

// Analytics types
export interface GovernanceHealth {
  overall: HealthScore;
  participation: HealthMetrics;
  decentralization: DecentralizationMetrics;
  effectiveness: EffectivenessMetrics;
  bias: BiasDetection;
  democraticScore: DemocraticScore;
}

export interface HealthScore {
  score: number;
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  trend: 'improving' | 'stable' | 'declining';
  lastUpdate: number;
  components: {
    participation: number;
    decentralization: number;
    transparency: number;
    accountability: number;
    efficiency: number;
  };
}

// Mobile specific types
export interface MobileVote {
  proposalId: string;
  choice: number;
  timestamp: number;
  platform: 'mobile' | 'web';
  biometricVerified: boolean;
  location?: LocationData;
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

export interface NotificationSettings {
  pushEnabled: boolean;
  emailEnabled: boolean;
  smsEnabled: boolean;
  votingReminders: boolean;
  proposalUpdates: boolean;
  governanceAlerts: boolean;
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

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// Configuration types
export interface VotingConfig {
  system: VotingSystem;
  minQuorum: number;
  supportThreshold: number;
  votingPeriod: number;
  executionDelay: number;
  customParameters?: Record<string, any>;
}

export interface DAOConfig {
  name: string;
  description: string;
  votingSystems: VotingConfig[];
  governanceToken: string;
  treasury: string;
  emergencyThreshold: number;
  requiredSignatures: number;
}

// Error types
export class VotingError extends Error {
  constructor(
    message: string,
    public code: string,
    public details?: any
  ) {
    super(message);
    this.name = 'VotingError';
  }
}

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface ValidationWarning {
  field: string;
  message: string;
  suggestion: string;
}

// Event types
export interface VotingEvent {
  type: 'proposal_created' | 'vote_cast' | 'proposal_executed' | 'amendment_submitted';
  proposalId: string;
  user?: string;
  data: any;
  timestamp: number;
}

// Real-time updates
export interface RealtimeUpdate {
  type: 'proposal_update' | 'vote_update' | 'result_update';
  proposalId: string;
  data: any;
  timestamp: number;
}

// Delegation types
export interface Delegation {
  id: string;
  delegator: string;
  delegate: string;
  amount: number;
  system: VotingSystem;
  createdAt: number;
  expiresAt?: number;
  rules?: DelegationRules;
}

export interface DelegationRules {
  autoVote?: boolean;
  abstainOnUnclear?: boolean;
  maxTokenSpend?: number;
  conditions?: string[];
}

// Batch voting types
export interface BatchVoteRequest {
  proposalIds: string[];
  choices: number[];
  metadata?: BatchVoteMetadata;
}

export interface BatchVoteMetadata {
  system: VotingSystem;
  tokensToSpend?: Record<string, string>;
  conditionalStatements?: Record<string, string>;
}

// Analytics and reporting types
export interface VoterProfile {
  address: string;
  votingHistory: VotingHistoryEntry[];
  reputationScore: number;
  participationRate: number;
  influenceScore: number;
  lastActive: number;
}

export interface ProposalAnalytics {
  engagement: number;
  participation: number;
  sentiment: number;
  velocity: number;
  reach: number;
}

export interface GovernanceReport {
  period: { start: number; end: number };
  metrics: GovernanceHealth;
  recommendations: string[];
  trends: TrendData[];
}

export interface TrendData {
  metric: string;
  values: { timestamp: number; value: number }[];
  trend: 'up' | 'down' | 'stable';
  confidence: number;
}