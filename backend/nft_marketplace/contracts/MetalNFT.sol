// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title MetalNFT
 * @dev Physical Metal-backed NFT Tokens with authentication and verification
 */
contract MetalNFT is ERC721URIStorage, Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;
    
    Counters.Counter private _tokenIdCounter;
    
    enum MetalType {
        GOLD,
        SILVER,
        PLATINUM,
        PALLADIUM,
        RHODIUM,
        RUTHENIUM
    }
    
    struct MetalMetadata {
        MetalType metalType;
        uint256 weight; // in grams
        uint256 purity; // percentage * 100 (e.g., 9999 = 99.99%)
        string assayCertificate;
        string storageFacility;
        string insurancePolicy;
        uint256 storageStartDate;
        bool isVerified;
        address verifier;
        string ipfsHash;
    }
    
    mapping(uint256 => MetalMetadata) public metalData;
    mapping(address => bool) public authorizedVerifiers;
    mapping(uint256 => bool) public usedAssayCertificates;
    
    event MetalTokenCreated(
        uint256 indexed tokenId, 
        address indexed owner, 
        MetalType metalType,
        uint256 weight,
        uint256 purity
    );
    
    event MetalTokenVerified(
        uint256 indexed tokenId, 
        address indexed verifier,
        string assayCertificate
    );
    
    event MetalTokenTransferred(
        uint256 indexed tokenId,
        address indexed from,
        address indexed to,
        uint256 price
    );
    
    constructor() ERC721("MetalNFT", "MNT") Ownable(msg.sender) {}
    
    /**
     * @dev Create new metal-backed NFT token
     */
    function mintMetalNFT(
        address to,
        MetalType metalType,
        uint256 weight,
        uint256 purity,
        string memory tokenURI,
        string memory assayCertificate,
        string memory storageFacility,
        string memory insurancePolicy
    ) external onlyOwner nonReentrant returns (uint256) {
        require(purity >= 0 && purity <= 10000, "Purity must be between 0% and 100%");
        require(weight > 0, "Weight must be greater than 0");
        require(!usedAssayCertificates[stringToBytes32(assayCertificate)], "Certificate already used");
        
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, tokenURI);
        
        metalData[tokenId] = MetalMetadata({
            metalType: metalType,
            weight: weight,
            purity: purity,
            assayCertificate: assayCertificate,
            storageFacility: storageFacility,
            insurancePolicy: insurancePolicy,
            storageStartDate: block.timestamp,
            isVerified: false,
            verifier: address(0),
            ipfsHash: ""
        });
        
        usedAssayCertificates[stringToBytes32(assayCertificate)] = true;
        
        emit MetalTokenCreated(tokenId, to, metalType, weight, purity);
        
        return tokenId;
    }
    
    /**
     * @dev Verify metal token authenticity
     */
    function verifyMetalNFT(
        uint256 tokenId,
        string memory ipfsHash
    ) external onlyAuthorizedVerifier nonReentrant {
        require(_exists(tokenId), "Token does not exist");
        require(!metalData[tokenId].isVerified, "Token already verified");
        
        metalData[tokenId].isVerified = true;
        metalData[tokenId].verifier = msg.sender;
        metalData[tokenId].ipfsHash = ipfsHash;
        
        emit MetalTokenVerified(tokenId, msg.sender, metalData[tokenId].assayCertificate);
    }
    
    /**
     * @dev Transfer metal token with price tracking
     */
    function transferMetalNFT(
        address to,
        uint256 tokenId
    ) external payable nonReentrant {
        require(_exists(tokenId), "Token does not exist");
        require(ownerOf(tokenId) == msg.sender, "Not token owner");
        require(to != address(0), "Invalid recipient");
        
        address from = ownerOf(tokenId);
        _transfer(from, to, tokenId);
        
        emit MetalTokenTransferred(tokenId, from, to, msg.value);
    }
    
    /**
     * @dev Get metal token metadata
     */
    function getMetalData(uint256 tokenId) external view returns (MetalMetadata memory) {
        require(_exists(tokenId), "Token does not exist");
        return metalData[tokenId];
    }
    
    /**
     * @dev Add authorized verifier
     */
    function addVerifier(address verifier) external onlyOwner {
        authorizedVerifiers[verifier] = true;
    }
    
    /**
     * @dev Remove authorized verifier
     */
    function removeVerifier(address verifier) external onlyOwner {
        authorizedVerifiers[verifier] = false;
    }
    
    /**
     * @dev Update token URI for metadata
     */
    function updateTokenURI(uint256 tokenId, string memory newTokenURI) external onlyOwner {
        require(_exists(tokenId), "Token does not exist");
        _setTokenURI(tokenId, newTokenURI);
    }
    
    /**
     * @dev Check if address is authorized verifier
     */
    modifier onlyAuthorizedVerifier() {
        require(authorizedVerifiers[msg.sender] || owner() == msg.sender, "Not authorized verifier");
        _;
    }
    
    /**
     * @dev Utility function to convert string to bytes32
     */
    function stringToBytes32(string memory source) private pure returns (bytes32 result) {
        bytes memory tempEmptyStringTest = bytes(source);
        if (tempEmptyStringTest.length == 0) {
            return 0x0;
        }
        assembly {
            result := mload(add(source, 32))
        }
    }
    
    /**
     * @dev Get total supply of metal tokens
     */
    function totalSupply() external view returns (uint256) {
        return _tokenIdCounter.current();
    }
}