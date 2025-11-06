import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { ethers } from 'ethers';
import { useWeb3 } from './Web3Context';

interface MetalNFT {
  tokenId: string;
  tokenURI: string;
  name: string;
  description: string;
  imageUrl: string;
  metalType: string;
  weight: number;
  purity: number;
  storageFacility: string;
  isVerified: boolean;
  owner: string;
  currentListing?: {
    listingId: string;
    price: string;
    isAuction: boolean;
    auctionEndTime?: string;
  };
}

interface Listing {
  listingId: string;
  nftContract: string;
  tokenId: string;
  seller: string;
  price: string;
  isAuction: boolean;
  auctionEndTime?: string;
  isActive: boolean;
  createdAt: string;
}

interface MarketplaceContextType {
  // NFT data
  metalNFTs: MetalNFT[];
  userNFTs: MetalNFT[];
  listings: Listing[];
  
  // Loading states
  isLoading: boolean;
  
  // Actions
  loadMetalNFTs: () => Promise<void>;
  loadUserNFTs: () => Promise<void>;
  loadListings: () => Promise<void>;
  createFixedPriceListing: (tokenId: string, price: string) => Promise<string>;
  createAuctionListing: (tokenId: string, startingPrice: string, duration: number) => Promise<string>;
  purchaseListing: (listingId: string, price: string) => Promise<void>;
  placeBid: (listingId: string, bidAmount: string) => Promise<void>;
  cancelListing: (listingId: string) => Promise<void>;
  
  // Metadata
  totalVolume: string;
  totalSales: number;
  floorPrice: string;
}

const MarketplaceContext = createContext<MarketplaceContextType | undefined>(undefined);

export const useMarketplace = () => {
  const context = useContext(MarketplaceContext);
  if (context === undefined) {
    throw new Error('useMarketplace must be used within a MarketplaceProvider');
  }
  return context;
};

// Contract ABIs (simplified for demo)
const METAL_NFT_ABI = [
  "function balanceOf(address owner) view returns (uint256)",
  "function tokenOfOwnerByIndex(address owner, uint256 index) view returns (uint256)",
  "function tokenURI(uint256 tokenId) view returns (string)",
  "function ownerOf(uint256 tokenId) view returns (address)",
  "function getMetalData(uint256 tokenId) view returns (tuple(string metalType,uint256 weight,uint256 purity,string storageFacility,bool isVerified))",
  "function approve(address to, uint256 tokenId)",
  "function transferFrom(address from, address to, uint256 tokenId)"
];

const MARKETPLACE_ABI = [
  "function createFixedPriceListing(address nftContract, uint256 tokenId, uint256 price, uint256 royaltyFee, address royaltyRecipient) returns (uint256)",
  "function createAuctionListing(address nftContract, uint256 tokenId, uint256 startingPrice, uint256 auctionDuration, uint256 royaltyFee, address royaltyRecipient) returns (uint256)",
  "function purchaseListing(uint256 listingId) payable",
  "function placeBid(uint256 listingId) payable",
  "function cancelListing(uint256 listingId)",
  "function getListing(uint256 listingId) view returns (tuple(uint256 id,address nftContract,uint256 tokenId,address seller,uint256 price,bool isAuction,uint256 auctionEndTime,address highestBidder,uint256 highestBid,bool isActive,uint256 createdAt,uint256 royaltyFee,address royaltyRecipient))",
  "function getUserListings(address user) view returns (uint256[])",
  "event ListingCreated(uint256 indexed listingId,address indexed seller,address indexed nftContract,uint256 tokenId,uint256 price,bool isAuction)",
  "event ListingPurchased(uint256 indexed listingId,address indexed buyer,address indexed seller,uint256 price)",
  "event BidPlaced(uint256 indexed listingId,address indexed bidder,uint256 amount)"
];

const MARKETPLACE_ADDRESS = "0x1234567890123456789012345678901234567890"; // Replace with actual address
const NFT_CONTRACT_ADDRESS = "0xabcdef1234567890abcdef1234567890abcdef12"; // Replace with actual address

