// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/Address.sol";

import "../interfaces/IDAO.sol";
import "../interfaces/IGovernanceToken.sol";
import "../interfaces/ITreasury.sol";
import "../interfaces/IVoting.sol";

/**
 * @title DAO Contract - Decentralized Autonomous Organization asosiy boshqaruvi
 * @notice DAO'ning markaziy boshqaruv contract'i
 */
contract DAO is IDAO, Ownable, ReentrancyGuard, Pausable {
    using SafeMath for uint256;
    using Address for address;

    // DAO strukturalari
    mapping(address => Member) public members;
    mapping(bytes32 => Proposal) public proposals;
    mapping(address => mapping(address => bool)) public delegates; // delegator => delegatee
    mapping(address => address) public delegationTo; // delegator => delegatee
    mapping(address => uint256) public delegatedVotingPower;
    
    uint256[] public proposalIds;
    uint256 public memberCount;
    uint256 public proposalCount;
    uint256 public totalVotingPower;
    
    // Konfiguratsiya
    uint256 public quorum = 1000000; // 1M voting power
    uint256 public votingPeriod = 604800; // 7 days
    uint256 public timelockDelay = 86400; // 1 day
    uint256 public maxProposalsPerMember = 5;
    
    // Adminlar va roles
    mapping(address => bool) public isAdmin;
    mapping(string => bool) public roles;
    mapping(string => mapping(address => bool)) public roleMembers;
    
    // Emergency
    bool public emergencyMode;
    uint256 public lastEmergencyAction;
    uint256 public emergencyCooldown = 3600; // 1 hour
    address public guardianAddress;
    
    // Events
    event AdminAdded(address indexed admin);
    event AdminRemoved(address indexed admin);
    event RoleCreated(string indexed role, string description);
    event MemberRoleUpdated(address indexed member, string newRole);
    event DelegationUpdated(address indexed from, address indexed to);
    event EmergencyActivated(string reason);
    event EmergencyDeactivated(string reason);
    event QuorumUpdated(uint256 oldQuorum, uint256 newQuorum);
    event VotingPeriodUpdated(uint256 oldPeriod, uint256 newPeriod);

    // Modifier
    modifier onlyAdmin() {
        require(isAdmin[msg.sender] || owner() == msg.sender, "Not admin");
        _;
    }

    modifier onlyGuardian() {
        require(msg.sender == guardianAddress || owner() == msg.sender, "Not guardian");
        _;
    }

    modifier onlyMember() {
        require(members[msg.sender].active, "Not a member");
        _;
    }

    modifier validProposalId(uint256 _proposalId) {
        require(proposals[keccak256(abi.encode(_proposalId))].id != 0, "Invalid proposal");
        _;
    }

    modifier notEmergency() {
        require(!emergencyMode, "Emergency mode active");
        _;
    }

    constructor() {
        isAdmin[msg.sender] = true;
        guardianAddress = msg.sender;
        
        // Default roles
        roles["admin"] = true;
        roles["member"] = true;
        roles["delegate"] = true;
        roles["treasury_manager"] = true;
        roles["proposer"] = true;
        
        roleMembers["admin"][msg.sender] = true;
    }

    // ===== MEMBER MANAGEMENT =====

    /**
     * @dev Yangi a'zoni qo'shish
     */
    function addMember(address _member, string memory _role) external onlyAdmin {
        require(_member != address(0), "Invalid address");
        require(members[_member].member == address(0), "Already member");
        require(roles[_role], "Invalid role");

        members[_member] = Member({
            member: _member,
            active: true,
            joinDate: block.timestamp,
            votingPower: 1000, // Default voting power
            role: _role,
            isDelegate: false
        });

        roleMembers[_role][_member] = true;
        totalVotingPower = totalVotingPower.add(1000);
        memberCount++;

        emit MemberAdded(_member, _role);
        emit MemberRoleUpdated(_member, _role);
    }

    /**
     * @dev A'zoni olib tashlash
     */
    function removeMember(address _member) external onlyAdmin {
        require(members[_member].member != address(0), "Not a member");
        
        Member storage member = members[_member];
        totalVotingPower = totalVotingPower.sub(member.votingPower);
        
        roleMembers[member.role][_member] = false;
        member.active = false;
        memberCount--;

        emit MemberRemoved(_member);
    }

    /**
     * @dev A'zoning role va voting power'ini yangilash
     */
    function updateMember(address _member, string memory _newRole) external onlyAdmin {
        require(members[_member].member != address(0), "Not a member");
        require(roles[_newRole], "Invalid role");

        Member storage member = members[_member];
        roleMembers[member.role][_member] = false;
        roleMembers[_newRole][_member] = true;
        member.role = _newRole;
        
        // Update voting power based on role
        uint256 oldPower = member.votingPower;
        member.votingPower = getVotingPowerByRole(_newRole);
        
        if (member.votingPower > oldPower) {
            totalVotingPower = totalVotingPower.add(member.votingPower.sub(oldPower));
        } else {
            totalVotingPower = totalVotingPower.sub(oldPower.sub(member.votingPower));
        }

        emit MemberUpdated(_member, _newRole, member.votingPower);
    }

    /**
     * @dev A'zo ma'lumotlarini olish
     */
    function getMember(address _member) external view override returns (Member memory) {
        return members[_member];
    }

    /**
     * @dev A'zolar sonini olish
     */
    function getMemberCount() external view override returns (uint256) {
        return memberCount;
    }

    /**
     * @dev A'zo ekanligini tekshirish
     */
    function isMember(address _member) external view override returns (bool) {
        return members[_member].active;
    }

    // ===== PROPOSAL MANAGEMENT =====

    /**
     * @dev Yangi taklif yaratish
     */
    function createProposal(
        string memory _title,
        string memory _description,
        bytes memory _data,
        VotingType _votingType,
        uint256 _votingPeriod,
        uint256 _votingPowerRequired
    ) external override onlyMember notEmergency returns (uint256) {
        // Proposal limit check
        require(getUserProposalCount(msg.sender) < maxProposalsPerMember, "Proposal limit reached");

        proposalCount++;
        uint256 proposalId = proposalCount;
        bytes32 proposalHash = keccak256(abi.encode(proposalId));

        proposals[proposalHash] = Proposal({
            id: proposalId,
            title: _title,
            description: _description,
            proposer: msg.sender,
            startTime: block.timestamp,
            endTime: block.timestamp.add(_votingPeriod > 0 ? _votingPeriod : votingPeriod),
            votingPowerRequired: _votingPowerRequired > 0 ? _votingPowerRequired : quorum,
            votesFor: 0,
            votesAgainst: 0,
            votesAbstain: 0,
            delegationVotes: 0,
            executed: false,
            cancelled: false,
            data: _data
        });

        proposalIds.push(proposalId);

        emit ProposalCreated(proposalId, msg.sender, _title);
        return proposalId;
    }

    /**
     * @dev Ovoz berish
     */
    function castVote(uint256 _proposalId, uint8 support) external override onlyMember nonReentrant {
        bytes32 proposalHash = keccak256(abi.encode(_proposalId));
        Proposal storage proposal = proposals[proposalHash];
        
        require(proposal.id != 0, "Invalid proposal");
        require(!proposal.cancelled && !proposal.executed, "Proposal not active");
        require(block.timestamp >= proposal.startTime && block.timestamp <= proposal.endTime, "Voting closed");
        require(support <= 2, "Invalid support value");

        // Check if user has already voted
        require(!hasVoted(proposalHash, msg.sender), "Already voted");

        uint256 votingPower = getVotingPower(msg.sender);

        // Apply vote
        if (support == 0) {
            proposal.votesAgainst = proposal.votesAgainst.add(votingPower);
        } else if (support == 1) {
            proposal.votesFor = proposal.votesFor.add(votingPower);
        } else {
            proposal.votesAbstain = proposal.votesAbstain.add(votingPower);
        }

        emit VoteCast(msg.sender, _proposalId, support, votingPower);
    }

    /**
     * @dev Taklifni bajarish
     */
    function executeProposal(uint256 _proposalId) external override onlyAdmin nonReentrant {
        bytes32 proposalHash = keccak256(abi.encode(_proposalId));
        Proposal storage proposal = proposals[proposalHash];
        
        require(proposal.id != 0, "Invalid proposal");
        require(!proposal.executed && !proposal.cancelled, "Already executed/cancelled");
        require(block.timestamp > proposal.endTime, "Voting not ended");
        
        // Check if proposal succeeded
        require(proposal.votesFor > proposal.votesAgainst, "Proposal failed");
        require(proposal.votesFor >= proposal.votingPowerRequired, "Quorum not reached");

        // Timelock delay
        require(block.timestamp >= proposal.endTime.add(timelockDelay), "Timelock period");

        // Execute the proposal
        proposal.executed = true;
        
        // Here you would typically call the actual function being proposed
        // This is a simplified version
        if (proposal.data.length > 0) {
            _executeTransaction(proposal.data);
        }

        emit ProposalExecuted(_proposalId);
    }

    /**
     * @dev Taklifni bekor qilish
     */
    function cancelProposal(uint256 _proposalId) external override {
        bytes32 proposalHash = keccak256(abi.encode(_proposalId));
        Proposal storage proposal = proposals[proposalHash];
        
        require(proposal.id != 0, "Invalid proposal");
        require(!proposal.executed, "Already executed");
        require(msg.sender == proposal.proposer || isAdmin[msg.sender] || owner() == msg.sender, "Not authorized");

        proposal.cancelled = true;

        emit ProposalCreated(_proposalId, proposal.proposer, proposal.title); // Reuse event for cancellation
    }

    /**
     * @dev Taklif ma'lumotlarini olish
     */
    function getProposal(uint256 _proposalId) external view override returns (Proposal memory) {
        return proposals[keccak256(abi.encode(_proposalId))];
    }

    /**
     * @dev Taklif holatini olish
     */
    function getProposalState(uint256 _proposalId) external view override returns (ProposalState) {
        bytes32 proposalHash = keccak256(abi.encode(_proposalId));
        Proposal storage proposal = proposals[proposalHash];
        
        if (proposal.id == 0) return ProposalState.Pending;
        if (proposal.cancelled) return ProposalState.Cancelled;
        if (proposal.executed) return ProposalState.Executed;
        if (block.timestamp < proposal.startTime) return ProposalState.Pending;
        if (block.timestamp > proposal.endTime) {
            if (proposal.votesFor < proposal.votingPowerRequired) return ProposalState.QuorumFailed;
            if (proposal.votesFor <= proposal.votesAgainst) return ProposalState.VotingFailed;
            return ProposalState.Succeeded;
        }
        
        return ProposalState.Active;
    }

    // ===== VOTING POWER FUNCTIONS =====

    /**
     * @dev Ovoz quvvatini olish
     */
    function getVotingPower(address _member) public view override returns (uint256) {
        Member storage member = members[_member];
        if (!member.active) return 0;

        uint256 basePower = member.votingPower;
        
        // Add delegated voting power
        basePower = basePower.add(delegatedVotingPower[_member]);
        
        return basePower;
    }

    /**
     * @dev Ovoz quvvatini topshirish
     */
    function delegateVoting(address _to) external override onlyMember {
        require(_to != msg.sender, "Cannot delegate to self");
        require(members[_to].active, "Delegate not active member");

        address currentDelegate = delegationTo[msg.sender];
        
        // Remove old delegation
        if (currentDelegate != address(0)) {
            delegatedVotingPower[currentDelegate] = delegatedVotingPower[currentDelegate].sub(getVotingPower(msg.sender));
            delegates[msg.sender][currentDelegate] = false;
        }

        // Set new delegation
        delegationTo[msg.sender] = _to;
        delegatedVotingPower[_to] = delegatedVotingPower[_to].add(getVotingPower(msg.sender));
        delegates[msg.sender][_to] = true;

        emit DelegationUpdated(msg.sender, _to);
    }

    /**
     * @dev Delegatsiyani bekor qilish
     */
    function undelegateVoting() external override onlyMember {
        address currentDelegate = delegationTo[msg.sender];
        require(currentDelegate != address(0), "No delegation");

        uint256 power = getVotingPower(msg.sender);
        delegatedVotingPower[currentDelegate] = delegatedVotingPower[currentDelegate].sub(power);
        delegates[msg.sender][currentDelegate] = false;
        delegationTo[msg.sender] = address(0);

        emit DelegationUpdated(msg.sender, address(0));
    }

    /**
     * @dev Umumiy ovoz quvvatini olish
     */
    function getTotalVotingPower() external view override returns (uint256) {
        return totalVotingPower;
    }

    // ===== STATISTICS =====

    /**
     * @dev Takliflar sonini olish
     */
    function getProposalCount() external view override returns (uint256) {
        return proposalCount;
    }

    /**
     * @dev Aktiv takliflar ro'yxati
     */
    function getActiveProposals() external view override returns (uint256[] memory) {
        uint256[] memory activeIds = new uint256[](proposalIds.length);
        uint256 count = 0;

        for (uint256 i = 0; i < proposalIds.length; i++) {
            ProposalState state = getProposalState(proposalIds[i]);
            if (state == ProposalState.Active || state == ProposalState.Pending) {
                activeIds[count] = proposalIds[i];
                count++;
            }
        }

        // Resize array
        uint256[] memory result = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = activeIds[i];
        }

        return result;
    }

    // ===== EMERGENCY FUNCTIONS =====

    /**
     * @dev Foydalanuvchi ovoz berganligini tekshirish
     */
    function hasVoted(bytes32 proposalHash, address voter) public view returns (bool) {
        // This would typically be stored in a mapping for efficiency
        // For simplicity, this is a placeholder
        return false;
    }

    /**
     * @dev Voting power by role
     */
    function getVotingPowerByRole(string memory _role) internal pure returns (uint256) {
        if (keccak256(abi.encodePacked(_role)) == keccak256(abi.encodePacked("admin"))) {
            return 10000;
        } else if (keccak256(abi.encodePacked(_role)) == keccak256(abi.encodePacked("treasury_manager"))) {
            return 5000;
        } else if (keccak256(abi.encodePacked(_role)) == keccak256(abi.encodePacked("delegate"))) {
            return 3000;
        } else if (keccak256(abi.encodePacked(_role)) == keccak256(abi.encodePacked("proposer"))) {
            return 2000;
        } else {
            return 1000; // Default member
        }
    }

    /**
     * @dev Get user proposal count
     */
    function getUserProposalCount(address _user) internal view returns (uint256) {
        uint256 count = 0;
        for (uint256 i = 0; i < proposalIds.length; i++) {
            if (proposals[keccak256(abi.encode(proposalIds[i]))].proposer == _user) {
                count++;
            }
        }
        return count;
    }

    /**
     * @dev Execute transaction data
     */
    function _executeTransaction(bytes memory data) internal {
        // This is a simplified implementation
        // In practice, you'd want to decode and execute the function call
        require(data.length > 0, "No transaction data");
    }

    /**
     * @dev Foydalanuvchi ovoz berganligini tekshirish (simplified)
     */
    function hasVoted(uint256 _proposalId, address _voter) public view override returns (bool) {
        return hasVoted(keccak256(abi.encode(_proposalId)), _voter);
    }

    // ===== GOVERNANCE FUNCTIONS =====

    /**
     * @dev Quorum'ni yangilash
     */
    function updateQuorum(uint256 _newQuorum) external onlyAdmin {
        require(_newQuorum > 0, "Quorum must be positive");
        uint256 oldQuorum = quorum;
        quorum = _newQuorum;
        emit QuorumUpdated(oldQuorum, _newQuorum);
    }

    /**
     * @dev Ovoz berish davri uzunligini yangilash
     */
    function updateVotingPeriod(uint256 _newPeriod) external onlyAdmin {
        require(_newPeriod >= 86400, "Minimum 1 day"); // Minimum 1 day
        uint256 oldPeriod = votingPeriod;
        votingPeriod = _newPeriod;
        emit VotingPeriodUpdated(oldPeriod, _newPeriod);
    }

    /**
     * @dev Yangilik qoidalarini yangilash
     */
    function updateGovernanceRules(bytes memory _newRules) external onlyAdmin {
        // Implement governance rules update logic
        // This could include updating voting mechanisms, proposal limits, etc.
    }

    /**
     * @dev Emergency pause
     */
    function emergencyPause() external override onlyGuardian {
        require(!emergencyMode, "Already in emergency");
        require(block.timestamp >= lastEmergencyAction.add(emergencyCooldown), "Cooldown active");
        
        emergencyMode = true;
        _pause();
        lastEmergencyAction = block.timestamp;
        
        emit EmergencyActivated("Emergency pause activated");
    }

    /**
     * @dev Emergency unpause
     */
    function emergencyUnpause() external override onlyGuardian {
        require(emergencyMode, "Not in emergency");
        
        emergencyMode = false;
        _unpause();
        
        emit EmergencyDeactivated("Emergency pause deactivated");
    }

    /**
     * @dev Emergency transfer
     */
    function emergencyTransfer(address _to, uint256 _amount, string memory _reason) external override onlyGuardian {
        require(emergencyMode, "Not in emergency mode");
        require(_to != address(0), "Invalid address");
        
        // Emergency transfer logic would go here
        // This could be used to move funds to safe addresses during emergencies
        
        emit TreasuryWithdrawal(_to, _amount, _reason);
    }

    /**
     * @dev Add admin
     */
    function addAdmin(address _admin) external onlyOwner {
        require(_admin != address(0), "Invalid address");
        require(!isAdmin[_admin], "Already admin");
        
        isAdmin[_admin] = true;
        emit AdminAdded(_admin);
    }

    /**
     * @dev Remove admin
     */
    function removeAdmin(address _admin) external onlyOwner {
        require(isAdmin[_admin], "Not admin");
        require(_admin != owner(), "Cannot remove owner");
        
        isAdmin[_admin] = false;
        emit AdminRemoved(_admin);
    }

    /**
     * @dev Set guardian address
     */
    function setGuardianAddress(address _guardian) external onlyOwner {
        require(_guardian != address(0), "Invalid address");
        guardianAddress = _guardian;
    }
}