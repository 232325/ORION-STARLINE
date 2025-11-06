// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IMetalToken {
    enum MetalType {
        GOLD,
        SILVER,
        PLATINUM,
        PALLADIUM,
        RHODIUM,
        IRIDIUM
    }
    
    struct MetalReserve {
        address custodian;
        uint256 totalPhysicalAmount;
        uint256 tokenSupply;
        bool isActive;
        uint256 lastAuditTime;
        bytes32 auditProof;
    }
    
    struct MintRequest {
        address to;
        uint256 amount;
        MetalType metalType;
        bytes32 proofOfReserve;
        address auditor;
    }
    
    struct PriceInfo {
        uint256 price;
        uint256 timestamp;
        address oracle;
        bool isValid;
    }
    
    // Basic ERC-20 functions
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    
    // Metal-specific functions
    function mintMetal(address to, uint256 amount, MetalType metalType, bytes32 proofOfReserve) external returns (bool);
    function burnMetal(address from, uint256 amount) external returns (bool);
    function withdrawPhysical(address to, uint256 amount) external returns (bool);
    function depositPhysical(uint256 amount) external payable returns (bool);
    
    // Reserve management
    function getReserveInfo() external view returns (MetalReserve memory);
    function verifyReserve(bytes32 proofOfReserve) external view returns (bool);
    function updateCustodian(address newCustodian) external;
    function auditReserve() external;
    
    // Price management
    function getCurrentPrice() external view returns (PriceInfo memory);
    function setPriceOracle(address oracle) external;
    function updatePrice(uint256 newPrice) external;
    
    // Compliance
    function isKYCVerified(address account) external view returns (bool);
    function checkCompliance(address from, address to, uint256 amount) external view returns (bool);
    function freezeAccount(address account) external;
    function unfreezeAccount(address account) external;
    
    // Events
    event MetalMinted(address indexed to, uint256 amount, MetalType metalType, bytes32 proofOfReserve);
    event MetalBurned(address indexed from, uint256 amount, MetalType metalType);
    event PhysicalWithdrawal(address indexed to, uint256 amount, MetalType metalType);
    event PhysicalDeposit(address indexed from, uint256 amount, MetalType metalType);
    event CustodianUpdated(address indexed oldCustodian, address indexed newCustodian);
    event ReserveAudited(uint256 timestamp, bytes32 auditProof);
    event PriceUpdated(uint256 newPrice, address indexed oracle);
    event AccountFrozen(address indexed account);
    event AccountUnfrozen(address indexed account);
}

interface IMetalNFT {
    enum MetalGrade {
        INVESTMENT_GRADE,
        COMMERCIAL_GRADE,
        INDUSTRIAL_GRADE,
        JEWELRY_GRADE
    }
    
    struct MetalCertificate {
        string serialNumber;
        uint256 weight; // in grams
        uint256 purity; // 24k gold = 999, silver = 999, etc.
        MetalType metalType;
        MetalGrade grade;
        address custodian;
        string storageLocation;
        bool isTokenized;
        uint256 tokenizationDate;
        bytes32 authenticityHash;
    }
    
    // ERC-721 functions
    function balanceOf(address owner) external view returns (uint256);
    function ownerOf(uint256 tokenId) external view returns (address);
    function tokenURI(uint256 tokenId) external view returns (string memory);
    function approve(address to, uint256 tokenId) external;
    function setApprovalForAll(address operator, bool approved) external;
    function getApproved(uint256 tokenId) external view returns (address);
    function isApprovedForAll(address owner, address operator) external view returns (bool);
    function transferFrom(address from, address to, uint256 tokenId) external;
    function safeTransferFrom(address from, address to, uint256 tokenId) external;
    function safeTransferFrom(address from, address to, uint256 tokenId, bytes memory data) external;
    
    // Metal NFT specific functions
    function mintMetalItem(address to, MetalCertificate calldata certificate) external returns (uint256);
    function updateCertificate(uint256 tokenId, MetalCertificate calldata certificate) external;
    function verifyAuthenticity(uint256 tokenId) external view returns (bool);
    function getCertificate(uint256 tokenId) external view returns (MetalCertificate memory);
    function transferWithPhysicalDelivery(uint256 tokenId, address to, address deliveryAddress) external;
    function destroyToken(uint256 tokenId, string calldata reason) external;
    
    // Events
    event MetalItemMinted(uint256 indexed tokenId, address indexed to, MetalCertificate certificate);
    event CertificateUpdated(uint256 indexed tokenId, MetalCertificate newCertificate);
    event PhysicalDeliveryInitiated(uint256 indexed tokenId, address indexed to, address deliveryAddress);
    event TokenDestroyed(uint256 indexed tokenId, string reason);
    event AuthenticityVerified(uint256 indexed tokenId, bool isAuthentic);
}