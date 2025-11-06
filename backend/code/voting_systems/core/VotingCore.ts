/**
 * @file VotingCore.ts
 * @description Advanced Voting Systems Core Engine
 * @author Advanced Voting Systems
 */

export interface VotingPower {
  basePower: number;
  reputationMultiplier: number;
  timeWeightedBonus: number;
  delegationBonus: number;
  totalPower: number;
}

export interface VoteWeight {
  raw: number;
  quadratic: number;
  conviction: number;
  delegator: number;
  total: number;
}

export class VotingCore {
  private config: VotingConfig;
  private voterProfiles: Map<string, VoterProfile> = new Map();
  private votingPowers: Map<string, VotingPower> = new Map();

  constructor(config: VotingConfig) {
    this.config = config;
  }

  /**
   * Calculate voting power for a voter across all systems
   */
  calculateVotingPower(voterAddress: string, proposalId: string): VotingPower {
    const profile = this.voterProfiles.get(voterAddress);
    if (!profile) {
      return this.getDefaultVotingPower();
    }

    // Base power from token holdings
    const basePower = this.calculateBasePower(voterAddress, proposalId);
    
    // Reputation multiplier based on voting history
    const reputationMultiplier = this.calculateReputationMultiplier(voterAddress);
    
    // Time-weighted bonus for long-term engagement
    const timeWeightedBonus = this.calculateTimeWeightedBonus(voterAddress);
    
    // Delegation bonus from received delegations
    const delegationBonus = this.calculateDelegationBonus(voterAddress);
    
    // Calculate total power with diminishing returns
    const totalPower = this.applyDiminishingReturns(
      basePower * reputationMultiplier * timeWeightedBonus * (1 + delegationBonus)
    );

    const power: VotingPower = {
      basePower,
      reputationMultiplier,
      timeWeightedBonus,
      delegationBonus,
      totalPower
    };

    this.votingPowers.set(`${voterAddress}:${proposalId}`, power);
    return power;
  }

  /**
   * Calculate vote weight for different voting systems
   */
  calculateVoteWeight(
    voterAddress: string,
    proposalId: string,
    tokensSpent: number,
    system: VotingSystem
  ): VoteWeight {
    const votingPower = this.votingPowers.get(`${voterAddress}:${proposalId}`);
    if (!votingPower) {
      return this.getDefaultVoteWeight();
    }

    const base = votingPower.totalPower;
    
    switch (system) {
      case VotingSystem.QUADRATIC:
        return this.calculateQuadraticWeight(base, tokensSpent);
      
      case VotingSystem.CONVICTION:
        return this.calculateConvictionWeight(base, voterAddress);
      
      case VotingSystem.DELEGATED_DPOS:
        return this.calculateDelegatorWeight(base, voterAddress, proposalId);
      
      case VotingSystem.HOLOGRAPHIC:
        return this.calculateHolographicWeight(base, voterAddress, proposalId);
      
      case VotingSystem.FUTARCHY:
        return this.calculateFutarchyWeight(base, voterAddress, proposalId);
      
      default:
        return this.getDefaultVoteWeight();
    }
  }

  /**
   * Apply quadratic voting formula
   */
  private calculateQuadraticWeight(basePower: number, tokensSpent: number): VoteWeight {
    const sqrtTokens = Math.sqrt(tokensSpent);
    const quadraticWeight = Math.min(sqrtTokens / 10, basePower * 0.1);
    
    return {
      raw: basePower,
      quadratic: quadraticWeight,
      conviction: 0,
      delegator: 0,
      total: basePower + quadraticWeight
    };
  }

  /**
   * Apply conviction voting formula
   */
  private calculateConvictionWeight(basePower: number, voterAddress: string): VoteWeight {
    const profile = this.voterProfiles.get(voterAddress);
    if (!profile) return this.getDefaultVoteWeight();
    
    const convictionLevel = profile.convictionLevel;
    const convictionWeight = (convictionLevel / 100) * basePower;
    
    return {
      raw: basePower,
      quadratic: 0,
      conviction: convictionWeight,
      delegator: 0,
      total: basePower * (1 + convictionLevel / 100)
    };
  }

  /**
   * Calculate delegator voting weight
   */
  private calculateDelegatorWeight(
    basePower: number,
    voterAddress: string,
    proposalId: string
  ): VoteWeight {
    const profile = this.voterProfiles.get(voterAddress);
    if (!profile) return this.getDefaultVoteWeight();
    
    const delegatedToMe = profile.receivedDelegations.get(proposalId) || 0;
    const delegatorWeight = delegatedToMe * 0.01; // 1% weight per delegation
    
    return {
      raw: basePower,
      quadratic: 0,
      conviction: 0,
      delegator: delegatorWeight,
      total: basePower + delegatorWeight
    };
  }

  /**
   * Calculate holographic consensus weight
   */
  private calculateHolographicWeight(
    basePower: number,
    voterAddress: string,
    proposalId: string
  ): VoteWeight {
    const profile = this.voterProfiles.get(voterAddress);
    if (!profile) return this.getDefaultVoteWeight();
    
    const subDAOStake = profile.subDAOs.get(proposalId) || 0;
    const holographicWeight = Math.sqrt(subDAOStake) * 0.1;
    
    return {
      raw: basePower,
      quadratic: 0,
      conviction: 0,
      delegator: holographicWeight,
      total: basePower + holographicWeight
    };
  }

