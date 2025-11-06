// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "../interfaces/tokens/IMetalTokens.sol";
import "../interfaces/IERC20.sol";
import "../utils/SafeMath.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @dev Physical metal storage and custody management system
 */
contract MetalStorageVault is AccessControl, ReentrancyGuard, Pausable {
    using SafeMath for uint256;
    
    bytes32 public constant STORAGE_MANAGER_ROLE = keccak256("STORAGE_MANAGER_ROLE");
    bytes32 public constant CUSTODIAN_ROLE = keccak256("CUSTODIAN_ROLE");
    bytes32 public constant AUDITOR_ROLE = keccak256("AUDITOR_ROLE");
    bytes32 public constant INSURANCE_PROVIDER_ROLE = keccak256("INSURANCE_PROVIDER_ROLE");
    bytes32 public constant REGULATORY_REPORTING_ROLE = keccak256("REGULATORY_REPORTING_ROLE");
    
    struct StorageFacility {
        string location;
        string country;
        address custodian;
        uint256 capacity;
        uint256 currentUsage;
        bool isActive;
        string certification;
        uint256 lastAudit;
        string auditReport;
        bytes32 auditProof;
        bool isInsured;
        address insuranceProvider;
        uint256 insuranceCoverage;
        uint256 insuranceExpiry;
    }
    
    struct MetalDeposit {
        MetalType metalType;
        uint256 weight; // in grams
        uint256 purity; // basis points (999 = 99.9%)
        string serialNumber;
        string storageLocation;
        uint256 depositDate;
        address depositor;
        bytes32 depositProof;
        bool isInsured;
        uint256 insuranceValue;
        string certification;
        bool isTokenized;
        uint256 tokenId; // NFT token ID if tokenized
    }
    
    struct CustodyAgreement {
        address client;
        address storageManager;
        uint256 monthlyFee;
        uint256 performanceBond;
        uint256 lastPayment;
        bool isActive;
        uint256 startDate;
        uint256 endDate;
        string agreementHash;
    }
    
    // Storage facilities
    mapping(string => StorageFacility) public storageFacilities;
    string[] public facilityLocations;
    
    // Metal deposits by location
    mapping(string => MetalDeposit[]) public depositsByLocation;
    
    // Custody agreements
    mapping(address => CustodyAgreement) public custodyAgreements;
    address[] public custodyClients;
    
    // Insurance tracking
    mapping(string => uint256) public insuranceClaims;
    mapping(bytes32 => bool) public processedClaims;
    
    // Regulatory reporting
    struct AuditReport {
        address auditor;
        uint256 reportDate;
        string reportHash;
        string findings;
        uint256 totalWeight;
        uint256 discrepancies;
        bool isCompliant;
        bytes32 proofHash;
    }
    
    mapping(string => AuditReport[]) public auditReports;
    uint256 public totalMetalWeight;
    mapping(MetalType => uint256) public metalWeightByType;
    
    // Events
    event FacilityRegistered(string location, address custodian, uint256 capacity);
    event MetalDepositRecorded(string location, bytes32 depositProof, uint256 weight, MetalType metalType);
    event MetalWithdrawn(string location, address recipient, uint256 weight, bytes32 withdrawalProof);
    event CustodyAgreementCreated(address client, string location, uint256 monthlyFee);
    event InsuranceClaimSubmitted(string location, uint256 amount, bytes32 claimHash);
    event AuditCompleted(string location, bool isCompliant, uint256 reportDate);
    event RegulatoryReportGenerated(string jurisdiction, uint256 reportDate, bytes32 reportHash);
    
    constructor() {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(STORAGE_MANAGER_ROLE, msg.sender);
        _setupRole(CUSTODIAN_ROLE, msg.sender);
        _setupRole(AUDITOR_ROLE, msg.sender);
        _setupRole(INSURANCE_PROVIDER_ROLE, msg.sender);
        _setupRole(REGULATORY_REPORTING_ROLE, msg.sender);
    }
    
    /**
     * @dev Storage facility management
     */
    function registerStorageFacility(
        string calldata location,
        address custodian,
        uint256 capacity,
        string calldata certification,
        address insuranceProvider
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(bytes(location).length > 0, "Invalid location");
        require(custodian != address(0), "Invalid custodian");
        require(capacity > 0, "Invalid capacity");
        
        storageFacilities[location] = StorageFacility({
            location: location,
            country: "", // To be set separately
            custodian: custodian,
            capacity: capacity,
            currentUsage: 0,
            isActive: true,
            certification: certification,
            lastAudit: block.timestamp,
            auditReport: "",
            auditProof: keccak256(abi.encodePacked(location, block.timestamp)),
            isInsured: insuranceProvider != address(0),
            insuranceProvider: insuranceProvider,
            insuranceCoverage: 0,
            insuranceExpiry: 0
        });
        
        facilityLocations.push(location);
        
        emit FacilityRegistered(location, custodian, capacity);
    }
    
    function updateFacilityCapacity(string calldata location, uint256 newCapacity) 
        external onlyRole(STORAGE_MANAGER_ROLE) {
        require(newCapacity > storageFacilities[location].currentUsage, "Capacity below current usage");
        storageFacilities[location].capacity = newCapacity;
    }
    
    function setInsuranceCoverage(
        string calldata location,
        uint256 coverage,
        uint256 expiryDate,
        address provider
    ) external onlyRole(INSURANCE_PROVIDER_ROLE) {
        require(storageFacilities[location].isActive, "Facility not active");
        
        storageFacilities[location].insuranceCoverage = coverage;
        storageFacilities[location].insuranceExpiry = expiryDate;
        storageFacilities[location].insuranceProvider = provider;
    }
    
    /**
     * @dev Metal deposit management
     */
    function recordMetalDeposit(
        string calldata location,
        MetalType metalType,
        uint256 weight,
        uint256 purity,
        string calldata serialNumber,
        address depositor,
        bytes32 depositProof,
        string calldata certification
    ) external onlyRole(CUSTODIAN_ROLE) returns (uint256 depositId) {
        require(storageFacilities[location].isActive, "Facility not active");
        require(weight > 0, "Invalid weight");
        require(purity >= 800 && purity <= 1000, "Invalid purity");
        require(depositor != address(0), "Invalid depositor");
        
        // Check capacity
        StorageFacility storage facility = storageFacilities[location];
        require(facility.currentUsage.add(weight) <= facility.capacity, "Insufficient capacity");
        
        depositId = depositsByLocation[location].length;
        
        MetalDeposit memory newDeposit = MetalDeposit({
            metalType: metalType,
            weight: weight,
            purity: purity,
            serialNumber: serialNumber,
            storageLocation: location,
            depositDate: block.timestamp,
            depositor: depositor,
            depositProof: depositProof,
            isInsured: facility.isInsured,
            insuranceValue: weight.mul(_getMetalBasePrice(metalType)).mul(purity).div(1000),
            certification: certification,
            isTokenized: false,
            tokenId: 0
        });
        
        depositsByLocation[location].push(newDeposit);
        facility.currentUsage = facility.currentUsage.add(weight);
        
        // Update global totals
        totalMetalWeight = totalMetalWeight.add(weight);
        metalWeightByType[metalType] = metalWeightByType[metalType].add(weight);
        
        emit MetalDepositRecorded(location, depositProof, weight, metalType);
    }
    
    function withdrawMetal(
        string calldata location,
        uint256 depositId,
        address recipient,
        uint256 weight,
        bytes32 withdrawalProof
    ) external onlyRole(CUSTODIAN_ROLE) returns (bool) {
        require(storageFacilities[location].isActive, "Facility not active");
        require(depositId < depositsByLocation[location].length, "Invalid deposit ID");
        require(recipient != address(0), "Invalid recipient");
        require(weight > 0, "Invalid weight");
        
        MetalDeposit storage deposit = depositsByLocation[location][depositId];
        require(deposit.weight >= weight, "Insufficient weight in deposit");
        
        // Update deposit
        deposit.weight = deposit.weight.sub(weight);
        
        // Update facility usage
        storageFacilities[location].currentUsage = storageFacilities[location].currentUsage.sub(weight);
        
        // Update global totals
        totalMetalWeight = totalMetalWeight.sub(weight);
        metalWeightByType[deposit.metalType] = metalWeightByType[deposit.metalType].sub(weight);
        
        emit MetalWithdrawn(location, recipient, weight, withdrawalProof);
        
        return true;
    }
    
    function getDepositsByLocation(string calldata location) 
        external view returns (MetalDeposit[] memory) {
        return depositsByLocation[location];
    }
    
    function getTotalWeightByType(MetalType metalType) external view returns (uint256) {
        return metalWeightByType[metalType];
    }
    
    function getTotalMetalWeight() external view returns (uint256) {
        return totalMetalWeight;
    }
    
    /**
     * @dev Custody agreement management
     */
    function createCustodyAgreement(
        address client,
        string calldata location,
        uint256 monthlyFee,
        uint256 performanceBond,
        uint256 durationMonths
    ) external onlyRole(STORAGE_MANAGER_ROLE) returns (bool) {
        require(storageFacilities[location].isActive, "Facility not active");
        require(client != address(0), "Invalid client");
        require(monthlyFee > 0, "Invalid monthly fee");
        
        CustodyAgreement storage agreement = custodyAgreements[client];
        require(!agreement.isActive, "Agreement already exists");
        
        uint256 startDate = block.timestamp;
        uint256 endDate = startDate.add(durationMonths.mul(30 days));
        
        custodyAgreements[client] = CustodyAgreement({
            client: client,
            storageManager: msg.sender,
            monthlyFee: monthlyFee,
            performanceBond: performanceBond,
            lastPayment: 0,
            isActive: true,
            startDate: startDate,
            endDate: endDate,
            agreementHash: keccak256(abi.encodePacked(client, location, monthlyFee, startDate))
        });
        
        custodyClients.push(client);
        
        emit CustodyAgreementCreated(client, location, monthlyFee);
        return true;
    }
    
    function processMonthlyPayment(address client, uint256 amount) 
        external payable returns (bool) {
        CustodyAgreement storage agreement = custodyAgreements[client];
        require(agreement.isActive, "Agreement not active");
        require(msg.value == amount, "Incorrect payment amount");
        
        agreement.lastPayment = block.timestamp;
        
        return true;
    }
    
    function terminateCustodyAgreement(address client, string calldata reason) 
        external onlyRole(STORAGE_MANAGER_ROLE) returns (bool) {
        CustodyAgreement storage agreement = custodyAgreements[client];
        require(agreement.isActive, "Agreement not active");
        
        agreement.isActive = false;
        
        // Refund performance bond if applicable
        if (agreement.performanceBond > 0) {
            // Implementation for bond refund
        }
        
        return true;
    }
    
    function getCustodyAgreement(address client) external view returns (CustodyAgreement memory) {
        return custodyAgreements[client];
    }
    
    /**
     * @dev Insurance claim management
     */
    function submitInsuranceClaim(
        string calldata location,
        uint256 claimAmount,
        string calldata incidentDescription,
        bytes calldata evidence
    ) external onlyRole(CUSTODIAN_ROLE) returns (bytes32 claimHash) {
        require(storageFacilities[location].isInsured, "Facility not insured");
        
        claimHash = keccak256(abi.encodePacked(
            location,
            claimAmount,
            incidentDescription,
            block.timestamp,
            evidence
        ));
        
        require(!processedClaims[claimHash], "Claim already processed");
        
        insuranceClaims[location] = insuranceClaims[location].add(claimAmount);
        
        emit InsuranceClaimSubmitted(location, claimAmount, claimHash);
    }
    
    function processInsuranceClaim(
        bytes32 claimHash,
        uint256 approvedAmount,
        string calldata approvalReason
    ) external onlyRole(INSURANCE_PROVIDER_ROLE) returns (bool) {
        require(!processedClaims[claimHash], "Claim already processed");
        
        processedClaims[claimHash] = true;
        
        // Insurance payout would be implemented here
        // This is a simplified version
        
        return true;
    }
    
    /**
     * @dev Audit and compliance functions
     */
    function conductAudit(
        string calldata location,
        uint256 physicalWeight,
        uint256 discrepancies,
        string calldata reportHash,
        string calldata findings,
        bool isCompliant
    ) external onlyRole(AUDITOR_ROLE) {
        require(storageFacilities[location].isActive, "Facility not active");
        require(physicalWeight > 0, "Invalid weight");
        
        AuditReport memory auditReport = AuditReport({
            auditor: msg.sender,
            reportDate: block.timestamp,
            reportHash: reportHash,
            findings: findings,
            totalWeight: physicalWeight,
            discrepancies: discrepancies,
            isCompliant: isCompliant,
            proofHash: keccak256(abi.encodePacked(location, physicalWeight, block.timestamp))
        });
        
        auditReports[location].push(auditReport);
        
        // Update facility last audit
        storageFacilities[location].lastAudit = block.timestamp;
        storageFacilities[location].auditReport = findings;
        storageFacilities[location].auditProof = auditReport.proofHash;
        
        emit AuditCompleted(location, isCompliant, block.timestamp);
    }
    
    function getAuditReports(string calldata location) 
        external view returns (AuditReport[] memory) {
        return auditReports[location];
    }
    
    function getLatestAudit(string calldata location) 
        external view returns (AuditReport memory) {
        AuditReport[] storage reports = auditReports[location];
        require(reports.length > 0, "No audit reports found");
        return reports[reports.length - 1];
    }
    
    /**
     * @dev Regulatory reporting
     */
    function generateRegulatoryReport(
        string calldata jurisdiction,
        string calldata reportType
    ) external view onlyRole(REGULATORY_REPORTING_ROLE) returns (bytes32 reportHash) {
        reportHash = keccak256(abi.encodePacked(
            jurisdiction,
            reportType,
            totalMetalWeight,
            metalWeightByType[MetalType.GOLD],
            metalWeightByType[MetalType.SILVER],
            block.timestamp
        ));
        
        return reportHash;
    }
    
    function generateComplianceReport(
        string calldata location,
        uint256 startDate,
        uint256 endDate
    ) external view returns (bytes32 reportHash) {
        require(startDate <= endDate, "Invalid date range");
        
        uint256 totalDeposits = 0;
        uint256 totalWithdrawals = 0;
        
        // Count deposits and withdrawals in the period
        MetalDeposit[] storage deposits = depositsByLocation[location];
        for (uint256 i = 0; i < deposits.length; i++) {
            if (deposits[i].depositDate >= startDate && deposits[i].depositDate <= endDate) {
                totalDeposits = totalDeposits.add(deposits[i].weight);
            }
        }
        
        reportHash = keccak256(abi.encodePacked(
            location,
            startDate,
            endDate,
            totalDeposits,
            totalWithdrawals,
            "COMPLIANCE_REPORT"
        ));
        
        return reportHash;
    }
    
    /**
     * @dev Utility functions
     */
    function getFacilityInfo(string calldata location) 
        external view returns (StorageFacility memory) {
        return storageFacilities[location];
    }
    
    function getAllFacilities() external view returns (string[] memory) {
        return facilityLocations;
    }
    
    function getCapacityUtilization(string calldata location) 
        external view returns (uint256 percentage) {
        StorageFacility storage facility = storageFacilities[location];
        if (facility.capacity == 0) return 0;
        return facility.currentUsage.mul(10000).div(facility.capacity); // basis points
    }
    
    function isInsured(string calldata location) external view returns (bool) {
        return storageFacilities[location].isInsured;
    }
    
    function getInsuranceExpiry(string calldata location) external view returns (uint256) {
        return storageFacilities[location].insuranceExpiry;
    }
    
    /**
     * @dev Internal helper functions
     */
    function _getMetalBasePrice(MetalType metalType) internal pure returns (uint256) {
        // Base prices in USD per gram (simplified)
        if (metalType == MetalType.GOLD) return 60 * 10**18; // $60/gram
        if (metalType == MetalType.SILVER) return 1 * 10**18; // $1/gram
        if (metalType == MetalType.PLATINUM) return 30 * 10**18; // $30/gram
        if (metalType == MetalType.PALLADIUM) return 25 * 10**18; // $25/gram
        return 0;
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
     * @dev Emergency functions
     */
    function emergencyWithdraw(string calldata location) 
        external onlyRole(DEFAULT_ADMIN_ROLE) whenPaused {
        // Emergency withdrawal procedures
        // This would be used in case of facility issues
    }
    
    /**
     * @dev Fallback function to receive ETH
     */
    receive() external payable {
        // Accept ETH payments for custody fees
    }
}