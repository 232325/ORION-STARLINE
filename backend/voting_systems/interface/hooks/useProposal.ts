/**
 * @file useProposal.ts
 * @description Hook for managing proposals
 * @author Advanced Voting Systems
 */

import { useState, useEffect, useCallback } from 'react';
import { Proposal, ProposalStage } from '../types/VotingTypes';

export function useProposal(proposalId: string) {
  const [proposal, setProposal] = useState<Proposal | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (proposalId) {
      loadProposal();
    }
  }, [proposalId]);

  const loadProposal = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Mock implementation - would fetch from API/contracts
      const mockProposal: Proposal = {
        id: proposalId,
        title: 'Increase Treasury Allocation for Development',
        description: 'This proposal aims to increase the treasury allocation for development initiatives from 10% to 15% of total treasury holdings. This will enable faster development of core features and improve the overall user experience.',
        proposer: '0x1234567890123456789012345678901234567890',
        createdAt: Date.now() - 86400000,
        currentStage: ProposalStage.VOTING,
        stages: [],
        submittedForVoting: true,
        votingStarted: true,
        executed: false,
        rejected: false,
        category: 'treasury',
        priority: 'high',
        tags: ['treasury', 'development', 'funding'],
        attachments: [],
        relatedProposals: [],
        discussionOpen: true,
        comments: [],
        amendments: [],
        votingSystem: 'quadratic',
        votingPower: {
          basePower: 100,
          reputationMultiplier: 1.2,
          timeWeightedBonus: 1.1,
          delegationBonus: 0.1,
          convictionLevel: 75,
          totalPower: 145
        },
        voteSettings: {
          minQuorum: 1000,
          supportThreshold: 0.6,
          votingPeriod: 7 * 24 * 60 * 60,
          executionDelay: 24 * 60 * 60
        },
        votes: new Map(),
        result: {
          finalDecision: 0,
          totalVotes: 156,
          weightedVotes: 2340,
          participationRate: 0.68,
          quorumMet: true,
          supportThresholdMet: false,
          systemBreakdown: new Map()
        }
      };

      setProposal(mockProposal);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load proposal');
    } finally {
      setIsLoading(false);
    }
  };

  const refreshProposal = useCallback(() => {
    loadProposal();
  }, [proposalId]);

  const submitAmendment = async (description: string, changes: any[]) => {
    if (!proposal) return;

    try {
      // Mock implementation - would call contract
      console.log('Submitting amendment:', { description, changes });
      
      // Update local state
      const updatedProposal = {
        ...proposal,
        amendments: [
          ...proposal.amendments,
          {
            id: `amend_${Date.now()}`,
            proposer: 'current_user',
            description,
            changes,
            status: 'pending',
            votes: new Map(),
            createdAt: Date.now()
          }
        ]
      };

      setProposal(updatedProposal);
      return { success: true, amendmentId: `amend_${Date.now()}` };
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to submit amendment');
    }
  };

  const voteOnAmendment = async (amendmentId: string, support: number) => {
    if (!proposal) return;

    try {
      // Mock implementation - would call contract
      console.log('Voting on amendment:', { amendmentId, support });
      
      // Update local state
      const updatedProposal = {
        ...proposal,
        amendments: proposal.amendments.map(amendment =>
          amendment.id === amendmentId
            ? { ...amendment, votes: new Map(amendment.votes.set('current_user', support)) }
            : amendment
        )
      };

      setProposal(updatedProposal);
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to vote on amendment');
    }
  };

  const addComment = async (content: string, parentId?: string) => {
    if (!proposal) return;

    try {
      // Mock implementation - would call API
      const newComment = {
        id: `comment_${Date.now()}`,
        author: 'current_user',
        content,
        timestamp: Date.now(),
        replies: [],
        likes: [],
        weight: 10,
        isOfficial: false,
        parentId
      };

      const updatedProposal = {
        ...proposal,
        comments: parentId
          ? updateCommentWithReply(proposal.comments, parentId, newComment)
          : [...proposal.comments, newComment]
      };

      setProposal(updatedProposal);
      return { success: true, commentId: newComment.id };
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to add comment');
    }
  };

  const updateCommentWithReply = (comments: any[], parentId: string, reply: any): any[] => {
    return comments.map(comment => {
      if (comment.id === parentId) {
        return {
          ...comment,
          replies: [...comment.replies, reply]
        };
      } else if (comment.replies.length > 0) {
        return {
          ...comment,
          replies: updateCommentWithReply(comment.replies, parentId, reply)
        };
      }
      return comment;
    });
  };

  const likeComment = async (commentId: string) => {
    if (!proposal) return;

    try {
      // Mock implementation
      const updatedProposal = {
        ...proposal,
        comments: updateCommentLikes(proposal.comments, commentId, 'current_user')
      };

      setProposal(updatedProposal);
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to like comment');
    }
  };

  const updateCommentLikes = (comments: any[], commentId: string, user: string): any[] => {
    return comments.map(comment => {
      if (comment.id === commentId) {
        const likes = new Set(comment.likes || []);
        if (likes.has(user)) {
          likes.delete(user);
        } else {
          likes.add(user);
        }
        return { ...comment, likes: Array.from(likes) };
      } else if (comment.replies.length > 0) {
        return {
          ...comment,
          replies: updateCommentLikes(comment.replies, commentId, user)
        };
      }
      return comment;
    });
  };

  const getProposalAge = (): string => {
    if (!proposal) return '';
    
    const now = Date.now();
    const age = now - proposal.createdAt;
    const days = Math.floor(age / (1000 * 60 * 60 * 24));
    const hours = Math.floor((age % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
    return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  };

  const isVotingActive = (): boolean => {
    if (!proposal) return false;
    
    const now = Date.now();
    const endTime = proposal.createdAt + (proposal.voteSettings?.votingPeriod || 0);
    return now < endTime && proposal.currentStage === ProposalStage.VOTING;
  };

  const getTimeRemaining = (): string => {
    if (!proposal || !isVotingActive()) return '';
    
    const now = Date.now();
    const endTime = proposal.createdAt + (proposal.voteSettings?.votingPeriod || 0);
    const remaining = endTime - now;
    
    const days = Math.floor(remaining / (1000 * 60 * 60 * 24));
    const hours = Math.floor((remaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (days > 0) return `${days}d ${hours}h`;
    return `${hours}h`;
  };

  const canUserVote = (userAddress: string): boolean => {
    if (!proposal || !isVotingActive()) return false;
    
    // Check if user has already voted
    return !proposal.votes.has(userAddress);
  };

  const getProposalProgress = (): number => {
    if (!proposal) return 0;
    
    const now = Date.now();
    const startTime = proposal.createdAt;
    const endTime = startTime + (proposal.voteSettings?.votingPeriod || 0);
    
    if (now >= endTime) return 100;
    if (now <= startTime) return 0;
    
    return ((now - startTime) / (endTime - startTime)) * 100;
  };

  return {
    proposal,
    isLoading,
    error,
    refreshProposal,
    submitAmendment,
    voteOnAmendment,
    addComment,
    likeComment,
    getProposalAge,
    isVotingActive,
    getTimeRemaining,
    canUserVote,
    getProposalProgress
  };
}