  /**
   * Calculate futarchy voting weight
   */
  private calculateFutarchyWeight(
    basePower: number,
    voterAddress: string,
    proposalId: string
  ): VoteWeight {
    const profile = this.voterProfiles.get(voterAddress);
    if (!profile) return this.getDefaultVoteWeight();
    
    const marketAccuracy = profile.marketPredictions.get(proposalId) || 0;
    const futarchyWeight = marketAccuracy * 0.1;
    
    return {
      raw: basePower,
      quadratic: 0,
      conviction: 0,
      delegator: futarchyWeight,
      total: basePower + futarchyWeight
    };
  }

  /**
   * Apply diminishing returns to prevent concentration
   */
  private applyDiminishingReturns(power: number): number {
    const exponent = this.config.diminishingReturnsExponent || 0.8;
    const maxPower = this.config.maxVotingPower || 10000;
    
    return Math.min(Math.pow(power, exponent), maxPower);
  }

  /**
   * Calculate base power from token holdings
   */
  private calculateBasePower(voterAddress: string, proposalId: string): number {
    const profile = this.voterProfiles.get(voterAddress);
    if (!profile) return 0;
    
    const tokenBalance = profile.tokenBalance;
    return Math.log10(tokenBalance + 1) * 100; // Logarithmic scaling
  }

  /**
   * Calculate reputation multiplier
   */
  private calculateReputationMultiplier(voterAddress: string): number {
    const profile = this.voterProfiles.get(voterAddress);
    if (!profile) return 1;
    
    const participation = profile.participationRate;
    const consistency = profile.votingConsistency;
    const reputation = (participation * 0.6 + consistency * 0.4) / 100;
    
    return Math.max(0.5, Math.min(2.0, reputation * 2));
  }

  /**
   * Calculate time-weighted bonus
   */
  private calculateTimeWeightedBonus(voterAddress: string): number {
    const profile = this.voterProfiles.get(voterAddress);
    if (!profile) return 1;
    
    const memberSince = profile.memberSince;
    const monthsActive = (Date.now() - memberSince) / (1000 * 60 * 60 * 24 * 30);
    
    return Math.min(1.5, 1 + (monthsActive * 0.05)); // 5% bonus per month
  }

  /**
   * Calculate delegation bonus
   */
  private calculateDelegationBonus(voterAddress: string): number {
    const profile = this.voterProfiles.get(voterAddress);
    if (!profile) return 0;
    
    const receivedDelegations = profile.receivedDelegations.size;
    return Math.min(0.5, receivedDelegations * 0.1); // 10% per delegation, max 50%
  }

  /**
   * Update voter profile
   */
  updateVoterProfile(address: string, updates: Partial<VoterProfile>): void {
    const existing = this.voterProfiles.get(address) || this.createDefaultProfile(address);
    this.voterProfiles.set(address, { ...existing, ...updates });
  }

  /**
   * Get voting history for analysis
   */
  getVotingHistory(voterAddress: string): VotingHistory[] {
    const profile = this.voterProfiles.get(voterAddress);
    return profile?.votingHistory || [];
  }

  /**
   * Batch calculate voting powers
   */
  async batchCalculateVotingPowers(voters: string[], proposalId: string): Promise<Map<string, VotingPower>> {
    const results = new Map<string, VotingPower>();
    
    for (const voter of voters) {
      const power = this.calculateVotingPower(voter, proposalId);
      results.set(voter, power);
    }
    
    return results;
  }

  /**
   * Default voting power
   */
  private getDefaultVotingPower(): VotingPower {
    return {
      basePower: 0,
      reputationMultiplier: 1,
      timeWeightedBonus: 1,
      delegationBonus: 0,
      totalPower: 0
    };
  }

  /**
   * Default vote weight
   */
  private getDefaultVoteWeight(): VoteWeight {
    return {
      raw: 0,
      quadratic: 0,
      conviction: 0,
      delegator: 0,
      total: 0
    };
  }

  /**
   * Create default profile
   */
  private createDefaultProfile(address: string): VoterProfile {
    return {
      address,
      memberSince: Date.now(),
      tokenBalance: 0,
      reputation: 500,
      participationRate: 0,
      votingConsistency: 0,
      convictionLevel: 0,
      stakingDuration: 0,
      marketPredictions: new Map(),
      receivedDelegations: new Map(),
      votingHistory: [],
      subDAOs: new Map(),
      governanceScore: 0,
      lastActivity: Date.now()
    };
  }

  /**
   * Validate vote weight calculation
   */
  validateVoteWeight(weight: VoteWeight): boolean {
    return (
      weight.raw >= 0 &&
      weight.quadratic >= 0 &&
      weight.conviction >= 0 &&
      weight.delegator >= 0 &&
      weight.total >= 0 &&
      weight.total >= weight.raw
    );
  }

  /**
   * Get configuration
   */
  getConfig(): VotingConfig {
    return { ...this.config };
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig: Partial<VotingConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }
}

/**
 * Configuration interface
 */
export interface VotingConfig {
  diminishingReturnsExponent?: number;
  maxVotingPower?: number;
  minReputation?: number;
  maxReputation?: number;
  reputationDecay?: number;
  delegationMultiplier?: number;
  convictionThreshold?: number;
}

/**
 * Voter profile interface
 */
export interface VoterProfile {
  address: string;
  memberSince: number;
  tokenBalance: number;
  reputation: number;
  participationRate: number;
  votingConsistency: number;
  convictionLevel: number;
  stakingDuration: number;
  marketPredictions: Map<string, number>;
  receivedDelegations: Map<string, number>;
  votingHistory: VotingHistory[];
  subDAOs: Map<string, number>;
  governanceScore: number;
  lastActivity: number;
}

/**
 * Voting history interface
 */
export interface VotingHistory {
  proposalId: string;
  timestamp: number;
  choice: number;
  system: VotingSystem;
  weight: number;
  outcome: number;
}

/**
 * Voting system types
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