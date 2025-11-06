// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title MetalNFTMarketplace
 * @dev NFT Marketplace for trading metal-backed tokens with auctions and fixed prices
 */
contract MetalNFTMarketplace is ReentrancyGuard, Ownable {
    using Counters for Counters.Counter;
    
    Counters.Counter private _listingIdCounter;
    
    struct Listing {
        uint256 id;
        address nftContract;
        uint256 tokenId;
        address seller;
        uint256 price;
        bool isAuction;
        uint256 auctionEndTime;
        address highestBidder;
        uint256 highestBid;
        bool isActive;
        uint256 createdAt;
        uint256 royaltyFee; // basis points (e.g., 250 = 2.5%)
        address royaltyRecipient;
    }
    
    struct Bid {
        address bidder;
        uint256 amount;
        uint256 timestamp;
    }
    
    mapping(uint256 => Listing) public listings;
    mapping(uint256 => mapping(address => uint256)) public bids; // listingId => bidder => amount
    mapping(uint256 => Bid[]) public listingBids; // listingId => array of bids
    mapping(address => uint256[]) public userListings; // user => listingIds
    
    uint256 public platformFee = 250; // 2.5% in basis points
    address public feeRecipient;
    
    event ListingCreated(
        uint256 indexed listingId,
        address indexed seller,
        address indexed nftContract,
        uint256 tokenId,
        uint256 price,
        bool isAuction
    );
    
    event ListingPurchased(
        uint256 indexed listingId,
        address indexed buyer,
        address indexed seller,
        uint256 price
    );
    
    event BidPlaced(
        uint256 indexed listingId,
        address indexed bidder,
        uint256 amount
    );
    
    event BidWithdrawn(
        uint256 indexed listingId,
        address indexed bidder,
        uint256 amount
    );
    
    event AuctionEnded(
        uint256 indexed listingId,
        address indexed winner,
        address indexed seller,
        uint256 finalPrice
    );
    
    event ListingCancelled(
        uint256 indexed listingId,
        address indexed seller
    );
    
    constructor(address _feeRecipient) Ownable(msg.sender) {
        feeRecipient = _feeRecipient;
    }
    
    /**
     * @dev Create fixed price listing
     */
    function createFixedPriceListing(
        address nftContract,
        uint256 tokenId,
        uint256 price,
        uint256 royaltyFee,
        address royaltyRecipient
    ) external nonReentrant returns (uint256) {
        require(price > 0, "Price must be greater than 0");
        require(nftContract != address(0), "Invalid NFT contract");
        
        IERC721(nftContract).transferFrom(msg.sender, address(this), tokenId);
        
        uint256 listingId = _listingIdCounter.current();
        _listingIdCounter.increment();
        
        listings[listingId] = Listing({
            id: listingId,
            nftContract: nftContract,
            tokenId: tokenId,
            seller: msg.sender,
            price: price,
            isAuction: false,
            auctionEndTime: 0,
            highestBidder: address(0),
            highestBid: 0,
            isActive: true,
            createdAt: block.timestamp,
            royaltyFee: royaltyFee,
            royaltyRecipient: royaltyRecipient
        });
        
        userListings[msg.sender].push(listingId);
        
        emit ListingCreated(listingId, msg.sender, nftContract, tokenId, price, false);
        
        return listingId;
    }
    
    /**
     * @dev Create auction listing
     */
    function createAuctionListing(
        address nftContract,
        uint256 tokenId,
        uint256 startingPrice,
        uint256 auctionDuration,
        uint256 royaltyFee,
        address royaltyRecipient
    ) external nonReentrant returns (uint256) {
        require(startingPrice > 0, "Starting price must be greater than 0");
        require(auctionDuration > 0, "Auction duration must be greater than 0");
        require(nftContract != address(0), "Invalid NFT contract");
        
        IERC721(nftContract).transferFrom(msg.sender, address(this), tokenId);
        
        uint256 listingId = _listingIdCounter.current();
        _listingIdCounter.increment();
        
        listings[listingId] = Listing({
            id: listingId,
            nftContract: nftContract,
            tokenId: tokenId,
            seller: msg.sender,
            price: startingPrice,
            isAuction: true,
            auctionEndTime: block.timestamp + auctionDuration,
            highestBidder: address(0),
            highestBid: 0,
            isActive: true,
            createdAt: block.timestamp,
            royaltyFee: royaltyFee,
            royaltyRecipient: royaltyRecipient
        });
        
        userListings[msg.sender].push(listingId);
        
        emit ListingCreated(listingId, msg.sender, nftContract, tokenId, startingPrice, true);
        
        return listingId;
    }
    
    /**
     * @dev Purchase fixed price listing
     */
    function purchaseListing(uint256 listingId) external payable nonReentrant {
        Listing storage listing = listings[listingId];
        
        require(listing.isActive, "Listing is not active");
        require(!listing.isAuction, "This is an auction listing");
        require(msg.value >= listing.price, "Insufficient payment");
        require(msg.sender != listing.seller, "Seller cannot purchase own listing");
        
        listing.isActive = false;
        
        // Calculate fees
        uint256 platformFeeAmount = (listing.price * platformFee) / 10000;
        uint256 royaltyAmount = (listing.price * listing.royaltyFee) / 10000;
        uint256 sellerAmount = listing.price - platformFeeAmount - royaltyAmount;
        
        // Transfer NFT to buyer
        IERC721(listing.nftContract).transferFrom(address(this), msg.sender, listing.tokenId);
        
        // Transfer payments
        payable(feeRecipient).transfer(platformFeeAmount);
        if (royaltyAmount > 0 && listing.royaltyRecipient != address(0)) {
            payable(listing.royaltyRecipient).transfer(royaltyAmount);
        }
        payable(listing.seller).transfer(sellerAmount);
        
        emit ListingPurchased(listingId, msg.sender, listing.seller, listing.price);
    }
    
    /**
     * @dev Place bid on auction
     */
    function placeBid(uint256 listingId) external payable nonReentrant {
        Listing storage listing = listings[listingId];
        
        require(listing.isActive, "Listing is not active");
        require(listing.isAuction, "This is not an auction listing");
        require(block.timestamp < listing.auctionEndTime, "Auction has ended");
        require(msg.value > listing.highestBid, "Bid must be higher than current highest bid");
        require(msg.sender != listing.seller, "Seller cannot bid on own listing");
        
        // Refund previous highest bidder
        if (listing.highestBidder != address(0)) {
            bids[listingId][listing.highestBidder] = 0;
            payable(listing.highestBidder).transfer(listing.highestBid);
        }
        
        listing.highestBidder = msg.sender;
        listing.highestBid = msg.value;
        bids[listingId][msg.sender] = msg.value;
        
        listingBids[listingId].push(Bid({
            bidder: msg.sender,
            amount: msg.value,
            timestamp: block.timestamp
        }));
        
        emit BidPlaced(listingId, msg.sender, msg.value);
    }
    
    /**
     * @dev Withdraw bid
     */
    function withdrawBid(uint256 listingId) external nonReentrant {
        uint256 bidAmount = bids[listingId][msg.sender];
        require(bidAmount > 0, "No bid to withdraw");
        require(bids[listingId][msg.sender] > 0, "Bid already withdrawn");
        
        Listing storage listing = listings[listingId];
        require(msg.sender == listing.highestBidder, "Can only withdraw highest bid");
        require(block.timestamp >= listing.auctionEndTime, "Cannot withdraw before auction ends");
        
        bids[listingId][msg.sender] = 0;
        payable(msg.sender).transfer(bidAmount);
        
        emit BidWithdrawn(listingId, msg.sender, bidAmount);
    }
    
    /**
     * @dev End auction and transfer NFT
     */
    function endAuction(uint256 listingId) external nonReentrant {
        Listing storage listing = listings[listingId];
        
        require(listing.isActive, "Listing is not active");
        require(listing.isAuction, "This is not an auction listing");
        require(block.timestamp >= listing.auctionEndTime, "Auction has not ended yet");
        
        listing.isActive = false;
        
        if (listing.highestBidder != address(0)) {
            // Calculate fees
            uint256 platformFeeAmount = (listing.highestBid * platformFee) / 10000;
            uint256 royaltyAmount = (listing.highestBid * listing.royaltyFee) / 10000;
            uint256 sellerAmount = listing.highestBid - platformFeeAmount - royaltyAmount;
            
            // Transfer NFT to winner
            IERC721(listing.nftContract).transferFrom(address(this), listing.highestBidder, listing.tokenId);
            
            // Transfer payments
            payable(feeRecipient).transfer(platformFeeAmount);
            if (royaltyAmount > 0 && listing.royaltyRecipient != address(0)) {
                payable(listing.royaltyRecipient).transfer(royaltyAmount);
            }
            payable(listing.seller).transfer(sellerAmount);
            
            emit AuctionEnded(listingId, listing.highestBidder, listing.seller, listing.highestBid);
        } else {
            // No bids, return NFT to seller
            IERC721(listing.nftContract).transferFrom(address(this), listing.seller, listing.tokenId);
            emit AuctionEnded(listingId, address(0), listing.seller, 0);
        }
    }
    
    /**
     * @dev Cancel listing
     */
    function cancelListing(uint256 listingId) external nonReentrant {
        Listing storage listing = listings[listingId];
        
        require(listing.isActive, "Listing is not active");
        require(msg.sender == listing.seller || owner() == msg.sender, "Not authorized to cancel");
        
        listing.isActive = false;
        
        // Return NFT to seller
        IERC721(listing.nftContract).transferFrom(address(this), listing.seller, listing.tokenId);
        
        emit ListingCancelled(listingId, listing.seller);
    }
    
    /**
     * @dev Get listing information
     */
    function getListing(uint256 listingId) external view returns (Listing memory) {
        return listings[listingId];
    }
    
    /**
     * @dev Get user listings
     */
    function getUserListings(address user) external view returns (uint256[] memory) {
        return userListings[user];
    }
    
    /**
     * @dev Get bid history for listing
     */
    function getListingBids(uint256 listingId) external view returns (Bid[] memory) {
        return listingBids[listingId];
    }
    
    /**
     * @dev Update platform fee
     */
    function setPlatformFee(uint256 _platformFee) external onlyOwner {
        require(_platformFee <= 1000, "Fee cannot exceed 10%");
        platformFee = _platformFee;
    }
    
    /**
     * @dev Update fee recipient
     */
    function setFeeRecipient(address _feeRecipient) external onlyOwner {
        require(_feeRecipient != address(0), "Invalid fee recipient");
        feeRecipient = _feeRecipient;
    }
    
    /**
     * @dev Withdraw contract balance
     */
    function withdraw() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
}