import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useMarketplace } from '../contexts/MarketplaceContext';
import { useWeb3 } from '../contexts/Web3Context';
import { 
  Wallet, 
  TrendingUp, 
  TrendingDown,
  Eye,
  Share2,
  Settings,
  Plus,
  Coins,
  Award,
  BarChart3,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

export const PortfolioPage: React.FC = () => {
  const { userNFTs, totalVolume, totalSales, floorPrice } = useMarketplace();
  const { account, isConnected } = useWeb3();
  const [activeTab, setActiveTab] = useState<'collection' | 'history' | 'analytics'>('collection');

  // Mock portfolio data
  const portfolioStats = {
    totalValue: "2.45",
    totalNFTs: userNFTs.length,
    gainLoss: "+15.3%",
    gainLossAmount: "+0.32 ETH",
    avgValue: "0.82 ETH",
    mostValued: userNFTs[0]?.name || "N/A",
    certifications: userNFTs.filter(nft => nft.isVerified).length
  };

  // Mock transaction history
  const transactionHistory = [
    {
      id: "1",
      type: "buy",
      nftName: "1 oz Gold Bar",
      price: "0.45",
      date: "2024-01-15",
      txHash: "0x1234567890abcdef",
      status: "confirmed"
    },
    {
      id: "2", 
      type: "sell",
      nftName: "Silver Eagle Coin",
      price: "0.89",
      date: "2024-01-10",
      txHash: "0xabcdef1234567890",
      status: "confirmed"
    },
    {
      id: "3",
      type: "bid",
      nftName: "Platinum Bar 10g", 
      price: "1.20",
      date: "2024-01-08",
      txHash: "0xfedcba0987654321",
      status: "pending"
    }
  ];

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return 'text-green-400';
      case 'pending': return 'text-yellow-400';
      case 'failed': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'confirmed': return <CheckCircle className="w-4 h-4" />;
      case 'pending': return <Clock className="w-4 h-4" />;
      case 'failed': return <AlertCircle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  if (!isConnected) {
    return (
      <div className="text-center py-16">
        <Wallet className="w-16 h-16 text-slate-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-white mb-4">
          Wallet ulanish kerak
        </h2>
        <p className="text-slate-400 mb-8 max-w-md mx-auto">
          Portfelingizni ko'rish va boshqarish uchun avval walletingizni ulang.
        </p>
        <button className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-8 py-3 rounded-xl font-semibold hover:from-yellow-600 hover:to-orange-600 transition-colors">
          Wallet ulash
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Mening Portfelem</h1>
          <div className="flex items-center space-x-4 text-slate-400">
            <span>Wallet: {formatAddress(account!)}</span>
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span>Ulangan</span>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <button className="flex items-center space-x-2 bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg transition-colors">
            <Share2 className="w-4 h-4" />
            <span>Ulashish</span>
          </button>
          <button className="flex items-center space-x-2 bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg transition-colors">
            <Settings className="w-4 h-4" />
            <span>Sozlamalar</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-slate-400 text-sm">Jami qiymat</h3>
            <BarChart3 className="w-5 h-5 text-yellow-400" />
          </div>
          <div className="text-2xl font-bold text-white mb-1">
            {portfolioStats.totalValue} ETH
          </div>
          <div className="flex items-center space-x-2 text-sm">
            <TrendingUp className="w-4 h-4 text-green-400" />
            <span className="text-green-400">{portfolioStats.gainLoss}</span>
            <span className="text-slate-400">({portfolioStats.gainLossAmount})</span>
          </div>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-slate-400 text-sm">NFT soni</h3>
            <Coins className="w-5 h-5 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-white mb-1">
            {portfolioStats.totalNFTs}
          </div>
          <div className="text-sm text-slate-400">
            O'rtacha qiymat: {portfolioStats.avgValue} ETH
          </div>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-slate-400 text-sm">Sertifikatlangan</h3>
            <Award className="w-5 h-5 text-green-400" />
          </div>
          <div className="text-2xl font-bold text-white mb-1">
            {portfolioStats.certifications}
          </div>
          <div className="text-sm text-slate-400">
            {portfolioStats.totalNFTs > 0 ? Math.round((portfolioStats.certifications / portfolioStats.totalNFTs) * 100) : 0}% tasdiqlangan
          </div>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-slate-400 text-sm">Eng qimmat</h3>
            <TrendingUp className="w-5 h-5 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-white mb-1 truncate">
            {portfolioStats.mostValued}
          </div>
          <div className="text-sm text-slate-400">
            Qimmatli aktiv
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-slate-800 rounded-xl border border-slate-700">
        <div className="flex border-b border-slate-700">
          {[
            { id: 'collection', label: 'Kolleksiya', icon: Coins },
            { id: 'history', label: 'Tarix', icon: Clock },
            { id: 'analytics', label: 'Tahlil', icon: BarChart3 }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 px-6 py-4 font-medium transition-colors ${
                activeTab === tab.id 
                  ? 'text-yellow-400 border-b-2 border-yellow-400 bg-slate-700/50' 
                  : 'text-slate-400 hover:text-white hover:bg-slate-700/30'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        <div className="p-6">
          {/* Collection Tab */}
          {activeTab === 'collection' && (
            <div className="space-y-6">
              {userNFTs.length === 0 ? (
                <div className="text-center py-12">
                  <Coins className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-slate-400 mb-2">
                    Hali NFT yo'q
                  </h3>
                  <p className="text-slate-500 mb-6">
                    Metall NFT sotib olish yoki yaratish orqali portfelngizni boshlang
                  </p>
                  <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <Link
                      to="/marketplace"
                      className="flex items-center space-x-2 bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-6 py-3 rounded-lg font-semibold hover:from-yellow-600 hover:to-orange-600 transition-colors"
                    >
                      <span>BoZorda sotib olish</span>
                    </Link>
                    <Link
                      to="/create-listing"
                      className="flex items-center space-x-2 border border-slate-600 text-slate-300 px-6 py-3 rounded-lg font-semibold hover:border-slate-500 hover:text-white transition-colors"
                    >
                      <Plus className="w-4 h-4" />
                      <span>Yaratish</span>
                    </Link>
                  </div>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {userNFTs.map((nft) => (
                    <div key={nft.tokenId} className="bg-slate-700 rounded-xl overflow-hidden border border-slate-600">
                      <div className="aspect-square bg-gradient-to-br from-slate-600 to-slate-700 relative">
                        {nft.imageUrl ? (
                          <img 
                            src={nft.imageUrl} 
                            alt={nft.name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <Coins className="w-16 h-16 text-slate-500" />
                          </div>
                        )}
                        
                        {nft.isVerified && (
                          <div className="absolute top-3 right-3 bg-green-500 rounded-full p-1">
                            <CheckCircle className="w-4 h-4 text-white" />
                          </div>
                        )}
                        
                        <div className="absolute bottom-3 left-3 bg-black/80 backdrop-blur-sm px-3 py-1 rounded-full">
                          <span className="text-yellow-400 font-semibold text-sm">
                            {nft.metalType}
                          </span>
                        </div>
                      </div>
                      
                      <div className="p-4">
                        <h3 className="text-lg font-semibold text-white mb-2">{nft.name}</h3>
                        <p className="text-slate-400 text-sm mb-3 line-clamp-2">{nft.description}</p>
                        
                        <div className="grid grid-cols-2 gap-4 mb-4">
                          <div>
                            <div className="text-xs text-slate-500">Vazn</div>
                            <div className="text-white font-semibold">{nft.weight}g</div>
                          </div>
                          <div>
                            <div className="text-xs text-slate-500">Tozalik</div>
                            <div className="text-white font-semibold">{nft.purity}%</div>
                          </div>
                        </div>

                        <div className="flex items-center justify-between">
                          <Link
                            to={`/metal/${nft.tokenId}`}
                            className="flex items-center space-x-2 bg-slate-600 hover:bg-slate-500 text-white px-3 py-2 rounded-lg text-sm transition-colors"
                          >
                            <Eye className="w-4 h-4" />
                            <span>Ko'rish</span>
                          </Link>
                          
                          <Link
                            to={`/certification/${nft.tokenId}`}
                            className="flex items-center space-x-2 bg-yellow-500 hover:bg-yellow-600 text-black px-3 py-2 rounded-lg text-sm font-semibold transition-colors"
                          >
                            <Award className="w-4 h-4" />
                            <span>Sertifikat</span>
                          </Link>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* History Tab */}
          {activeTab === 'history' && (
            <div className="space-y-4">
              {transactionHistory.map((tx) => (
                <div key={tx.id} className="bg-slate-700 rounded-lg p-4 border border-slate-600">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        tx.type === 'buy' ? 'bg-green-500' : 
                        tx.type === 'sell' ? 'bg-red-500' : 'bg-blue-500'
                      }`}>
                        {tx.type === 'buy' ? <TrendingUp className="w-4 h-4 text-white" /> :
                         tx.type === 'sell' ? <TrendingDown className="w-4 h-4 text-white" /> :
                         <Clock className="w-4 h-4 text-white" />}
                      </div>
                      <div>
                        <div className="text-white font-semibold">
                          {tx.type === 'buy' ? 'Sotib olindi' : 
                           tx.type === 'sell' ? 'Sotildi' : 'Bid qo\'yildi'}
                        </div>
                        <div className="text-slate-400 text-sm">{tx.nftName}</div>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-white font-semibold">{tx.price} ETH</div>
                      <div className="text-slate-400 text-sm">{tx.date}</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(tx.status)}
                      <span className={`text-sm ${getStatusColor(tx.status)}`}>
                        {tx.status === 'confirmed' ? 'Tasdiqlangan' :
                         tx.status === 'pending' ? 'Kutilmoqda' : 'Xato'}
                      </span>
                    </div>
                    
                    <div className="text-slate-400 text-sm font-mono">
                      {formatAddress(tx.txHash)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Analytics Tab */}
          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-slate-700 rounded-lg p-6">
                  <h3 className="text-white font-semibold mb-4">Portfel taqsimoti</h3>
                  <div className="space-y-3">
                    {['Oltin', 'Kumush', 'Platina', 'Palladiy'].map((metal, index) => {
                      const percentage = [45, 30, 15, 10][index];
                      return (
                        <div key={metal} className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className={`w-3 h-3 rounded-full ${
                              ['bg-yellow-500', 'bg-gray-400', 'bg-blue-400', 'bg-purple-400'][index]
                            }`}></div>
                            <span className="text-slate-300">{metal}</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <div className="w-24 bg-slate-600 rounded-full h-2">
                              <div 
                                className={`h-2 rounded-full ${
                                  ['bg-yellow-500', 'bg-gray-400', 'bg-blue-400', 'bg-purple-400'][index]
                                }`}
                                style={{ width: `${percentage}%` }}
                              ></div>
                            </div>
                            <span className="text-white text-sm font-semibold w-12">{percentage}%</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="bg-slate-700 rounded-lg p-6">
                  <h3 className="text-white font-semibold mb-4">Performans metriklari</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-400">7 kunlik o'zgarish</span>
                      <span className="text-green-400 font-semibold">+8.5%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-400">30 kunlik o'zgarish</span>
                      <span className="text-green-400 font-semibold">+15.3%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-400">Jami ROI</span>
                      <span className="text-yellow-400 font-semibold">+23.7%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-400">Eng yaxshi aktiv</span>
                      <span className="text-white font-semibold">1 oz Gold Bar</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Performance Chart Placeholder */}
              <div className="bg-slate-700 rounded-lg p-6">
                <h3 className="text-white font-semibold mb-4">Qiymat dinamikasi</h3>
                <div className="h-64 bg-slate-800 rounded-lg flex items-center justify-center">
                  <div className="text-center text-slate-400">
                    <BarChart3 className="w-12 h-12 mx-auto mb-2" />
                    <p>Grafik ma'lumotlari tez orada</p>
                    <p className="text-sm">Integratsiya jarayonida</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};