// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./tokens/MetalToken.sol";
import "./tokens/MetalNFT.sol";
import "./dex/DEXAggregator.sol";
import "./amm/CustomMetalAMM.sol";
import "./compliance/ComplianceRegistry.sol";
import "./storage/MetalStorageVault.sol";
import "../interfaces/tokens/IMetalTokens.sol";
import "../interfaces/IERC20.sol";
import "../utils/SafeMath.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @dev Main system orchestrator for metal tokenization and DEX integration
 */
contract MetalTokenizationSystem is AccessControl, ReentrancyGuard, Pausable {
    using SafeMath for uint256;
    
    bytes32 public constant SYSTEM_ADMIN_ROLE = keccak256("SYSTEM_ADMIN_ROLE");
    bytes32 public constant TOKEN_MANAGER_ROLE = keccak256("TOKEN_MANAGER_ROLE");
    bytes32 public constant DEX_MANAGER_ROLE = keccak256("DEX_MANAGER_ROLE");
    bytes32 public constant VAULT_MANAGER_ROLE = keccak256("VAULT_MANAGER_ROLE");
    bytes32 public constant COMPLIANCE_ADMIN_ROLE = keccak256("COMPLIANCE_ADMIN_ROLE");
    
    // Core system components
    address public metalToken; // ERC-20 fungible metal tokens
    address public metalNFT; // ERC-721 unique metal items
    address public dexAggregator; // Multi-DEX integration
    address public customAMM; // Custom liquidity pools
    address public complianceRegistry; // KYC/AML system
    address public storageVault; // Physical metal storage
    
    // System configuration
    uint256 public totalValueLocked;
    uint256 public activeDeposits;
    uint256 public totalSwaps;
    uint256 public systemFee;
    address public feeRecipient;
    
    // Metal tracking
    mapping(MetalType => uint256) public metalTokenSupply;
    mapping(MetalType => uint256) public totalPhysicalBacking;
    
    // System statistics
    struct SystemStats {
        uint256 totalVolume;
        uint256 activeUsers;
        uint256 completedTrades;
        uint256 mintedTokens;
        uint256 burnedTokens;
        uint256 totalFees;
        uint256 gasUsed;
    }
    
    SystemStats public stats;
    
    // Events
    event SystemInitialized(address metalToken, address metalNFT, address dexAggregator, address customAMM);
    event MetalTokenMinted(address indexed to, MetalType metalType, uint256 amount, uint256 value);
    event MetalNFTMinted(address indexed to, uint256 tokenId, MetalType metalType, string serialNumber);
    event SwapExecuted(address indexed trader, address tokenIn, address tokenOut, uint256 amountIn, uint256 amountOut, uint256 fee);
    event LiquidityAdded(bytes32 indexed poolId, address indexed provider, uint256 amountA, uint256 amountB);
    event ComplianceVerified(address indexed user, ComplianceStatus status);
    event MetalDeposited(address indexed depositor, MetalType metalType, uint256 weight, string location);
    event SystemFeeUpdated(uint256 oldFee, uint256 newFee);
    
    constructor(
        address _metalToken,
        address _metalNFT,
        address _dexAggregator,
        address _customAMM,
        address _complianceRegistry,
        address _storageVault,
        address _feeRecipient
    ) {
        require(_metalToken != address(0), "Invalid metal token");
        require(_metalNFT != address(0), "Invalid metal NFT");
        require(_dexAggregator != address(0), "Invalid DEX aggregator");
        require(_customAMM != address(0), "Invalid custom AMM");
        require(_complianceRegistry != address(0), "Invalid compliance registry");
        require(_storageVault != address(0), "Invalid storage vault");
        require(_feeRecipient != address(0), "Invalid fee recipient");
        
        // Initialize system components
        metalToken = _metalToken;
        metalNFT = _metalNFT;
        dexAggregator = _dexAggregator;
        customAMM = _customAMM;
        complianceRegistry = _complianceRegistry;
        storageVault = _storageVault;
        feeRecipient = _feeRecipient;
        
        // Setup roles
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(SYSTEM_ADMIN_ROLE, msg.sender);
        _setupRole(TOKEN_MANAGER_ROLE, msg.sender);
        _setupRole(DEX_MANAGER_ROLE, msg.sender);
        _setupRole(VAULT_MANAGER_ROLE, msg.sender);
        _setupRole(COMPLIANCE_ADMIN_ROLE, msg.sender);
        
        // Initialize system statistics
        stats = SystemStats({
            totalVolume: 0,
            activeUsers: 0,
            completedTrades: 0,
            mintedTokens: 0,
            burnedTokens: 0,
            totalFees: 0,
            gasUsed: 0
        });
        
        systemFee = 50; // 0.5% default fee
        
        emit SystemInitialized(_metalToken, _metalNFT, _dexAggregator, _customAMM);
    }
    
    /**
     * @dev Mint fungible metal tokens backed by physical deposits
     */
    function mintFungibleMetalTokens(
        address to,
        MetalType metalType,
        uint256 amount,
        string calldata location,
        bytes32 depositProof
    ) external onlyRole(TOKEN_MANAGER_ROLE) returns (bool) {
        require(to != address(0), "Invalid recipient");
        require(amount > 0, "Invalid amount");
        
        // Check compliance
        IMetalToken(metalToken).checkCompliance(address(0), to, amount);
        
        // Mint tokens
        IMetalToken(metalToken).mintMetal(to, amount, metalType, depositProof);
        
        // Update statistics
        metalTokenSupply[metalType] = metalTokenSupply[metalType].add(amount);
        stats.mintedTokens = stats.mintedTokens.add(amount);
        
        // Update TVL
        uint256 tokenValue = amount.mul(_getMetalPrice(metalType)).div(1e18);
        totalValueLocked = totalValueLocked.add(tokenValue);
        
        emit MetalTokenMinted(to, metalType, amount, tokenValue);
        return true;
    }
    
    /**
     * @dev Mint unique metal NFT
     */
    function mintUniqueMetal(
        address to,
        MetalType metalType,
        uint256 weight,
        uint256 purity,
        string calldata serialNumber,
        string calldata storageLocation,
        string calldata certification
    ) external onlyRole(TOKEN_MANAGER_ROLE) returns (uint256 tokenId) {
        require(to != address(0), "Invalid recipient");
        require(weight > 0, "Invalid weight");
        require(purity >= 800 && purity <= 1000, "Invalid purity");
        
        // Create metal certificate
        IMetalNFT.MetalCertificate memory certificate = IMetalNFT.MetalCertificate({
            serialNumber: serialNumber,
            weight: weight,
            purity: purity,
            metalType: metalType,
            grade: IMetalNFT.MetalGrade.INVESTMENT_GRADE,
            custodian: msg.sender,
            storageLocation: storageLocation,
            isTokenized: true,
            tokenizationDate: block.timestamp,
            authenticityHash: keccak256(abi.encodePacked(serialNumber, weight, purity, block.timestamp))
        });
        
        // Mint NFT
        tokenId = IMetalNFT(metalNFT).mintMetalItem(to, certificate);
        
        // Update statistics
        stats.mintedTokens = stats.mintedTokens.add(1);
        totalValueLocked = totalValueLocked.add(weight.mul(_getMetalPrice(metalType)).div(1e18));
        metalTokenSupply[metalType] = metalTokenSupply[metalType].add(weight);
        
        emit MetalNFTMinted(to, tokenId, metalType, serialNumber);
        return tokenId;
    }
    
    /**
     * @dev Execute token swap through DEX aggregator
     */
    function executeTokenSwap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 minAmountOut,
        uint256 deadline,
        address[] calldata path,
        uint24[] calldata fees,
        uint8 dexId
    ) external nonReentrant whenNotPaused returns (uint256 amountOut) {
        require(amountIn > 0, "Invalid amount");
        require(block.timestamp <= deadline, "Deadline exceeded");
        
        // Check user compliance
        ComplianceRegistry complianceReg = ComplianceRegistry(complianceRegistry);
        ComplianceStatus status = complianceReg.getComplianceStatus(msg.sender);
        require(status != ComplianceStatus.FROZEN && status != ComplianceStatus.SUSPENDED, "User restricted");
        
        // Check transaction AML risk
        IAMLMonitor.AMLRisk risk = complianceReg.analyzeTransaction(
            msg.sender,
            address(this),
            amountIn,
            "SYSTEM_SWAP"
        );
        require(risk != IAMLMonitor.AMLRisk.BLOCKED, "Transaction blocked by AML");
        
        // Record transaction for compliance
        complianceReg.recordTransaction(
            msg.sender,
            address(this),
            amountIn,
            "US",
            "TOKEN_SWAP"
        );
        
        // Calculate system fee
        uint256 fee = amountIn.mul(systemFee).div(10000);
        uint256 netAmountIn = amountIn.sub(fee);
        
        // Execute swap
        DEXAggregator.SwapParams memory swapParams = DEXAggregator.SwapParams({
            tokenIn: tokenIn,
            tokenOut: tokenOut,
            amountIn: netAmountIn,
            minAmountOut: minAmountOut,
            deadline: deadline,
            path: path,
            fees: fees,
            dexId: dexId,
            isMultiHop: path.length > 2
        });
        
        // Transfer tokens from user
        IERC20(tokenIn).transferFrom(msg.sender, address(this), amountIn);
        
        // Transfer fee to recipient
        if (fee > 0) {
            IERC20(tokenIn).transfer(feeRecipient, fee);
            stats.totalFees = stats.totalFees.add(fee);
        }
        
        // Execute swap through aggregator (simplified - in practice would use actual swap function)
        amountOut = _executeSwap(swapParams);
        
        // Update statistics
        stats.totalVolume = stats.totalVolume.add(amountIn);
        stats.completedTrades = stats.completedTrades.add(1);
        stats.activeUsers = stats.activeUsers.add(1);
        
        emit SwapExecuted(msg.sender, tokenIn, tokenOut, amountIn, amountOut, fee);
        
        return amountOut;
    }
    
    /**
     * @dev Add liquidity to custom AMM
     */
    function addLiquidityToAMM(
        bytes32 poolId,
        address tokenA,
        address tokenB,
        uint256 amountA,
        uint256 amountB,
        uint256 minAmountA,
        uint256 minAmountB,
        uint256 deadline
    ) external nonReentrant whenNotPaused returns (uint256 liquidityMinted) {
        require(amountA > 0 && amountB > 0, "Invalid amounts");
        require(block.timestamp <= deadline, "Deadline exceeded");
        
        // Check compliance for liquidity providers
        ComplianceRegistry complianceReg = ComplianceRegistry(complianceRegistry);
        ComplianceStatus status = complianceReg.getComplianceStatus(msg.sender);
        require(status != ComplianceStatus.FROZEN && status != ComplianceStatus.SUSPENDED, "User restricted");
        
        // Record transaction
        complianceReg.recordTransaction(
            msg.sender,
            address(this),
            amountA.add(amountB),
            "US",
            "LIQUIDITY_PROVISION"
        );
        
        // Transfer tokens
        IERC20(tokenA).transferFrom(msg.sender, address(this), amountA);
        IERC20(tokenB).transferFrom(msg.sender, address(this), amountB);
        
        // Approve AMM (simplified)
        // In practice, would call actual AMM functions
        
        liquidityMinted = 0; // Would be actual liquidity minted
        
        emit LiquidityAdded(poolId, msg.sender, amountA, amountB);
        
        return liquidityMinted;
    }
    
    /**
     * @dev Deposit physical metals to storage
     */
    function depositPhysicalMetals(
        MetalType metalType,
        uint256 weight,
        uint256 purity,
        string calldata serialNumber,
        string calldata location,
        string calldata certification
    ) external nonReentrant whenNotPaused returns (uint256 depositId) {
        require(weight > 0, "Invalid weight");
        require(purity >= 800 && purity <= 1000, "Invalid purity");
        
        // Check user compliance
        ComplianceRegistry complianceReg = ComplianceRegistry(complianceRegistry);
        ComplianceStatus status = complianceReg.getComplianceStatus(msg.sender);
        require(status != ComplianceStatus.FROZEN && status != ComplianceStatus.SUSPENDED, "User restricted");
        
        // Record transaction
        complianceReg.recordTransaction(
            msg.sender,
            address(this),
            weight.mul(_getMetalPrice(metalType)).div(1e18),
            "US",
            "PHYSICAL_DEPOSIT"
        );
        
        // Deposit to storage
        bytes32 depositProof = keccak256(abi.encodePacked(serialNumber, weight, purity, block.timestamp));
        depositId = MetalStorageVault(storageVault).recordMetalDeposit(
            location,
            metalType,
            weight,
            purity,
            serialNumber,
            msg.sender,
            depositProof,
            certification
        );
        
        // Update statistics
        totalPhysicalBacking[metalType] = totalPhysicalBacking[metalType].add(weight);
        activeDeposits = activeDeposits.add(1);
        
        emit MetalDeposited(msg.sender, metalType, weight, location);
        
        return depositId;
    }
    
    /**
     * @dev Withdraw physical metals from storage
     */
    function withdrawPhysicalMetals(
        string calldata location,
        uint256 depositId,
        uint256 weight,
        address recipient
    ) external nonReentrant returns (bool) {
        require(depositId >= 0, "Invalid deposit ID");
        require(weight > 0, "Invalid weight");
        require(recipient != address(0), "Invalid recipient");
        
        // Check if user is the original depositor or authorized
        // In practice, this would check ownership or authorization
        
        MetalStorageVault storageVaultContract = MetalStorageVault(storageVault);
        IMetalStorageVault.MetalDeposit memory deposit = storageVaultContract.getDepositsByLocation(location)[depositId];
        
        require(deposit.depositor == msg.sender, "Not authorized");
        require(deposit.weight >= weight, "Insufficient weight");
        
        // Withdraw from storage
        bytes32 withdrawalProof = keccak256(abi.encodePacked(location, depositId, weight, block.timestamp));
        bool success = storageVaultContract.withdrawMetal(location, depositId, recipient, weight, withdrawalProof);
        
        if (success) {
            // Update statistics
            totalPhysicalBacking[deposit.metalType] = totalPhysicalBacking[deposit.metalType].sub(weight);
            activeDeposits = activeDeposits.sub(1);
        }
        
        return success;
    }
    
    /**
     * @dev Verify compliance for an address
     */
    function verifyCompliance(address user) external returns (bool) {
        ComplianceRegistry complianceReg = ComplianceRegistry(complianceRegistry);
        ComplianceStatus status = complianceReg.getComplianceStatus(user);
        
        emit ComplianceVerified(user, status);
        
        return status == ComplianceStatus.KYC_APPROVED;
    }
    
    /**
     * @dev Get system statistics
     */
    function getSystemStats() external view returns (SystemStats memory) {
        return stats;
    }
    
    /**
     * @dev Get metal token supply
     */
    function getMetalTokenSupply(MetalType metalType) external view returns (uint256) {
        return metalTokenSupply[metalType];
    }
    
    /**
     * @dev Get total physical backing
     */
    function getTotalPhysicalBacking(MetalType metalType) external view returns (uint256) {
        return totalPhysicalBacking[metalType];
    }
    
    /**
     * @dev Get system health metrics
     */
    function getSystemHealth() external view returns (
        uint256 tvl,
        uint256 backingRatio,
        uint256 activeDeposits,
        uint256 totalUsers,
        uint256 totalVolume
    ) {
        return (
            totalValueLocked,
            totalValueLocked > 0 ? totalPhysicalBacking[MetalType.GOLD].mul(10000).div(totalValueLocked) : 0,
            activeDeposits,
            stats.activeUsers,
            stats.totalVolume
        );
    }
    
    /**
     * @dev Admin functions
     */
    function setSystemFee(uint256 newFee) external onlyRole(SYSTEM_ADMIN_ROLE) {
        require(newFee <= 1000, "Fee too high (max 10%)");
        uint256 oldFee = systemFee;
        systemFee = newFee;
        emit SystemFeeUpdated(oldFee, newFee);
    }
    
    function pause() external onlyRole(SYSTEM_ADMIN_ROLE) {
        _pause();
    }
    
    function unpause() external onlyRole(SYSTEM_ADMIN_ROLE) {
        _unpause();
    }
    
    /**
     * @dev Emergency functions
     */
    function emergencyWithdraw(address token, uint256 amount) external onlyRole(SYSTEM_ADMIN_ROLE) whenPaused {
        IERC20(token).transfer(feeRecipient, amount);
    }
    
    function upgradeSystemComponents(
        address newMetalToken,
        address newMetalNFT,
        address newCustomAMM
    ) external onlyRole(SYSTEM_ADMIN_ROLE) whenPaused {
        require(newMetalToken != address(0), "Invalid new metal token");
        require(newMetalNFT != address(0), "Invalid new metal NFT");
        require(newCustomAMM != address(0), "Invalid new AMM");
        
        metalToken = newMetalToken;
        metalNFT = newMetalNFT;
        customAMM = newCustomAMM;
    }
    
    /**
     * @dev Internal helper functions
     */
    function _executeSwap(DEXAggregator.SwapParams memory swapParams) internal returns (uint256) {
        // Simplified swap execution - in practice would use actual DEX aggregator
        // This is a placeholder for the actual swap logic
        
        uint256 estimatedAmountOut = swapParams.amountIn.mul(95).div(100); // 5% slippage estimate
        return estimatedAmountOut;
    }
    
    function _getMetalPrice(MetalType metalType) internal pure returns (uint256) {
        // Current metal prices in USD per gram (simplified)
        if (metalType == MetalType.GOLD) return 60 * 10**18; // $60/gram
        if (metalType == MetalType.SILVER) return 1 * 10**18; // $1/gram
        if (metalType == MetalType.PLATINUM) return 30 * 10**18; // $30/gram
        if (metalType == MetalType.PALLADIUM) return 25 * 10**18; // $25/gram
        return 0;
    }
    
    /**
     * @dev Fallback function to receive ETH
     */
    receive() external payable {
        // Accept ETH for system operations
    }
}