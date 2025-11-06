// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "../interfaces/compliance/ICompliance.sol";
import "../utils/SafeMath.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @dev Comprehensive compliance and KYC/AML registry system
 */
contract ComplianceRegistry is ICompliance, AccessControl, Pausable {
    using SafeMath for uint256;
    
    bytes32 public constant COMPLIANCE_OFFICER_ROLE = keccak256("COMPLIANCE_OFFICER_ROLE");
    bytes32 public constant REGULATOR_ROLE = keccak256("REGULATOR_ROLE");
    bytes32 public constant AUDITOR_ROLE = keccak256("AUDITOR_ROLE");
    bytes32 public constant KYC_PROVIDER_ROLE = keccak256("KYC_PROVIDER_ROLE");
    
    // Compliance data storage
    mapping(address => ComplianceData) private _complianceData;
    mapping(address => ComplianceStatus) private _complianceStatus;
    mapping(address => RiskLevel) private _riskLevels;
    
    // Transaction monitoring
    mapping(bytes32 => TransactionRecord) private _transactions;
    uint256 public transactionCount;
    
    // Suspicious activity tracking
    struct SuspiciousReport {
        address reporter;
        address reportedAccount;
        string activityType;
        string details;
        bytes evidence;
        uint256 timestamp;
        bool isReviewed;
        ComplianceStatus action;
    }
    
    mapping(uint256 => SuspiciousReport) public suspiciousReports;
    uint256 public reportCount;
    
    // Regulatory reporting
    mapping(bytes32 => RegulatoryReport) public regulatoryReports;
    uint256 public reportCounter;
    
    // Sanctions and watchlists
    mapping(address => SanctionList) private _sanctions;
    mapping(bytes32 => bool) private _countrySanctions;
    
    // Audit trail
    mapping(address => bytes32[]) private _auditTrails;
    mapping(bytes32 => bool) private _auditHashes;
    
    // Events
    event ComplianceOfficerAssigned(address indexed officer, bool status);
    event RegulatorRegistered(address indexed regulator, string jurisdiction);
    event TransactionFlagged(bytes32 indexed txHash, address indexed from, address indexed to, string reason);
    event SuspiciousActivityReviewed(uint256 indexed reportId, ComplianceStatus action);
    event RegulatoryReportSubmitted(bytes32 indexed reportHash, string jurisdiction, ReportType reportType);
    event SanctionsScreening(address indexed account, bool isSanctioned);
    event AuditLogCreated(address indexed account, bytes32 actionHash, string actionType);
    
    constructor() {
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(COMPLIANCE_OFFICER_ROLE, msg.sender);
        _setupRole(REGULATOR_ROLE, msg.sender);
    }
    
    /**
     * @dev Compliance management functions
     */
    function registerCompliance(
        address account,
        ComplianceData calldata complianceInfo,
        bytes calldata proof
    ) external override onlyRole(KYC_PROVIDER_ROLE) {
        require(account != address(0), "Invalid account");
        require(complianceInfo.verificationDate <= block.timestamp, "Future verification date");
        
        // Verify proof hash
        bytes32 proofHash = keccak256(abi.encodePacked(complianceInfo, proof));
        require(_auditHashes[proofHash] == false, "Duplicate proof");
        
        // Update compliance data
        _complianceData[account] = complianceInfo;
        _complianceStatus[account] = complianceInfo.status;
        _riskLevels[account] = complianceInfo.riskLevel;
        
        // Store audit trail
        _createAuditLog(account, proofHash, "COMPLIANCE_REGISTERED");
        
        emit ComplianceRegistered(account, complianceInfo);
    }
    
    function updateCompliance(
        address account,
        ComplianceData calldata complianceInfo,
        bytes calldata proof
    ) external override onlyRole(KYC_PROVIDER_ROLE) {
        require(account != address(0), "Invalid account");
        
        // Verify proof hash
        bytes32 proofHash = keccak256(abi.encodePacked(complianceInfo, proof));
        require(_auditHashes[proofHash] == false, "Duplicate proof");
        
        // Update compliance data
        _complianceData[account] = complianceInfo;
        _complianceStatus[account] = complianceInfo.status;
        _riskLevels[account] = complianceInfo.riskLevel;
        
        // Store audit trail
        _createAuditLog(account, proofHash, "COMPLIANCE_UPDATED");
        
        emit ComplianceUpdated(account, complianceInfo);
    }
    
    function getComplianceData(address account) external view override returns (ComplianceData memory) {
        return _complianceData[account];
    }
    
    function getComplianceStatus(address account) external view override returns (ComplianceStatus) {
        return _complianceStatus[account];
    }
    
    function getRiskLevel(address account) external view override returns (RiskLevel) {
        return _riskLevels[account];
    }
    
    /**
     * @dev Transaction monitoring
     */
    function recordTransaction(
        address from,
        address to,
        uint256 amount,
        string calldata country,
        string calldata purpose
    ) external override returns (bytes32 txHash) {
        require(from != address(0) && to != address(0), "Invalid addresses");
        require(amount > 0, "Invalid amount");
        
        // Generate transaction hash
        txHash = keccak256(abi.encodePacked(
            transactionCount,
            from,
            to,
            amount,
            block.timestamp,
            blockhash(block.number - 1)
        ));
        
        // Create transaction record
        _transactions[txHash] = TransactionRecord({
            from: from,
            to: to,
            amount: amount,
            timestamp: block.timestamp,
            txHash: txHash,
            country: country,
            purpose: purpose,
            isFlagged: false
        });
        
        transactionCount = transactionCount.add(1);
        
        // Auto-flag large transactions for high-risk accounts
        if (_riskLevels[from] == RiskLevel.HIGH || _riskLevels[to] == RiskLevel.HIGH) {
            if (amount > 10000 * 10**18) { // > $10k threshold
                _transactions[txHash].isFlagged = true;
                emit TransactionFlagged(txHash, from, to, "High-risk account large transaction");
            }
        }
        
        emit TransactionRecorded(from, to, amount, txHash);
        _createAuditLog(from, txHash, "TRANSACTION_RECORDED");
        _createAuditLog(to, txHash, "TRANSACTION_RECORDED");
        
        return txHash;
    }
    
    function flagTransaction(bytes32 txHash, string calldata reason) external override onlyRole(COMPLIANCE_OFFICER_ROLE) {
        require(_transactions[txHash].timestamp > 0, "Transaction not found");
        require(!_transactions[txHash].isFlagged, "Already flagged");
        
        _transactions[txHash].isFlagged = true;
        emit TransactionFlagged(txHash, _transactions[txHash].from, _transactions[txHash].to, reason);
        _createAuditLog(msg.sender, txHash, "TRANSACTION_FLAGGED");
    }
    
    function getTransactionRecord(bytes32 txHash) external view override returns (TransactionRecord memory) {
        return _transactions[txHash];
    }
    
    /**
     * @dev Suspicious activity reporting
     */
    function reportSuspiciousActivity(
        address account,
        string calldata activityType,
        string calldata details,
        bytes calldata evidence
    ) external override onlyRole(COMPLIANCE_OFFICER_ROLE) returns (uint256 reportId) {
        require(account != address(0), "Invalid account");
        bytes32 evidenceHash = keccak256(evidence);
        
        reportId = reportCount;
        suspiciousReports[reportId] = SuspiciousReport({
            reporter: msg.sender,
            reportedAccount: account,
            activityType: activityType,
            details: details,
            evidence: evidence,
            timestamp: block.timestamp,
            isReviewed: false,
            action: ComplianceStatus.UNVERIFIED
        });
        
        reportCount = reportCount.add(1);
        _createAuditLog(account, evidenceHash, "SUSPICIOUS_ACTIVITY_REPORTED");
        
        emit SuspiciousActivityReported(account, reportId, activityType);
    }
    
    function getSuspiciousReports(address account) external view override returns (uint256[] memory) {
        uint256[] memory reports = new uint256[](reportCount);
        uint256 count = 0;
        
        for (uint256 i = 0; i < reportCount; i++) {
            if (suspiciousReports[i].reportedAccount == account) {
                reports[count] = i;
                count++;
            }
        }
        
        // Resize array
        uint256[] memory result = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = reports[i];
        }
        
        return result;
    }
    
    /**
     * @dev AML monitoring
     */
    function performAMLCheck(address account) external override returns (AMLCheck memory) {
        AMLRisk risk = _assessAMLRisk(account);
        string memory riskFactors = _generateRiskFactors(account);
        
        AMLCheck memory check = AMLCheck({
            account: account,
            risk: risk,
            riskFactors: riskFactors,
            timestamp: block.timestamp,
            isActive: true,
            reviewDate: block.timestamp.add(30 days)
        });
        
        _createAuditLog(account, keccak256(abi.encodePacked(risk)), "AML_CHECK_PERFORMED");
        
        return check;
    }
    
    function updateAMLRisk(address account, AMLRisk risk, string calldata riskFactors) external override {
        require(hasRole(COMPLIANCE_OFFICER_ROLE, msg.sender), "Unauthorized");
        
        // Update risk level in compliance data
        if (_complianceData[account].verificationDate > 0) {
            _complianceData[account].riskLevel = RiskLevel(risk);
            _riskLevels[account] = RiskLevel(risk);
        }
        
        _createAuditLog(account, keccak256(abi.encodePacked(risk, riskFactors)), "AML_RISK_UPDATED");
    }
    
    /**
     * @dev Sanctions screening
     */
    function checkSanctions(address account) public view override returns (bool isSanctioned) {
        // Check account sanctions
        if (_sanctions[account].account != address(0)) {
            return _sanctions[account].isActive;
        }
        
        // Check country sanctions (simplified implementation)
        ComplianceData memory complianceData = _complianceData[account];
        return _countrySanctions[keccak256(bytes(complianceData.jurisdiction))];
    }
    
    function addToSanctionList(SanctionList calldata sanction) external override onlyRole(REGULATOR_ROLE) {
        require(sanction.account != address(0), "Invalid account");
        
        _sanctions[sanction.account] = SanctionList({
            account: sanction.account,
            name: sanction.name,
            country: sanction.country,
            category: sanction.category,
            proofHash: keccak256(sanction.category),
            isActive: sanction.isActive
        });
        
        _createAuditLog(sanction.account, sanction.proofHash, "SANCTION_ADDED");
    }
    
    function removeFromSanctionList(address account) external override onlyRole(REGULATOR_ROLE) {
        require(_sanctions[account].account != address(0), "Account not sanctioned");
        
        _sanctions[account].isActive = false;
        _createAuditLog(account, _sanctions[account].proofHash, "SANCTION_REMOVED");
    }
    
    /**
     * @dev Transaction analysis
     */
    function analyzeTransaction(
        address from,
        address to,
        uint256 amount,
        string calldata jurisdiction
    ) external override returns (AMLRisk risk) {
        // Check sanctions
        if (checkSanctions(from) || checkSanctions(to)) {
            return AMLRisk.BLOCKED;
        }
        
        // Check compliance status
        ComplianceStatus fromStatus = _complianceStatus[from];
        ComplianceStatus toStatus = _complianceStatus[to];
        
        if (fromStatus == ComplianceStatus.FROZEN || toStatus == ComplianceStatus.FROZEN) {
            return AMLRisk.BLOCKED;
        }
        
        if (fromStatus == ComplianceStatus.SUSPENDED || toStatus == ComplianceStatus.SUSPENDED) {
            return AMLRisk.ENHANCED_DUE_DILIGENCE;
        }
        
        // Check risk levels
        RiskLevel fromRisk = _riskLevels[from];
        RiskLevel toRisk = _riskLevels[to];
        
        if (fromRisk == RiskLevel.CRITICAL || toRisk == RiskLevel.CRITICAL) {
            return AMLRisk.BLOCKED;
        }
        
        // Check transaction patterns
        if (amount > 100000 * 10**18) { // > $100k
            if (fromRisk == RiskLevel.HIGH || toRisk == RiskLevel.HIGH) {
                return AMLRisk.ENHANCED_DUE_DILIGENCE;
            }
        }
        
        // Default risk assessment
        if (fromRisk == RiskLevel.HIGH || toRisk == RiskLevel.HIGH) {
            return AMLRisk.MONITOR;
        }
        
        return AMLRisk.CLEAR;
    }
    
    /**
     * @dev Regulatory reporting
     */
    function generateTransactionReport(
        string calldata jurisdiction,
        uint256 startDate,
        uint256 endDate
    ) external view override onlyRole(REGULATOR_ROLE) returns (RegulatoryReport memory) {
        require(startDate <= endDate, "Invalid date range");
        require(block.timestamp >= endDate, "End date in future");
        
        bytes32 reportHash = keccak256(abi.encodePacked(
            jurisdiction,
            startDate,
            endDate,
            "TRANSACTION_REPORT",
            transactionCount
        ));
        
        return RegulatoryReport({
            reportType: ReportType.TRANSACTION_REPORT,
            jurisdiction: jurisdiction,
            reportingPeriod: endDate.sub(startDate),
            dataHash: reportHash,
            submissionDate: 0,
            status: "GENERATED",
            submissionHash: bytes32(0)
        });
    }
    
    function generateSuspiciousActivityReport(
        string calldata jurisdiction,
        address[] calldata accounts
    ) external view override onlyRole(REGULATOR_ROLE) returns (RegulatoryReport memory) {
        uint256 flaggedCount = 0;
        for (uint256 i = 0; i < reportCount; i++) {
            if (!suspiciousReports[i].isReviewed) {
                flaggedCount++;
            }
        }
        
        bytes32 reportHash = keccak256(abi.encodePacked(
            jurisdiction,
            accounts,
            flaggedCount,
            block.timestamp
        ));
        
        return RegulatoryReport({
            reportType: ReportType.SUSPICIOUS_ACTIVITY_REPORT,
            jurisdiction: jurisdiction,
            reportingPeriod: 0,
            dataHash: reportHash,
            submissionDate: 0,
            status: "GENERATED",
            submissionHash: bytes32(0)
        });
    }
    
    function submitRegulatoryReport(
        ReportType reportType,
        string calldata jurisdiction,
        bytes calldata reportData,
        bytes calldata signature
    ) external override onlyRole(REGULATOR_ROLE) returns (bytes32 reportHash) {
        reportHash = keccak256(abi.encodePacked(
            reportType,
            jurisdiction,
            reportData,
            signature,
            block.timestamp
        ));
        
        regulatoryReports[reportHash] = RegulatoryReport({
            reportType: reportType,
            jurisdiction: jurisdiction,
            reportingPeriod: 0,
            dataHash: keccak256(reportData),
            submissionDate: block.timestamp,
            status: "SUBMITTED",
            submissionHash: reportHash
        });
        
        reportCounter = reportCounter.add(1);
        emit RegulatoryReportSubmitted(reportHash, jurisdiction, reportType);
        _createAuditLog(msg.sender, reportHash, "REGULATORY_REPORT_SUBMITTED");
    }
    
    function getReportStatus(bytes32 reportHash) external view override returns (RegulatoryReport memory) {
        return regulatoryReports[reportHash];
    }
    
    /**
     * @dev Access control functions
     */
    function setComplianceOfficer(address officer, bool status) external override onlyRole(DEFAULT_ADMIN_ROLE) {
        require(officer != address(0), "Invalid officer address");
        
        if (status) {
            grantRole(COMPLIANCE_OFFICER_ROLE, officer);
        } else {
            revokeRole(COMPLIANCE_OFFICER_ROLE, officer);
        }
        
        emit ComplianceOfficerSet(officer, status);
    }
    
    function setRegulator(address regulator, string calldata jurisdiction) external override onlyRole(DEFAULT_ADMIN_ROLE) {
        require(regulator != address(0), "Invalid regulator address");
        
        grantRole(REGULATOR_ROLE, regulator);
        _createAuditLog(regulator, keccak256(bytes(jurisdiction)), "REGULATOR_REGISTERED");
        
        emit RegulatorRegistered(regulator, jurisdiction);
    }
    
    /**
     * @dev Audit trail functions
     */
    function getAuditTrail(address account) external view returns (bytes32[] memory) {
        return _auditTrails[account];
    }
    
    /**
     * @dev Internal helper functions
     */
    function _createAuditLog(address account, bytes32 actionHash, string memory actionType) internal {
        _auditHashes[actionHash] = true;
        _auditTrails[account].push(actionHash);
        
        emit AuditLogCreated(account, actionHash, actionType);
    }
    
    function _assessAMLRisk(address account) internal view returns (AMLRisk) {
        ComplianceStatus status = _complianceStatus[account];
        RiskLevel riskLevel = _riskLevels[account];
        
        if (checkSanctions(account)) {
            return AMLRisk.BLOCKED;
        }
        
        if (status == ComplianceStatus.KYC_REJECTED || status == ComplianceStatus.FROZEN) {
            return AMLRisk.BLOCKED;
        }
        
        if (status == ComplianceStatus.KYC_PENDING) {
            return AMLRisk.ENHANCED_DUE_DILIGENCE;
        }
        
        if (riskLevel == RiskLevel.CRITICAL) {
            return AMLRisk.BLOCKED;
        }
        
        if (riskLevel == RiskLevel.HIGH) {
            return AMLRisk.ENHANCED_DUE_DILIGENCE;
        }
        
        if (riskLevel == RiskLevel.MEDIUM) {
            return AMLRisk.MONITOR;
        }
        
        return AMLRisk.CLEAR;
    }
    
    function _generateRiskFactors(address account) internal view returns (string memory) {
        ComplianceStatus status = _complianceStatus[account];
        RiskLevel riskLevel = _riskLevels[account];
        
        if (status == ComplianceStatus.KYC_PENDING) {
            return "KYC verification pending";
        }
        
        if (status == ComplianceStatus.SUSPENDED) {
            return "Account suspended pending investigation";
        }
        
        if (riskLevel == RiskLevel.HIGH) {
            return "High-risk jurisdiction or activity pattern";
        }
        
        if (riskLevel == RiskLevel.MEDIUM) {
            return "Medium-risk account requiring monitoring";
        }
        
        return "Low-risk verified account";
    }
}