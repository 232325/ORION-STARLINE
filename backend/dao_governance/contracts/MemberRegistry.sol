// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

import "../interfaces/IDAO.sol";

/**
 * @title MemberRegistry Contract - DAO A'zolar Ro'yxati va Boshqaruvi
 * @notice DAO a'zolarini ro'yxatga olish, role boshqaruvi va permission management
 */
contract MemberRegistry is IDAO, Ownable, ReentrancyGuard, Pausable {
    using SafeMath for uint256;
    using EnumerableSet for EnumerableSet.AddressSet;
    using Counters for Counters.Counter;

    // Strukturalar
    mapping(address => MemberInfo) public memberInfo;
    EnumerableSet.AddressSet private activeMembers;
    mapping(string => EnumerableSet.AddressSet) private roleMembers;
    mapping(address => mapping(address => bool)) public permissions;
    
    // Role permissions
    mapping(string => mapping(string => bool)) public rolePermissions;
    
    // Counter
    Counters.Counter private memberCounter;
    
    // Settings
    uint256 public maxMembers = 1000;
    uint256 public minStakingAmount = 1000;
    uint256 public memberVerificationPeriod = 86400; // 24 hours
    
    // Events
    event MemberVerified(address indexed member);
    event MemberSuspended(address indexed member, string reason);
    event MemberReinstated(address indexed member);
    event RolePermissionUpdated(string indexed role, string indexed permission, bool granted);
    event MemberKYCUpdated(address indexed member, bool verified, string kycLevel);

    // Modifiers
    modifier onlyActiveMember() {
        require(memberInfo[msg.sender].active, "Not an active member");
        _;
    }

    modifier validMember(address _member) {
        require(_member != address(0), "Invalid address");
        require(memberInfo[_member].member != address(0), "Member not found");
        _;
    }

    modifier validRole(string memory _role) {
        require(bytes(_role).length > 0, "Invalid role");
        _;
    }

    modifier notBlacklisted(address _member) {
        require(!memberInfo[_member].isBlacklisted, "Member is blacklisted");
        _;
    }

    constructor() {
        _initializeRoles();
    }

    // ===== MEMBER MANAGEMENT =====

    /**
     * @dev A'zo qo'shish
     */
    function addMember(address _member, string memory _role) 
        external 
        override 
        onlyOwner 
        nonReentrant 
        validMember(_member) 
        notBlacklisted(_member) 
    {
        require(activeMembers.length() < maxMembers, "Maximum members reached");
        require(!memberInfo[_member].active, "Already a member");
        require(_isValidRole(_role), "Invalid role");

        memberCounter.increment();
        
        memberInfo[_member] = MemberInfo({
            member: _member,
            active: true,
            joinDate: block.timestamp,
            votingPower: 1000, // Default voting power
            role: _role,
            isDelegate: false,
            lastActiveDate: block.timestamp,
            stakingAmount: 0,
            verificationStatus: VerificationStatus.Pending,
            kycLevel: "None",
            reputation: 0,
            isBlacklisted: false,
            suspensionDate: 0,
            notes: ""
        });

        activeMembers.add(_member);
        roleMembers[_role].add(_member);

        emit MemberAdded(_member, _role);
    }

    /**
     * @dev A'zoni olib tashlash
     */
    function removeMember(address _member) 
        external 
        override 
        onlyOwner 
        nonReentrant 
        validMember(_member) 
    {
        MemberInfo storage info = memberInfo[_member];
        
        activeMembers.remove(_member);
        roleMembers[info.role].remove(_member);
        
        info.active = false;
        
        emit MemberRemoved(_member);
    }

    /**
     * @dev A'zo ma'lumotlarini yangilash
     */
    function updateMember(address _member, string memory _newRole) 
        external 
        override 
        onlyOwner 
        nonReentrant 
        validMember(_member) 
        validRole(_newRole) 
    {
        MemberInfo storage info = memberInfo[_member];
        require(_isValidRole(_newRole), "Invalid new role");

        // Remove from old role
        roleMembers[info.role].remove(_member);
        
        // Add to new role
        roleMembers[_newRole].add(_member);
        
        // Update role and voting power
        info.role = _newRole;
        info.votingPower = _calculateVotingPowerByRole(_newRole, info.stakingAmount);
        
        emit MemberUpdated(_member, _newRole, info.votingPower);
    }

    /**
     * @dev A'zo ma'lumotlarini olish
     */
    function getMember(address _member) 
        external 
        view 
        override 
        validMember(_member) 
        returns (MemberInfo memory) 
    {
        return memberInfo[_member];
    }

    /**
     * @dev A'zolar sonini olish
     */
    function getMemberCount() external view override returns (uint256) {
        return activeMembers.length();
    }

    /**
     * @dev A'zo ekanligini tekshirish
     */
    function isMember(address _member) external view override returns (bool) {
        return memberInfo[_member].active;
    }

    /**
     * @dev A'zolarni ro'yxati
     */
    function getMembers(uint256 _offset, uint256 _limit) 
        external 
        view 
        returns (address[] memory members, MemberInfo[] memory info) 
    {
        uint256 totalMembers = activeMembers.length();
        uint256 end = _offset.add(_limit);
        if (end > totalMembers) end = totalMembers;
        
        members = new address[](end.sub(_offset));
        info = new MemberInfo[](end.sub(_offset));
        
        for (uint256 i = _offset; i < end; i++) {
            address member = activeMembers.at(i);
            members[i.sub(_offset)] = member;
            info[i.sub(_offset)] = memberInfo[member];
        }
    }

    /**
     * @dev A'zolarni role bo'yicha olish
     */
    function getMembersByRole(string memory _role) 
        external 
        view 
        validRole(_role) 
        returns (address[] memory members) 
    {
        uint256 roleMemberCount = roleMembers[_role].length();
        members = new address[](roleMemberCount);
        
        for (uint256 i = 0; i < roleMemberCount; i++) {
            members[i] = roleMembers[_role].at(i);
        }
    }

    // ===== ROLE MANAGEMENT =====

    /**
     * @dev Role yaratish
     */
    function createRole(string memory _role, string[] memory _permissions) 
        external 
        onlyOwner 
        validRole(_role) 
    {
        require(!_isValidRole(_role), "Role already exists");
        
        // Add basic permissions by default
        for (uint256 i = 0; i < _permissions.length; i++) {
            rolePermissions[_role][_permissions[i]] = true;
        }
        
        emit RoleCreated(_role, string(abi.encodePacked("Created with ", _permissions.length, " permissions")));
    }

    /**
     * @dev Role permission'ini yangilash
     */
    function updateRolePermission(
        string memory _role, 
        string memory _permission, 
        bool _granted
    ) 
        external 
        onlyOwner 
        validRole(_role) 
    {
        rolePermissions[_role][_permission] = _granted;
        emit RolePermissionUpdated(_role, _permission, _granted);
    }

    /**
     * @dev A'zoning permission'ini tekshirish
     */
    function hasPermission(address _member, string memory _permission) 
        external 
        view 
        returns (bool) 
    {
        if (msg.sender != owner() && msg.sender != _member) return false;
        
        MemberInfo memory info = memberInfo[_member];
        if (!info.active) return false;
        
        return rolePermissions[info.role][_permission];
    }

    // ===== VERIFICATION & KYC =====

    /**
     * @dev A'zo verification
     */
    function verifyMember(address _member) 
        external 
        onlyOwner 
        validMember(_member) 
        nonReentrant 
    {
        MemberInfo storage info = memberInfo[_member];
        info.verificationStatus = VerificationStatus.Verified;
        info.verificationDate = block.timestamp;
        
        emit MemberVerified(_member);
    }

    /**
     * @dev KYC ma'lumotlarini yangilash
     */
    function updateKYC(address _member, bool _verified, string memory _kycLevel) 
        external 
        onlyOwner 
        validMember(_member) 
        nonReentrant 
    {
        MemberInfo storage info = memberInfo[_member];
        info.kycLevel = _kycLevel;
        info.verificationStatus = _verified ? VerificationStatus.Verified : VerificationStatus.Pending;
        
        emit MemberKYCUpdated(_member, _verified, _kycLevel);
    }

    /**
     * @dev A'zoni suspend qilish
     */
    function suspendMember(address _member, string memory _reason) 
        external 
        onlyOwner 
        validMember(_member) 
        nonReentrant 
    {
        MemberInfo storage info = memberInfo[_member];
        info.active = false;
        info.suspensionDate = block.timestamp;
        info.notes = _reason;
        
        activeMembers.remove(_member);
        roleMembers[info.role].remove(_member);
        
        emit MemberSuspended(_member, _reason);
    }

    /**
     * @dev A'zoni qayta tiklash
     */
    function reinstateMember(address _member) 
        external 
        onlyOwner 
        validMember(_member) 
        nonReentrant 
    {
        MemberInfo storage info = memberInfo[_member];
        require(info.suspensionDate > 0, "Member not suspended");
        
        info.active = true;
        info.suspensionDate = 0;
        info.notes = "";
        
        activeMembers.add(_member);
        roleMembers[info.role].add(_member);
        
        emit MemberReinstated(_member);
    }

    // ===== STAKING INTEGRATION =====

    /**
     * @dev A'zo staking'ini yangilash
     */
    function updateStakingAmount(address _member, uint256 _amount) 
        external 
        onlyOwner 
        validMember(_member) 
    {
        MemberInfo storage info = memberInfo[_member];
        info.stakingAmount = _amount;
        
        // Recalculate voting power
        info.votingPower = _calculateVotingPowerByRole(info.role, _amount);
    }

    // ===== VOTING & DELEGATION =====

    /**
     * @dev Ovoz topshirish (delegatsiya)
     */
    function delegateVoting(address _to) 
        external 
        override 
        onlyActiveMember 
        validMember(_to) 
        nonReentrant 
    {
        require(_to != msg.sender, "Cannot delegate to self");
        
        MemberInfo storage delegator = memberInfo[msg.sender];
        MemberInfo storage delegatee = memberInfo[_to];
        
        require(delegatee.isDelegate || delegatee.role == "admin", "Recipient not authorized as delegate");
        require(delegator.verificationStatus == VerificationStatus.Verified, "Delegator not verified");
        
        // Remove old delegation if exists
        address currentDelegate = delegator.delegatedTo;
        if (currentDelegate != address(0)) {
            _removeDelegation(currentDelegate, msg.sender);
        }
        
        // Set new delegation
        _setDelegation(_to, msg.sender);
        
        emit DelegationCreated(msg.sender, _to);
    }

    /**
     * @dev Delegatsiyani bekor qilish
     */
    function undelegateVoting() 
        external 
        override 
        onlyActiveMember 
        nonReentrant 
    {
        address currentDelegate = memberInfo[msg.sender].delegatedTo;
        require(currentDelegate != address(0), "No active delegation");
        
        _removeDelegation(currentDelegate, msg.sender);
        
        emit DelegationRevoked(msg.sender, currentDelegate);
    }

    // ===== REPUTATION & METRICS =====

    /**
     * @dev A'zo reputation'ini yangilash
     */
    function updateReputation(address _member, int256 _change) 
        external 
        onlyOwner 
        validMember(_member) 
    {
        memberInfo[_member].reputation = uint256(int256(memberInfo[_member].reputation) + _change);
    }

    /**
     * @dev A'zo aktivlik qilganlik vaqtini yangilash
     */
    function updateLastActive(address _member) 
        external 
        validMember(_member) 
    {
        if (memberInfo[_member].active) {
            memberInfo[_member].lastActiveDate = block.timestamp;
        }
    }

    /**
     * @dev A'zo statistikasi
     */
    function getMemberStats() 
        external 
        view 
        returns (
            uint256 totalMembers,
            uint256 verifiedMembers,
            uint256 totalStaked,
            uint256 averageVotingPower,
            uint256 delegateCount
        ) 
    {
        totalMembers = activeMembers.length();
        totalStaked = 0;
        uint256 votingPowerSum = 0;
        delegateCount = 0;
        
        for (uint256 i = 0; i < activeMembers.length(); i++) {
            address member = activeMembers.at(i);
            MemberInfo memory info = memberInfo[member];
            
            if (info.verificationStatus == VerificationStatus.Verified) {
                verifiedMembers++;
            }
            
            totalStaked += info.stakingAmount;
            votingPowerSum += info.votingPower;
            
            if (info.isDelegate) {
                delegateCount++;
            }
        }
        
        averageVotingPower = totalMembers > 0 ? votingPowerSum / totalMembers : 0;
    }

    // ===== INTERNAL FUNCTIONS =====

    /**
     * @dev Role'ni tekshirish
     */
    function _isValidRole(string memory _role) internal pure returns (bool) {
        bytes32 roleHash = keccak256(abi.encodePacked(_role));
        
        return roleHash == keccak256(abi.encodePacked("admin")) ||
               roleHash == keccak256(abi.encodePacked("member")) ||
               roleHash == keccak256(abi.encodePacked("delegate")) ||
               roleHash == keccak256(abi.encodePacked("treasury_manager")) ||
               roleHash == keccak256(abi.encodePacked("proposer")) ||
               roleHash == keccak256(abi.encodePacked("verified")) ||
               roleHash == keccak256(abi.encodePacked("auditor"));
    }

    /**
     * @dev Voting power hisoblash
     */
    function _calculateVotingPowerByRole(string memory _role, uint256 _stakingAmount) 
        internal 
        pure 
        returns (uint256) 
    {
        uint256 basePower;
        
        if (keccak256(abi.encodePacked(_role)) == keccak256(abi.encodePacked("admin"))) {
            basePower = 10000;
        } else if (keccak256(abi.encodePacked(_role)) == keccak256(abi.encodePacked("treasury_manager"))) {
            basePower = 5000;
        } else if (keccak256(abi.encodePacked(_role)) == keccak256(abi.encodePacked("delegate"))) {
            basePower = 3000;
        } else if (keccak256(abi.encodePacked(_role)) == keccak256(abi.encodePacked("proposer"))) {
            basePower = 2000;
        } else if (keccak256(abi.encodePacked(_role)) == keccak256(abi.encodePacked("verified"))) {
            basePower = 1500;
        } else if (keccak256(abi.encodePacked(_role)) == keccak256(abi.encodePacked("auditor"))) {
            basePower = 1000;
        } else {
            basePower = 1000; // Default member
        }
        
        // Add staking bonus
        if (_stakingAmount >= minStakingAmount) {
            uint256 stakingBonus = _stakingAmount.div(100); // 1% bonus per 100 tokens
            return basePower.add(stakingBonus);
        }
        
        return basePower;
    }

    /**
     * @dev Delegatsiya o'rnatish
     */
    function _setDelegation(address _delegatee, address _delegator) internal {
        MemberInfo storage delegatee = memberInfo[_delegatee];
        MemberInfo storage delegator = memberInfo[_delegator];
        
        delegatee.delegatedFrom.add(_delegator);
        delegator.delegatedTo = _delegatee;
        delegatee.isDelegate = true;
    }

    /**
     * @dev Delegatsiyani olib tashlash
     */
    function _removeDelegation(address _delegatee, address _delegator) internal {
        MemberInfo storage delegatee = memberInfo[_delegatee];
        MemberInfo storage delegator = memberInfo[_delegator];
        
        delegatee.delegatedFrom.remove(_delegator);
        delegator.delegatedTo = address(0);
        
        // Check if delegatee still has delegators
        if (delegatee.delegatedFrom.length() == 0) {
            delegatee.isDelegate = false;
        }
    }

    /**
     * @dev Role'larni ishga tushirish
     */
    function _initializeRoles() internal {
        // Default roles are already created in constructor
        // This function can be extended for complex role hierarchies
    }

    // ===== ADMIN FUNCTIONS =====

    /**
     * @dev Max members limit'ini o'rnatish
     */
    function setMaxMembers(uint256 _maxMembers) external onlyOwner {
        require(_maxMembers > activeMembers.length(), "Cannot set below current members");
        maxMembers = _maxMembers;
    }

    /**
     * @dev Minimum staking amount'ni o'rnatish
     */
    function setMinStakingAmount(uint256 _minStaking) external onlyOwner {
        minStakingAmount = _minStaking;
    }

    /**
     * @dev Emergency pause
     */
    function emergencyPause() external onlyOwner {
        _pause();
    }

    /**
     * @dev Emergency unpause
     */
    function emergencyUnpause() external onlyOwner {
        _unpause();
    }
}