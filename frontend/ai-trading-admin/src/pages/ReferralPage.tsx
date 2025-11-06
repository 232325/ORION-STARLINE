import { useEffect, useState } from 'react';
import { GiftIcon, UsersIcon, CurrencyDollarIcon, ShareIcon } from '@heroicons/react/24/outline';

interface ReferralStats {
  total_referrals: number;
  active_referrals: number;
  total_earnings: number;
  pending_earnings: number;
  referrals: Array<{
    id: string;
    referred_user_email: string;
    status: string;
    commission_earned: number;
    created_at: string;
  }>;
}

export default function ReferralPage() {
  const [stats, setStats] = useState<ReferralStats | null>(null);
  const [referralCode, setReferralCode] = useState('');
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    loadReferralData();
  }, []);

  async function loadReferralData() {
    try {
      // Get stats
      const statsResponse = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/referral-system`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ action: 'get_stats' })
        }
      );
      const statsData = await statsResponse.json();
      setStats(statsData.stats);
    } catch (error) {
      console.error('Error loading referral data:', error);
    } finally {
      setLoading(false);
    }
  }

  async function generateReferralCode() {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/referral-system`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ action: 'generate_code' })
        }
      );
      const data = await response.json();
      if (data.success) {
        setReferralCode(data.referral.code);
      }
    } catch (error) {
      console.error('Error generating code:', error);
    }
  }

  function copyToClipboard() {
    const url = `${window.location.origin}?ref=${referralCode}`;
    navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white">Yuklanmoqda...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Referral Dasturi</h2>
        <p className="text-slate-400">Do'stlaringizni taklif qiling va daromad oling</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-blue-600/20 rounded-lg">
              <UsersIcon className="w-6 h-6 text-blue-400" />
            </div>
          </div>
          <p className="text-slate-400 text-sm mb-1">Jami Referrallar</p>
          <p className="text-3xl font-bold text-white">{stats?.total_referrals || 0}</p>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-green-600/20 rounded-lg">
              <GiftIcon className="w-6 h-6 text-green-400" />
            </div>
          </div>
          <p className="text-slate-400 text-sm mb-1">Faol Referrallar</p>
          <p className="text-3xl font-bold text-green-400">{stats?.active_referrals || 0}</p>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-purple-600/20 rounded-lg">
              <CurrencyDollarIcon className="w-6 h-6 text-purple-400" />
            </div>
          </div>
          <p className="text-slate-400 text-sm mb-1">Jami Daromad</p>
          <p className="text-3xl font-bold text-white">${stats?.total_earnings.toFixed(2) || '0.00'}</p>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-yellow-600/20 rounded-lg">
              <CurrencyDollarIcon className="w-6 h-6 text-yellow-400" />
            </div>
          </div>
          <p className="text-slate-400 text-sm mb-1">Kutilayotgan</p>
          <p className="text-3xl font-bold text-yellow-400">${stats?.pending_earnings.toFixed(2) || '0.00'}</p>
        </div>
      </div>

      {/* Referral Link */}
      <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 backdrop-blur-xl rounded-xl border border-blue-700/50 p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-2xl font-bold text-white mb-2">Sizning Referral Havolangiz</h3>
            <p className="text-slate-300">Do'stlaringiz bilan ulashing va 10% komissiya oling</p>
          </div>
          <ShareIcon className="w-12 h-12 text-blue-400" />
        </div>

        {!referralCode ? (
          <button
            onClick={generateReferralCode}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
          >
            Referral Kod Yaratish
          </button>
        ) : (
          <div className="space-y-4">
            <div className="flex gap-3">
              <input
                type="text"
                value={`${window.location.origin}?ref=${referralCode}`}
                readOnly
                className="flex-1 bg-slate-800 text-white px-4 py-3 rounded-lg border border-slate-700"
              />
              <button
                onClick={copyToClipboard}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
              >
                {copied ? 'Nusxalandi!' : 'Nusxalash'}
              </button>
            </div>
            <p className="text-slate-400 text-sm">
              Sizning referral kodingiz: <span className="text-white font-bold">{referralCode}</span>
            </p>
          </div>
        )}
      </div>

      {/* How it works */}
      <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-8">
        <h3 className="text-2xl font-bold text-white mb-6">Qanday Ishlaydi?</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="w-16 h-16 bg-blue-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-blue-400">1</span>
            </div>
            <h4 className="text-white font-medium mb-2">Havolani Ulashing</h4>
            <p className="text-slate-400 text-sm">Do'stlaringizga va ijtimoiy tarmoqlarda ulashing</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-green-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-green-400">2</span>
            </div>
            <h4 className="text-white font-medium mb-2">Ro'yxatdan O'tish</h4>
            <p className="text-slate-400 text-sm">Ular sizning havolangiz orqali ro'yxatdan o'tadilar</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 bg-purple-600/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-purple-400">3</span>
            </div>
            <h4 className="text-white font-medium mb-2">Daromad Oling</h4>
            <p className="text-slate-400 text-sm">Ularning to'lovlaridan 10% komissiya oling</p>
          </div>
        </div>
      </div>

      {/* Referrals List */}
      {stats && stats.referrals.length > 0 && (
        <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
          <h3 className="text-xl font-bold text-white mb-4">So'nggi Referrallar</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Foydalanuvchi</th>
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Status</th>
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Komissiya</th>
                  <th className="text-left py-3 px-4 text-slate-400 font-medium">Sana</th>
                </tr>
              </thead>
              <tbody>
                {stats.referrals.map((referral) => (
                  <tr key={referral.id} className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors">
                    <td className="py-3 px-4 text-white">{referral.referred_user_email}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        referral.status === 'active'
                          ? 'bg-green-500/20 text-green-400'
                          : 'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {referral.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-green-400 font-medium">${referral.commission_earned.toFixed(2)}</td>
                    <td className="py-3 px-4 text-slate-400">
                      {new Date(referral.created_at).toLocaleDateString('uz-UZ')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
