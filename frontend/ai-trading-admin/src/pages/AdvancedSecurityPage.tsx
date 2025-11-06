import { useState, useEffect } from 'react';
import { Shield, Lock, Smartphone, Globe, AlertCircle, CheckCircle } from 'lucide-react';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';

export default function AdvancedSecurityPage() {
  const { user } = useAuth();
  const [securityScore, setSecurityScore] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadSecurityScore();
  }, [user]);

  const loadSecurityScore = async () => {
    if (!user) return;

    setLoading(true);
    try {
      const { data, error } = await supabase.functions.invoke('advanced-security', {
        method: 'GET',
        body: { user_id: user.id, action: 'security-score' },
      });

      if (error) throw error;
      setSecurityScore(data);
    } catch (error) {
      console.error('Xatolik:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-red-900 to-slate-900 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
          <Shield className="w-10 h-10 text-red-400" />
          Advanced Security
        </h1>
        <p className="text-slate-400">Kengaytirilgan xavfsizlik sozlamalari va monitoring</p>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <Shield className="w-12 h-12 text-red-400 animate-pulse mx-auto mb-4" />
          <p className="text-slate-400">Yuklanmoqda...</p>
        </div>
      ) : securityScore ? (
        <div className="space-y-6">
          {/* Security Score */}
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">Xavfsizlik darajasi</h2>
            <div className="flex items-center gap-8">
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-400">Ball</span>
                  <span className={`text-2xl font-bold ${securityScore.color === 'green' ? 'text-green-400' : securityScore.color === 'blue' ? 'text-blue-400' : securityScore.color === 'yellow' ? 'text-yellow-400' : 'text-red-400'}`}>
                    {securityScore.score}/{securityScore.maxScore}
                  </span>
                </div>
                <div className="relative h-4 bg-slate-700/50 rounded-full overflow-hidden">
                  <div
                    className={`absolute h-full transition-all ${securityScore.color === 'green' ? 'bg-green-500' : securityScore.color === 'blue' ? 'bg-blue-500' : securityScore.color === 'yellow' ? 'bg-yellow-500' : 'bg-red-500'}`}
                    style={{ width: `${(securityScore.score / securityScore.maxScore) * 100}%` }}
                  />
                </div>
                <p className={`mt-2 font-semibold ${securityScore.color === 'green' ? 'text-green-400' : securityScore.color === 'blue' ? 'text-blue-400' : securityScore.color === 'yellow' ? 'text-yellow-400' : 'text-red-400'}`}>
                  {securityScore.level}
                </p>
              </div>
            </div>
          </div>

          {/* Security Factors */}
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
            <h3 className="text-xl font-bold text-white mb-4">Xavfsizlik omillari</h3>
            <div className="space-y-3">
              {securityScore.factors.map((factor: any, index: number) => (
                <div key={index} className={`flex items-start gap-3 p-4 rounded-lg ${factor.status === 'good' ? 'bg-green-500/10 border border-green-500/30' : factor.status === 'warning' ? 'bg-yellow-500/10 border border-yellow-500/30' : 'bg-red-500/10 border border-red-500/30'}`}>
                  {factor.status === 'good' ? (
                    <CheckCircle className="w-5 h-5 text-green-400 mt-0.5" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-yellow-400 mt-0.5" />
                  )}
                  <div className="flex-1">
                    <p className="text-white font-medium">{factor.name}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-sm text-slate-400">Ball: {factor.points}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          {securityScore.recommendations && securityScore.recommendations.length > 0 && (
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <AlertCircle className="w-6 h-6 text-blue-400" />
                Tavsiyalar
              </h3>
              <ul className="space-y-2">
                {securityScore.recommendations.map((rec: string, index: number) => (
                  <li key={index} className="text-slate-300 flex items-start gap-2">
                    <span className="text-blue-400 mt-1">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Security Features */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* 2FA */}
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6 hover:border-red-500/50 transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-red-500/20 rounded-lg">
                  <Lock className="w-6 h-6 text-red-400" />
                </div>
                <h3 className="text-lg font-bold text-white">Ikki faktorli autentifikatsiya</h3>
              </div>
              <p className="text-slate-400 text-sm mb-4">
                Hisobingizni qo'shimcha himoya qatlami bilan mustahkamlang
              </p>
              <button className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-all">
                Boshqarish
              </button>
            </div>

            {/* IP Whitelist */}
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6 hover:border-red-500/50 transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-blue-500/20 rounded-lg">
                  <Globe className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="text-lg font-bold text-white">IP Whitelist</h3>
              </div>
              <p className="text-slate-400 text-sm mb-4">
                Faqat ishonchli IP manzillardan kirishga ruxsat bering
              </p>
              <button className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all">
                Sozlash
              </button>
            </div>

            {/* Device Management */}
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6 hover:border-red-500/50 transition-all">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-green-500/20 rounded-lg">
                  <Smartphone className="w-6 h-6 text-green-400" />
                </div>
                <h3 className="text-lg font-bold text-white">Qurilmalar boshqaruvi</h3>
              </div>
              <p className="text-slate-400 text-sm mb-4">
                Hisobingizga ulangan qurilmalarni ko'ring va boshqaring
              </p>
              <button className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-all">
                Ko'rish
              </button>
            </div>
          </div>

          {/* Security Tips */}
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
            <h3 className="text-xl font-bold text-white mb-4">Xavfsizlik maslahatlari</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-start gap-3">
                <Shield className="w-5 h-5 text-red-400 mt-0.5" />
                <div>
                  <p className="text-white font-medium mb-1">Kuchli parol ishlating</p>
                  <p className="text-slate-400 text-sm">Kamida 12 ta belgi, harflar, raqamlar va maxsus belgilar</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Shield className="w-5 h-5 text-red-400 mt-0.5" />
                <div>
                  <p className="text-white font-medium mb-1">2FA faollashtiring</p>
                  <p className="text-slate-400 text-sm">Qo'shimcha xavfsizlik qatlami hisobingizni himoya qiladi</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Shield className="w-5 h-5 text-red-400 mt-0.5" />
                <div>
                  <p className="text-white font-medium mb-1">Shubhali faollikni monitoring qiling</p>
                  <p className="text-slate-400 text-sm">Hisobingizga kirish tarixini muntazam tekshiring</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Shield className="w-5 h-5 text-red-400 mt-0.5" />
                <div>
                  <p className="text-white font-medium mb-1">Yechib olish manzillarini cheklang</p>
                  <p className="text-slate-400 text-sm">Faqat tasdiqlangan manzillarga pul yechish imkonini bering</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-12">
          <Shield className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400">Ma'lumot yuklanmadi</p>
          <button
            onClick={loadSecurityScore}
            className="mt-4 px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-all"
          >
            Qayta yuklash
          </button>
        </div>
      )}
    </div>
  );
}