export const MarketplaceProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { provider, signer, account } = useWeb3();
  
  const [metalNFTs, setMetalNFTs] = useState<MetalNFT[]>([]);
  const [userNFTs, setUserNFTs] = useState<MetalNFT[]>([]);
  const [listings, setListings] = useState<Listing[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // Marketplace metrics
  const [totalVolume, setTotalVolume] = useState("0");
  const [totalSales, setTotalSales] = useState(0);
  const [floorPrice, setFloorPrice] = useState("0");

  // Mock data for demonstration
  const mockMetalNFTs: MetalNFT[] = [
    {
      tokenId: "1",
      tokenURI: "ipfs://mock-nft-1",
      name: "1 oz Gold Bar",
      description: "Certified 999.9 pure gold bar from Brink's vault",
      imageUrl: "/images/gold-bar-1oz.jpg",
      metalType: "GOLD",
      weight: 31.1035,
      purity: 99.99,
      storageFacility: "Brink's Global Services",
      isVerified: true,
      owner: "0x1234567890123456789012345678901234567890",
      currentListing: {
        listingId: "1",
        price: "0.5",
        isAuction: false
      }
    },
    {
      tokenId: "2",
      tokenURI: "ipfs://mock-nft-2",
      name: "1 oz Silver Coin",
      description: "American Silver Eagle coin with certification",
      imageUrl: "/images/silver-eagle.jpg",
      metalType: "SILVER",
      weight: 31.1035,
      purity: 99.9,
      storageFacility: "Malca-Amit Global",
      isVerified: true,
      owner: "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
      currentListing: {
        listingId: "2",
        price: "1.2",
        isAuction: true,
        auctionEndTime: "2024-12-31T23:59:59Z"
      }
    },
    {
      tokenId: "3",
      tokenURI: "ipfs://mock-nft-3",
      name: "Platinum Bar 10g",
      description: "High-grade platinum bar from certified refinery",
      imageUrl: "/images/platinum-bar-10g.jpg",
      metalType: "PLATINUM",
      weight: 10.0,
      purity: 99.95,
      storageFacility: "Deloitte Vault",
      isVerified: true,
      owner: "0xfedcbafedcbafedcbafedcbafedcbafedcbafedc",
    }
  ];

  const mockListings: Listing[] = [
    {
      listingId: "1",
      nftContract: NFT_CONTRACT_ADDRESS,
      tokenId: "1",
      seller: "0x1234567890123456789012345678901234567890",
      price: "0.5",
      isAuction: false,
      isActive: true,
      createdAt: "2024-01-01T00:00:00Z"
    },
    {
      listingId: "2",
      nftContract: NFT_CONTRACT_ADDRESS,
      tokenId: "2",
      seller: "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
      price: "1.2",
      isAuction: true,
      auctionEndTime: "2024-12-31T23:59:59Z",
      isActive: true,
      createdAt: "2024-01-01T00:00:00Z"
    }
  ];

  const loadMetalNFTs = useCallback(async () => {
    setIsLoading(true);
    try {
      // Simulate API call with mock data
      setTimeout(() => {
        setMetalNFTs(mockMetalNFTs);
        setIsLoading(false);
      }, 1000);
    } catch (error) {
      console.error('NFT larni yuklashda xato:', error);
      setIsLoading(false);
    }
  }, []);

  const loadUserNFTs = useCallback(async () => {
    if (!account) return;
    
    setIsLoading(true);
    try {
      // Filter NFTs owned by current user
      const userNftData = mockMetalNFTs.filter(nft => 
        nft.owner.toLowerCase() === account.toLowerCase()
      );
      setUserNFTs(userNftData);
    } catch (error) {
      console.error('Foydalanuvchi NFT larini yuklashda xato:', error);
    } finally {
      setIsLoading(false);
    }
  }, [account]);

  const loadListings = useCallback(async () => {
    setIsLoading(true);
    try {
      setTimeout(() => {
        setListings(mockListings);
        
        // Calculate metrics
        const activeListings = mockListings.filter(l => l.isActive);
        const prices = activeListings.map(l => parseFloat(l.price));
        setFloorPrice(prices.length > 0 ? Math.min(...prices).toString() : "0");
        setTotalSales(150); // Mock data
        setTotalVolume("125.5"); // Mock data
        
        setIsLoading(false);
      }, 500);
    } catch (error) {
      console.error('Listing larni yuklashda xato:', error);
      setIsLoading(false);
    }
  }, []);

  const createFixedPriceListing = async (tokenId: string, price: string): Promise<string> => {
    if (!signer) throw new Error('Wallet ulanmagan');
    
    try {
      // Mock implementation
      const listingId = Math.random().toString();
      console.log(`Fixed price listing yaratilmoqda: token ${tokenId}, narx ${price} ETH`);
      
      // Here you would interact with the actual smart contract
      // const marketplace = new ethers.Contract(MARKETPLACE_ADDRESS, MARKETPLACE_ABI, signer);
      // const tx = await marketplace.createFixedPriceListing(NFT_CONTRACT_ADDRESS, tokenId, ethers.parseEther(price), 250, account);
      // await tx.wait();
      
      return listingId;
    } catch (error) {
      console.error('Fixed price listing yaratishda xato:', error);
      throw error;
    }
  };

  const createAuctionListing = async (tokenId: string, startingPrice: string, duration: number): Promise<string> => {
    if (!signer) throw new Error('Wallet ulanmagan');
    
    try {
      const listingId = Math.random().toString();
      console.log(`Auction listing yaratilmoqda: token ${tokenId}, boshlang'ich narx ${startingPrice} ETH, davomiylik ${duration} sekund`);
      
      // Mock implementation
      return listingId;
    } catch (error) {
      console.error('Auction listing yaratishda xato:', error);
      throw error;
    }
  };

  const purchaseListing = async (listingId: string, price: string): Promise<void> => {
    if (!signer) throw new Error('Wallet ulanmagan');
    
    try {
      console.log(`Listing sotib olinmoqda: ${listingId}, narx ${price} ETH`);
      
      // Mock implementation
      // const marketplace = new ethers.Contract(MARKETPLACE_ADDRESS, MARKETPLACE_ABI, signer);
      // const tx = await marketplace.purchaseListing(listingId, { value: ethers.parseEther(price) });
      // await tx.wait();
      
    } catch (error) {
      console.error('Listing sotib olishda xato:', error);
      throw error;
    }
  };

  const placeBid = async (listingId: string, bidAmount: string): Promise<void> => {
    if (!signer) throw new Error('Wallet ulanmagan');
    
    try {
      console.log(`Bid qo'yilmoqda: ${listingId}, miqdor ${bidAmount} ETH`);
      
      // Mock implementation
    } catch (error) {
      console.error('Bid qo\'yishda xato:', error);
      throw error;
    }
  };

  const cancelListing = async (listingId: string): Promise<void> => {
    if (!signer) throw new Error('Wallet ulanmagan');
    
    try {
      console.log(`Listing bekor qilinmoqda: ${listingId}`);
      
      // Mock implementation
    } catch (error) {
      console.error('Listing bekor qilishda xato:', error);
      throw error;
    }
  };

  // Load data when account changes
  useEffect(() => {
    loadMetalNFTs();
    if (account) {
      loadUserNFTs();
    }
  }, [account, loadMetalNFTs, loadUserNFTs]);

  // Load listings on component mount
  useEffect(() => {
    loadListings();
  }, [loadListings]);

  const value: MarketplaceContextType = {
    metalNFTs,
    userNFTs,
    listings,
    isLoading,
    loadMetalNFTs,
    loadUserNFTs,
    loadListings,
    createFixedPriceListing,
    createAuctionListing,
    purchaseListing,
    placeBid,
    cancelListing,
    totalVolume,
    totalSales,
    floorPrice,
  };

  return (
    <MarketplaceContext.Provider value={value}>
      {children}
    </MarketplaceContext.Provider>
  );
};