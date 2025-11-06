// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IComplianceRegistry {
    enum ComplianceStatus {
        UNVERIFIED,
        KYC_PENDING,
        KYC_APPROVED,
        KYC_REJECTED,
        FROZEN,
        SUSPENDED
    }
    
    enum RiskLevel {
        LOW,
        MEDIUM,
        HIGH,
        CRITICAL
    }
    
    struct ComplianceData {
        ComplianceStatus status;
        RiskLevel riskLevel;
        string jurisdiction;
        string verificationType;
        uint256 verificationDate;
        uint256 expiryDate;
        address verifier;
        bool isAccredited;
        uint256 spendingLimit;
        bytes32 dataHash;
    }
    
    struct TransactionRecord {
        address from;
        address to;
        uint256 amount;
        uint256 timestamp;
        bytes32 txHash;
        string country;
        string purpose;
        bool isFlagged;
    }
    
    // Compliance management
    function registerCompliance(
        address account,
        ComplianceData calldata complianceInfo,
        bytes calldata proof
    ) external;
    
    function updateCompliance(
        address account,
        ComplianceData calldata complianceInfo,
        bytes calldata proof
    ) external;
    
    function getComplianceData(address account) external view returns (ComplianceData memory);
    function getComplianceStatus(address account) external view returns (ComplianceStatus);
    function getRiskLevel(address account) external view returns (RiskLevel);
    
    // Transaction monitoring
    function recordTransaction(
        address from,
        address to,
        uint256 amount,
        string calldata country,
        string calldata purpose
    ) external returns (bytes32 txHash);
    
    function flagTransaction(bytes32 txHash, string calldata reason) external;
    function getTransactionRecord(bytes32 txHash) external view returns (TransactionRecord memory);
    
    // Suspicious activity
    function reportSuspiciousActivity(
        address account,
        string calldata activityType,
        string calldata details,
        bytes calldata evidence
    ) external returns (uint256 reportId);
    
    function getSuspiciousReports(address account) external view returns (uint256[] memory);
    
    // Regulatory reporting
    function generateComplianceReport(
        string calldata reportType,
        uint256 startDate,
        uint256 endDate
    ) external view returns (bytes32 reportHash);
    
    // Access control
    function setComplianceOfficer(address officer, bool status) external;
    function setRegulator(address regulator, string calldata jurisdiction) external;
    
    // Events
    event ComplianceRegistered(address indexed account, ComplianceData complianceInfo);
    event ComplianceUpdated(address indexed account, ComplianceData newInfo);
    event TransactionRecorded(address indexed from, address indexed to, uint256 amount, bytes32 txHash);
    event SuspiciousActivityReported(address indexed account, uint256 reportId, string activityType);
    event ComplianceOfficerSet(address indexed officer, bool status);
}

interface IAMLMonitor {
    enum AMLRisk {
        CLEAR,
        MONITOR,
        ENHANCED_DUE_DILIGENCE,
        BLOCKED
    }
    
    struct AMLCheck {
        address account;
        AMLRisk risk;
        string riskFactors;
        uint256 timestamp;
        bool isActive;
        uint256 reviewDate;
    }
    
    struct SanctionList {
        address account;
        string name;
        string country;
        string category;
        bytes32 proofHash;
        bool isActive;
    }
    
    // AML checks
    function performAMLCheck(address account) external returns (AMLCheck memory);
    function updateAMLRisk(address account, AMLRisk risk, string calldata riskFactors) external;
    
    // Sanctions screening
    function checkSanctions(address account) external view returns (bool isSanctioned);
    function addToSanctionList(SanctionList calldata sanction) external;
    function removeFromSanctionList(address account) external;
    
    // Transaction monitoring
    function analyzeTransaction(
        address from,
        address to,
        uint256 amount,
        string calldata jurisdiction
    ) external returns (AMLRisk risk);
    
    // Due diligence
    function initiateDueDiligence(address account, string calldata reason) external;
    function submitDueDiligenceReport(address account, bytes calldata report) external;
    
    // Events
    event AMLCheckPerformed(address indexed account, AMLRisk risk);
    event SanctionScreening(address indexed account, bool isSanctioned);
    event DueDiligenceInitiated(address indexed account, string reason);
}

interface IRegulatoryReporter {
    enum ReportType {
        TRANSACTION_REPORT,
        CASH_TRANSACTION_REPORT,
        SUSPICIOUS_ACTIVITY_REPORT,
        COMPLIANCE_CERTIFICATE,
        ANNUAL_COMPLIANCE
    }
    
    struct RegulatoryReport {
        ReportType reportType;
        string jurisdiction;
        uint256 reportingPeriod;
        bytes32 dataHash;
        uint256 submissionDate;
        string status;
        bytes32 submissionHash;
    }
    
    // Report generation
    function generateTransactionReport(
        string calldata jurisdiction,
        uint256 startDate,
        uint256 endDate
    ) external view returns (RegulatoryReport memory);
    
    function generateSuspiciousActivityReport(
        string calldata jurisdiction,
        address[] calldata accounts
    ) external view returns (RegulatoryReport memory);
    
    // Report submission
    function submitRegulatoryReport(
        ReportType reportType,
        string calldata jurisdiction,
        bytes calldata reportData,
        bytes calldata signature
    ) external returns (bytes32 reportHash);
    
    function getReportStatus(bytes32 reportHash) external view returns (RegulatoryReport memory);
    
    // Compliance certificates
    function issueComplianceCertificate(
        address entity,
        string calldata certificateType,
        uint256 expiryDate,
        bytes calldata supportingDocuments
    ) external returns (bytes32 certificateHash);
    
    // Events
    event ReportGenerated(ReportType reportType, string jurisdiction, bytes32 reportHash);
    event ReportSubmitted(ReportType reportType, bytes32 submissionHash, string status);
    event ComplianceCertificateIssued(address indexed entity, bytes32 certificateHash);
}