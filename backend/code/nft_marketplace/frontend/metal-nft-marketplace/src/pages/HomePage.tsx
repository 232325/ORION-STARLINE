import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useMarketplace } from '../contexts/MarketplaceContext';
import { useWeb3 } from '../contexts/Web3Context';
import { 
  TrendingUp, 
  Shield, 
  Coins, 
  Award, 
  Users, 
  BarChart3,
  ArrowRight,
  CheckCircle,
  Lock,
  Globe
} from 'lucide-react';

export const HomePage: React.FC = () => {
  const { totalVolume, totalSales, floorPrice, metalNFTs } = useMarketplace();
  const { isConnected } = useWeb3();

  const features = [
    {
      icon: Shield,
      title: 'Sertifikatlangan Metallar',
      description: 'Har bir NFT mustaqil laboratoriya tomonidan tekshirilgan va tasdiqlangan metallarga bog\'langan'
    },
    {
      icon: Lock,
      title: 'Xavfsiz Saqlash',
      description: 'Metallar dunyodagi eng ishonchli vault kompaniyalarida (Brink\'s, Malca-Amit) saqlanadi'
    },
    {
      icon: Award,
      title: 'Sug\'urta Himoyasi',
      description: 'Har bir aktiv sug\'urta bilan himoyalangan va qonuniy hujjatlar bilan tasdiqlangan'
    },
    {
      icon: Globe,
      title: 'Global Bozor',
      description: 'OpenSea, Foundation, SuperRare va boshqa platformalar orqali global savdo'
    }
  ];

  const stats = [
    { label: 'Jami Savdo', value: `${totalSales}`, suffix: '' },
    { label: 'Jami Hajm', value: totalVolume, suffix: ' ETH' },
    { label: 'Floor Price', value: floorPrice, suffix: ' ETH' },
    { label: 'Aktiv NFT', value: metalNFTs.length.toString(), suffix: '' }
  ];

  const recentNFTs = metalNFTs.slice(0, 3);

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center py-16">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            <span className="bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 bg-clip-text text-transparent">
              Metallarga Asoslangan
            </span>
            <br />
            <span className="text-white">NFT Bozor</span>
          </h1>
          <p className="text-xl text-slate-300 mb-8 leading-relaxed">
            Oltin, kumush, платина va boshqa qimmatbop metallarga asoslangan 
            autentik NFT tokenlari bilan tanishing. Har bir token real metallarga 
            bog'langan va professional laboratoriya tomonidan tasdiqlangan.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link
              to="/marketplace"
              className="flex items-center space-x-2 bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-8 py-4 rounded-xl font-semibold hover:from-yellow-600 hover:to-orange-600 transition-all transform hover:scale-105"
            >
              <span>Bozorni Ko'rish</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            
            {!isConnected && (
              <Link
                to="/portfolio"
                className="flex items-center space-x-2 border-2 border-slate-600 text-slate-300 px-8 py-4 rounded-xl font-semibold hover:border-slate-500 hover:text-white transition-colors"
              >
                <span>Portfel Yaratish</span>
              </Link>
            )}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-slate-800/50 rounded-2xl p-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-3xl font-bold text-yellow-400 mb-2">
                {stat.value}{stat.suffix}
              </div>
              <div className="text-slate-400">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section>
        <h2 className="text-3xl font-bold text-center mb-12 text-white">
          Nega MetalNFT?
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <div key={index} className="bg-slate-800/50 p-6 rounded-xl border border-slate-700 hover:border-yellow-500/50 transition-colors">
              <div className="w-12 h-12 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-lg flex items-center justify-center mb-4">
                <feature.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-slate-400 text-sm">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Recent NFTs Section */}
      <section>
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-bold text-white">So'nggi Metall NFTlar</h2>
          <Link 
            to="/marketplace"
            className="flex items-center space-x-2 text-yellow-400 hover:text-yellow-300 transition-colors"
          >
            <span>Barchasini ko'rish</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        
        <div className="grid md:grid-cols-3 gap-6">
          {recentNFTs.map((nft) => (
            <Link 
              key={nft.tokenId} 
              to={`/metal/${nft.tokenId}`}
              className="bg-slate-800 rounded-xl overflow-hidden border border-slate-700 hover:border-yellow-500/50 transition-colors group"
            >
              <div className="aspect-square bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center relative overflow-hidden">
                {nft.imageUrl ? (
                  <img 
                    src={nft.imageUrl} 
                    alt={nft.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                  />
                ) : (
                  <Coins className="w-16 h-16 text-slate-600" />
                )}
                
                {nft.isVerified && (
                  <div className="absolute top-3 right-3 bg-green-500 rounded-full p-1">
                    <CheckCircle className="w-4 h-4 text-white" />
                  </div>
                )}
                
                <div className="absolute bottom-3 left-3 bg-black/80 backdrop-blur-sm px-2 py-1 rounded">
                  <span className="text-yellow-400 font-semibold text-sm">
                    {nft.metalType}
                  </span>
                </div>
              </div>
              
              <div className="p-4">
                <h3 className="text-lg font-semibold text-white mb-2">{nft.name}</h3>
                <p className="text-slate-400 text-sm mb-3 line-clamp-2">{nft.description}</p>
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-xs text-slate-500">Vazn</div>
                    <div className="text-white font-semibold">{nft.weight}g</div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500">Tozalik</div>
                    <div className="text-white font-semibold">{nft.purity}%</div>
                  </div>
                  {nft.currentListing && (
                    <div>
                      <div className="text-xs text-slate-500">Narx</div>
                      <div className="text-yellow-400 font-semibold">{nft.currentListing.price} ETH</div>
                    </div>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-slate-800 to-slate-700 rounded-2xl p-12 text-center">
        <h2 className="text-3xl font-bold text-white mb-4">
          Metall NFT Dunyosiga Qo'shiling
        </h2>
        <p className="text-slate-300 mb-8 max-w-2xl mx-auto">
          Real metallarga bog'langan, sertifikatlangan va sug'urtalangan NFT tokenlari 
          bilan investitsiya portfelngizni diversifikatsiya qiling.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/marketplace"
            className="flex items-center justify-center space-x-2 bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-8 py-4 rounded-xl font-semibold hover:from-yellow-600 hover:to-orange-600 transition-all"
          >
            <TrendingUp className="w-5 h-5" />
            <span>BoZorda Savdo Qilish</span>
          </Link>
          
          <Link
            to="/create-listing"
            className="flex items-center justify-center space-x-2 border-2 border-slate-500 text-slate-300 px-8 py-4 rounded-xl font-semibold hover:border-slate-400 hover:text-white transition-colors"
          >
            <Coins className="w-5 h-5" />
            <span>NFT Yaratish</span>
          </Link>
        </div>
      </section>
    </div>
  );
};