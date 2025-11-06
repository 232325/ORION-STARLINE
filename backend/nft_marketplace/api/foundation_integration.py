"""
Foundation API Integration for NFT Marketplace
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional
import json
from dataclasses import dataclass

@dataclass
class FoundationAsset:
    id: str
    token_id: str
    title: str
    description: str
    image_url: str
    creator: Dict
    owner: Dict
    current_price: Optional[float] = None
    is_auction: bool = False
    auction_end_time: Optional[str] = None

class FoundationAPI:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://api.foundation.app"
        self.headers = {
            "Accept": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    async def get_artworks(
        self, 
        limit: int = 20,
        offset: int = 0,
        creator: str = None,
        owner: str = None
    ) -> List[FoundationAsset]:
        """Get artworks from Foundation"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/graphql"
            
            query = """
            query GetArtworks($limit: Int!, $offset: Int!, $creator: String, $owner: String) {
                artworks(
                    first: $limit,
                    skip: $offset,
                    where: {
                        creator: $creator,
                        owner: $owner
                    }
                ) {
                    id
                    tokenId
                    title
                    description
                    media {
                        image {
                            url
                        }
                    }
                    creator {
                        id
                        username
                        profileImage
                    }
                    owner {
                        id
                        username
                        profileImage
                    }
                    ... on Auction {
                        reservePriceInETH
                        isPrimarySale
                        endsAt
                    }
                }
            }
            """
            
            variables = {
                "limit": limit,
                "offset": offset
            }
            
            if creator:
                variables["creator"] = creator
            if owner:
                variables["owner"] = owner
            
            payload = {
                "query": query,
                "variables": variables
            }
            
            async with session.post(url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    artworks = []
                    
                    for art_data in data.get("data", {}).get("artworks", []):
                        artwork = FoundationAsset(
                            id=art_data.get("id"),
                            token_id=art_data.get("tokenId"),
                            title=art_data.get("title"),
                            description=art_data.get("description"),
                            image_url=art_data.get("media", {}).get("image", {}).get("url"),
                            creator=art_data.get("creator"),
                            owner=art_data.get("owner")
                        )
                        
                        # Check if it's an auction
                        if "reservePriceInETH" in art_data:
                            artwork.is_auction = True
                            artwork.current_price = float(art_data.get("reservePriceInETH", 0))
                            artwork.auction_end_time = art_data.get("endsAt")
                        
                        artworks.append(artwork)
                    
                    return artworks
                else:
                    raise Exception(f"Foundation API error: {response.status}")

    async def get_artwork(self, artwork_id: str) -> Optional[FoundationAsset]:
        """Get single artwork details"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/graphql"
            
            query = """
            query GetArtwork($id: ID!) {
                artwork(id: $id) {
                    id
                    tokenId
                    title
                    description
                    media {
                        image {
                            url
                        }
                    }
                    creator {
                        id
                        username
                        profileImage
                    }
                    owner {
                        id
                        username
                        profileImage
                    }
                    ... on Auction {
                        reservePriceInETH
                        isPrimarySale
                        endsAt
                    }
                    ... on FixedPriceSale {
                        priceInETH
                    }
                }
            }
            """
            
            variables = {"id": artwork_id}
            
            payload = {
                "query": query,
                "variables": variables
            }
            
            async with session.post(url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    art_data = data.get("data", {}).get("artwork")
                    
                    if not art_data:
                        return None
                    
                    artwork = FoundationAsset(
                        id=art_data.get("id"),
                        token_id=art_data.get("tokenId"),
                        title=art_data.get("title"),
                        description=art_data.get("description"),
                        image_url=art_data.get("media", {}).get("image", {}).get("url"),
                        creator=art_data.get("creator"),
                        owner=art_data.get("owner")
                    )
                    
                    # Check if it's an auction or fixed price
                    if "reservePriceInETH" in art_data:
                        artwork.is_auction = True
                        artwork.current_price = float(art_data.get("reservePriceInETH", 0))
                        artwork.auction_end_time = art_data.get("endsAt")
                    elif "priceInETH" in art_data:
                        artwork.current_price = float(art_data.get("priceInETH", 0))
                    
                    return artwork
                else:
                    raise Exception(f"Foundation API error: {response.status}")

    async def get_collections(self, creator: str = None) -> List[Dict]:
        """Get collections"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/graphql"
            
            query = """
            query GetCollections($creator: String) {
                collections(
                    where: {
                        creator: $creator
                    }
                ) {
                    id
                    name
                    description
                    coverImage {
                        url
                    }
                    artworksCount
                    totalVolume
                }
            }
            """
            
            variables = {}
            if creator:
                variables["creator"] = creator
            
            payload = {
                "query": query,
                "variables": variables
            }
            
            async with session.post(url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", {}).get("collections", [])
                else:
                    raise Exception(f"Foundation API error: {response.status}")

    async def search_artworks(self, query_text: str, limit: int = 20) -> List[FoundationAsset]:
        """Search artworks"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/graphql"
            
            query = """
            query SearchArtworks($query: String!, $limit: Int!) {
                searchArtworks(
                    query: $query,
                    first: $limit
                ) {
                    id
                    tokenId
                    title
                    description
                    media {
                        image {
                            url
                        }
                    }
                    creator {
                        id
                        username
                        profileImage
                    }
                    owner {
                        id
                        username
                        profileImage
                    }
                }
            }
            """
            
            variables = {
                "query": query_text,
                "limit": limit
            }
            
            payload = {
                "query": query,
                "variables": variables
            }
            
            async with session.post(url, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    artworks = []
                    
                    for art_data in data.get("data", {}).get("searchArtworks", []):
                        artwork = FoundationAsset(
                            id=art_data.get("id"),
                            token_id=art_data.get("tokenId"),
                            title=art_data.get("title"),
                            description=art_data.get("description"),
                            image_url=art_data.get("media", {}).get("image", {}).get("url"),
                            creator=art_data.get("creator"),
                            owner=art_data.get("owner")
                        )
                        artworks.append(artwork)
                    
                    return artworks
                else:
                    raise Exception(f"Foundation API error: {response.status}")

class MetalNFTFoundationIntegrator:
    """Integration layer for Metal NFTs with Foundation"""
    
    def __init__(self, foundation_api: FoundationAPI):
        self.foundation_api = foundation_api
    
    async def get_metal_artworks(self, metal_type: str = None) -> List[FoundationAsset]:
        """Get Metal-themed artworks"""
        search_terms = [
            "gold NFT", "silver NFT", "platinum NFT", "palladium NFT",
            "metal artwork", "precious metals", "bullion NFT"
        ]
        
        if metal_type:
            search_terms = [f"{metal_type} NFT", f"{metal_type} artwork"]
        
        all_artworks = []
        
        for term in search_terms:
            try:
                artworks = await self.foundation_api.search_artworks(term, limit=10)
                all_artworks.extend(artworks)
            except Exception as e:
                print(f"Error searching for {term}: {e}")
        
        # Remove duplicates based on ID
        unique_artworks = {}
        for artwork in all_artworks:
            unique_artworks[artwork.id] = artwork
        
        return list(unique_artworks.values())
    
    async def analyze_metal_nft_market(self) -> Dict:
        """Analyze metal NFT market on Foundation"""
        metal_artworks = await self.get_metal_artworks()
        
        total_supply = len(metal_artworks)
        auction_count = sum(1 for art in metal_artworks if art.is_auction)
        fixed_price_count = total_supply - auction_count
        
        prices = [art.current_price for art in metal_artworks if art.current_price]
        avg_price = sum(prices) / len(prices) if prices else 0
        floor_price = min(prices) if prices else 0
        
        return {
            "total_metal_nfts": total_supply,
            "auction_count": auction_count,
            "fixed_price_count": fixed_price_count,
            "average_price": avg_price,
            "floor_price": floor_price,
            "market_activity": "active" if total_supply > 10 else "emerging"
        }
    
    async def get_metal_creators(self) -> List[Dict]:
        """Get creators specializing in metal NFTs"""
        metal_artworks = await self.get_metal_artworks()
        
        creators = {}
        for artwork in metal_artworks:
            creator_id = artwork.creator.get("id")
            if creator_id not in creators:
                creators[creator_id] = {
                    "id": creator_id,
                    "username": artwork.creator.get("username"),
                    "profile_image": artwork.creator.get("profileImage"),
                    "artwork_count": 0,
                    "total_value": 0
                }
            
            creators[creator_id]["artwork_count"] += 1
            if artwork.current_price:
                creators[creator_id]["total_value"] += artwork.current_price
        
        # Sort by total value
        sorted_creators = sorted(
            creators.values(), 
            key=lambda x: x["total_value"], 
            reverse=True
        )
        
        return sorted_creators

# Example usage
async def main():
    """Example usage of Foundation integration"""
    foundation_api = FoundationAPI()
    integrator = MetalNFTFoundationIntegrator(foundation_api)
    
    # Get metal artworks
    metal_artworks = await integrator.get_metal_artworks("gold")
    print(f"Found {len(metal_artworks)} gold artworks")
    
    # Analyze market
    market_analysis = await integrator.analyze_metal_nft_market()
    print(f"Market analysis: {market_analysis}")
    
    # Get top creators
    top_creators = await integrator.get_metal_creators()
    print(f"Top creators: {top_creators[:5]}")

if __name__ == "__main__":
    asyncio.run(main())
