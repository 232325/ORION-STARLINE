"""
SuperRare API Integration for NFT Marketplace
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional
import json
from dataclasses import dataclass
import time

@dataclass
class SuperRareArtwork:
    id: str
    token_id: str
    name: str
    description: str
    image_url: str
    video_url: Optional[str] = None
    artist: Dict = None
    owner: Dict = None
    current_price: Optional[float] = None
    is_sold: bool = False
    sale_date: Optional[str] = None
    medium: Optional[str] = None

class SuperRareAPI:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://superrare.com"
        self.headers = {
            "User-Agent": "MetalNFT-Integration/1.0",
            "Accept": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    async def get_artworks(
        self, 
        limit: int = 20,
        offset: int = 0,
        status: str = "all"  # all, available, sold
    ) -> List[SuperRareArtwork]:
        """Get artworks from SuperRare"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/v2/artworks"
            params = {
                "limit": limit,
                "offset": offset,
                "status": status
            }
            
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    artworks = []
                    
                    for art_data in data.get("artworks", []):
                        media = art_data.get("media", {})
                        artwork = SuperRareArtwork(
                            id=art_data.get("id"),
                            token_id=art_data.get("tokenId"),
                            name=art_data.get("name"),
                            description=art_data.get("description"),
                            image_url=media.get("imageUrl"),
                            video_url=media.get("videoUrl"),
                            artist=art_data.get("artist"),
                            owner=art_data.get("owner"),
                            medium=art_data.get("medium")
                        )
                        
                        # Check if sold
                        if art_data.get("isSold"):
                            artwork.is_sold = True
                            sale_data = art_data.get("sale", {})
                            artwork.sale_date = sale_data.get("date")
                            price_eth = sale_data.get("price")
                            if price_eth:
                                artwork.current_price = float(price_eth)
                        
                        artworks.append(artwork)
                    
                    return artworks
                else:
                    raise Exception(f"SuperRare API error: {response.status}")

    async def get_artwork(self, artwork_id: str) -> Optional[SuperRareArtwork]:
        """Get single artwork details"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/v2/artworks/{artwork_id}"
            
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    art_data = await response.json()
                    media = art_data.get("media", {})
                    
                    artwork = SuperRareArtwork(
                        id=art_data.get("id"),
                        token_id=art_data.get("tokenId"),
                        name=art_data.get("name"),
                        description=art_data.get("description"),
                        image_url=media.get("imageUrl"),
                        video_url=media.get("videoUrl"),
                        artist=art_data.get("artist"),
                        owner=art_data.get("owner"),
                        medium=art_data.get("medium")
                    )
                    
                    if art_data.get("isSold"):
                        artwork.is_sold = True
                        sale_data = art_data.get("sale", {})
                        artwork.sale_date = sale_data.get("date")
                        price_eth = sale_data.get("price")
                        if price_eth:
                            artwork.current_price = float(price_eth)
                    
                    return artwork
                elif response.status == 404:
                    return None
                else:
                    raise Exception(f"SuperRare API error: {response.status}")

    async def search_artworks(self, query: str, limit: int = 20) -> List[SuperRareArtwork]:
        """Search artworks"""
        # SuperRare doesn't have a direct search API, so we'll filter available artworks
        all_artworks = await self.get_artworks(limit=100, status="all")
        
        # Filter by query (case-insensitive search in name and description)
        filtered_artworks = []
        query_lower = query.lower()
        
        for artwork in all_artworks:
            if (query_lower in artwork.name.lower() or 
                query_lower in artwork.description.lower() or
                (artwork.medium and query_lower in artwork.medium.lower())):
                filtered_artworks.append(artwork)
            
            if len(filtered_artworks) >= limit:
                break
        
        return filtered_artworks[:limit]

    async def get_artists(self, limit: int = 20) -> List[Dict]:
        """Get artists"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/v2/artists"
            params = {"limit": limit}
            
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("artists", [])
                else:
                    raise Exception(f"SuperRare API error: {response.status}")

    async def get_artist_artworks(self, artist_id: str, limit: int = 20) -> List[SuperRareArtwork]:
        """Get artworks by artist"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/v2/artists/{artist_id}/artworks"
            params = {"limit": limit}
            
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    artworks = []
                    
                    for art_data in data.get("artworks", []):
                        media = art_data.get("media", {})
                        artwork = SuperRareArtwork(
                            id=art_data.get("id"),
                            token_id=art_data.get("tokenId"),
                            name=art_data.get("name"),
                            description=art_data.get("description"),
                            image_url=media.get("imageUrl"),
                            video_url=media.get("videoUrl"),
                            artist=art_data.get("artist"),
                            owner=art_data.get("owner"),
                            medium=art_data.get("medium")
                        )
                        artworks.append(artwork)
                    
                    return artworks
                else:
                    raise Exception(f"SuperRare API error: {response.status}")

class MetalNFTSuperRareIntegrator:
    """Integration layer for Metal NFTs with SuperRare"""
    
    def __init__(self, superrare_api: SuperRareAPI):
        self.superrare_api = superrare_api
    
    async def get_metal_artworks(self, metal_type: str = None) -> List[SuperRareArtwork]:
        """Get Metal-themed artworks from SuperRare"""
        search_terms = ["metal", "gold", "silver", "platinum", "palladium", "bullion"]
        
        if metal_type:
            search_terms = [metal_type.lower()]
        
        all_artworks = []
        
        for term in search_terms:
            try:
                artworks = await self.superrare_api.search_artworks(term, limit=20)
                all_artworks.extend(artworks)
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"Error searching for {term}: {e}")
        
        # Remove duplicates based on ID
        unique_artworks = {}
        for artwork in all_artworks:
            unique_artworks[artwork.id] = artwork
        
        return list(unique_artworks.values())
    
    async def get_metal_nft_statistics(self) -> Dict:
        """Get statistics for Metal NFTs on SuperRare"""
        metal_artworks = await self.get_metal_artworks()
        
        total_artworks = len(metal_artworks)
        sold_artworks = sum(1 for art in metal_artworks if art.is_sold)
        available_artworks = total_artworks - sold_artworks
        
        sold_prices = [art.current_price for art in metal_artworks if art.is_sold and art.current_price]
        avg_sale_price = sum(sold_prices) / len(sold_prices) if sold_prices else 0
        highest_price = max(sold_prices) if sold_prices else 0
        
        # Medium analysis
        mediums = {}
        for art in metal_artworks:
            medium = art.medium or "Unknown"
            if medium not in mediums:
                mediums[medium] = 0
            mediums[medium] += 1
        
        return {
            "total_metal_artworks": total_artworks,
            "sold_artworks": sold_artworks,
            "available_artworks": available_artworks,
            "sold_percentage": (sold_artworks / total_artworks * 100) if total_artworks > 0 else 0,
            "average_sale_price": avg_sale_price,
            "highest_sale_price": highest_price,
            "medium_distribution": mediums,
            "market_maturity": "mature" if sold_artworks > 20 else "emerging"
        }
    
    async def track_metal_creator_activity(self) -> List[Dict]:
        """Track metal-focused creators on SuperRare"""
        metal_artworks = await self.get_metal_artworks()
        
        creators = {}
        for artwork in metal_artworks:
            artist_id = artwork.artist.get("id") if artwork.artist else None
            if not artist_id:
                continue
                
            if artist_id not in creators:
                creators[artist_id] = {
                    "id": artist_id,
                    "name": artwork.artist.get("name", "Unknown"),
                    "artwork_count": 0,
                    "sold_count": 0,
                    "total_sales_value": 0,
                    "latest_artwork": artwork.name if artwork else None
                }
            
            creators[artist_id]["artwork_count"] += 1
            if artwork.is_sold:
                creators[artist_id]["sold_count"] += 1
                if artwork.current_price:
                    creators[artist_id]["total_sales_value"] += artwork.current_price
        
        # Calculate success rate and sort
        for creator in creators.values():
            creator["success_rate"] = (creator["sold_count"] / creator["artwork_count"] * 100) if creator["artwork_count"] > 0 else 0
        
        sorted_creators = sorted(
            creators.values(),
            key=lambda x: x["total_sales_value"],
            reverse=True
        )
        
        return sorted_creators

# Rarible API Integration
class RaribleAPI:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://api.rarible.com"
        self.headers = {
            "Accept": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    async def get_items(
        self, 
        blockchain: str = "ETHEREUM",
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict]:
        """Get items from Rarible"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/v0.1/items"
            params = {
                "blockchain": blockchain,
                "size": limit,
                "from": offset
            }
            
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("items", [])
                else:
                    raise Exception(f"Rarible API error: {response.status}")

    async def get_item(self, item_id: str) -> Optional[Dict]:
        """Get single item details"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/v0.1/items/{item_id}"
            
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return None
                else:
                    raise Exception(f"Rarible API error: {response.status}")

class MetalNFTRaribleIntegrator:
    """Integration layer for Metal NFTs with Rarible"""
    
    def __init__(self, rarible_api: RaribleAPI):
        self.rarible_api = rarible_api
    
    async def get_metal_items(self, metal_type: str = None) -> List[Dict]:
        """Get Metal-themed items from Rarible"""
        search_terms = ["metal", "gold", "silver", "platinum", "palladium", "bullion"]
        
        if metal_type:
            search_terms = [metal_type.lower()]
        
        all_items = []
        
        for term in search_terms:
            try:
                items = await self.rarible_api.get_items(limit=50)
                # Filter items by term (this is a simplified version)
                filtered_items = [
                    item for item in items 
                    if term in str(item.get("meta", {})).lower()
                ]
                all_items.extend(filtered_items)
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"Error searching Rarible for {term}: {e}")
        
        return all_items

# Example usage
async def main():
    """Example usage of SuperRare and Rarible integrations"""
    
    # SuperRare integration
    superrare_api = SuperRareAPI()
    superrare_integrator = MetalNFTSuperRareIntegrator(superrare_api)
    
    print("Fetching SuperRare metal artworks...")
    metal_artworks = await superrare_integrator.get_metal_artworks("gold")
    print(f"Found {len(metal_artworks)} gold artworks on SuperRare")
    
    # Get statistics
    stats = await superrare_integrator.get_metal_nft_statistics()
    print(f"SuperRare Metal NFT Statistics: {stats}")
    
    # Rarible integration
    rarible_api = RaribleAPI()
    rarible_integrator = MetalNFTRaribleIntegrator(rarible_api)
    
    print("Fetching Rarible metal items...")
    metal_items = await rarible_integrator.get_metal_items("silver")
    print(f"Found {len(metal_items)} silver items on Rarible")

if __name__ == "__main__":
    asyncio.run(main())
