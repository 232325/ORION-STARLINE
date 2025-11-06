import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMarketplace } from '../contexts/MarketplaceContext';
import { useWeb3 } from '../contexts/Web3Context';
import { 
  Upload, 
  Coins, 
  Clock, 
  DollarSign, 
  Info,
  CheckCircle,
  AlertCircle,
  ArrowLeft,
  Calendar,
  Tag
} from 'lucide-react';

export const CreateListingPage: React.FC = () => {
  const navigate = useNavigate();
  const { userNFTs, createFixedPriceListing, createAuctionListing } = useMarketplace();
  const { isConnected } = useWeb3();
  
  const [selectedNFT, setSelectedNFT] = useState<any>(null);
  const [listingType, setListingType] = useState<'fixed' | 'auction'>('fixed');
  const [price, setPrice] = useState('');
  const [duration, setDuration] = useState(7); // days
  const [royaltyFee, setRoyaltyFee] = useState(2.5);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Filter NFTs that are not already listed
  const availableNFTs = userNFTs.filter(nft => !nft.currentListing);

  const listingTypes = [
    {
      id: 'fixed',
      title: 'Qat\'iy narx',
      description: 'Bir martalik narxda sotish',
      icon: DollarSign,
      recommended: 'Tez sotish uchun'
    },
    {
      id: 'auction',
      title: 'Auction',
      description: 'Konkursli savdo',
      icon: Clock,
      recommended: 'Maksimal narx uchun'
    }
  ];

  const durationOptions = [
    { value: 1, label: '1 kun' },
    { value: 3, label: '3 kun' },
    { value: 7, label: '1 hafta' },
    { value: 14, label: '2 hafta' },
    { value: 30, label: '1 oy' }
  ];

  const handleCreateListing = async () => {
    if (!selectedNFT || !price) {
      setError('Barcha maydonlarni to\'ldiring');
      return;
    }

    if (!isConnected) {
      setError('Wallet ulanish kerak');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      let listingId;
      
      if (listingType === 'fixed') {
        listingId = await createFixedPriceListing(selectedNFT.tokenId, price);
        console.log('Fixed price listing yaratildi:', listingId);
      } else {
        const auctionDuration = duration * 24 * 60 * 60; // Convert to seconds
        listingId = await createAuctionListing(selectedNFT.tokenId, price, auctionDuration);
        console.log('Auction listing yaratildi:', listingId);
      }

      // Success - redirect to marketplace or listing details
      navigate('/marketplace');
    } catch (error) {
      console.error('Listing yaratishda xato:', error);
      setError('Listing yaratishda xato yuz berdi. Qaytadan urinib ko\'ring.');
    } finally {
      setIsLoading(false);
    }
  };

  const formatETH = (value: string) => {
    const num = parseFloat(value);
    return isNaN(num) ? 0 : num;
  };

  const calculatePlatformFee = () => {
    const ethValue = formatETH(price);
    return (ethValue * 0.025).toFixed(4); // 2.5% platform fee
  };

  const calculateRoyalty = () => {
    const ethValue = formatETH(price);
    return (ethValue * (royaltyFee / 100)).toFixed(4);
  };

  if (!isConnected) {
    return (
      <div className="text-center py-16">
        <Coins className="w-16 h-16 text-slate-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-white mb-4">
          Wallet ulanish kerak
        </h2>
        <p className="text-slate-400 mb-8">
          Listing yaratish uchun avval walletingizni ulang.
        </p>
        <button className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-8 py-3 rounded-xl font-semibold">
          Wallet ulash
        </button>
      </div>
    );
  }

  if (availableNFTs.length === 0) {
    return (
      <div className="text-center py-16">
        <Coins className="w-16 h-16 text-slate-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-white mb-4">
          Hech qanday NFT yo'q
        </h2>
        <p className="text-slate-400 mb-8">
          Listing yaratish uchun avval metall NFT sotib oling yoki yarating.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button 
            onClick={() => navigate('/marketplace')}
            className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-8 py-3 rounded-xl font-semibold"
          >
            BoZorda sotib olish
          </button>
          <button 
            onClick={() => navigate('/create-nft')}
            className="border border-slate-600 text-slate-300 px-8 py-3 rounded-xl font-semibold hover:border-slate-500"
          >
            NFT yaratish
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4 mb-8">
        <button 
          onClick={() => navigate(-1)}
          className="p-2 text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-3xl font-bold text-white">Listing Yaratish</h1>
          <p className="text-slate-400">O'z Metall NFT ingizni sotish</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main Form */}
        <div className="lg:col-span-2 space-y-6">
          {/* NFT Selection */}
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <h2 className="text-xl font-semibold text-white mb-4">NFT tanlang</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {availableNFTs.map((nft) => (
                <div
                  key={nft.tokenId}
                  onClick={() => setSelectedNFT(nft)}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                    selectedNFT?.tokenId === nft.tokenId 
                      ? 'border-yellow-500 bg-yellow-500/10' 
                      : 'border-slate-600 hover:border-slate-500'
                  }`}
                >
                  <div className="flex items-center space-x-4">
                    <div className="w-16 h-16 bg-gradient-to-br from-slate-600 to-slate-700 rounded-lg flex-shrink-0">
                      {nft.imageUrl ? (
                        <img 
                          src={nft.imageUrl} 
                          alt={nft.name}
                          className="w-full h-full object-cover rounded-lg"
                        />
                      ) : (
                        <Coins className="w-8 h-8 text-slate-500 m-auto" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-white font-semibold truncate">{nft.name}</h3>
                      <p className="text-slate-400 text-sm truncate">{nft.description}</p>
                      <div className="flex items-center space-x-4 mt-2 text-xs text-slate-500">
                        <span>{nft.weight}g</span>
                        <span>{nft.purity}%</span>
                        <span>{nft.metalType}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Listing Type */}
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <h2 className="text-xl font-semibold text-white mb-4">Listing turi</h2>
            <div className="grid md:grid-cols-2 gap-4">
              {listingTypes.map((type) => (
                <div
                  key={type.id}
                  onClick={() => setListingType(type.id as 'fixed' | 'auction')}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                    listingType === type.id 
                      ? 'border-yellow-500 bg-yellow-500/10' 
                      : 'border-slate-600 hover:border-slate-500'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`p-2 rounded-lg ${
                      listingType === type.id ? 'bg-yellow-500' : 'bg-slate-700'
                    }`}>
                      <type.icon className={`w-5 h-5 ${
                        listingType === type.id ? 'text-black' : 'text-white'
                      }`} />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-white font-semibold">{type.title}</h3>
                      <p className="text-slate-400 text-sm">{type.description}</p>
                      <p className="text-yellow-400 text-xs mt-1">{type.recommended}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Price & Details */}
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <h2 className="text-xl font-semibold text-white mb-4">
              {listingType === 'fixed' ? 'Narx' : 'Boshlang\'ich narx'}
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-slate-400 text-sm mb-2">Narx (ETH)</label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                  <input
                    type="number"
                    step="0.001"
                    min="0"
                    value={price}
                    onChange={(e) => setPrice(e.target.value)}
                    placeholder="0.00"
                    className="w-full pl-10 pr-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-yellow-500"
                  />
                </div>
              </div>

              {listingType === 'auction' && (
                <div>
                  <label className="block text-slate-400 text-sm mb-2">Davomiylik</label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                    <select
                      value={duration}
                      onChange={(e) => setDuration(parseInt(e.target.value))}
                      className="w-full pl-10 pr-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-yellow-500 appearance-none"
                    >
                      {durationOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              )}

              <div>
                <label className="block text-slate-400 text-sm mb-2">
                  Royalty foizi (%)
                </label>
                <div className="relative">
                  <Tag className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="10"
                    value={royaltyFee}
                    onChange={(e) => setRoyaltyFee(parseFloat(e.target.value))}
                    placeholder="2.5"
                    className="w-full pl-10 pr-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-yellow-500"
                  />
                </div>
                <p className="text-slate-500 text-xs mt-1">
                  Har bir sotuvda oladigan foiz miqdoringiz
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Preview & Summary */}
        <div className="space-y-6">
          {/* Preview */}
          {selectedNFT && (
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
              <h3 className="text-white font-semibold mb-4">Preview</h3>
              <div className="space-y-4">
                <div className="aspect-square bg-gradient-to-br from-slate-600 to-slate-700 rounded-lg overflow-hidden">
                  {selectedNFT.imageUrl ? (
                    <img 
                      src={selectedNFT.imageUrl} 
                      alt={selectedNFT.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <Coins className="w-16 h-16 text-slate-500" />
                    </div>
                  )}
                </div>
                <div>
                  <h4 className="text-white font-semibold">{selectedNFT.name}</h4>
                  <p className="text-slate-400 text-sm">{selectedNFT.description}</p>
                </div>
              </div>
            </div>
          )}

          {/* Summary */}
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <h3 className="text-white font-semibold mb-4">Xulosa</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-400">Listing turi:</span>
                <span className="text-white">
                  {listingType === 'fixed' ? 'Qat\'iy narx' : 'Auction'}
                </span>
              </div>
              
              {price && (
                <>
                  <div className="flex justify-between">
                    <span className="text-slate-400">{listingType === 'fixed' ? 'Narx' : 'Boshlang\'ich narx'}:</span>
                    <span className="text-white">{price} ETH</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-slate-400">Platforma xaraji:</span>
                    <span className="text-white">{calculatePlatformFee()} ETH</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-slate-400">Royalty:</span>
                    <span className="text-white">{calculateRoyalty()} ETH</span>
                  </div>
                  
                  <div className="border-t border-slate-600 pt-3 flex justify-between">
                    <span className="text-white font-semibold">Siz oladigan:</span>
                    <span className="text-green-400 font-semibold">
                      {(formatETH(price) - formatETH(calculatePlatformFee()) - formatETH(calculateRoyalty())).toFixed(4)} ETH
                    </span>
                  </div>
                </>
              )}
              
              {listingType === 'auction' && (
                <div className="flex justify-between">
                  <span className="text-slate-400">Davomiylik:</span>
                  <span className="text-white">{duration} kun</span>
                </div>
              )}
            </div>

            <button
              onClick={handleCreateListing}
              disabled={!selectedNFT || !price || isLoading}
              className={`w-full mt-6 py-3 rounded-lg font-semibold transition-colors ${
                selectedNFT && price && !isLoading
                  ? 'bg-gradient-to-r from-yellow-500 to-orange-500 text-white hover:from-yellow-600 hover:to-orange-600'
                  : 'bg-slate-700 text-slate-400 cursor-not-allowed'
              }`}
            >
              {isLoading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Yaratilmoqda...</span>
                </div>
              ) : (
                `${listingType === 'fixed' ? 'Fixed Price Listing' : 'Auction'} Yaratish`
              )}
            </button>
          </div>

          {/* Info */}
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <div className="flex items-start space-x-3">
              <Info className="w-5 h-5 text-blue-400 mt-0.5" />
              <div className="text-sm">
                <h4 className="text-white font-semibold mb-2">Muhim ma'lumotlar</h4>
                <ul className="text-slate-400 space-y-1">
                  <li>• NFT transfer qilinmagunsa listing faol bo'lmaydi</li>
                  <li>• Auction vaqt tugagandan so'ng avtomatik yakunlanadi</li>
                  <li>• Royalty har bir sotuvda to'lanadi</li>
                  <li>• Listing istalgan vaqtda bekor qilinishi mumkin</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-500/10 border border-red-500 rounded-lg p-4 flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 text-red-400" />
          <span className="text-red-400">{error}</span>
        </div>
      )}
    </div>
  );
};