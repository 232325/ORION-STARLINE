/**
 * @file useMobileVoting.ts
 * @description Mobile-specific voting hooks
 * @author Advanced Voting Systems
 */

import { useState, useEffect } from 'react';
import { Proposal, VotingSystem, MobileVote, BiometricData } from '../types/MobileTypes';

export function useMobileVoting() {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProposals();
  }, []);

  const loadProposals = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Mock data - would load from actual API/contracts
      const mockProposals: Proposal[] = [
        {
          id: 'prop_1',
          title: 'Increase Treasury Allocation for Development',
          description: 'Proposal to allocate 10% more of treasury funds for development initiatives.',
          proposer: '0x1234567890123456789012345678901234567890',
          createdAt: Date.now() - 86400000, // 1 day ago
          currentStage: 'voting',
          votingEndTime: Date.now() + 432000000, // 5 days from now
          category: 'treasury',
          priority: 'high',
          votingSystem: VotingSystem.QUADRATIC,
          status: 'active'
        },
        {
          id: 'prop_2',
          title: 'Implement Conviction Voting for Long-term Proposals',
          description: 'Transition certain proposals to conviction voting system.',
          proposer: '0x0987654321098765432109876543210987654321',
          createdAt: Date.now() - 172800000, // 2 days ago
          currentStage: 'discussion',
          votingEndTime: Date.now() + 604800000, // 7 days from now
          category: 'governance',
          priority: 'medium',
          votingSystem: VotingSystem.CONVICTION,
          status: 'active'
        }
      ];

      setProposals(mockProposals);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load proposals');
    } finally {
      setIsLoading(false);
    }
  };

  const vote = async (proposalId: string, choice: number, metadata: MobileVote['metadata']) => {
    try {
      // Mock voting process
      console.log('Casting vote:', { proposalId, choice, metadata });
      
      // In real implementation, this would:
      // 1. Verify biometric authentication
      // 2. Sign transaction with mobile wallet
      // 3. Send to blockchain
      // 4. Handle confirmation
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update local state
      setProposals(prev => prev.map(p => 
        p.id === proposalId 
          ? { ...p, userVote: choice }
          : p
      ));

      return { success: true, transactionHash: 'mock_tx_hash' };
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Voting failed');
    }
  };

  const getVotingPower = async (proposalId: string): Promise<number> => {
    // Mock calculation
    return 125.5 + Math.random() * 50;
  };

  const getProposalDetails = async (proposalId: string): Promise<Proposal | null> => {
    return proposals.find(p => p.id === proposalId) || null;
  };

  const getVotingHistory = async (): Promise<MobileVote[]> => {
    // Mock voting history
    return [
      {
        proposalId: 'prop_1',
        choice: 1,
        timestamp: Date.now() - 3600000,
        platform: 'mobile',
        biometricVerified: true
      }
    ];
  };

  const verifyBiometric = async (): Promise<BiometricData> => {
    // Mock biometric verification
    return {
      verified: true,
      method: 'fingerprint',
      confidence: 0.95,
      timestamp: Date.now()
    };
  };

  const getNotifications = async () => {
    // Mock notifications
    return [
      {
        id: 'notif_1',
        type: 'voting_reminder',
        title: 'Vote on Treasury Allocation Proposal',
        message: 'Your vote is needed on this important treasury decision',
        timestamp: Date.now() - 1800000,
        read: false,
        proposalId: 'prop_1'
      }
    ];
  };

  const markNotificationAsRead = async (notificationId: string) => {
    // Mark notification as read
    console.log('Notification marked as read:', notificationId);
  };

  const refreshProposals = () => {
    loadProposals();
  };

  const getActiveProposals = (): Proposal[] => {
    return proposals.filter(p => p.status === 'active' && p.currentStage !== 'executed');
  };

  const getCompletedProposals = (): Proposal[] => {
    return proposals.filter(p => p.status === 'completed' || p.currentStage === 'executed');
  };

  const getProposalsByCategory = (category: string): Proposal[] => {
    return proposals.filter(p => p.category === category);
  };

  const searchProposals = (query: string): Proposal[] => {
    const lowercaseQuery = query.toLowerCase();
    return proposals.filter(p => 
      p.title.toLowerCase().includes(lowercaseQuery) ||
      p.description.toLowerCase().includes(lowercaseQuery)
    );
  };

  return {
    proposals,
    isLoading,
    error,
    vote,
    getVotingPower,
    getProposalDetails,
    getVotingHistory,
    verifyBiometric,
    getNotifications,
    markNotificationAsRead,
    refreshProposals,
    getActiveProposals,
    getCompletedProposals,
    getProposalsByCategory,
    searchProposals
  };
}