import { useState, useEffect } from 'react';
import { Store, TrendingUp, Star, DollarSign, Users, Search, Filter } from 'lucide-react';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';

interface MarketplaceItem {
  id: string;
  title: string;
  description: string;
  item_type: string;
  price: number;
  currency: string;
  seller: {
    username: string;
    avatar_url: string;
  };
  average_rating: number;
  total_sales: number;
  views_count: number;
  performance_data: any;
  features: string[];
  created_at: string;
}

export default function MarketplacePage() {
  const { user } = useAuth();
  const [items, setItems] = useState<MarketplaceItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    type: '',
    sort: 'popularity',
    search: '',
  });

  useEffect(() => {
    loadItems();
  }, [filters]);

  const loadItems = async () => {
    setLoading(true);
    try {
      const queryParams = new URLSearchParams({
        ...filters,
        limit: '20',
        offset: '0',
      });

      const { data, error } = await supabase.functions.invoke('premium-marketplace', {
        method: 'GET',
        body: { action: 'list-items', ...filters },
      });

      if (error) throw error;
      setItems(data.items || []);
    } catch (error) {
      console.error('Xatolik:', error);
    } finally {
      setLoading(false);
    }
  };

  const purchaseItem = async (itemId: string) => {
    if (!user) {
      alert('Xarid qilish uchun tizimga kiring');
      return;
    }

    if (!confirm('Haqiqatan ham bu itemni sotib olmoqchimisiz?')) return;

    try {
      const { data, error } = await supabase.functions.invoke('premium-marketplace', {
        body: {
          item_id: itemId,
          buyer_id: user.id,
          payment_method: 'balance',
          action: 'purchase-item',
        },
      });

      if (error) throw error;
      alert(data.message);
      loadItems();
    } catch (error: any) {
      alert(error.message || 'Xarid amalga oshmadi');
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'strategy':
        return <TrendingUp className="w-5 h-5" />;
      case 'signal':
        return <Star className="w-5 h-5" />;
      case 'bot':
        return <Users className="w-5 h-5" />;
      default:
        return <Store className="w-5 h-5" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'strategy':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'signal':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'bot':
        return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      default:
        return 'bg-green-500/20 text-green-400 border-green-500/30';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
          <Store className="w-10 h-10 text-purple-400" />
          Premium Marketplace
        </h1>
        <p className="text-slate-400">Premium strategiya, signal va botlar bozori</p>
      </div>

      {/* Search & Filters */}
      <div className="mb-8 space-y-4">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              placeholder="Qidiruv..."
              className="w-full pl-12 pr-4 py-3 bg-slate-800/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-purple-500"
            />
          </div>
        </div>

        <div className="flex gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-purple-400" />
            <span className="text-slate-400 text-sm">Filtrlar:</span>
          </div>

          {/* Type Filter */}
          <select
            value={filters.type}
            onChange={(e) => setFilters({ ...filters, type: e.target.value })}
            className="px-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-purple-500"
          >
            <option value="">Barcha turlar</option>
            <option value="strategy">Strategiyalar</option>
            <option value="signal">Signallar</option>
            <option value="bot">Botlar</option>
            <option value="indicator">Indikatorlar</option>
          </select>

          {/* Sort Filter */}
          <select
            value={filters.sort}
            onChange={(e) => setFilters({ ...filters, sort: e.target.value })}
            className="px-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-purple-500"
          >
            <option value="popularity">Mashhur</option>
            <option value="price-low">Arzon birinchi</option>
            <option value="price-high">Qimmat birinchi</option>
            <option value="rating">Reyting bo'yicha</option>
            <option value="newest">Yangi</option>
          </select>
        </div>
      </div>

      {/* Items Grid */}
      {loading ? (
        <div className="text-center py-12">
          <Store className="w-12 h-12 text-purple-400 animate-pulse mx-auto mb-4" />
          <p className="text-slate-400">Yuklanmoqda...</p>
        </div>
      ) : items.length === 0 ? (
        <div className="text-center py-12 bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl">
          <Store className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400">Itemlar topilmadi</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map(item => (
            <div
              key={item.id}
              className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl overflow-hidden hover:border-purple-500/50 transition-all group"
            >
              {/* Header */}
              <div className="p-6 pb-4">
                <div className="flex items-start justify-between mb-3">
                  <div className={`px-3 py-1 rounded-lg border flex items-center gap-2 ${getTypeColor(item.item_type)}`}>
                    {getTypeIcon(item.item_type)}
                    <span className="text-sm font-medium">{item.item_type}</span>
                  </div>
                  {item.average_rating > 0 && (
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                      <span className="text-white font-semibold">{item.average_rating.toFixed(1)}</span>
                    </div>
                  )}
                </div>

                <h3 className="text-xl font-bold text-white mb-2 group-hover:text-purple-400 transition-colors">
                  {item.title}
                </h3>
                <p className="text-slate-400 text-sm mb-4 line-clamp-2">{item.description}</p>

                {/* Seller */}
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                    <Users className="w-5 h-5 text-purple-400" />
                  </div>
                  <div>
                    <p className="text-white text-sm font-medium">{item.seller.username}</p>
                    <p className="text-slate-500 text-xs">{item.total_sales} sotilgan</p>
                  </div>
                </div>

                {/* Features */}
                {item.features && item.features.length > 0 && (
                  <div className="mb-4">
                    <div className="flex flex-wrap gap-2">
                      {item.features.slice(0, 3).map((feature, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-slate-900/50 text-slate-400 rounded text-xs"
                        >
                          {feature}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Stats */}
                <div className="grid grid-cols-2 gap-3 mb-4">
                  {item.performance_data?.expected_return && (
                    <div className="p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
                      <p className="text-xs text-slate-400 mb-1">Daromad</p>
                      <p className="text-green-400 font-bold">{item.performance_data.expected_return}</p>
                    </div>
                  )}
                  {item.performance_data?.win_rate && (
                    <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                      <p className="text-xs text-slate-400 mb-1">Win Rate</p>
                      <p className="text-blue-400 font-bold">{item.performance_data.win_rate}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Footer */}
              <div className="px-6 py-4 bg-slate-900/50 border-t border-slate-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-400 text-xs mb-1">Narx</p>
                    <p className="text-2xl font-bold text-white">
                      ${item.price}
                      <span className="text-sm text-slate-400 ml-1">{item.currency}</span>
                    </p>
                  </div>
                  <button
                    onClick={() => purchaseItem(item.id)}
                    className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-all flex items-center gap-2"
                  >
                    <DollarSign className="w-4 h-4" />
                    Sotib olish
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Sell Your Own */}
      <div className="mt-12 max-w-4xl mx-auto bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-purple-500/30 rounded-2xl p-8 text-center">
        <Store className="w-16 h-16 text-purple-400 mx-auto mb-4" />
        <h2 className="text-3xl font-bold text-white mb-3">O'z strategiyangizni soting!</h2>
        <p className="text-slate-300 mb-6">
          Premium strategiya, signal yoki botni marketplace'ga joylashtiring va passive daromad oling
        </p>
        <button className="px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-bold transition-all">
          Item joylashtirish
        </button>
      </div>
    </div>
  );
}
