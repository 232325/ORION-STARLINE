import { useState, useEffect } from 'react';
import { FileCheck, Upload, CheckCircle, XCircle, Clock, AlertTriangle } from 'lucide-react';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';

interface KYCData {
  id: string;
  verification_status: string;
  full_name: string;
  date_of_birth: string;
  nationality: string;
  document_type: string;
  face_match_score: number;
  risk_score: number;
  verified_at: string | null;
  created_at: string;
}

export default function KYCPage() {
  const { user } = useAuth();
  const [kycData, setKycData] = useState<KYCData | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    full_name: '',
    date_of_birth: '',
    nationality: 'UZ',
    address: '',
    document_type: 'passport' as 'passport' | 'id_card' | 'drivers_license',
    document_number: '',
  });

  const [files, setFiles] = useState({
    document_front: null as File | null,
    document_back: null as File | null,
    selfie: null as File | null,
  });

  useEffect(() => {
    loadKYCStatus();
  }, [user]);

  const loadKYCStatus = async () => {
    if (!user) return;

    setLoading(true);
    try {
      const { data, error } = await supabase.functions.invoke('kyc-aml-verification', {
        method: 'GET',
        body: { user_id: user.id },
      });

      if (error) throw error;
      if (data.kyc) setKycData(data.kyc);
    } catch (error) {
      console.error('Xatolik:', error);
    } finally {
      setLoading(false);
    }
  };

  const submitKYC = async () => {
    if (!user) return;

    // Validatsiya
    if (!formData.full_name || !formData.date_of_birth || !formData.document_number) {
      alert('Barcha majburiy maydonlarni to\'ldiring');
      return;
    }

    if (!files.document_front || !files.selfie) {
      alert('Hujjat rasmi va selfie yuklang');
      return;
    }

    setSubmitting(true);
    try {
      // Fayllarni yuklash (mock - real implementation Supabase Storage)
      const documentFrontUrl = 'https://example.com/doc_front_' + Date.now() + '.jpg';
      const documentBackUrl = files.document_back
        ? 'https://example.com/doc_back_' + Date.now() + '.jpg'
        : undefined;
      const selfieUrl = 'https://example.com/selfie_' + Date.now() + '.jpg';

      // KYC ma'lumotlarini yuborish
      const { data, error } = await supabase.functions.invoke('kyc-aml-verification', {
        body: {
          user_id: user.id,
          ...formData,
          document_front_url: documentFrontUrl,
          document_back_url: documentBackUrl,
          selfie_url: selfieUrl,
        },
      });

      if (error) throw error;

      alert(data.message);
      setKycData(data.kyc);
    } catch (error) {
      console.error('Xatolik:', error);
      alert('KYC yuborishda xatolik yuz berdi');
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'text-green-400';
      case 'pending': return 'text-yellow-400';
      case 'rejected': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved': return <CheckCircle className="w-6 h-6 text-green-400" />;
      case 'pending': return <Clock className="w-6 h-6 text-yellow-400" />;
      case 'rejected': return <XCircle className="w-6 h-6 text-red-400" />;
      default: return <AlertTriangle className="w-6 h-6 text-slate-400" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-emerald-900 to-slate-900 p-6 flex items-center justify-center">
        <div className="text-center">
          <FileCheck className="w-12 h-12 text-emerald-400 animate-pulse mx-auto mb-4" />
          <p className="text-slate-400">Yuklanmoqda...</p>
        </div>
      </div>
    );
  }

  if (kycData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-emerald-900 to-slate-900 p-6">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-4xl font-bold text-white mb-8 flex items-center gap-3">
            <FileCheck className="w-10 h-10 text-emerald-400" />
            KYC Verifikatsiya
          </h1>

          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl p-8">
            {/* Status */}
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-slate-900/50 mb-4">
                {getStatusIcon(kycData.verification_status)}
              </div>
              <h2 className={`text-3xl font-bold ${getStatusColor(kycData.verification_status)} mb-2`}>
                {kycData.verification_status === 'approved' ? 'Tasdiqlangan' :
                 kycData.verification_status === 'pending' ? 'Tekshirilmoqda' :
                 kycData.verification_status === 'rejected' ? 'Rad etildi' : 'Noma\'lum'}
              </h2>
              <p className="text-slate-400">
                {kycData.verified_at
                  ? `Tasdiqlangan: ${new Date(kycData.verified_at).toLocaleDateString('uz')}`
                  : `Yuborilgan: ${new Date(kycData.created_at).toLocaleDateString('uz')}`}
              </p>
            </div>

            {/* Info */}
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-slate-900/50 rounded-lg">
                  <p className="text-slate-400 text-sm mb-1">To'liq ism</p>
                  <p className="text-white font-semibold">{kycData.full_name}</p>
                </div>
                <div className="p-4 bg-slate-900/50 rounded-lg">
                  <p className="text-slate-400 text-sm mb-1">Tug'ilgan sana</p>
                  <p className="text-white font-semibold">{kycData.date_of_birth}</p>
                </div>
                <div className="p-4 bg-slate-900/50 rounded-lg">
                  <p className="text-slate-400 text-sm mb-1">Millat</p>
                  <p className="text-white font-semibold">{kycData.nationality}</p>
                </div>
                <div className="p-4 bg-slate-900/50 rounded-lg">
                  <p className="text-slate-400 text-sm mb-1">Hujjat turi</p>
                  <p className="text-white font-semibold">{kycData.document_type}</p>
                </div>
              </div>

              {/* Scores */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                  <p className="text-slate-400 text-sm mb-1">Yuz taqqoslash</p>
                  <p className="text-blue-400 font-bold text-2xl">{kycData.face_match_score}%</p>
                </div>
                <div className="p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                  <p className="text-slate-400 text-sm mb-1">Risk darajasi</p>
                  <p className="text-purple-400 font-bold text-2xl">{kycData.risk_score}</p>
                </div>
              </div>
            </div>

            {kycData.verification_status === 'pending' && (
              <div className="mt-6 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                <p className="text-yellow-400 text-sm">
                  ⏳ Ma'lumotlaringiz tekshirilmoqda. Bu 24-48 soat davom etishi mumkin.
                </p>
              </div>
            )}

            {kycData.verification_status === 'rejected' && (
              <div className="mt-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                <p className="text-red-400 text-sm">
                  ❌ KYC rad etildi. Iltimos, to'g'ri ma'lumotlar bilan qaytadan urinib ko'ring.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-emerald-900 to-slate-900 p-6">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
          <FileCheck className="w-10 h-10 text-emerald-400" />
          KYC Verifikatsiya
        </h1>
        <p className="text-slate-400 mb-8">Identifikatsiyangizni tasdiqlang</p>

        <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-2xl p-8">
          <div className="space-y-6">
            {/* Personal Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-slate-300 mb-2">To'liq ism *</label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                  placeholder="Ism Familiya"
                />
              </div>

              <div>
                <label className="block text-slate-300 mb-2">Tug'ilgan sana *</label>
                <input
                  type="date"
                  value={formData.date_of_birth}
                  onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 mb-2">Millat *</label>
                <select
                  value={formData.nationality}
                  onChange={(e) => setFormData({ ...formData, nationality: e.target.value })}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="UZ">O'zbekiston</option>
                  <option value="RU">Rossiya</option>
                  <option value="US">AQSh</option>
                  <option value="GB">Buyuk Britaniya</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-300 mb-2">Hujjat turi *</label>
                <select
                  value={formData.document_type}
                  onChange={(e) => setFormData({ ...formData, document_type: e.target.value as any })}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="passport">Pasport</option>
                  <option value="id_card">ID karta</option>
                  <option value="drivers_license">Haydovchilik guvohnomasi</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-slate-300 mb-2">Manzil</label>
              <input
                type="text"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                placeholder="To'liq manzil"
              />
            </div>

            <div>
              <label className="block text-slate-300 mb-2">Hujjat raqami *</label>
              <input
                type="text"
                value={formData.document_number}
                onChange={(e) => setFormData({ ...formData, document_number: e.target.value })}
                className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-emerald-500"
                placeholder="AA1234567"
              />
            </div>

            {/* File Uploads */}
            <div className="space-y-4">
              <div className="p-4 border-2 border-dashed border-slate-700 rounded-lg hover:border-emerald-500 transition-all">
                <label className="block cursor-pointer">
                  <div className="flex items-center gap-3 mb-2">
                    <Upload className="w-5 h-5 text-emerald-400" />
                    <span className="text-slate-300">Hujjat (old tomon) *</span>
                  </div>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => setFiles({ ...files, document_front: e.target.files?.[0] || null })}
                    className="hidden"
                  />
                  <p className="text-slate-500 text-sm">
                    {files.document_front ? files.document_front.name : 'Rasm yuklang'}
                  </p>
                </label>
              </div>

              <div className="p-4 border-2 border-dashed border-slate-700 rounded-lg hover:border-emerald-500 transition-all">
                <label className="block cursor-pointer">
                  <div className="flex items-center gap-3 mb-2">
                    <Upload className="w-5 h-5 text-emerald-400" />
                    <span className="text-slate-300">Hujjat (orqa tomon)</span>
                  </div>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => setFiles({ ...files, document_back: e.target.files?.[0] || null })}
                    className="hidden"
                  />
                  <p className="text-slate-500 text-sm">
                    {files.document_back ? files.document_back.name : 'Rasm yuklang (opsional)'}
                  </p>
                </label>
              </div>

              <div className="p-4 border-2 border-dashed border-slate-700 rounded-lg hover:border-emerald-500 transition-all">
                <label className="block cursor-pointer">
                  <div className="flex items-center gap-3 mb-2">
                    <Upload className="w-5 h-5 text-emerald-400" />
                    <span className="text-slate-300">Selfie *</span>
                  </div>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => setFiles({ ...files, selfie: e.target.files?.[0] || null })}
                    className="hidden"
                  />
                  <p className="text-slate-500 text-sm">
                    {files.selfie ? files.selfie.name : 'Yuzingiz bilan rasm yuklang'}
                  </p>
                </label>
              </div>
            </div>

            <button
              onClick={submitKYC}
              disabled={submitting}
              className="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-bold transition-all disabled:opacity-50"
            >
              {submitting ? 'Yuborilmoqda...' : 'Yuborish'}
            </button>

            <p className="text-slate-500 text-sm text-center">
              * Ma'lumotlaringiz xavfsiz saqlashadi va faqat verifikatsiya uchun ishlatiladi
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
