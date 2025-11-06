/**
 * @file votingUtils.ts
 * @description Utility functions for Advanced Voting Systems
 * @author Advanced Voting Systems
 */

import { ethers } from 'ethers';
import { VotingSystem, Proposal, Vote, VotingPower } from '../interface/types/VotingTypes';

/**
 * Format voting power for display
 */
export function formatVotingPower(power: number, decimals: number = 2): string {
  if (power === 0) return '0';
  if (power < 1) return power.toFixed(4);
  if (power < 1000) return power.toFixed(decimals);
  if (power < 1000000) return (power / 1000).toFixed(1) + 'K';
  if (power < 1000000000) return (power / 1000000).toFixed(1) + 'M';
  return (power / 1000000000).toFixed(1) + 'B';
}

/**
 * Calculate time remaining for proposal
 */
export function getTimeRemaining(endTime: number): {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  total: number;
  expired: boolean;
} {
  const now = Date.now();
  const remaining = endTime - now;
  
  if (remaining <= 0) {
    return {
      days: 0,
      hours: 0,
      minutes: 0,
      seconds: 0,
      total: 0,
      expired: true
    };
  }
  
  const days = Math.floor(remaining / (1000 * 60 * 60 * 24));
  const hours = Math.floor((remaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((remaining % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((remaining % (1000 * 60)) / 1000);
  
  return {
    days,
    hours,
    minutes,
    seconds,
    total: remaining,
    expired: false
  };
}

/**
 * Format time remaining for display
 */
export function formatTimeRemaining(endTime: number): string {
  const { days, hours, minutes, seconds, expired } = getTimeRemaining(endTime);
  
  if (expired) return 'Expired';
  
  if (days > 0) return `${days}d ${hours}h`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  if (minutes > 0) return `${minutes}m ${seconds}s`;
  return `${seconds}s`;
}

/**
 * Calculate voting weight based on system and parameters
 */
export function calculateVoteWeight(
  system: VotingSystem,
  basePower: number,
  parameters: Record<string, any>
): number {
  switch (system) {
    case VotingSystem.QUADRATIC:
      const tokensSpent = parameters.tokensSpent || 0;
      return Math.sqrt(tokensSpent) * basePower;
    
    case VotingSystem.CONVICTION:
      const conviction = parameters.convictionLevel || 0;
      return conviction * basePower / 100;
    
    case VotingSystem.DELEGATED_DPOS:
      const delegatedPower = parameters.delegatedPower || 0;
      return (basePower + delegatedPower) * 1.1; // 10% bonus
    
    case VotingSystem.HOLOGRAPHIC:
      const subDAOWeight = parameters.subDAOWeight || 1;
      return basePower * Math.sqrt(subDAOWeight);
    
    case VotingSystem.FUTARCHY:
      const marketAccuracy = parameters.marketAccuracy || 0.5;
      return basePower * (0.5 + marketAccuracy * 0.5);
    
    default:
      return basePower;
  }
}

/**
 * Calculate participation rate
 */
export function calculateParticipationRate(
  totalVotes: number,
  totalEligibleVoters: number
): number {
  if (totalEligibleVoters === 0) return 0;
  return (totalVotes / totalEligibleVoters) * 100;
}

/**
 * Calculate support percentage
 */
export function calculateSupportPercentage(
  yesVotes: number,
  noVotes: number,
  abstainVotes: number = 0
): { support: number; against: number; abstain: number } {
  const totalVotes = yesVotes + noVotes + abstainVotes;
  
  if (totalVotes === 0) {
    return { support: 0, against: 0, abstain: 0 };
  }
  
  return {
    support: (yesVotes / totalVotes) * 100,
    against: (noVotes / totalVotes) * 100,
    abstain: (abstainVotes / totalVotes) * 100
  };
}

/**
 * Validate proposal data
 */
export function validateProposal(proposal: Partial<Proposal>): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];
  
  if (!proposal.title || proposal.title.length < 5) {
    errors.push('Title must be at least 5 characters');
  }
  
  if (!proposal.description || proposal.description.length < 50) {
    errors.push('Description must be at least 50 characters');
  }
  
  if (!proposal.category) {
    errors.push('Category is required');
  }
  
  if (!proposal.priority) {
    errors.push('Priority is required');
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Calculate governance health score
 */
export function calculateGovernanceHealth(metrics: {
  participation: number;
  decentralization: number;
  effectiveness: number;
  bias: number;
  transparency: number;
}): { score: number; grade: string; status: string } {
  const weights = {
    participation: 0.25,
    decentralization: 0.2,
    effectiveness: 0.25,
    bias: 0.15,
    transparency: 0.15
  };
  
  const score = 
    metrics.participation * weights.participation +
    metrics.decentralization * weights.decentralization +
    metrics.effectiveness * weights.effectiveness +
    (100 - metrics.bias) * weights.bias + // Invert bias score
    metrics.transparency * weights.transparency;
  
  let grade: string;
  let status: string;
  
  if (score >= 90) {
    grade = 'A';
    status = 'Excellent';
  } else if (score >= 80) {
    grade = 'B';
    status = 'Good';
  } else if (score >= 70) {
    grade = 'C';
    status = 'Fair';
  } else if (score >= 60) {
    grade = 'D';
    status = 'Poor';
  } else {
    grade = 'F';
    status = 'Critical';
  }
  
  return { score: Math.round(score), grade, status };
}

/**
 * Generate unique proposal ID
 */
export function generateProposalId(): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substr(2, 9);
  return `prop_${timestamp}_${random}`;
}

/**
 * Calculate quadratic vote weight
 */
export function calculateQuadraticWeight(tokensSpent: number, basePower: number): number {
  const sqrtTokens = Math.sqrt(tokensSpent);
  return sqrtTokens * basePower;
}

/**
 * Calculate conviction level decay
 */
export function calculateConvictionDecay(
  convictionLevel: number,
  timeSinceLastAction: number,
  decayRate: number = 0.01
): number {
  const decayPeriods = timeSinceLastAction / (24 * 60 * 60 * 1000); // Convert to days
  const decayAmount = convictionLevel * decayRate * decayPeriods;
  return Math.max(0, convictionLevel - decayAmount);
}

/**
 * Calculate delegation power
 */
export function calculateDelegationPower(
  ownStake: number,
  receivedDelegations: number,
  delegationMultiplier: number = 1.1
): number {
  return (ownStake + receivedDelegations) * delegationMultiplier;
}

/**
 * Format address for display
 */
export function formatAddress(address: string, length: number = 4): string {
  if (!address) return '';
  if (address.length <= length * 2 + 3) return address;
  return `${address.slice(0, length)}...${address.slice(-length)}`;
}

/**
 * Calculate voting power concentration (HHI)
 */
export function calculateConcentrationIndex(votingPowers: number[]): number {
  const total = votingPowers.reduce((sum, power) => sum + power, 0);
  if (total === 0) return 0;
  
  let hhi = 0;
  for (const power of votingPowers) {
    const share = power / total;
    hhi += share * share;
  }
  
  return hhi; // Returns value between 0 and 1
}

/**
 * Detect voting patterns
 */
export function detectVotingPattern(votes: Vote[]): {
  pattern: string;
  confidence: number;
  description: string;
} {
  if (votes.length < 3) {
    return {
      pattern: 'insufficient_data',
      confidence: 0,
      description: 'Not enough voting history to detect pattern'
    };
  }
  
  // Simple pattern detection - would be more sophisticated in real implementation
  const yesVotes = votes.filter(v => v.choice > 0).length;
  const noVotes = votes.filter(v => v.choice < 0).length;
  const abstainVotes = votes.filter(v => v.choice === 0).length;
  
  const total = votes.length;
  const yesRatio = yesVotes / total;
  const noRatio = noVotes / total;
  const abstainRatio = abstainVotes / total;
  
  if (yesRatio > 0.8) {
    return {
      pattern: 'yes_voter',
      confidence: yesRatio,
      description: 'Consistently votes Yes on proposals'
    };
  } else if (noRatio > 0.8) {
    return {
      pattern: 'no_voter',
      confidence: noRatio,
      description: 'Consistently votes No on proposals'
    };
  } else if (abstainRatio > 0.8) {
    return {
      pattern: 'abstain_voter',
      confidence: abstainRatio,
      description: 'Mainly abstains from voting'
    };
  } else {
    return {
      pattern: 'mixed_voter',
      confidence: 1 - Math.max(yesRatio, noRatio, abstainRatio),
      description: 'Votes variably across proposals'
    };
  }
}

/**
 * Calculate reputation score based on voting history
 */
export function calculateReputationScore(votes: Vote[]): number {
  if (votes.length === 0) return 500; // Default neutral score
  
  let participationScore = Math.min(votes.length * 10, 300);
  let consistencyScore = 0;
  let weightScore = 0;
  
  // Calculate consistency (how often they vote with majority)
  const majorityVotes = votes.filter(v => v.weight > 0);
  if (majorityVotes.length > 0) {
    const avgWeight = majorityVotes.reduce((sum, v) => sum + v.weight, 0) / majorityVotes.length;
    consistencyScore = Math.min(avgWeight * 50, 400);
  }
  
  // Calculate weight-based score
  const totalWeight = votes.reduce((sum, v) => sum + v.weight, 0);
  weightScore = Math.min(Math.log10(totalWeight + 1) * 100, 300);
  
  return Math.min(participationScore + consistencyScore + weightScore, 1000);
}

/**
 * Calculate effective voting power with all bonuses
 */
export function calculateEffectiveVotingPower(votingPower: VotingPower): number {
  const base = votingPower.basePower;
  const reputationBonus = base * (votingPower.reputationMultiplier - 1);
  const timeBonus = base * (votingPower.timeWeightedBonus - 1);
  const delegationBonus = base * votingPower.delegationBonus;
  
  const total = base + reputationBonus + timeBonus + delegationBonus;
  
  // Apply diminishing returns
  const diminishingFactor = 0.8;
  const maxPower = 10000;
  
  return Math.min(Math.pow(total, diminishingFactor), maxPower);
}

/**
 * Format currency amount
 */
export function formatCurrency(amount: number, decimals: number = 2): string {
  if (amount === 0) return '0';
  if (amount < 0.01) return '< 0.01';
  if (amount < 1000) return amount.toFixed(decimals);
  if (amount < 1000000) return (amount / 1000).toFixed(1) + 'K';
  if (amount < 1000000000) return (amount / 1000000).toFixed(1) + 'M';
  return (amount / 1000000000).toFixed(1) + 'B';
}

/**
 * Convert timestamp to readable date
 */
export function formatTimestamp(timestamp: number): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) {
    return 'Today';
  } else if (diffDays === 1) {
    return 'Yesterday';
  } else if (diffDays < 7) {
    return `${diffDays} days ago`;
  } else {
    return date.toLocaleDateString();
  }
}

/**
 * Validate Ethereum address
 */
export function isValidAddress(address: string): boolean {
  return ethers.isAddress(address);
}

/**
 * Calculate gas estimate for voting transaction
 */
export function estimateGas(method: string, parameters: any[]): number {
  // Mock gas estimation - would be more accurate with real contract ABI
  const gasEstimates: Record<string, number> = {
    simple_vote: 21000,
    quadratic_vote: 35000,
    conviction_vote: 42000,
    delegation_vote: 28000,
    holographic_vote: 65000,
    futarchy_vote: 55000
  };
  
  return gasEstimates[method] || 30000;
}