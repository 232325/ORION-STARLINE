import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useMarketplace } from '../contexts/MarketplaceContext';
import { 
  Search, 
  Filter, 
  Grid, 
  List, 
  SlidersHorizontal,
  CheckCircle,
  Clock,
  TrendingUp,
  Coins,
  ArrowUpDown
} from 'lucide-react';

type SortOption = 'price-low' | 'price-high' | 'weight-low' | 'weight-high' | 'newest' | 'oldest';
type FilterType = 'all' | 'gold' | 'silver' | 'platinum' | 'palladium';
type ViewMode = 'grid' | 'list';

export const MarketplacePage: React.FC = () => {
  const { metalNFTs, isLoading } = useMarketplace();
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<SortOption>('newest');
  const [filterBy, setFilterBy] = useState<FilterType>('all');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [showFilters, setShowFilters] = useState(false);

  // Filter and sort NFTs
  const filteredAndSortedNFTs = React.useMemo(() => {
    let filtered = metalNFTs.filter(nft => {
      const matchesSearch = nft.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           nft.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesFilter = filterBy === 'all' || nft.metalType.toLowerCase() === filterBy;
      return matchesSearch && matchesFilter;
    });

    // Sort NFTs
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'price-low':
          return parseFloat(a.currentListing?.price || '999') - parseFloat(b.currentListing?.price || '999');
        case 'price-high':
          return parseFloat(b.currentListing?.price || '0') - parseFloat(a.currentListing?.price || '0');
        case 'weight-low':
          return a.weight - b.weight;
        case 'weight-high':
          return b.weight - a.weight;
        case 'newest':
          return parseInt(b.tokenId) - parseInt(a.tokenId);
        case 'oldest':
          return parseInt(a.tokenId) - parseInt(b.tokenId);
        default:
          return 0;
      }
    });

    return filtered;
  }, [metalNFTs, searchTerm, sortBy, filterBy]);

  const metalTypes = [
    { value: 'all', label: 'Barchasi', color: 'bg-gray-500' },
    { value: 'gold', label: 'Oltin', color: 'bg-yellow-500' },
    { value: 'silver', label: 'Kumush', color: 'bg-gray-400' },
    { value: 'platinum', label: 'Platina', color: 'bg-blue-400' },
    { value: 'palladium', label: 'Palladiy', color: 'bg-purple-400' }
  ];

  const sortOptions = [
    { value: 'newest', label: 'Eng yangi' },
    { value: 'oldest', label: 'Eng kecha' },
    { value: 'price-low', label: 'Narx: pastdan yuqoriga' },
    { value: 'price-high', label: 'Narx: yuqoridan pastga' },
    { value: 'weight-low', label: 'Vazn: kamdan ko\'pga' },
    { value: 'weight-high', label: 'Vazn: ko\'pdan kamga' }
  ];

  const NFTCard: React.FC<{ nft: any }> = ({ nft }) => (
    <Link 
      to={`/metal/${nft.tokenId}`}
      className="bg-slate-800 rounded-xl overflow-hidden border border-slate-700 hover:border-yellow-500/50 transition-all duration-300 group"
    >
      <div className="aspect-square bg-gradient-to-br from-slate-700 to-slate-800 relative overflow-hidden">
        {nft.imageUrl ? (
          <img 
            src={nft.imageUrl} 
            alt={nft.name}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Coins className="w-16 h-16 text-slate-600" />
          </div>
        )}
        
        {/* Status badges */}
        <div className="absolute top-3 left-3 flex gap-2">
          {nft.isVerified && (
            <div className="bg-green-500 rounded-full p-1">
              <CheckCircle className="w-4 h-4 text-white" />
            </div>
          )}
          {nft.currentListing?.isAuction && (
            <div className="bg-blue-500 rounded-full p-1">
              <Clock className="w-4 h-4 text-white" />
            </div>
          )}
        </div>

        {/* Metal type badge */}
        <div className="absolute bottom-3 left-3 bg-black/80 backdrop-blur-sm px-3 py-1 rounded-full">
          <span className="text-yellow-400 font-semibold text-sm">
            {nft.metalType}
          </span>
        </div>

        {/* Price badge */}
        {nft.currentListing && (
          <div className="absolute bottom-3 right-3 bg-yellow-500 text-black px-3 py-1 rounded-full font-semibold">
            {nft.currentListing.price} ETH
          </div>
        )}
      </div>
      
      <div className="p-4">
        <h3 className="text-lg font-semibold text-white mb-2 line-clamp-1">{nft.name}</h3>
        <p className="text-slate-400 text-sm mb-3 line-clamp-2">{nft.description}</p>
        
        <div className="grid grid-cols-2 gap-4 mb-3">
          <div>
            <div className="text-xs text-slate-500">Vazn</div>
            <div className="text-white font-semibold">{nft.weight}g</div>
          </div>
          <div>
            <div className="text-xs text-slate-500">Tozalik</div>
            <div className="text-white font-semibold">{nft.purity}%</div>
          </div>
        </div>

        <div className="text-xs text-slate-500">
          Saqlash: {nft.storageFacility}
        </div>
      </div>
    </Link>
  );

  const NFTListItem: React.FC<{ nft: any }> = ({ nft }) => (
    <Link 
      to={`/metal/${nft.tokenId}`}
      className="bg-slate-800 rounded-xl p-4 border border-slate-700 hover:border-yellow-500/50 transition-colors flex items-center space-x-4 group"
    >
      <div className="w-20 h-20 bg-gradient-to-br from-slate-700 to-slate-800 rounded-lg flex-shrink-0 relative overflow-hidden">
        {nft.imageUrl ? (
          <img 
            src={nft.imageUrl} 
            alt={nft.name}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
          />
        ) : (
          <Coins className="w-8 h-8 text-slate-600 m-auto" />
        )}
        
        {nft.isVerified && (
          <div className="absolute -top-1 -right-1 bg-green-500 rounded-full p-1">
            <CheckCircle className="w-3 h-3 text-white" />
          </div>
        )}
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold text-white truncate">{nft.name}</h3>
          <div className="flex items-center space-x-2">
            <span className="bg-yellow-500 text-black px-2 py-1 rounded text-sm font-semibold">
              {nft.metalType}
            </span>
            {nft.currentListing && (
              <span className="text-yellow-400 font-semibold">
                {nft.currentListing.price} ETH
              </span>
            )}
          </div>
        </div>
        
        <p className="text-slate-400 text-sm mb-2 line-clamp-1">{nft.description}</p>
        
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-4">
            <span className="text-slate-500">Vazn: <span className="text-white">{nft.weight}g</span></span>
            <span className="text-slate-500">Tozalik: <span className="text-white">{nft.purity}%</span></span>
          </div>
          <span className="text-slate-500 truncate">{nft.storageFacility}</span>
        </div>
      </div>
    </Link>
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Metall NFT Bozor</h1>
          <p className="text-slate-400">
            {filteredAndSortedNFTs.length} ta NFT topildi
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-lg ${viewMode === 'grid' ? 'bg-yellow-500 text-black' : 'bg-slate-700 text-slate-300'}`}
          >
            <Grid className="w-4 h-4" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-lg ${viewMode === 'list' ? 'bg-yellow-500 text-black' : 'bg-slate-700 text-slate-300'}`}
          >
            <List className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-slate-800 rounded-xl p-6">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
            <input
              type="text"
              placeholder="NFT nomi yoki tavsifni qidirish..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-yellow-500"
            />
          </div>

          {/* Sort */}
          <div className="flex items-center space-x-2">
            <ArrowUpDown className="w-4 h-4 text-slate-400" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortOption)}
              className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-yellow-500"
            >
              {sortOptions.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>

          {/* Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 bg-slate-700 hover:bg-slate-600 border border-slate-600 rounded-lg px-3 py-2 text-white transition-colors"
          >
            <SlidersHorizontal className="w-4 h-4" />
            <span>Filter</span>
          </button>
        </div>

        {/* Filter Options */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-slate-700">
            <div className="flex flex-wrap gap-2">
              {metalTypes.map(type => (
                <button
                  key={type.value}
                  onClick={() => setFilterBy(type.value as FilterType)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg border transition-colors ${
                    filterBy === type.value 
                      ? 'bg-yellow-500 text-black border-yellow-500' 
                      : 'bg-slate-700 text-slate-300 border-slate-600 hover:border-slate-500'
                  }`}
                >
                  <div className={`w-3 h-3 rounded-full ${type.color}`}></div>
                  <span>{type.label}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Results */}
      {filteredAndSortedNFTs.length === 0 ? (
        <div className="text-center py-16">
          <Coins className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-slate-400 mb-2">
            NFT topilmadi
          </h3>
          <p className="text-slate-500">
            Qidiruv so'rovlaringizni o'zgartirib ko'ring
          </p>
        </div>
      ) : (
        <div className={
          viewMode === 'grid' 
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
            : 'space-y-4'
        }>
          {filteredAndSortedNFTs.map((nft) => 
            viewMode === 'grid' ? <NFTCard key={nft.tokenId} nft={nft} /> : <NFTListItem key={nft.tokenId} nft={nft} />
          )}
        </div>
      )}
    </div>
  );
};