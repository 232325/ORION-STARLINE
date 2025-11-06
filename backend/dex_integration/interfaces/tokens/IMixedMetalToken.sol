// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IMixedMetalToken {
    enum AssetType {
        FUNGIBLE_METAL,
        NFT_METAL,
        COMPOSITE_ASSET,
        DERIVATIVE_TOKEN
    }
    
    struct MixedMetalAsset {
        AssetType assetType;
        uint256 metalType; // 0: Gold, 1: Silver, 2: Platinum, 3: Palladium
        uint256 amount; // For fungible assets
        uint256 tokenId; // For NFT assets
        uint256 weight; // In grams
        uint256 purity; // 999 for pure metals
        bytes32 assetHash; // Hash for verification
        address custodyAddress;
    }
    
    struct BatchMintData {
        address to;
        uint256[] ids;
        uint256[] amounts;
        bytes data;
        MixedMetalAsset[] assets;
    }
    
    struct BatchTransferData {
        address from;
        address to;
        uint256[] ids;
        uint256[] amounts;
        bytes data;
    }
    
    // ERC-1155 functions
    function balanceOf(address account, uint256 id) external view returns (uint256);
    function balanceOfBatch(address[] calldata accounts, uint256[] calldata ids) 
        external view returns (uint256[] memory);
    
    function setApprovalForAll(address operator, bool approved) external;
    function isApprovedForAll(address account, address operator) external view returns (bool);
    
    function safeTransferFrom(address from, address to, uint256 id, uint256 amount, bytes calldata data) external;
    function safeBatchTransferFrom(
        address from, 
        address to, 
        uint256[] calldata ids, 
        uint256[] calldata amounts, 
        bytes calldata data
    ) external;
    
    function uri(uint256 id) external view returns (string memory);
    
    // Mixed metal specific functions
    function mintMixedMetal(BatchMintData calldata mintData) external returns (uint256[] memory);
    function burnMixedMetal(address from, uint256[] calldata ids, uint256[] calldata amounts) external;
    
    function createCompositeAsset(
        string calldata name,
        string calldata symbol,
        uint256[] calldata componentIds,
        uint256[] calldata componentAmounts,
        MixedMetalAsset[] calldata assets
    ) external returns (uint256 compositeTokenId);
    
    function decomposeAsset(uint256 compositeTokenId) external;
    function verifyAssetComposition(uint256 id) external view returns (MixedMetalAsset memory);
    
    // Metal bundle operations
    function bundleAssets(
        uint256[] calldata assetIds,
        uint256[] calldata amounts,
        address recipient
    ) external returns (uint256 bundleTokenId);
    
    function unbundleAsset(uint256 bundleTokenId) external;
    
    // Price and valuation
    function getAssetValue(uint256 id) external view returns (uint256 usdValue);
    function getPortfolioValue(address account) external view returns (uint256 totalValue);
    function calculatePortfolioRisk(address account) external view returns (uint256 riskScore);
    
    // Compliance and KYC
    function checkTransferCompliance(
        address from, 
        address to, 
        uint256[] calldata ids, 
        uint256[] calldata amounts
    ) external view returns (bool);
    
    // Events
    event MixedMetalMinted(address indexed to, uint256[] ids, uint256[] amounts, bytes data);
    event CompositeAssetCreated(uint256 indexed tokenId, string name, string symbol);
    event AssetsBundled(uint256 indexed bundleTokenId, address indexed recipient, uint256[] assetIds);
    event AssetDecomposed(uint256 indexed compositeTokenId);
    event PortfolioValuation(address indexed account, uint256 totalValue);
}