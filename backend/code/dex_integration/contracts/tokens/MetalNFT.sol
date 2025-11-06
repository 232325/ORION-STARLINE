// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "../interfaces/tokens/IMetalTokens.sol";
import "../interfaces/IERC20.sol";
import "../utils/SafeMath.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @dev Implementation of ERC-721 for unique metal items with certificates
 */
contract MetalNFT is IMetalNFT, ERC721, ERC721URIStorage, AccessControl, Pausable {
    using SafeMath for uint256;
    using Strings for uint256;
    
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant CUSTODIAN_ROLE = keccak256("CUSTODIAN_ROLE");
    bytes32 public constant CERTIFIER_ROLE = keccak256("CERTIFIER_ROLE");
    bytes32 public constant COMPLIANCE_ROLE = keccak256("COMPLIANCE_ROLE");
    
    // NFT metadata
    string private _baseTokenURI;
    uint256 private _tokenIds;
    
    // Metal certificates mapping
    mapping(uint256 => MetalCertificate) private _certificates;
    
    // Authenticity verification
    mapping(address => bool) private _authenticators;
    mapping(bytes32 => bool) private _usedAuthenticityHashes;
    
    // Compliance tracking
    mapping(address => ComplianceStatus) public accountComplianceStatus;
    mapping(address => bool) private _frozenAccounts;
    
    // Events
    event AuthenticityCertificateIssued(uint256 indexed tokenId, bytes32 authenticityHash);
    event PhysicalDeliveryConfirmed(uint256 indexed tokenId, string trackingNumber);
    event ComplianceCheckPerformed(address indexed from, address indexed to, uint256 tokenId, bool approved);
    event AuthenticityVerificationPerformed(uint256 indexed tokenId, bool isAuthentic);
    
    constructor(
        string memory name,
        string memory symbol,
        string memory baseTokenURI_
    ) ERC721(name, symbol) {
        _baseTokenURI = baseTokenURI_;
        
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setupRole(MINTER_ROLE, msg.sender);
        _setupRole(CUSTODIAN_ROLE, msg.sender);
        _setupRole(CERTIFIER_ROLE, msg.sender);
        _setupRole(COMPLIANCE_ROLE, msg.sender);
    }
    
    /**
     * @dev ERC-721 standard functions
     */
    function balanceOf(address owner) public view override(ERC721, IERC165) returns (uint256) {
        require(owner != address(0), "ERC721: balance query for the zero address");
        return _balances[owner];
    }
    
    function ownerOf(uint256 tokenId) public view override(ERC721, IERC165) returns (address) {
        address owner = _owners[tokenId];
        require(owner != address(0), "ERC721: owner query for nonexistent token");
        return owner;
    }
    
    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        require(_exists(tokenId), "ERC721Metadata: URI query for nonexistent token");
        return string(abi.encodePacked(_baseURI, _tokenURIs[tokenId]));
    }
    
    function approve(address to, uint256 tokenId) public override(ERC721, IERC165) {
        address owner = ERC721.ownerOf(tokenId);
        require(to != owner, "ERC721: approval to current owner");
        require(
            _msgSender() == owner || isApprovedForAll(owner, _msgSender()),
            "ERC721: approve caller is not owner nor approved for all"
        );
        _approve(to, tokenId);
    }
    
    function setApprovalForAll(address operator, bool approved) public override(ERC721, IERC165) {
        require(_msgSender() != operator, "ERC721: approve to caller");
        _operatorApprovals[_msgSender()][operator] = approved;
        emit ApprovalForAll(_msgSender(), operator, approved);
    }
    
    function getApproved(uint256 tokenId) public view override(ERC721, IERC165) returns (address) {
        require(_exists(tokenId), "ERC721Metadata: approved query for nonexistent token");
        return _tokenApprovals[tokenId];
    }
    
    function isApprovedForAll(address owner, address operator) public view override(ERC721, IERC165) returns (bool) {
        return _operatorApprovals[owner][operator];
    }
    
    function transferFrom(
        address from,
        address to,
        uint256 tokenId
    ) public override(ERC721, IERC165) {
        require(_isApprovedOrOwner(_msgSender(), tokenId), "ERC721: transfer caller is not owner nor approved");
        _transfer(from, to, tokenId);
    }
    
    function safeTransferFrom(
        address from,
        address to,
        uint256 tokenId
    ) public override(ERC721, IERC165) {
        safeTransferFrom(from, to, tokenId, "");
    }
    
    function safeTransferFrom(
        address from,
        address to,
        uint256 tokenId,
        bytes memory _data
    ) public override(ERC721, IERC165) {
        require(_isApprovedOrOwner(_msgSender(), tokenId), "ERC721: transfer caller is not owner nor approved");
        _safeTransfer(from, to, tokenId, _data);
    }
    
    /**
     * @dev Metal NFT specific functions
     */
    function mintMetalItem(address to, MetalCertificate calldata certificate) 
        external override onlyRole(MINTER_ROLE) whenNotPaused returns (uint256) {
        require(to != address(0), "Cannot mint to zero address");
        require(!_usedAuthenticityHashes[certificate.authenticityHash], "Authenticity hash already used");
        
        _tokenIds = _tokenIds.add(1);
        uint256 newTokenId = _tokenIds;
        
        // Create certificate
        _certificates[newTokenId] = MetalCertificate({
            serialNumber: certificate.serialNumber,
            weight: certificate.weight,
            purity: certificate.purity,
            metalType: certificate.metalType,
            grade: certificate.grade,
            custodian: certificate.custodian,
            storageLocation: certificate.storageLocation,
            isTokenized: true,
            tokenizationDate: block.timestamp,
            authenticityHash: certificate.authenticityHash
        });
        
        // Mark authenticity hash as used
        _usedAuthenticityHashes[certificate.authenticityHash] = true;
        
        // Mint NFT
        _safeMint(to, newTokenId);
        
        emit MetalItemMinted(newTokenId, to, certificate);
        emit AuthenticityCertificateIssued(newTokenId, certificate.authenticityHash);
        
        return newTokenId;
    }
    
    function updateCertificate(uint256 tokenId, MetalCertificate calldata newCertificate) 
        external override onlyRole(CERTIFIER_ROLE) {
        require(_exists(tokenId), "Token does not exist");
        require(
            hasRole(DEFAULT_ADMIN_ROLE, msg.sender) || 
            msg.sender == _certificates[tokenId].custodian,
            "Not authorized to update certificate"
        );
        
        MetalCertificate storage currentCert = _certificates[tokenId];
        
        // Only allow certain fields to be updated
        currentCert.custodian = newCertificate.custodian;
        currentCert.storageLocation = newCertificate.storageLocation;
        currentCert.weight = newCertificate.weight;
        currentCert.purity = newCertificate.purity;
        
        emit CertificateUpdated(tokenId, newCertificate);
    }
    
    function verifyAuthenticity(uint256 tokenId) public view override returns (bool) {
        require(_exists(tokenId), "Token does not exist");
        MetalCertificate memory cert = _certificates[tokenId];
        return !_usedAuthenticityHashes[cert.authenticityHash];
    }
    
    function getCertificate(uint256 tokenId) external view override returns (MetalCertificate memory) {
        require(_exists(tokenId), "Token does not exist");
        return _certificates[tokenId];
    }
    
    function transferWithPhysicalDelivery(
        uint256 tokenId,
        address to,
        address deliveryAddress
    ) external override {
        require(ownerOf(tokenId) == msg.sender, "Not token owner");
        require(to != address(0), "Invalid recipient");
        require(deliveryAddress != address(0), "Invalid delivery address");
        
        // Check compliance
        require(checkTransferCompliance(msg.sender, to, tokenId), "Compliance check failed");
        
        // Transfer NFT
        _transfer(msg.sender, to, tokenId);
        
        // Emit delivery event (actual delivery would be handled off-chain)
        emit PhysicalDeliveryInitiated(tokenId, to, deliveryAddress);
    }
    
    function destroyToken(uint256 tokenId, string calldata reason) external override {
        require(ownerOf(tokenId) == msg.sender, "Not token owner");
        
        // Burn token
        _burn(tokenId);
        delete _certificates[tokenId];
        
        emit TokenDestroyed(tokenId, reason);
    }
    
    /**
     * @dev Compliance and security functions
     */
    function checkTransferCompliance(address from, address to, uint256 tokenId) public view returns (bool) {
        // Check if accounts are frozen
        if (_frozenAccounts[from] || _frozenAccounts[to]) return false;
        
        // Check compliance status for high-value items
        MetalCertificate memory cert = _certificates[tokenId];
        if (cert.weight > 100) { // High-value items (over 100g)
            ComplianceStatus fromStatus = accountComplianceStatus[from];
            ComplianceStatus toStatus = accountComplianceStatus[to];
            
            if (fromStatus == ComplianceStatus.KYC_PENDING || 
                toStatus == ComplianceStatus.KYC_PENDING) {
                return false;
            }
            
            if (fromStatus == ComplianceStatus.KYC_REJECTED || 
                toStatus == ComplianceStatus.KYC_REJECTED) {
                return false;
            }
        }
        
        return true;
    }
    
    function setComplianceStatus(address account, ComplianceStatus status) 
        external onlyRole(COMPLIANCE_ROLE) {
        require(account != address(0), "Invalid account");
        accountComplianceStatus[account] = status;
        
        if (status == ComplianceStatus.FROZEN) {
            _frozenAccounts[account] = true;
            emit AccountFrozen(account);
        } else if (status == ComplianceStatus.KYC_REJECTED) {
            _frozenAccounts[account] = true;
            emit AccountFrozen(account);
        } else {
            _frozenAccounts[account] = false;
        }
    }
    
    function freezeAccount(address account) external onlyRole(COMPLIANCE_ROLE) {
        require(account != address(0), "Invalid account");
        _frozenAccounts[account] = true;
        accountComplianceStatus[account] = ComplianceStatus.FROZEN;
        emit AccountFrozen(account);
    }
    
    function unfreezeAccount(address account) external onlyRole(COMPLIANCE_ROLE) {
        require(account != address(0), "Invalid account");
        _frozenAccounts[account] = false;
        accountComplianceStatus[account] = ComplianceStatus.KYC_APPROVED;
        emit AccountUnfrozen(account);
    }
    
    /**
     * @dev Authenticity verification
     */
    function addAuthenticator(address authenticator) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(authenticator != address(0), "Invalid authenticator");
        _authenticators[authenticator] = true;
    }
    
    function removeAuthenticator(address authenticator) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(authenticator != address(0), "Invalid authenticator");
        _authenticators[authenticator] = false;
    }
    
    function verifyMetalAuthenticity(uint256 tokenId) external returns (bool) {
        require(_authenticators[msg.sender], "Not authorized authenticator");
        require(_exists(tokenId), "Token does not exist");
        
        MetalCertificate memory cert = _certificates[tokenId];
        require(cert.authenticityHash != bytes32(0), "No authenticity hash");
        
        bool isAuthentic = verifyAuthenticity(tokenId);
        emit AuthenticityVerified(tokenId, isAuthentic);
        
        return isAuthentic;
    }
    
    /**
     * @dev Utility functions
     */
    function getTokenDetails(uint256 tokenId) external view returns (
        string memory serialNumber,
        uint256 weight,
        uint256 purity,
        MetalType metalType,
        MetalGrade grade,
        string memory storageLocation
    ) {
        require(_exists(tokenId), "Token does not exist");
        MetalCertificate memory cert = _certificates[tokenId];
        
        return (
            cert.serialNumber,
            cert.weight,
            cert.purity,
            cert.metalType,
            cert.grade,
            cert.storageLocation
        );
    }
    
    function getMetalTokensByType(MetalType metalType) external view returns (uint256[] memory) {
        uint256[] memory metalTokenIds = new uint256[](_tokenIds);
        uint256 count = 0;
        
        for (uint256 i = 1; i <= _tokenIds; i++) {
            if (_certificates[i].metalType == metalType && _exists(i)) {
                metalTokenIds[count] = i;
                count++;
            }
        }
        
        // Resize array to actual count
        uint256[] memory result = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = metalTokenIds[i];
        }
        
        return result;
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
     * @dev Internal functions
     */
    function _transfer(
        address from,
        address to,
        uint256 tokenId
    ) internal override(ERC721) whenNotPaused {
        require(!_frozenAccounts[from], "From account is frozen");
        require(!_frozenAccounts[to], "To account is frozen");
        require(checkTransferCompliance(from, to, tokenId), "Compliance check failed");
        
        super._transfer(from, to, tokenId);
        emit ComplianceCheckPerformed(from, to, tokenId, true);
    }
    
    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
        delete _certificates[tokenId];
    }
    
    function _baseURI() internal view override(ERC721) returns (string memory) {
        return _baseTokenURI;
    }
    
    // The following functions are overrides required by Solidity.
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage, AccessControl, IERC165)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
    
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }
}