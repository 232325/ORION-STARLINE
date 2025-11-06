// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../contracts/tokens/MetalToken.sol";
import "../contracts/tokens/MetalNFT.sol";
import "../contracts/dex/DEXAggregator.sol";
import "../contracts/amm/CustomMetalAMM.sol";
import "../contracts/compliance/ComplianceRegistry.sol";
import "../contracts/storage/MetalStorageVault.sol";
import "../contracts/MetalTokenizationSystem.sol";

/**
 * @title Comprehensive test suite for Metal Tokenization System
 */
contract MetalTokenizationSystemTest is Test {
    // Test contracts
    MetalToken public metalToken;
    MetalNFT public metalNFT;
    DEXAggregator public dexAggregator;
    CustomMetalAMM public customAMM;
    ComplianceRegistry public complianceRegistry;
    MetalStorageVault public storageVault;
    MetalTokenizationSystem public tokenizationSystem;
    
    // Test accounts
    address public admin;
    address public user1;
    address public user2;
    address public custodian;
    address public complianceOfficer;
    address public feeRecipient;
    
    // Test data
    string constant NEW_YORK_VAULT = "New York Vault, Manhattan";
    string constant LONDON_VAULT = "London Vault, Canary Wharf";
    string constant GOLD_SERIAL = "GOLD-2024-001";
    string constant SILVER_SERIAL = "SILVER-2024-001";
    
    function setUp() public {
        // Setup test accounts
        admin = address(this);
        user1 = address(0x1);
        user2 = address(0x2);
        custodian = address(0x3);
        complianceOfficer = address(0x4);
        feeRecipient = address(0x5);
        
        // Deploy contracts
        _deployContracts();
        _setupSystem();
    }
    
    function test_01_DeploySystem() public {
        console.log("🧪 Test 1: System Deployment");
        
        assertTrue(address(metalToken) != address(0));
        assertTrue(address(metalNFT) != address(0));
        assertTrue(address(dexAggregator) != address(0));
        assertTrue(address(customAMM) != address(0));
        assertTrue(address(complianceRegistry) != address(0));
        assertTrue(address(storageVault) != address(0));
        assertTrue(address(tokenizationSystem) != address(0));
        
        console.log("✅ All contracts deployed successfully");
    }
    
    function test_02_FungibleMetalToken() public {
        console.log("🧪 Test 2: Fungible Metal Token Operations");
        
        uint256 mintAmount = 1000 * 10**18; // 1000 tokens
        
        // Mint metal tokens
        vm.prank(admin);
        metalToken.mintMetal(user1, mintAmount, IMetalToken.MetalType.GOLD, keccak256("proof"));
        
        uint256 balance = metalToken.balanceOf(user1);
        assertEq(balance, mintAmount);
        
        console.log("✅ Metal tokens minted successfully");
        console.log("   Balance:", balance / 10**18, "GOLD tokens");
        
        // Test transfer
        vm.prank(user1);
        metalToken.transfer(user2, 100 * 10**18);
        
        balance = metalToken.balanceOf(user1);
        uint256 user2Balance = metalToken.balanceOf(user2);
        assertEq(balance, 900 * 10**18);
        assertEq(user2Balance, 100 * 10**18);
        
        console.log("✅ Token transfer successful");
        console.log("   User1 balance:", balance / 10**18, "tokens");
        console.log("   User2 balance:", user2Balance / 10**18, "tokens");
    }
    
    function test_03_UniqueMetalNFT() public {
        console.log("🧪 Test 3: Unique Metal NFT Operations");
        
        IMetalNFT.MetalCertificate memory certificate = IMetalNFT.MetalCertificate({
            serialNumber: GOLD_SERIAL,
            weight: 100, // 100 grams
            purity: 999, // 99.9%
            metalType: IMetalNFT.MetalType.GOLD,
            grade: IMetalNFT.MetalGrade.INVESTMENT_GRADE,
            custodian: custodian,
            storageLocation: NEW_YORK_VAULT,
            isTokenized: true,
            tokenizationDate: block.timestamp,
            authenticityHash: keccak256("auth-proof")
        });
        
        // Mint NFT
        vm.startPrank(admin);
        uint256 tokenId = metalNFT.mintMetalItem(user1, certificate);
        vm.stopPrank();
        
        assertEq(metalNFT.ownerOf(tokenId), user1);
        
        console.log("✅ Metal NFT minted successfully");
        console.log("   Token ID:", tokenId);
        console.log("   Owner:", metalNFT.ownerOf(tokenId));
        
        // Get certificate details
        IMetalNFT.MetalCertificate memory retrievedCert = metalNFT.getCertificate(tokenId);
        assertEq(retrievedCert.serialNumber, GOLD_SERIAL);
        assertEq(retrievedCert.weight, 100);
        
        console.log("✅ Certificate retrieved successfully");
        console.log("   Serial:", retrievedCert.serialNumber);
        console.log("   Weight:", retrievedCert.weight, "grams");
    }
    
    function test_04_ComplianceSystem() public {
        console.log("🧪 Test 4: Compliance and KYC System");
        
        // Register user compliance
        ComplianceRegistry.ComplianceData memory complianceData = ComplianceRegistry.ComplianceData({
            status: ComplianceRegistry.ComplianceStatus.KYC_APPROVED,
            riskLevel: ComplianceRegistry.RiskLevel.LOW,
            jurisdiction: "US",
            verificationType: "Passport",
            verificationDate: block.timestamp,
            expiryDate: block.timestamp + 365 days,
            verifier: complianceOfficer,
            isAccredited: true,
            spendingLimit: 1000000 * 10**18,
            dataHash: keccak256("compliance-proof")
        });
        
        bytes memory proof = "KYC verification proof";
        
        vm.prank(complianceOfficer);
        complianceRegistry.registerCompliance(user1, complianceData, proof);
        
        ComplianceRegistry.ComplianceStatus status = complianceRegistry.getComplianceStatus(user1);
        assertEq(uint256(status), uint256(ComplianceRegistry.ComplianceStatus.KYC_APPROVED));
        
        console.log("✅ KYC verification completed");
        console.log("   Status:", _complianceStatusToString(status));
        
        // Record transaction
        bytes32 txHash = complianceRegistry.recordTransaction(
            user1,
            user2,
            1000 * 10**18,
            "US",
            "TEST_TRANSACTION"
        );
        
        assertTrue(txHash != bytes32(0));
        
        console.log("✅ Transaction recorded");
        console.log("   Transaction Hash:", vm.toString(txHash));
    }
    
    function test_05_StorageVault() public {
        console.log("🧪 Test 5: Physical Metal Storage");
        
        // Record metal deposit
        uint256 depositWeight = 5000; // 5kg gold
        bytes32 depositProof = keccak256("deposit-proof-123");
        
        vm.prank(custodian);
        uint256 depositId = storageVault.recordMetalDeposit(
            NEW_YORK_VAULT,
            IMetalNFT.MetalType.GOLD,
            depositWeight,
            999, // 99.9% purity
            GOLD_SERIAL,
            user1,
            depositProof,
            "LBMA Certified"
        );
        
        MetalStorageVault.MetalDeposit memory deposit = 
            storageVault.getDepositsByLocation(NEW_YORK_VAULT)[depositId];
        
        assertEq(deposit.weight, depositWeight);
        assertEq(deposit.depositor, user1);
        
        console.log("✅ Metal deposit recorded");
        console.log("   Deposit ID:", depositId);
        console.log("   Weight:", deposit.weight, "grams");
        console.log("   Location:", deposit.storageLocation);
        
        // Check facility info
        MetalStorageVault.StorageFacility memory facility = 
            storageVault.getFacilityInfo(NEW_YORK_VAULT);
            
        assertTrue(facility.isActive);
        
        console.log("✅ Storage facility active");
        console.log("   Location:", facility.location);
        console.log("   Capacity:", facility.capacity, "grams");
    }
    
    function test_06_CustomAMM() public {
        console.log("🧪 Test 6: Custom AMM Liquidity Pool");
        
        // Create pool
        bytes32 poolId = keccak256(abi.encodePacked(
            address(metalToken),
            address(0x0), // USD proxy
            IMetalNFT.MetalType.GOLD
        ));
        
        vm.prank(admin);
        customAMM.createPool(
            address(metalToken),
            address(0x0), // USD proxy
            100 * 10**18, // 100 tokens
            6000 * 10**18, // 6000 USD worth
            IMetalNFT.MetalType.GOLD
        );
        
        CustomMetalAMM.PoolInfo memory poolInfo = customAMM.getPoolInfo(poolId);
        assertTrue(poolInfo.isActive);
        
        console.log("✅ Liquidity pool created");
        console.log("   Pool ID:", vm.toString(poolId));
        console.log("   Token A:", poolInfo.tokenA);
        console.log("   Token B:", poolInfo.tokenB);
        console.log("   Total Supply:", poolInfo.totalSupply / 10**18, "LP tokens");
    }
    
    function test_07_IntegratedWorkflow() public {
        console.log("🧪 Test 7: Integrated Workflow Simulation");
        
        uint256 depositWeight = 10000; // 10kg gold
        uint256 mintAmount = 5000 * 10**18; // 5000 tokens
        
        // Step 1: Deposit physical metal
        vm.prank(custodian);
        storageVault.recordMetalDeposit(
            NEW_YORK_VAULT,
            IMetalNFT.MetalType.GOLD,
            depositWeight,
            999,
            "WORKFLOW-001",
            user1,
            keccak256("workflow-proof"),
            "LBMA Certified"
        );
        
        // Step 2: Mint fungible tokens
        vm.startPrank(admin);
        tokenizationSystem.mintFungibleMetalTokens(
            user1,
            IMetalNFT.MetalType.GOLD,
            mintAmount,
            NEW_YORK_VAULT,
            keccak256("mint-proof")
        );
        vm.stopPrank();
        
        // Step 3: Mint unique NFT
        IMetalNFT.MetalCertificate memory certificate = IMetalNFT.MetalCertificate({
            serialNumber: "UNIQUE-001",
            weight: 500, // 500g unique piece
            purity: 999,
            metalType: IMetalNFT.MetalType.GOLD,
            grade: IMetalNFT.MetalGrade.INVESTMENT_GRADE,
            custodian: custodian,
            storageLocation: NEW_YORK_VAULT,
            isTokenized: true,
            tokenizationDate: block.timestamp,
            authenticityHash: keccak256("unique-proof")
        });
        
        vm.startPrank(admin);
        uint256 tokenId = tokenizationSystem.mintUniqueMetal(
            user2,
            IMetalNFT.MetalType.GOLD,
            500,
            999,
            "UNIQUE-001",
            NEW_YORK_VAULT,
            "Investment Grade Certificate"
        );
        vm.stopPrank();
        
        // Step 4: Check system stats
        MetalTokenizationSystem.SystemStats memory stats = tokenizationSystem.getSystemStats();
        
        console.log("✅ Integrated workflow completed");
        console.log("   Total Volume:", stats.totalVolume / 10**18);
        console.log("   Active Users:", stats.activeUsers);
        console.log("   Minted Tokens:", stats.mintedTokens);
        console.log("   NFT Token ID:", tokenId);
        
        // Verify final balances
        assertTrue(metalToken.balanceOf(user1) == mintAmount);
        assertTrue(metalNFT.ownerOf(tokenId) == user2);
        
        console.log("✅ All balances verified");
    }
    
    function test_08_ComplianceEnforcement() public {
        console.log("🧪 Test 8: Compliance Enforcement");
        
        // Try to mint for frozen user (should fail)
        vm.startPrank(admin);
        metalToken.freezeAccount(user1);
        vm.stopPrank();
        
        vm.prank(admin);
        bool success = metalToken.mintMetal(user1, 1000, IMetalNFT.MetalType.GOLD, keccak256("proof"));
        
        assertFalse(success);
        console.log("✅ Minting to frozen account blocked");
        
        // Unfreeze and verify
        vm.prank(admin);
        metalToken.unfreezeAccount(user1);
        
        vm.prank(admin);
        success = metalToken.mintMetal(user1, 1000, IMetalNFT.MetalType.GOLD, keccak256("proof"));
        
        assertTrue(success);
        console.log("✅ Minting after unfreeze successful");
    }
    
    function test_09_EmergencyPause() public {
        console.log("🧪 Test 9: Emergency Pause Functionality");
        
        // Pause system
        vm.prank(admin);
        tokenizationSystem.pause();
        
        // Try operations while paused (should fail)
        vm.prank(admin);
        vm.expectRevert("Pausable: paused");
        metalToken.mintMetal(user1, 1000, IMetalNFT.MetalType.GOLD, keccak256("proof"));
        
        console.log("✅ Operations blocked during pause");
        
        // Unpause
        vm.prank(admin);
        tokenizationSystem.unpause();
        
        // Verify operations work again
        vm.prank(admin);
        bool success = metalToken.mintMetal(user1, 1000, IMetalNFT.MetalType.GOLD, keccak256("proof"));
        assertTrue(success);
        
        console.log("✅ Operations restored after unpause");
    }
    
    function test_10_SystemHealthMetrics() public {
        console.log("🧪 Test 10: System Health Metrics");
        
        // Simulate various operations
        vm.prank(admin);
        storageVault.recordMetalDeposit(
            NEW_YORK_VAULT,
            IMetalNFT.MetalType.GOLD,
            10000,
            999,
            "HEALTH-TEST",
            user1,
            keccak256("health-proof"),
            "LBMA Certified"
        );
        
        vm.prank(admin);
        metalToken.mintMetal(user1, 5000 * 10**18, IMetalNFT.MetalType.GOLD, keccak256("mint-proof"));
        
        vm.prank(admin);
        customAMM.createPool(
            address(metalToken),
            address(0x0),
            100 * 10**18,
            6000 * 10**18,
            IMetalNFT.MetalType.GOLD
        );
        
        // Get health metrics
        (
            uint256 tvl,
            uint256 backingRatio,
            uint256 activeDeposits,
            uint256 totalUsers,
            uint256 totalVolume
        ) = tokenizationSystem.getSystemHealth();
        
        console.log("✅ System Health Metrics:");
        console.log("   TVL:", tvl / 10**18);
        console.log("   Backing Ratio:", backingRatio / 100, "%");
        console.log("   Active Deposits:", activeDeposits);
        console.log("   Total Users:", totalUsers);
        console.log("   Total Volume:", totalVolume / 10**18);
        
        assertTrue(tvl > 0);
        assertTrue(activeDeposits > 0);
    }
    
    /**
     * @dev Internal helper functions
     */
    function _deployContracts() internal {
        // Compliance Registry
        complianceRegistry = new ComplianceRegistry();
        
        // Metal Token (ERC-20)
        metalToken = new MetalToken(
            "Gold Token",
            "GOLD",
            IMetalNFT.MetalType.GOLD,
            custodian
        );
        
        // Metal NFT (ERC-721)
        metalNFT = new MetalNFT(
            "Unique Metals NFT",
            "UMNFT",
            "ipfs://metadata/"
        );
        
        // DEX Aggregator (with mock addresses)
        dexAggregator = new DEXAggregator(
            address(0x1), // Uniswap V3 Router
            address(0x2), // Uniswap V3 Factory
            address(0x3), // SushiSwap Router
            address(0x4), // SushiSwap Factory
            address(0x5), // PancakeSwap V3 Router
            address(0x6)  // PancakeSwap V2 Router
        );
        
        // Custom AMM
        customAMM = new CustomMetalAMM(feeRecipient);
        
        // Storage Vault
        storageVault = new MetalStorageVault();
        
        // Tokenization System
        tokenizationSystem = new MetalTokenizationSystem(
            address(metalToken),
            address(metalNFT),
            address(dexAggregator),
            address(customAMM),
            address(complianceRegistry),
            address(storageVault),
            feeRecipient
        );
    }
    
    function _setupSystem() internal {
        // Grant roles
        vm.startPrank(admin);
        
        // Tokenization system roles
        tokenizationSystem.grantRole(
            keccak256("SYSTEM_ADMIN_ROLE"), 
            admin
        );
        tokenizationSystem.grantRole(
            keccak256("TOKEN_MANAGER_ROLE"), 
            admin
        );
        tokenizationSystem.grantRole(
            keccak256("DEX_MANAGER_ROLE"), 
            admin
        );
        tokenizationSystem.grantRole(
            keccak256("VAULT_MANAGER_ROLE"), 
            admin
        );
        tokenizationSystem.grantRole(
            keccak256("COMPLIANCE_ADMIN_ROLE"), 
            admin
        );
        
        // Metal token roles
        metalToken.grantRole(
            keccak256("MINTER_ROLE"), 
            address(tokenizationSystem)
        );
        metalToken.grantRole(
            keccak256("COMPLIANCE_ROLE"), 
            complianceOfficer
        );
        
        // Metal NFT roles
        metalNFT.grantRole(
            keccak256("MINTER_ROLE"), 
            address(tokenizationSystem)
        );
        metalNFT.grantRole(
            keccak256("COMPLIANCE_ROLE"), 
            complianceOfficer
        );
        
        // Storage vault roles
        storageVault.grantRole(
            keccak256("STORAGE_MANAGER_ROLE"), 
            admin
        );
        storageVault.grantRole(
            keccak256("CUSTODIAN_ROLE"), 
            custodian
        );
        
        // Compliance registry roles
        complianceRegistry.grantRole(
            keccak256("COMPLIANCE_OFFICER_ROLE"), 
            complianceOfficer
        );
        complianceRegistry.grantRole(
            keccak256("KYC_PROVIDER_ROLE"), 
            complianceOfficer
        );
        
        vm.stopPrank();
        
        // Register storage facilities
        vm.startPrank(admin);
        storageVault.registerStorageFacility(
            NEW_YORK_VAULT,
            custodian,
            1000000, // 1 ton capacity
            "ISO 9001:2015",
            address(0) // No insurance
        );
        
        storageVault.registerStorageFacility(
            LONDON_VAULT,
            custodian,
            2000000, // 2 ton capacity
            "BS EN ISO 9001:2015",
            address(0)
        );
        vm.stopPrank();
    }
    
    function _complianceStatusToString(ComplianceRegistry.ComplianceStatus status) 
        internal pure returns (string memory) {
        if (status == ComplianceRegistry.ComplianceStatus.UNVERIFIED) {
            return "UNVERIFIED";
        } else if (status == ComplianceRegistry.ComplianceStatus.KYC_PENDING) {
            return "KYC_PENDING";
        } else if (status == ComplianceRegistry.ComplianceStatus.KYC_APPROVED) {
            return "KYC_APPROVED";
        } else if (status == ComplianceRegistry.ComplianceStatus.KYC_REJECTED) {
            return "KYC_REJECTED";
        } else if (status == ComplianceRegistry.ComplianceStatus.FROZEN) {
            return "FROZEN";
        } else {
            return "SUSPENDED";
        }
    }
}