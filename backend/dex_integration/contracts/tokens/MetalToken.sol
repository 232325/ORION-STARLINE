// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "../interfaces/tokens/IMetalTokens.sol";
import "../interfaces/IERC20.sol";
import "../utils/SafeMath.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @dev Implementation of ERC-20 fungible metal tokens with physical backing
 */
contract MetalToken is IMetalToken, IERC20, AccessControl, Pausable {
    using SafeMath for uint256;
    
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant CUSTODIAN_ROLE = keccak256("CUSTODIAN_ROLE");
    bytes32 public constant AUDITOR_ROLE = keccak256("AUDITOR_ROLE");
    bytes32 public constant COMPLIANCE_ROLE = keccak256("COMPLIANCE_ROLE");
    
    string private _name;
    string private _symbol;
    uint8 private constant _decimals = 18;
    
    // Mapping of metal types
    mapping(MetalType => MetalReserve) private _reserves;
    mapping(address => bool) private _frozenAccounts;
    mapping(address => mapping(address => uint256)) private _allowances;
    
    // Compliance tracking
    mapping(address => uint256) public kycVerificationTime;
    mapping(address => ComplianceStatus) public accountComplianceStatus;
    
    // Price oracle
    PriceInfo public currentPrice;
    address public priceOracle;
    
    // Events
    event MintRequestProcessed(address indexed requester, bool approved, string reason);
    event AccountFrozenWithReason(address indexed account, string reason);
    event KYCVerified(address indexed account, uint256 expiryDate);
    event ComplianceCheckFailed(address indexed from, address indexed to, uint256 amount, string reason);
    
    constructor(
        string memory name_,
        string memory symbol_,
        MetalType metalType_,
        address custodian_
    ) {
        _name = name_;
        _symbol = symbol_;
        
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(MINTER_ROLE, msg.sender);
        _setupRole(CUSTODIAN_ROLE, custodian_);
        _setupRole(AUDITOR_ROLE, msg.sender);
        _setupRole(COMPLIANCE_ROLE, msg.sender);
        
        // Initialize reserve for the specified metal type
        _reserves[metalType_] = MetalReserve({
            custodian: custodian_,
            totalPhysicalAmount: 0,
            tokenSupply: 0,
            isActive: true,
            lastAuditTime: block.timestamp,
            auditProof: bytes32(0)
        });
        
        currentPrice = PriceInfo({
            price: 0,
            timestamp: block.timestamp,
            oracle: address(0),
            isValid: false
        });
    }
    
    /**
     * @dev ERC-20 standard functions
     */
    function name() public view override returns (string memory) {
        return _name;
    }
    
    function symbol() public view override returns (string memory) {
        return _symbol;
    }
    
    function decimals() public pure override returns (uint8) {
        return _decimals;
    }
    
    function totalSupply() public view override returns (uint256) {
        uint256 total;
        for (uint256 i = 0; i < 6; i++) {
            MetalType metalType = MetalType(i);
            total = total.add(_reserves[metalType].tokenSupply);
        }
        return total;
    }
    
    function balanceOf(address account) public view override returns (uint256) {
        uint256 totalBalance = 0;
        for (uint256 i = 0; i < 6; i++) {
            MetalType metalType = MetalType(i);
            totalBalance = totalBalance.add(balanceOfMetal(account, metalType));
        }
        return totalBalance;
    }
    
    function balanceOfMetal(address account, MetalType metalType) public view returns (uint256) {
        // For simplicity, assuming each token represents a specific metal type
        // In a more complex implementation, you might have different token contracts for each metal
        return _balances[account];
    }
    
    function transfer(address to, uint256 amount) public override returns (bool) {
        return _transfer(msg.sender, to, amount);
    }
    
    function allowance(address owner, address spender) public view override returns (uint256) {
        return _allowances[owner][spender];
    }
    
    function approve(address spender, uint256 amount) public override returns (bool) {
        _approve(msg.sender, spender, amount);
        return true;
    }
    
    function transferFrom(address from, address to, uint256 amount) public override returns (bool) {
        uint256 currentAllowance = _allowances[from][msg.sender];
        require(currentAllowance >= amount, "ERC20: transfer amount exceeds allowance");
        
        _transfer(from, to, amount);
        _approve(from, msg.sender, currentAllowance.sub(amount));
        return true;
    }
    
    /**
     * @dev Metal-specific functions
     */
    function mintMetal(
        address to,
        uint256 amount,
        MetalType metalType,
        bytes32 proofOfReserve
    ) external override onlyRole(MINTER_ROLE) whenNotPaused returns (bool) {
        require(to != address(0), "Cannot mint to zero address");
        require(amount > 0, "Cannot mint zero amount");
        require(_reserves[metalType].isActive, "Reserve not active");
        
        // Verify reserve proof
        require(verifyReserve(proofOfReserve), "Invalid reserve proof");
        
        // Check compliance
        require(checkCompliance(address(0), to, amount), "Compliance check failed");
        
        // Update reserve
        _reserves[metalType].totalPhysicalAmount = _reserves[metalType].totalPhysicalAmount.add(amount);
        _reserves[metalType].tokenSupply = _reserves[metalType].tokenSupply.add(amount);
        
        // Mint tokens
        _mint(to, amount);
        
        emit MetalMinted(to, amount, metalType, proofOfReserve);
        return true;
    }
    
    function burnMetal(address from, uint256 amount) external override onlyRole(MINTER_ROLE) returns (bool) {
        require(from != address(0), "Cannot burn from zero address");
        require(amount > 0, "Cannot burn zero amount");
        require(balanceOf(from) >= amount, "Insufficient balance");
        
        // Find which metal type to burn (simplified)
        MetalType metalType = MetalType.GOLD; // This should be determined by token metadata
        
        // Check compliance
        require(checkCompliance(from, address(0), amount), "Compliance check failed");
        
        // Update reserve
        _reserves[metalType].totalPhysicalAmount = _reserves[metalType].totalPhysicalAmount.sub(amount);
        _reserves[metalType].tokenSupply = _reserves[metalType].tokenSupply.sub(amount);
        
        // Burn tokens
        _burn(from, amount);
        
        emit MetalBurned(from, amount, metalType);
        return true;
    }
    
    function withdrawPhysical(address to, uint256 amount) external override returns (bool) {
        require(_frozenAccounts[msg.sender] == false, "Account is frozen");
        require(checkCompliance(msg.sender, to, amount), "Compliance check failed");
        
        // Find appropriate metal type (simplified)
        MetalType metalType = MetalType.GOLD;
        require(_reserves[metalType].totalPhysicalAmount >= amount, "Insufficient physical reserves");
        
        // Update reserve
        _reserves[metalType].totalPhysicalAmount = _reserves[metalType].totalPhysicalAmount.sub(amount);
        _reserves[metalType].tokenSupply = _reserves[metalType].tokenSupply.sub(amount);
        
        // Burn tokens
        _burn(msg.sender, amount);
        
        emit PhysicalWithdrawal(to, amount, metalType);
        emit MetalBurned(msg.sender, amount, metalType);
        
        return true;
    }
    
    function depositPhysical(uint256 amount) external payable override returns (bool) {
        require(amount > 0, "Cannot deposit zero amount");
        require(msg.value >= 1000, "Insufficient gas deposit");
        
        // Find appropriate metal type (simplified)
        MetalType metalType = MetalType.GOLD;
        
        // Update reserve
        _reserves[metalType].totalPhysicalAmount = _reserves[metalType].totalPhysicalAmount.add(amount);
        _reserves[metalType].tokenSupply = _reserves[metalType].tokenSupply.add(amount);
        
        // Mint tokens
        _mint(msg.sender, amount);
        
        emit PhysicalDeposit(msg.sender, amount, metalType);
        emit MetalMinted(msg.sender, amount, metalType, bytes32(0));
        
        return true;
    }
    
    /**
     * @dev Reserve management functions
     */
    function getReserveInfo() external view override returns (MetalReserve memory) {
        MetalType metalType = MetalType.GOLD; // Simplified - should be determined by token metadata
        return _reserves[metalType];
    }
    
    function verifyReserve(bytes32 proofOfReserve) public view override returns (bool) {
        // Simplified verification - in practice, this would involve complex proof verification
        return proofOfReserve != bytes32(0);
    }
    
    function updateCustodian(address newCustodian) external override onlyRole(CUSTODIAN_ROLE) {
        require(newCustodian != address(0), "Invalid custodian address");
        MetalType metalType = MetalType.GOLD;
        address oldCustodian = _reserves[metalType].custodian;
        _reserves[metalType].custodian = newCustodian;
        emit CustodianUpdated(oldCustodian, newCustodian);
    }
    
    function auditReserve() external override onlyRole(AUDITOR_ROLE) {
        MetalType metalType = MetalType.GOLD;
        _reserves[metalType].lastAuditTime = block.timestamp;
        _reserves[metalType].auditProof = keccak256(abi.encode(block.timestamp, block.difficulty));
        emit ReserveAudited(block.timestamp, _reserves[metalType].auditProof);
    }
    
    /**
     * @dev Price management functions
     */
    function getCurrentPrice() external view override returns (PriceInfo memory) {
        return currentPrice;
    }
    
    function setPriceOracle(address oracle) external override onlyRole(DEFAULT_ADMIN_ROLE) {
        require(oracle != address(0), "Invalid oracle address");
        priceOracle = oracle;
    }
    
    function updatePrice(uint256 newPrice) external override {
        require(msg.sender == priceOracle || hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "Unauthorized");
        require(newPrice > 0, "Invalid price");
        
        currentPrice = PriceInfo({
            price: newPrice,
            timestamp: block.timestamp,
            oracle: msg.sender,
            isValid: true
        });
        
        emit PriceUpdated(newPrice, msg.sender);
    }
    
    /**
     * @dev Compliance functions
     */
    function isKYCVerified(address account) public view override returns (bool) {
        return accountComplianceStatus[account] == ComplianceStatus.KYC_APPROVED;
    }
    
    function checkCompliance(address from, address to, uint256 amount) public view override returns (bool) {
        // Simplified compliance check
        if (from != address(0) && _frozenAccounts[from]) return false;
        if (to != address(0) && _frozenAccounts[to]) return false;
        
        // Check KYC requirements for large amounts
        if (amount > 1000 * 10**decimals()) {
            return isKYCVerified(from) && isKYCVerified(to);
        }
        
        return true;
    }
    
    function freezeAccount(address account) external override onlyRole(COMPLIANCE_ROLE) {
        require(account != address(0), "Invalid account");
        _frozenAccounts[account] = true;
        emit AccountFrozen(account);
    }
    
    function unfreezeAccount(address account) external override onlyRole(COMPLIANCE_ROLE) {
        require(account != address(0), "Invalid account");
        _frozenAccounts[account] = false;
        emit AccountUnfrozen(account);
    }
    
    /**
     * @dev Internal ERC-20 functions
     */
    mapping(address => uint256) private _balances;
    
    function _mint(address account, uint256 amount) internal {
        require(account != address(0), "ERC20: mint to the zero address");
        _balances[account] = _balances[account].add(amount);
        emit Transfer(address(0), account, amount);
    }
    
    function _burn(address account, uint256 amount) internal {
        require(account != address(0), "ERC20: burn from the zero address");
        uint256 accountBalance = _balances[account];
        require(accountBalance >= amount, "ERC20: burn amount exceeds balance");
        _balances[account] = accountBalance.sub(amount);
        emit Transfer(account, address(0), amount);
    }
    
    function _transfer(address from, address to, uint256 amount) internal whenNotPaused returns (bool) {
        require(from != address(0), "ERC20: transfer from the zero address");
        require(to != address(0), "ERC20: transfer to the zero address");
        require(!_frozenAccounts[from], "From account is frozen");
        require(!_frozenAccounts[to], "To account is frozen");
        require(checkCompliance(from, to, amount), "Compliance check failed");
        
        uint256 fromBalance = _balances[from];
        require(fromBalance >= amount, "ERC20: transfer amount exceeds balance");
        _balances[from] = fromBalance.sub(amount);
        _balances[to] = _balances[to].add(amount);
        
        emit Transfer(from, to, amount);
        return true;
    }
    
    function _approve(address owner, address spender, uint256 amount) internal {
        require(owner != address(0), "ERC20: approve from the zero address");
        require(spender != address(0), "ERC20: approve to the zero address");
        _allowances[owner][spender] = amount;
        emit Approval(owner, spender, amount);
    }
    
    /**
     * @dev Pausable functions
     */
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }
    
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }
    
    /**
     * @dev Fallback function to receive ETH
     */
    receive() external payable {}
}