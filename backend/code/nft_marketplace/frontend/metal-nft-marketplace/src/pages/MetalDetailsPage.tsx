import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useMarketplace } from '../contexts/MarketplaceContext';
import { 
  ArrowLeft,
  Heart,
  Share2,
  ExternalLink,
  Award,
  Building,
  Calendar,
  Weight,
  Gauge,
  MapPin,
  Shield,
  TrendingUp,
  ShoppingCart,
  Gavel,
  Coins,
  CheckCircle,
  AlertCircle,
  DollarSign
} from 'lucide-react';

export const MetalDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { purchaseListing, placeBid } = useMarketplace();
  const [activeTab, setActiveTab] = useState<'overview' | 'history' | 'analytics'>('overview');
  const [bidAmount, setBidAmount] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Mock NFT details
  const nftDetails = {
    tokenId: id,
    name: "1 oz Gold Bar",
    description: "Certified 999.9 pure gold bar from Brink's vault. This premium gold bar represents exceptional quality and comes with full certification from accredited laboratories.",
    imageUrl: "/images/gold-bar-1oz.jpg",
    
    metalType: "GOLD",
    weight: 31.1035,
    purity: 99.99,
    storageFacility: "Brink's Global Services",
    isVerified: true,
    
    owner: "0x1234567890123456789012345678901234567890",
    creator: "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
    
    currentListing: {
      listingId: "1",
      price: "1.45",
      isAuction: true,
      auctionEndTime: "2024-12-31T23:59:59Z",
      highestBid: "1.45",
      highestBidder: "0xabcd...ef12",
      bidCount: 5
    },
    
    certifications: {
      assay: "ASSAY-MTL-2024-001",
      storage: "STOR-BR-001-2024",
      audit: "AUDIT-DEL-2024-001"
    },
    
    metadata: {
      mintDate: "2024-01-15T10:30:00Z",
      lastSale: "2024-01-10T15:20:00Z",
      royaltyFee: 2.5,
      totalVolume: "5.2"
    },

    transactionHistory: [
      {
        type: "mint",
        from: "0x0",
        to: "0x1234...5678",
        price: "0",
        date: "2024-01-15",
        txHash: "0x1234567890abcdef"
      },
      {
        type: "sale",
        from: "0x1234...5678",
        to: "0xabcd...ef12",
        price: "1.20",
        date: "2024-01-10",
        txHash: "0xabcdef1234567890"
      }
    ]
  };

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const handlePurchase = async () => {
    if (!nftDetails.currentListing || !nftDetails.currentListing.isAuction) {
      setIsLoading(true);
      try {
        await purchaseListing(nftDetails.currentListing!.listingId, nftDetails.currentListing!.price);
        console.log('NFT sotib olindi');
      } catch (error) {
        console.error('Sotib olishda xato:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleBid = async () => {
    if (!bidAmount || !nftDetails.currentListing) return;
    
    setIsLoading(true);
    try {
      await placeBid(nftDetails.currentListing.listingId, bidAmount);
      console.log('Bid qo\'yildi:', bidAmount);
    } catch (error) {
      console.error('Bid qo\'yishda xato:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Umumiy ma\'lumot' },
    { id: 'history', label: 'Tarix' },
    { id: 'analytics', label: 'Tahlil' }
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4 mb-8">
        <Link to="/marketplace" className="p-2 text-slate-400 hover:text-white transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-white mb-2">{nftDetails.name}</h1>
          <p className="text-slate-400">Token #{nftDetails.tokenId}</p>
        </div>
        <div className="flex items-center space-x-2">
          <button className="p-2 text-slate-400 hover:text-red-400 transition-colors">
            <Heart className="w-5 h-5" />
          </button>
          <button className="p-2 text-slate-400 hover:text-white transition-colors">
            <Share2 className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* NFT Image & Details */}
          <div className="bg-slate-800 rounded-xl overflow-hidden border border-slate-700">
            <div className="aspect-square bg-gradient-to-br from-slate-700 to-slate-800 relative">
              {nftDetails.imageUrl ? (
                <img 
                  src={nftDetails.imageUrl} 
                  alt={nftDetails.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <Coins className="w-24 h-24 text-slate-600" />
                </div>
              )}
              
              {nftDetails.isVerified && (
                <div className="absolute top-4 right-4 bg-green-500 rounded-full p-2">
                  <CheckCircle className="w-6 h-6 text-white" />
                </div>
              )}
              
              <div className="absolute bottom-4 left-4 bg-black/80 backdrop-blur-sm px-4 py-2 rounded-full">
                <span className="text-yellow-400 font-semibold">
                  {nftDetails.metalType}
                </span>
              </div>
            </div>
            
            <div className="p-6">
              <p className="text-slate-300 mb-6 leading-relaxed">
                {nftDetails.description}
              </p>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <Weight className="w-6 h-6 text-yellow-400 mx-auto mb-2" />
                  <div className="text-slate-400 text-sm">Vazn</div>
                  <div className="text-white font-semibold">{nftDetails.weight}g</div>
                </div>
                <div className="text-center">
                  <Gauge className="w-6 h-6 text-blue-400 mx-auto mb-2" />
                  <div className="text-slate-400 text-sm">Tozalik</div>
                  <div className="text-white font-semibold">{nftDetails.purity}%</div>
                </div>
                <div className="text-center">
                  <Building className="w-6 h-6 text-green-400 mx-auto mb-2" />
                  <div className="text-slate-400 text-sm">Saqlash</div>
                  <div className="text-white font-semibold text-sm">Brink's</div>
                </div>
                <div className="text-center">
                  <Award className="w-6 h-6 text-purple-400 mx-auto mb-2" />
                  <div className="text-slate-400 text-sm">Status</div>
                  <div className="text-green-400 font-semibold">Tasdiqlangan</div>
                </div>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="bg-slate-800 rounded-xl border border-slate-700">
            <div className="flex border-b border-slate-700">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex-1 px-6 py-4 font-medium transition-colors ${
                    activeTab === tab.id 
                      ? 'text-yellow-400 border-b-2 border-yellow-400 bg-slate-700/50' 
                      : 'text-slate-400 hover:text-white hover:bg-slate-700/30'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            <div className="p-6">
              {/* Overview Tab */}
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="bg-slate-700 rounded-lg p-4">
                      <h3 className="text-white font-semibold mb-3 flex items-center space-x-2">
                        <Award className="w-5 h-5 text-yellow-400" />
                        <span>Assay Sertifikat</span>
                      </h3>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-slate-400">Raqam:</span>
                          <span className="text-white">{nftDetails.certifications.assay}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Laboratoriya:</span>
                          <span className="text-white">MTL Inc.</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Sana:</span>
                          <span className="text-white">2024-01-10</span>
                        </div>
                      </div>
                    </div>

                    <div className="bg-slate-700 rounded-lg p-4">
                      <h3 className="text-white font-semibold mb-3 flex items-center space-x-2">
                        <Building className="w-5 h-5 text-blue-400" />
                        <span>Saqlash Sertifikat</span>
                      </h3>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-slate-400">Facility:</span>
                          <span className="text-white">{nftDetails.storageFacility}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Vault:</span>
                          <span className="text-white">BR-001-A</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-400">Sug'urta:</span>
                          <span className="text-green-400">Faol</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-slate-700 rounded-lg p-4">
                    <h3 className="text-white font-semibold mb-3 flex items-center space-x-2">
                      <Shield className="w-5 h-5 text-green-400" />
                      <span>Audit ma'lumotlari</span>
                    </h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Oxirgi audit:</span>
                        <span className="text-white">2024-01-20</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Auditor:</span>
                        <span className="text-white">Deloitte</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Compliance score:</span>
                        <span className="text-green-400">95.5/100</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* History Tab */}
              {activeTab === 'history' && (
                <div className="space-y-4">
                  {nftDetails.transactionHistory.map((tx, index) => (
                    <div key={index} className="bg-slate-700 rounded-lg p-4 border border-slate-600">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-3">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                            tx.type === 'mint' ? 'bg-green-500' : 
                            tx.type === 'sale' ? 'bg-blue-500' : 'bg-purple-500'
                          }`}>
                            {tx.type === 'mint' ? <Award className="w-4 h-4 text-white" /> :
                             tx.type === 'sale' ? <TrendingUp className="w-4 h-4 text-white" /> :
                             <ExternalLink className="w-4 h-4 text-white" />}
                          </div>
                          <div>
                            <div className="text-white font-semibold capitalize">
                              {tx.type === 'mint' ? 'Yaratildi' : 
                               tx.type === 'sale' ? 'Sotildi' : 'Transfer'}
                            </div>
                            <div className="text-slate-400 text-sm">
                              {tx.type === 'sale' ? `${tx.price} ETH` : 'Mint'}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-white">{tx.date}</div>
                          <div className="text-slate-400 text-sm font-mono">
                            {formatAddress(tx.txHash)}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Analytics Tab */}
              {activeTab === 'analytics' && (
                <div className="space-y-6">
                  <div className="grid md:grid-cols-3 gap-4">
                    <div className="bg-slate-700 rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-yellow-400 mb-1">
                        {nftDetails.metadata.totalVolume}
                      </div>
                      <div className="text-slate-400 text-sm">Jami savdo (ETH)</div>
                    </div>
                    <div className="bg-slate-700 rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-green-400 mb-1">
                        {nftDetails.metadata.royaltyFee}%
                      </div>
                      <div className="text-slate-400 text-sm">Royalty foizi</div>
                    </div>
                    <div className="bg-slate-700 rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-blue-400 mb-1">
                        {nftDetails.currentListing?.bidCount || 0}
                      </div>
                      <div className="text-slate-400 text-sm">Bidlar soni</div>
                    </div>
                  </div>

                  <div className="bg-slate-700 rounded-lg p-4">
                    <h3 className="text-white font-semibold mb-4">Owner ma'lumotlari</h3>
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Joriy ega:</span>
                        <span className="text-white font-mono">{formatAddress(nftDetails.owner)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Yaratuvchi:</span>
                        <span className="text-white font-mono">{formatAddress(nftDetails.creator)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Mint sanasi:</span>
                        <span className="text-white">{new Date(nftDetails.metadata.mintDate).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Action Panel */}
        <div className="space-y-6">
          {/* Price/Action Card */}
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <div className="text-center mb-6">
              {nftDetails.currentListing ? (
                nftDetails.currentListing.isAuction ? (
                  <>
                    <div className="text-3xl font-bold text-white mb-2">
                      {nftDetails.currentListing.currentBid} ETH
                    </div>
                    <div className="text-slate-400 text-sm">Joriy bid</div>
                    <div className="text-slate-400 text-sm mt-2">
                      {nftDetails.currentListing.bidCount} bid qo'yilgan
                    </div>
                  </>
                ) : (
                  <>
                    <div className="text-3xl font-bold text-yellow-400 mb-2">
                      {nftDetails.currentListing.price} ETH
                    </div>
                    <div className="text-slate-400 text-sm">Qat'iy narx</div>
                  </>
                )
              ) : (
                <>
                  <div className="text-2xl font-bold text-slate-400 mb-2">
                    Sotilmayapti
                  </div>
                  <div className="text-slate-500 text-sm">Aktiv listing yo'q</div>
                </>
              )}
            </div>

            {/* Auction Actions */}
            {nftDetails.currentListing?.isAuction && (
              <div className="space-y-4">
                <div>
                  <label className="block text-slate-400 text-sm mb-2">Bid miqdori (ETH)</label>
                  <input
                    type="number"
                    step="0.01"
                    min={parseFloat(nftDetails.currentListing.highestBid) + 0.01}
                    value={bidAmount}
                    onChange={(e) => setBidAmount(e.target.value)}
                    placeholder={`Min: ${(parseFloat(nftDetails.currentListing.highestBid) + 0.01).toFixed(2)}`}
                    className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-yellow-500"
                  />
                </div>
                
                <button
                  onClick={handleBid}
                  disabled={!bidAmount || isLoading}
                  className={`w-full py-3 rounded-lg font-semibold transition-colors ${
                    bidAmount && !isLoading
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700'
                      : 'bg-slate-700 text-slate-400 cursor-not-allowed'
                  }`}
                >
                  {isLoading ? (
                    <div className="flex items-center justify-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Bid qo'yilmoqda...</span>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center space-x-2">
                      <Gavel className="w-4 h-4" />
                      <span>Bid qo'yish</span>
                    </div>
                  )}
                </button>
              </div>
            )}

            {/* Fixed Price Actions */}
            {nftDetails.currentListing && !nftDetails.currentListing.isAuction && (
              <button
                onClick={handlePurchase}
                disabled={isLoading}
                className={`w-full py-3 rounded-lg font-semibold transition-colors ${
                  !isLoading
                    ? 'bg-gradient-to-r from-yellow-500 to-orange-500 text-white hover:from-yellow-600 hover:to-orange-600'
                    : 'bg-slate-700 text-slate-400 cursor-not-allowed'
                }`}
              >
                {isLoading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Sotib olinmoqda...</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center space-x-2">
                    <ShoppingCart className="w-4 h-4" />
                    <span>Sotib olish</span>
                  </div>
                )}
              </button>
            )}
          </div>

          {/* Certifications */}
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <h3 className="text-white font-semibold mb-4">Sertifikatlar</h3>
            <div className="space-y-3">
              <Link 
                to={`/certification/${id}`}
                className="flex items-center space-x-3 bg-slate-700 hover:bg-slate-600 rounded-lg p-3 transition-colors"
              >
                <Award className="w-5 h-5 text-yellow-400" />
                <div className="flex-1">
                  <div className="text-white font-semibold">Assay Sertifikat</div>
                  <div className="text-slate-400 text-sm">{nftDetails.certifications.assay}</div>
                </div>
                <ExternalLink className="w-4 h-4 text-slate-400" />
              </Link>
              
              <div className="flex items-center space-x-3 bg-slate-700 rounded-lg p-3">
                <Building className="w-5 h-5 text-blue-400" />
                <div className="flex-1">
                  <div className="text-white font-semibold">Saqlash Sertifikat</div>
                  <div className="text-slate-400 text-sm">{nftDetails.certifications.storage}</div>
                </div>
                <CheckCircle className="w-4 h-4 text-green-400" />
              </div>
            </div>
          </div>

          {/* Quick Info */}
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <h3 className="text-white font-semibold mb-4">Tezkor ma'lumot</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-400">Token ID:</span>
                <span className="text-white font-mono">#{nftDetails.tokenId}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Standard:</span>
                <span className="text-white">ERC-721</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Blockchain:</span>
                <span className="text-white">Ethereum</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Tasdiqlangan:</span>
                <div className="flex items-center space-x-1">
                  <CheckCircle className="w-4 h-4 text-green-400" />
                  <span className="text-green-400">Ha</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};