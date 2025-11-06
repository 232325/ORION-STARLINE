"""
OpenSea API Integration for NFT Marketplace
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional
import json
from dataclasses import dataclass
import base64

@dataclass
class OpenSeaAsset:
    id: int
    token_id: str
    name: str
    description: str
    image_url: str
    permalink: str
    collection: Dict
    owner: Dict
    last_sale: Optional[Dict] = None
    top_bid: Optional[Dict] = None
    listing_date: Optional[str] = None
    is_nsfw: bool = False

class OpenSeaAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.opensea.io"
        self.headers = {
            "X-API-KEY": api_key,
            "Accept": "application/json"
        }

    async def get_collections(self, limit: int = 50) -> List[Dict]:
        """Get collections list"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/collections"
            params = {"limit": limit}
            
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"OpenSea API error: {response.status}")

    async def get_assets(
        self, 
        collection: str = None, 
        owner: str = None, 
        token_ids: List[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[OpenSeaAsset]:
        """Get NFT assets"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/assets"
            params = {
                "limit": limit,
                "offset": offset
            }
            
            if collection:
                params["collection"] = collection
            if owner:
                params["owner"] = owner
            if token_ids:
                params["token_ids"] = ",".join(token_ids)
            
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    assets = []
                    for asset_data in data.get("assets", []):
                        asset = OpenSeaAsset(
                            id=asset_data.get("id"),
                            token_id=asset_data.get("token_id"),
                            name=asset_data.get("name"),
                            description=asset_data.get("description"),
                            image_url=asset_data.get("image_url"),
                            permalink=asset_data.get("permalink"),
                            collection=asset_data.get("collection"),
                            owner=asset_data.get("owner"),
                            last_sale=asset_data.get("last_sale"),
                            top_bid=asset_data.get("top_bid"),
                            listing_date=asset_data.get("listing_date"),
                            is_nsfw=asset_data.get("is_nsfw", False)
                        )
                        assets.append(asset)
                    return assets
                else:
                    raise Exception(f"OpenSea API error: {response.status}")

    async def get_asset(self, contract_address: str, token_id: str) -> Optional[Dict]:
        """Get single asset details"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/asset/{contract_address}/{token_id}"
            
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return None
                else:
                    raise Exception(f"OpenSea API error: {response.status}")

    async def get_orders(
        self, 
        asset_contract_address: str = None,
        token_id: str = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict]:
        """Get orders/listings"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/orders"
            params = {
                "limit": limit,
                "offset": offset
            }
            
            if asset_contract_address:
                params["asset_contract_address"] = asset_contract_address
            if token_id:
                params["token_id"] = token_id
            
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("orders", [])
                else:
                    raise Exception(f"OpenSea API error: {response.status}")

    async def create_listing(
        self,
        asset_contract_address: str,
        token_id: str,
        price_eth: str,
        expiration_time: int = None
    ) -> Dict:
        """Create a listing (requires wallet signature)"""
        listing_data = {
            "asset": {
                "token_id": token_id,
                "address": asset_contract_address
            },
            "starting_price": price_eth
        }
        
        if expiration_time:
            listing_data["expiration_time"] = expiration_time
        
        # This would require proper authentication and wallet integration
        # For now, return the structure
        return listing_data

    async def get_events(
        self,
        asset_contract_address: str = None,
        token_id: str = None,
        event_type: str = "sale",
        limit: int = 20
    ) -> List[Dict]:
        """Get events (sales, transfers, etc.)"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/events"
            params = {
                "event_type": event_type,
                "limit": limit
            }
            
            if asset_contract_address:
                params["asset_contract_address"] = asset_contract_address
            if token_id:
                params["token_id"] = token_id
            
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("asset_events", [])
                else:
                    raise Exception(f"OpenSea API error: {response.status}")

    async def get_collection_stats(self, collection_slug: str) -> Dict:
        """Get collection statistics"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/collection/{collection_slug}/stats"
            
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"OpenSea API error: {response.status}")

class MetalNFTOpenSeaIntegrator:
    """Integration layer for Metal NFTs with OpenSea"""
    
    def __init__(self, opensea_api: OpenSeaAPI):
        self.opensea_api = opensea_api
    
    async def get_metal_nfts(self, metal_type: str = None) -> List[OpenSeaAsset]:
        """Get Metal NFTs by type"""
        # Filter collection or search for metal-related tokens
        collections = await self.opensea_api.get_collections(limit=100)
        
        # Find metal-related collections
        metal_collections = []
        for collection in collections:
            name = collection.get("name", "").lower()
            description = collection.get("description", "").lower()
            
            if any(metal in name + description for metal in ["gold", "silver", "platinum", "palladium", "metal", "nft"]):
                metal_collections.append(collection.get("slug"))
        
        all_assets = []
        for collection_slug in metal_collections:
            assets = await self.opensea_api.get_assets(collection=collection_slug, limit=50)
            all_assets.extend(assets)
        
        # Filter by metal type if specified
        if metal_type:
            filtered_assets = []
            for asset in all_assets:
                metadata = asset.collection.get("metadata", {})
                description = metadata.get("description", "").lower()
                if metal_type.lower() in description:
                    filtered_assets.append(asset)
            return filtered_assets
        
        return all_assets
    
    async def get_market_data(self, contract_address: str) -> Dict:
        """Get market data for Metal NFT contract"""
        assets = await self.opensea_api.get_assets(token_ids=["1"], limit=10)
        events = await self.opensea_api.get_events(asset_contract_address=contract_address)
        
        # Calculate statistics
        total_sales = len(events)
        total_volume = sum(float(event.get("payment", {}).get("value", 0)) for event in events)
        avg_price = total_volume / total_sales if total_sales > 0 else 0
        
        return {
            "total_sales": total_sales,
            "total_volume": total_volume,
            "average_price": avg_price,
            "floor_price": min([float(event.get("payment", {}).get("value", 0)) for event in events], default=0)
        }
    
    async def sync_metal_nfts(self, contract_address: str, token_ids: List[str]) -> List[Dict]:
        """Sync Metal NFTs to OpenSea"""
        synced_nfts = []
        
        for token_id in token_ids:
            try:
                asset = await self.opensea_api.get_asset(contract_address, token_id)
                if asset:
                    synced_nfts.append({
                        "token_id": token_id,
                        "contract_address": contract_address,
                        "opensea_url": asset.get("permalink"),
                        "synced_at": asyncio.get_event_loop().time()
                    })
            except Exception as e:
                print(f"Error syncing token {token_id}: {e}")
        
        return synced_nfts

# Example usage
async def main():
    """Example usage of OpenSea integration"""
    api_key = "your_opensea_api_key"
    opensea_api = OpenSeaAPI(api_key)
    integrator = MetalNFTOpenSeaIntegrator(opensea_api)
    
    # Get gold NFTs
    gold_nfts = await integrator.get_metal_nfts("gold")
    print(f"Found {len(gold_nfts)} gold NFTs")
    
    # Get market data
    contract_address = "0x..."  # Your contract address
    market_data = await integrator.get_market_data(contract_address)
    print(f"Market data: {market_data}")

if __name__ == "__main__":
    asyncio.run(main())
