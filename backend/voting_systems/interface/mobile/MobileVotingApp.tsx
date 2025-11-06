/**
 * @file MobileVotingApp.tsx
 * @description Mobile Voting Application Interface
 * @author Advanced Voting Systems
 */

import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, Modal, Alert, TextInput } from 'react-native';
import { useWalletConnect } from '../hooks/useWalletConnect';
import { useMobileVoting } from '../hooks/useMobileVoting';
import { Proposal, VotingSystem, MobileVote } from '../types/MobileTypes';
import { LinearGradient } from 'expo-linear-gradient';

interface MobileVotingAppProps {
  proposalId?: string;
}

export const MobileVotingApp: React.FC<MobileVotingAppProps> = ({ proposalId }) => {
  const { wallet, connectWallet, disconnectWallet } = useWalletConnect();
  const { proposals, vote, getVotingPower, isLoading } = useMobileVoting();
  
  const [selectedProposal, setSelectedProposal] = useState<Proposal | null>(null);
  const [selectedChoice, setSelectedChoice] = useState<number>(0);
  const [votingPower, setVotingPower] = useState<number>(0);
  const [showProposalModal, setShowProposalModal] = useState(false);
  const [biometricVerified, setBiometricVerified] = useState(false);

  useEffect(() => {
    if (wallet && !biometricVerified) {
      verifyBiometric();
    }
  }, [wallet]);

  const verifyBiometric = async () => {
    // Biometric verification for mobile
    try {
      // Implementation would use platform-specific biometric APIs
      setBiometricVerified(true);
    } catch (error) {
      Alert.alert('Biometric Verification Failed', 'Please try again.');
    }
  };

  const handleVote = async (choice: number) => {
    if (!wallet || !selectedProposal || !biometricVerified) return;

    try {
      await vote(selectedProposal.id, choice, {
        timestamp: Date.now(),
        platform: 'mobile',
        biometricVerified
      });
      
      Alert.alert('Vote Cast', 'Your vote has been recorded successfully!');
      setSelectedProposal(null);
      setSelectedChoice(0);
    } catch (error) {
      Alert.alert('Voting Failed', 'Please try again.');
    }
  };

  const renderHeader = () => (
    <LinearGradient
      colors={['#4F46E5', '#7C3AED']}
      className="px-6 pt-12 pb-6"
    >
      <Text className="text-white text-2xl font-bold text-center">
        Advanced Voting
      </Text>
      <Text className="text-indigo-100 text-center mt-2">
        Mobile Governance Interface
      </Text>
      
      {wallet ? (
        <View className="mt-4 flex-row justify-between items-center">
          <View>
            <Text className="text-indigo-100 text-sm">Connected</Text>
            <Text className="text-white font-medium">
              {wallet.address.slice(0, 6)}...{wallet.address.slice(-4)}
            </Text>
          </View>
          <TouchableOpacity
            onPress={disconnectWallet}
            className="bg-white/20 px-4 py-2 rounded-lg"
          >
            <Text className="text-white text-sm">Disconnect</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <TouchableOpacity
          onPress={connectWallet}
          className="mt-4 bg-white/20 px-6 py-3 rounded-lg"
        >
          <Text className="text-white font-medium text-center">Connect Wallet</Text>
        </TouchableOpacity>
      )}
    </LinearGradient>
  );

  const renderProposalCard = (proposal: Proposal) => (
    <TouchableOpacity
      key={proposal.id}
      onPress={() => {
        setSelectedProposal(proposal);
        loadVotingPower(proposal.id);
        setShowProposalModal(true);
      }}
      className="mx-4 mb-4 bg-white rounded-xl shadow-lg overflow-hidden"
    >
      <View className="p-4">
        <View className="flex-row justify-between items-start mb-2">
          <Text className="text-lg font-semibold text-gray-900 flex-1">
            {proposal.title}
          </Text>
          <View className={`px-2 py-1 rounded-full ml-2 ${
            proposal.priority === 'critical' ? 'bg-red-100' :
            proposal.priority === 'high' ? 'bg-orange-100' :
            proposal.priority === 'medium' ? 'bg-yellow-100' : 'bg-gray-100'
          }`}>
            <Text className={`text-xs font-medium ${
              proposal.priority === 'critical' ? 'text-red-800' :
              proposal.priority === 'high' ? 'text-orange-800' :
              proposal.priority === 'medium' ? 'text-yellow-800' : 'text-gray-800'
            }`}>
              {proposal.priority.toUpperCase()}
            </Text>
          </View>
        </View>
        
        <Text className="text-gray-600 text-sm mb-3" numberOfLines={2}>
          {proposal.description}
        </Text>
        
        <View className="flex-row justify-between items-center">
          <View className="flex-row space-x-2">
            <Text className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
              {proposal.category}
            </Text>
            <Text className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
              {proposal.currentStage}
            </Text>
          </View>
          
          <Text className="text-xs text-gray-500">
            {new Date(proposal.createdAt).toLocaleDateString()}
          </Text>
        </View>
      </View>
      
      <View className="px-4 py-2 bg-gray-50 border-t border-gray-100">
        <Text className="text-xs text-gray-600">
          Time remaining: {getTimeRemaining(proposal.votingEndTime)}
        </Text>
      </View>
    </TouchableOpacity>
  );

  const renderVotingModal = () => (
    <Modal
      visible={showProposalModal}
      animationType="slide"
      presentationStyle="pageSheet"
    >
      <View className="flex-1 bg-white">
        <View className="px-4 py-6 border-b border-gray-200">
          <TouchableOpacity
            onPress={() => setShowProposalModal(false)}
            className="absolute right-4 top-6"
          >
            <Text className="text-gray-500 text-lg">✕</Text>
          </TouchableOpacity>
          
          <Text className="text-xl font-bold text-gray-900">
            {selectedProposal?.title}
          </Text>
          <Text className="text-gray-600 mt-1">
            Your Voting Power: {votingPower.toFixed(2)}
          </Text>
        </View>

        <ScrollView className="flex-1 p-4">
          <View className="mb-6">
            <Text className="text-gray-900 mb-3">{selectedProposal?.description}</Text>
            
            <View className="flex-row space-x-2 mb-4">
              <Text className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                {selectedProposal?.category}
              </Text>
              <Text className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                {getVotingSystemName(selectedProposal?.votingSystem || VotingSystem.SIMPLE)}
              </Text>
            </View>
          </View>

          <Text className="text-lg font-semibold text-gray-900 mb-4">
            Cast Your Vote
          </Text>

          <View className="space-y-3 mb-6">
            {[
              { choice: -1, label: 'No', color: '#EF4444', icon: '✗' },
              { choice: 0, label: 'Abstain', color: '#6B7280', icon: '○' },
              { choice: 1, label: 'Yes', color: '#10B981', icon: '✓' }
            ].map(({ choice, label, color, icon }) => (
              <TouchableOpacity
                key={choice}
                onPress={() => setSelectedChoice(choice)}
                className={`p-4 rounded-xl border-2 ${
                  selectedChoice === choice ? 'border-blue-500' : 'border-gray-200'
                }`}
                style={{
                  backgroundColor: selectedChoice === choice ? `${color}10` : 'white',
                  borderColor: selectedChoice === choice ? color : '#E5E7EB'
                }}
              >
                <View className="flex-row items-center">
                  <Text className="text-2xl mr-3" style={{ color }}>
                    {icon}
                  </Text>
                  <View className="flex-1">
                    <Text className="font-semibold" style={{ color }}>
                      {label}
                    </Text>
                    {selectedChoice === choice && (
                      <Text className="text-sm text-gray-600">
                        Weight: {getVoteWeight(choice).toFixed(2)}
                      </Text>
                    )}
                  </View>
                </View>
              </TouchableOpacity>
            ))}
          </View>

          {biometricVerified && (
            <TouchableOpacity
              onPress={() => handleVote(selectedChoice)}
              disabled={selectedChoice === 0}
              className={`py-4 rounded-xl ${
                selectedChoice === 0 ? 'bg-gray-300' : 'bg-blue-600'
              }`}
            >
              <Text className={`text-center font-semibold ${
                selectedChoice === 0 ? 'text-gray-500' : 'text-white'
              }`}>
                Cast Vote
              </Text>
            </TouchableOpacity>
          )}
          
          {!biometricVerified && (
            <TouchableOpacity
              onPress={verifyBiometric}
              className="py-4 rounded-xl bg-orange-600"
            >
              <Text className="text-center font-semibold text-white">
                Verify Identity to Vote
              </Text>
            </TouchableOpacity>
          )}
        </ScrollView>
      </View>
    </Modal>
  );

  const loadVotingPower = async (proposalId: string) => {
    if (!wallet) return;
    try {
      const power = await getVotingPower(proposalId);
      setVotingPower(power);
    } catch (error) {
      console.error('Failed to load voting power:', error);
    }
  };

  return (
    <View className="flex-1 bg-gray-50">
      {renderHeader()}
      
      {!wallet ? (
        <View className="flex-1 justify-center items-center px-6">
          <Text className="text-center text-gray-600 mb-6">
            Connect your wallet to start voting on proposals
          </Text>
          <TouchableOpacity
            onPress={connectWallet}
            className="bg-blue-600 px-8 py-4 rounded-xl"
          >
            <Text className="text-white font-semibold">Connect Wallet</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <ScrollView className="flex-1">
          <View className="py-4">
            <Text className="text-lg font-semibold text-gray-900 px-4 mb-4">
              Active Proposals ({proposals.length})
            </Text>
            
            {isLoading ? (
              <View className="px-4">
                {[...Array(3)].map((_, i) => (
                  <View key={i} className="bg-white rounded-xl p-4 mb-4 mx-4">
                    <View className="bg-gray-200 h-4 rounded mb-2 w-3/4"></View>
                    <View className="bg-gray-200 h-3 rounded mb-3 w-full"></View>
                    <View className="flex-row space-x-2">
                      <View className="bg-gray-200 h-6 w-16 rounded"></View>
                      <View className="bg-gray-200 h-6 w-20 rounded"></View>
                    </View>
                  </View>
                ))}
              </View>
            ) : proposals.length > 0 ? (
              proposals.map(renderProposalCard)
            ) : (
              <View className="px-6 py-12">
                <Text className="text-center text-gray-500">
                  No active proposals
                </Text>
              </View>
            )}
          </View>
        </ScrollView>
      )}
      
      {renderVotingModal()}
    </View>
  );
};

// Helper functions
function getTimeRemaining(endTime: number): string {
  const now = Date.now();
  const remaining = endTime - now;
  
  if (remaining <= 0) return 'Ended';
  
  const days = Math.floor(remaining / (1000 * 60 * 60 * 24));
  const hours = Math.floor((remaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((remaining % (1000 * 60 * 60)) / (1000 * 60));
  
  if (days > 0) return `${days}d ${hours}h`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
}

function getVotingSystemName(system: VotingSystem): string {
  const names = {
    [VotingSystem.SIMPLE]: 'Simple',
    [VotingSystem.QUADRATIC]: 'Quadratic',
    [VotingSystem.CONVICTION]: 'Conviction',
    [VotingSystem.DELEGATED_DPOS]: 'Delegated',
    [VotingSystem.HOLOGRAPHIC]: 'Holographic',
    [VotingSystem.FUTARCHY]: 'Futarchy',
    [VotingSystem.CONDITIONAL]: 'Conditional'
  };
  return names[system] || 'Unknown';
}

function getVoteWeight(choice: number): number {
  // Simplified weight calculation for mobile
  return Math.abs(choice) * 10;
}