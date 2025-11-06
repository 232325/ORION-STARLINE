import { useState, useEffect } from 'react';
import { Wallet, Bitcoin, QrCode, Clock, CheckCircle, XCircle } from 'lucide-react';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';

interface Payment {
  id: string;
  currency: string;
  amount: number;
  usd_amount: number;
  payment_address: string;
  status: string;
  transaction_hash: string | null;
  created_at: string;
  expires_at: string;
}

export default function CryptoPaymentPage() {
  const { user } = useAuth();
  const [payments, setPayments] = useState<Payment[]>([]);
  const [currencies, setCurrencies] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  
  const [formData, setFormData] = useState({
    currency: 'BTC',
    amount: 0.001,
    purpose: 'deposit',
  });

  const [activePayment, setActivePayment] = useState<any>(null);

  useEffect(() => {
    loadCurrencies();
    loadPayments();
  }, [user]);

  const loadCurrencies = async () => {
    try {
      const { data, error } = await supabase.functions.invoke('crypto-payment-gateway', {
        method: 'GET',
        body: { action: 'supported-currencies' },
      });

      if (error) throw error;
      setCurrencies(data.currencies || []);
    } catch (error) {
      console.error('Xatolik:', error);
    }
  };

  const loadPayments = async () => {
    if (!user) return;

    setLoading(true);
    try {
      const { data, error } = await supabase.functions.invoke('crypto-payment-gateway', {
        method: 'POST',
        body: { user_id: user.id, action: 'payment-history' },
      });

      if (error) throw error;
      setPayments(data.payments || []);
    } catch (error) {
      console.error('Xatolik:', error);
    } finally {
      setLoading(false);
    }
  };

  const createPayment = async () => {
    if (!user) return;

    setCreating(true);
    try {
      const { data, error } = await supabase.functions.invoke('crypto-payment-gateway', {
        body: {
          user_id: user.id,
          ...formData,
          action: 'create-payment',
        },
      });

      if (error) throw error;
      setActivePayment(data.payment);
      loadPayments();
    } catch (error) {
      console.error('Xatolik:', error);
    } finally {
      setCreating(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-400" />;
      case 'expired':
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-400" />;
      default:
        return <Clock className="w-5 h-5 text-slate-400" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-yellow-900 to-slate-900 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
          <Bitcoin className="w-10 h-10 text-yellow-400" />
          Crypto Payment Gateway
        </h1>
        <p className="text-slate-400">Kripto valyuta to'lovlari</p>
      </div>

      {/* Create Payment */}
      {!activePayment && (
        <div className="mb-8 max-w-3xl mx-auto">
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">Yangi to'lov yaratish</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <label className="block text-slate-400 mb-2">Kripto valyuta</label>
                <select
                  value={formData.currency}
                  onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-yellow-500"
                >
                  {currencies.map(c => (
                    <option key={c.symbol} value={c.symbol}>{c.name} ({c.symbol})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-400 mb-2">Miqdor</label>
                <input
                  type="number"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: Number(e.target.value) })}
                  step="0.001"
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-yellow-500"
                />
              </div>
            </div>

            <button
              onClick={createPayment}
              disabled={creating}
              className="w-full py-4 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg font-bold transition-all disabled:opacity-50"
            >
              {creating ? 'Yaratilmoqda...' : 'To\'lov yaratish'}
            </button>
          </div>
        </div>
      )}

      {/* Active Payment */}
      {activePayment && (
        <div className="mb-8 max-w-3xl mx-auto">
          <div className="bg-slate-800/50 backdrop-blur border border-yellow-500/50 rounded-2xl p-8">
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-white mb-2">To'lov kutilmoqda</h2>
              <p className="text-slate-400">Quyidagi manzilga {activePayment.amount} {activePayment.currency} yuboring</p>
            </div>

            {/* QR Code */}
            <div className="flex justify-center mb-6">
              <img
                src={activePayment.qr_code_url}
                alt="QR Code"
                className="w-64 h-64 bg-white p-4 rounded-xl"
              />
            </div>

            {/* Payment Address */}
            <div className="mb-6">
              <label className="block text-slate-400 text-sm mb-2">To'lov manzili</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={activePayment.payment_address}
                  readOnly
                  className="flex-1 px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white font-mono"
                />
                <button
                  onClick={() => navigator.clipboard.writeText(activePayment.payment_address)}
                  className="px-6 py-3 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-all"
                >
                  Nusxalash
                </button>
              </div>
            </div>

            {/* Instructions */}
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 mb-6">
              <h3 className="text-white font-semibold mb-2">Ko'rsatmalar:</h3>
              <ol className="space-y-1 text-slate-300 text-sm list-decimal list-inside">
                {activePayment.instructions?.map((inst: string, i: number) => (
                  <li key={i}>{inst}</li>
                ))}
              </ol>
            </div>

            {/* Timer */}
            <div className="text-center">
              <p className="text-slate-400 text-sm">
                Amal qilish muddati: {new Date(activePayment.expires_at).toLocaleTimeString('uz')}
              </p>
            </div>

            <button
              onClick={() => setActivePayment(null)}
              className="w-full mt-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-all"
            >
              Yopish
            </button>
          </div>
        </div>
      )}

      {/* Payment History */}
      <div className="max-w-7xl mx-auto">
        <h2 className="text-2xl font-bold text-white mb-6">To'lovlar tarixi</h2>
        
        {loading ? (
          <div className="text-center py-12">
            <Wallet className="w-12 h-12 text-yellow-400 animate-pulse mx-auto mb-4" />
            <p className="text-slate-400">Yuklanmoqda...</p>
          </div>
        ) : payments.length === 0 ? (
          <div className="text-center py-12 bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl">
            <Wallet className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">Hozircha to'lovlar yo'q</p>
          </div>
        ) : (
          <div className="space-y-3">
            {payments.map(payment => (
              <div
                key={payment.id}
                className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6 hover:border-yellow-500/50 transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="p-3 bg-yellow-500/20 rounded-lg">
                      {getStatusBadge(payment.status)}
                    </div>

                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-white font-bold text-lg">{payment.amount} {payment.currency}</h3>
                        <span className={`px-3 py-1 rounded-lg text-sm font-medium ${
                          payment.status === 'completed'
                            ? 'bg-green-500/20 text-green-400'
                            : payment.status === 'pending'
                            ? 'bg-yellow-500/20 text-yellow-400'
                            : 'bg-red-500/20 text-red-400'
                        }`}>
                          {payment.status}
                        </span>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm mb-3">
                        <div>
                          <p className="text-slate-400">USD qiymati</p>
                          <p className="text-white font-semibold">${payment.usd_amount.toFixed(2)}</p>
                        </div>
                        <div>
                          <p className="text-slate-400">Sana</p>
                          <p className="text-white">{new Date(payment.created_at).toLocaleDateString('uz')}</p>
                        </div>
                        {payment.transaction_hash && (
                          <div>
                            <p className="text-slate-400">TX Hash</p>
                            <p className="text-white font-mono text-xs truncate">{payment.transaction_hash}</p>
                          </div>
                        )}
                      </div>

                      <div className="p-3 bg-slate-900/50 rounded-lg">
                        <p className="text-slate-400 text-xs mb-1">Manzil</p>
                        <p className="text-white font-mono text-sm truncate">{payment.payment_address}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
