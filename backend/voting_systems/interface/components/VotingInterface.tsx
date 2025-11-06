/**
 * @file VotingInterface.tsx
 * @description Web3 Voting Interface for Advanced Voting Systems
 * @author Advanced Voting Systems
 */

import React, { useState, useEffect } from 'react';
import { useWeb3React } from '@web3-react/core';
import { ethers } from 'ethers';
import { VotingSystem, Proposal, VotingPower } from '../types/VotingTypes';
import { useVotingPower } from '../hooks/useVotingPower';
import { useProposal } from '../hooks/useProposal';
import { useVoting } from '../hooks/useVoting';

interface VotingInterfaceProps {
  proposalId: string;
  votingSystem: VotingSystem;
  onVote?: (proposalId: string, choice: number, metadata?: any) => void;
}

export const VotingInterface: React.FC<VotingInterfaceProps> = ({
  proposalId,
  votingSystem,
  onVote
}) => {
  const { account, library } = useWeb3React();
  const { votingPower, isLoading: powerLoading } = useVotingPower(account, proposalId);
  const { proposal, isLoading: proposalLoading } = useProposal(proposalId);
  const { castVote, isVoting } = useVoting();

  const [selectedChoice, setSelectedChoice] = useState<number>(0);
  const [tokensToSpend, setTokensToSpend] = useState<string>('');
  const [conditionalStatement, setConditionalStatement] = useState<string>('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    // Reset form when proposal changes
    setSelectedChoice(0);
    setTokensToSpend('');
    setConditionalStatement('');
  }, [proposalId]);

  const handleVote = async () => {
    if (!account || !proposal || isVoting) return;

    try {
      const metadata = {
        tokensSpent: tokensToSpend ? ethers.parseEther(tokensToSpend) : 0,
        conditionalStatement,
        timestamp: Date.now()
      };

      await castVote(proposalId, selectedChoice, votingSystem, metadata);
      onVote?.(proposalId, selectedChoice, metadata);
      
      // Reset form
      setSelectedChoice(0);
      setTokensToSpend('');
      setConditionalStatement('');
    } catch (error) {
      console.error('Voting failed:', error);
    }
  };

  const calculateVoteWeight = (choice: number): number => {
    if (!votingPower) return 0;
    
    const baseWeight = votingPower.totalPower;
    const tokensSpent = tokensToSpend ? parseFloat(tokensToSpend) : 0;
    
    switch (votingSystem) {
      case VotingSystem.QUADRATIC:
        return Math.sqrt(tokensSpent) * baseWeight;
      case VotingSystem.CONVICTION:
        return votingPower.reputationMultiplier * votingPower.convictionLevel * baseWeight;
      case VotingSystem.DELEGATED_DPOS:
        return votingPower.delegationBonus * baseWeight;
      case VotingSystem.HOLOGRAPHIC:
        return votingPower.timeWeightedBonus * baseWeight;
      case VotingSystem.FUTARCHY:
        return votingPower.reputationMultiplier * baseWeight;
      default:
        return baseWeight;
    }
  };

  if (proposalLoading || powerLoading) {
    return (
      <div className="animate-pulse">
        <div className="bg-gray-200 h-8 w-3/4 mb-4 rounded"></div>
        <div className="bg-gray-200 h-20 w-full mb-4 rounded"></div>
        <div className="bg-gray-200 h-12 w-1/2 rounded"></div>
      </div>
    );
  }

  if (!proposal) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">Proposal not found</p>
      </div>
    );
  }

  if (!account) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">Please connect your wallet to vote</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      {/* Proposal Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{proposal.title}</h2>
        <div className="flex items-center space-x-4 text-sm text-gray-600">
          <span>Category: {proposal.category}</span>
          <span>Priority: {proposal.priority}</span>
          <span>Stage: {proposal.currentStage}</span>
        </div>
      </div>

      {/* Voting System Info */}
      <div className="mb-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-semibold text-blue-900 mb-2">
          {getVotingSystemName(votingSystem)}
        </h3>
        <p className="text-blue-700 text-sm">
          {getVotingSystemDescription(votingSystem)}
        </p>
        {votingPower && (
          <div className="mt-2 text-sm text-blue-600">
            <p>Your Voting Power: {votingPower.totalPower.toFixed(2)}</p>
            <p>Reputation Bonus: {(votingPower.reputationMultiplier * 100).toFixed(1)}%</p>
            <p>Time-weighted Bonus: {(votingPower.timeWeightedBonus * 100).toFixed(1)}%</p>
          </div>
        )}
      </div>

      {/* Vote Options */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Cast Your Vote</h3>
        
        <div className="grid grid-cols-3 gap-4 mb-4">
          {[
            { choice: -1, label: 'No', color: 'red', icon: '✗' },
            { choice: 0, label: 'Abstain', color: 'gray', icon: '○' },
            { choice: 1, label: 'Yes', color: 'green', icon: '✓' }
          ].map(({ choice, label, color, icon }) => (
            <button
              key={choice}
              onClick={() => setSelectedChoice(choice)}
              className={`p-4 border-2 rounded-lg transition-all ${
                selectedChoice === choice
                  ? `border-${color}-500 bg-${color}-50`
                  : `border-${color}-200 hover:border-${color}-300`
              }`}
            >
              <div className="text-center">
                <div className={`text-2xl mb-2 ${
                  selectedChoice === choice ? `text-${color}-600` : `text-${color}-400`
                }`}>
                  {icon}
                </div>
                <div className={`font-semibold ${
                  selectedChoice === choice ? `text-${color}-900` : `text-${color}-700`
                }`}>
                  {label}
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  Weight: {calculateVoteWeight(choice).toFixed(2)}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* System-specific inputs */}
      {votingSystem === VotingSystem.QUADRATIC && (
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tokens to Spend (Square root affects your vote weight)
          </label>
          <input
            type="number"
            value={tokensToSpend}
            onChange={(e) => setTokensToSpend(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter tokens to spend"
            max={votingPower?.basePower || 0}
          />
          <p className="text-xs text-gray-500 mt-1">
            Vote weight = √(tokens spent) × voting power
          </p>
        </div>
      )}

      {/* Conditional Voting */}
      {showAdvanced && (
        <div className="mb-4 p-4 bg-gray-50 rounded-lg">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Conditional Statement (Optional)
          </label>
          <textarea
            value={conditionalStatement}
            onChange={(e) => setConditionalStatement(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            rows={3}
            placeholder="IF [condition] THEN [action]"
          />
          <p className="text-xs text-gray-500 mt-1">
            Create conditional votes based on specific outcomes
          </p>
        </div>
      )}

      {/* Advanced Options Toggle */}
      <div className="mb-4">
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          {showAdvanced ? 'Hide' : 'Show'} Advanced Options
        </button>
      </div>

      {/* Voting Results Preview */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-semibold text-gray-900 mb-2">Your Vote Summary</h4>
        <div className="text-sm space-y-1">
          <p>Choice: {selectedChoice === -1 ? 'No' : selectedChoice === 0 ? 'Abstain' : 'Yes'}</p>
          <p>Estimated Weight: {calculateVoteWeight(selectedChoice).toFixed(2)}</p>
          {votingSystem === VotingSystem.QUADRATIC && tokensToSpend && (
            <p>Tokens to Spend: {tokensToSpend}</p>
          )}
          {conditionalStatement && (
            <p>Condition: {conditionalStatement}</p>
          )}
        </div>
      </div>

      {/* Submit Vote */}
      <div className="flex justify-between items-center">
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-blue-600 hover:text-blue-800"
        >
          Advanced Options
        </button>
        
        <button
          onClick={handleVote}
          disabled={isVoting || selectedChoice === 0}
          className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
            isVoting || selectedChoice === 0
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {isVoting ? 'Voting...' : 'Cast Vote'}
        </button>
      </div>

      {/* Voting Power Breakdown */}
      {votingPower && (
        <div className="mt-6 p-4 border rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-2">Your Voting Power Breakdown</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Base Power:</span>
              <span className="ml-2 font-medium">{votingPower.basePower.toFixed(2)}</span>
            </div>
            <div>
              <span className="text-gray-600">Reputation Bonus:</span>
              <span className="ml-2 font-medium">
                {(votingPower.reputationMultiplier * 100).toFixed(1)}%
              </span>
            </div>
            <div>
              <span className="text-gray-600">Time-weighted Bonus:</span>
              <span className="ml-2 font-medium">
                {(votingPower.timeWeightedBonus * 100).toFixed(1)}%
              </span>
            </div>
            <div>
              <span className="text-gray-600">Delegation Bonus:</span>
              <span className="ml-2 font-medium">
                {(votingPower.delegationBonus * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Helper functions
function getVotingSystemName(system: VotingSystem): string {
  const names = {
    [VotingSystem.SIMPLE]: 'Simple Majority Voting',
    [VotingSystem.QUADRATIC]: 'Quadratic Voting',
    [VotingSystem.CONVICTION]: 'Conviction Voting',
    [VotingSystem.DELEGATED_DPOS]: 'Delegated Proof of Stake',
    [VotingSystem.HOLOGRAPHIC]: 'Holographic Consensus',
    [VotingSystem.FUTARCHY]: 'Futarchy Prediction Markets',
    [VotingSystem.CONDITIONAL]: 'Conditional Voting'
  };
  return names[system] || 'Unknown System';
}

function getVotingSystemDescription(system: VotingSystem): string {
  const descriptions = {
    [VotingSystem.SIMPLE]: 'One token, one vote. Simple majority rule.',
    [VotingSystem.QUADRATIC]: 'Spend tokens to gain voting power. Power = √(tokens spent).',
    [VotingSystem.CONVICTION]: 'Long-term commitment determines voting influence.',
    [VotingSystem.DELEGATED_DPOS]: 'Vote with stake and receive delegation from others.',
    [VotingSystem.HOLOGRAPHIC]: 'Consensus across multiple SubDAOs using holographic weighting.',
    [VotingSystem.FUTARCHY]: 'Voting power based on prediction market accuracy.',
    [VotingSystem.CONDITIONAL]: 'Votes with if-then conditions based on other outcomes.'
  };
  return descriptions[system] || 'Unknown voting system description.';
}