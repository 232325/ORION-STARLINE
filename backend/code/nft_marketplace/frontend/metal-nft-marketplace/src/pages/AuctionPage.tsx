import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useMarketplace } from '../contexts/MarketplaceContext';
import { 
  Clock, 
  Users, 
  Gavel,
  TrendingUp,
  CheckCircle,
  Coins,
  Award,
  ArrowLeft,
  ExternalLink
} from 'lucide-react';

export const AuctionPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { placeBid, purchaseListing } = useMarketplace();
  const [bidAmount, setBidAmount] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [timeLeft, setTimeLeft] = useState<string>('');

  // Mock auction data
  const auctionData = {
    id: id,
    nftName: "1 oz Gold Bar",
    nftImage: "/images/gold-bar-1oz.jpg",
    description: "Certified 999.9 pure gold bar from Brink's vault",
    metalType: "GOLD",
    weight: 31.1035,
    purity: 99.99,
    storageFacility: "Brink's Global Services",
    startingPrice: "1.20",
    currentBid: "1.45",
    highestBidder: "0x1234...5678",
    bidCount: 12,
    endTime: "2024-12-31T23:59:59Z",
    isVerified: true,
    seller: "0xabcd...efgh"
  };

  // Calculate time left
  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date().getTime();
      const end = new Date(auctionData.endTime).getTime();
      const difference = end - now;

      if (difference > 0) {
        const days = Math.floor(difference / (1000 * 60 * 60 * 24));
        const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
        
        setTimeLeft(`${days} kun ${hours} soat ${minutes} daqiqa`);
      } else {
        setTimeLeft('Auction tugagan');
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const handleBid = async () => {
    if (!bidAmount || parseFloat(bidAmount) <= parseFloat(auctionData.currentBid)) {
      return;
    }

    setIsLoading(true);
    try {
      await placeBid(id!, bidAmount);
      console.log('Bid qo\'yildi:', bidAmount);
    } catch (error) {
      console.error('Bid qo\'yishda xato:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const bids = [
    { amount: "1.45", bidder: "0x1234...5678", time: "2 soat oldin" },
    { amount: "1.35", bidder: "0xabcd...ef01", time: "5 soat oldin" },
    { amount: "1.30", bidder: "0x2345...6789", time: "1 kun oldin" },
    { amount: "1.25", bidder: "0x3456...7890", time: "2 kun oldin" },
  ];

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center space-x-4 mb-8">
        <Link to="/marketplace" className="p-2 text-slate-400 hover:text-white transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-white">Auction</h1>
          <p className="text-slate-400">NFT #{id}</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* NFT Details */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-800 rounded-xl overflow-hidden border border-slate-700">
            <div className="aspect-square bg-gradient-to-br from-slate-700 to-slate-800 relative">
              {auctionData.nftImage ? (
                <img 
                  src={auctionData.nftImage} 
                  alt={auctionData.nftName}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <Coins className="w-24 h-24 text-slate-600" />
                </div>
              )}
              
              {auctionData.isVerified && (
                <div className="absolute top-4 right-4 bg-green-500 rounded-full p-2">
                  <CheckCircle className="w-6 h-6 text-white" />
                </div>
              )}
              
              <div className="absolute bottom-4 left-4 bg-black/80 backdrop-blur-sm px-4 py-2 rounded-full">
                <span className="text-yellow-400 font-semibold">
                  {auctionData.metalType}
                </span>
              </div>
            </div>
            
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-white mb-2">{auctionData.nftName}</h2>
                  <p className="text-slate-400">{auctionData.description}</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-yellow-400 mb-1">
                    {auctionData.currentBid} ETH
                  </div>
                  <div className="text-slate-400 text-sm">Joriy bid</div>
                </div>
              </div>
              
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="text-center">
                  <div className="text-slate-400 text-sm">Vazn</div>
                  <div className="text-white font-semibold">{auctionData.weight}g</div>
                </div>
                <div className="text-center">
                  <div className="text-slate-400 text-sm">Tozalik</div>
                  <div className="text-white font-semibold">{auctionData.purity}%</div>
                </div>
                <div className="text-center">
                  <div className="text-slate-400 text-sm">Bidlar soni</div>
                  <div className="text-white font-semibold">{auctionData.bidCount}</div>
                </div>
              </div>

              <div className="bg-slate-700 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Award className="w-5 h-5 text-green-400" />
                  <span className="text-white font-semibold">Sertifikat ma'lumotlari</span>
                </div>
                <div className="text-slate-400 text-sm">
                  Saqlash: {auctionData.storageFacility}<br/>
                  Sertifikat: ✅ Tasdiqlangan<br/>
                  Sug'urta: ✅ Faol
                </div>
              </div>
            </div>
          </div>

          {/* Bid History */}
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <h3 className="text-xl font-semibold text-white mb-4">Bid tarixi</h3>
            <div className="space-y-3">
              {bids.map((bid, index) => (
                <div key={index} className="flex items-center justify-between bg-slate-700 rounded-lg p-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                      <Users className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <div className="text-white font-semibold">{bid.bidder}</div>
                      <div className="text-slate-400 text-sm">{bid.time}</div>
                    </div>
                  </div>
                  <div className="text-yellow-400 font-bold">{bid.amount} ETH</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Auction Panel */}
        <div className="space-y-6">
          {/* Time Left */}
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <div className="text-center">
              <div className="flex items-center justify-center space-x-2 mb-4">
                <Clock className="w-6 h-6 text-red-400" />
                <span className="text-xl font-bold text-white">Vaqt tugashiga</span>
              </div>
              <div className="text-3xl font-bold text-red-400 mb-2">
                {timeLeft}
              </div>
              <div className="text-slate-400">
                Auction yakunlanish vaqti: {new Date(auctionData.endTime).toLocaleDateString()}
              </div>
            </div>
          </div>

          {/* Bidding Panel */}
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <div className="text-center mb-6">
              <Gavel className="w-12 h-12 text-yellow-400 mx-auto mb-3" />
              <h3 className="text-xl font-semibold text-white mb-2">Bid qo'yish</h3>
              <div className="text-slate-400">
                Joriy narx: <span className="text-yellow-400 font-semibold">{auctionData.currentBid} ETH</span>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-slate-400 text-sm mb-2">Bid miqdori (ETH)</label>
                <input
                  type="number"
                  step="0.01"
                  min={parseFloat(auctionData.currentBid) + 0.01}
                  value={bidAmount}
                  onChange={(e) => setBidAmount(e.target.value)}
                  placeholder={`Min: ${parseFloat(auctionData.currentBid) + 0.01}`}
                  className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-yellow-500"
                />
              </div>

              <div className="text-sm text-slate-400">
                <p>Minimal bid: {(parseFloat(auctionData.currentBid) + 0.01).toFixed(2)} ETH</p>
                <p>Platforma xaraji: 2.5%</p>
              </div>

              <button
                onClick={handleBid}
                disabled={!bidAmount || parseFloat(bidAmount) <= parseFloat(auctionData.currentBid) || isLoading}
                className={`w-full py-3 rounded-lg font-semibold transition-colors ${
                  bidAmount && parseFloat(bidAmount) > parseFloat(auctionData.currentBid) && !isLoading
                    ? 'bg-gradient-to-r from-yellow-500 to-orange-500 text-white hover:from-yellow-600 hover:to-orange-600'
                    : 'bg-slate-700 text-slate-400 cursor-not-allowed'
                }`}
              >
                {isLoading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Bid qo'yilmoqda...</span>
                  </div>
                ) : (
                  'Bid qo\'yish'
                )}
              </button>
            </div>
          </div>

          {/* Quick Bid */}
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <h3 className="text-white font-semibold mb-4">Tezkor bid</h3>
            <div className="grid grid-cols-2 gap-2">
              {['+0.05', '+0.10', '+0.25', '+0.50'].map((increment) => (
                <button
                  key={increment}
                  onClick={() => setBidAmount((parseFloat(auctionData.currentBid) + parseFloat(increment)).toFixed(2))}
                  className="bg-slate-700 hover:bg-slate-600 text-white py-2 px-3 rounded-lg text-sm transition-colors"
                >
                  {increment} ETH
                </button>
              ))}
            </div>
          </div>

          {/* Highest Bidder */}
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <div className="flex items-center space-x-2 mb-3">
              <TrendingUp className="w-5 h-5 text-green-400" />
              <span className="text-white font-semibold">Eng yuqori bidder</span>
            </div>
            <div className="text-slate-400">
              <p className="mb-1">Wallet: {auctionData.highestBidder}</p>
              <p>Miqdor: <span className="text-yellow-400 font-semibold">{auctionData.currentBid} ETH</span></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};