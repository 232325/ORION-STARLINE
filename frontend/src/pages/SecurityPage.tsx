import { useState, useEffect } from 'react';
import { ShieldCheckIcon, KeyIcon, DocumentDuplicateIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';

export default function SecurityPage() {
  const { user } = useAuth();
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);
  const [showSetup, setShowSetup] = useState(false);
  const [qrCodeUrl, setQrCodeUrl] = useState('');
  const [secret, setSecret] = useState('');
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [verificationCode, setVerificationCode] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    check2FAStatus();
  }, []);

  async function check2FAStatus() {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/two-factor-auth`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ action: 'status' })
        }
      );
      const data = await response.json();
      setTwoFactorEnabled(data.enabled || false);
    } catch (error) {
      console.error('Error checking 2FA status:', error);
    }
  }

  async function setup2FA() {
    setLoading(true);
    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/two-factor-auth`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ action: 'setup' })
        }
      );
      const data = await response.json();
      
      if (data.success) {
        setQrCodeUrl(data.qr_code_url);
        setSecret(data.secret);
        setBackupCodes(data.backup_codes);
        setShowSetup(true);
      }
    } catch (error) {
      console.error('Error setting up 2FA:', error);
      alert('Xatolik yuz berdi');
    } finally {
      setLoading(false);
    }
  }

  async function verify2FA() {
    if (!verificationCode || verificationCode.length !== 6) {
      alert('6 raqamli kodni kiriting');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/two-factor-auth`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            action: 'verify',
            token: verificationCode
          })
        }
      );
      const data = await response.json();
      
      if (data.verified) {
        setTwoFactorEnabled(true);
        setShowSetup(false);
        alert('2FA muvaffaqiyatli faollashtirildi!');
      } else {
        alert('Noto\'g\'ri kod');
      }
    } catch (error) {
      console.error('Error verifying 2FA:', error);
      alert('Xatolik yuz berdi');
    } finally {
      setLoading(false);
    }
  }

  async function disable2FA() {
    if (!confirm('2FA ni o\'chirishni xohlaysizmi?')) return;

    setLoading(true);
    try {
      await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/two-factor-auth`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ action: 'disable' })
        }
      );
      setTwoFactorEnabled(false);
      alert('2FA o\'chirildi');
    } catch (error) {
      console.error('Error disabling 2FA:', error);
      alert('Xatolik yuz berdi');
    } finally {
      setLoading(false);
    }
  }

  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text);
    alert('Nusxalandi!');
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">Xavfsizlik Sozlamalari</h2>
        <p className="text-slate-400">Hisobingizni himoya qiling</p>
      </div>

      {/* 2FA Status Card */}
      <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            <div className={`p-4 rounded-lg ${twoFactorEnabled ? 'bg-green-600/20' : 'bg-slate-700'}`}>
              <ShieldCheckIcon className={`w-8 h-8 ${twoFactorEnabled ? 'text-green-400' : 'text-slate-400'}`} />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white mb-2">Ikki Faktorli Autentifikatsiya (2FA)</h3>
              <p className="text-slate-400 mb-4">
                {twoFactorEnabled 
                  ? 'Hisobingiz 2FA bilan himoyalangan' 
                  : 'Hisobingizga qo\'shimcha xavfsizlik qavati qo\'shing'}
              </p>
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                twoFactorEnabled
                  ? 'bg-green-500/20 text-green-400'
                  : 'bg-red-500/20 text-red-400'
              }`}>
                {twoFactorEnabled ? 'Faol' : 'Faol emas'}
              </div>
            </div>
          </div>
          {!twoFactorEnabled ? (
            <button
              onClick={setup2FA}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              {loading ? 'Yuklanmoqda...' : 'Faollashtirish'}
            </button>
          ) : (
            <button
              onClick={disable2FA}
              disabled={loading}
              className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              {loading ? 'Yuklanmoqda...' : 'O\'chirish'}
            </button>
          )}
        </div>
      </div>

      {/* Setup Modal */}
      {showSetup && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-800 rounded-2xl max-w-2xl w-full p-8 border border-slate-700">
            <h3 className="text-2xl font-bold text-white mb-6">2FA Sozlash</h3>

            <div className="space-y-6">
              {/* Step 1: QR Code */}
              <div>
                <h4 className="text-lg font-medium text-white mb-3">1. Authenticator ilovasini ishga tushiring</h4>
                <p className="text-slate-400 mb-4">
                  Google Authenticator, Authy yoki boshqa TOTP ilova ishlatishingiz mumkin
                </p>
              </div>

              {/* QR Code Display */}
              <div className="bg-slate-900 rounded-lg p-6">
                <div className="flex flex-col items-center">
                  <div className="bg-white p-4 rounded-lg mb-4">
                    <img
                      src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(qrCodeUrl)}`}
                      alt="2FA QR Code"
                      className="w-48 h-48"
                    />
                  </div>
                  <p className="text-slate-400 text-sm mb-2">Yoki qo'lda kiriting:</p>
                  <div className="flex items-center gap-2">
                    <code className="bg-slate-800 px-4 py-2 rounded text-white font-mono text-sm">
                      {secret}
                    </code>
                    <button
                      onClick={() => copyToClipboard(secret)}
                      className="p-2 hover:bg-slate-700 rounded transition-colors"
                    >
                      <DocumentDuplicateIcon className="w-5 h-5 text-slate-400" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Step 2: Verify */}
              <div>
                <h4 className="text-lg font-medium text-white mb-3">2. Kodni kiriting</h4>
                <div className="flex gap-3">
                  <input
                    type="text"
                    value={verificationCode}
                    onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    placeholder="6 raqamli kod"
                    maxLength={6}
                    className="flex-1 bg-slate-900 text-white px-4 py-3 rounded-lg border border-slate-700 focus:border-blue-500 outline-none text-center text-2xl font-mono tracking-wider"
                  />
                  <button
                    onClick={verify2FA}
                    disabled={loading || verificationCode.length !== 6}
                    className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
                  >
                    {loading ? 'Tekshirilmoqda...' : 'Tasdiqlash'}
                  </button>
                </div>
              </div>

              {/* Backup Codes */}
              {backupCodes.length > 0 && (
                <div>
                  <h4 className="text-lg font-medium text-white mb-3">3. Zaxira kodlarni saqlang</h4>
                  <p className="text-slate-400 mb-3 text-sm">
                    Agar ilova yo'qolsa, bu kodlar bilan kirishingiz mumkin. Har bir kod faqat bir marta ishlatiladi.
                  </p>
                  <div className="bg-slate-900 rounded-lg p-4">
                    <div className="grid grid-cols-2 gap-2">
                      {backupCodes.map((code, index) => (
                        <div key={index} className="flex items-center justify-between bg-slate-800 px-3 py-2 rounded">
                          <code className="text-white font-mono text-sm">{code}</code>
                          <button
                            onClick={() => copyToClipboard(code)}
                            className="ml-2 p-1 hover:bg-slate-700 rounded"
                          >
                            <DocumentDuplicateIcon className="w-4 h-4 text-slate-400" />
                          </button>
                        </div>
                      ))}
                    </div>
                    <button
                      onClick={() => {
                        const allCodes = backupCodes.join('\n');
                        copyToClipboard(allCodes);
                      }}
                      className="mt-3 w-full py-2 bg-slate-700 hover:bg-slate-600 text-white rounded text-sm transition-colors"
                    >
                      Barcha kodlarni nusxalash
                    </button>
                  </div>
                </div>
              )}

              <button
                onClick={() => setShowSetup(false)}
                className="w-full py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
              >
                Yopish
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Other Security Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-blue-600/20 rounded-lg">
              <KeyIcon className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white mb-2">Parol O'zgartirish</h3>
              <p className="text-slate-400 text-sm mb-4">
                Kuchli parol ishlatishingizni tavsiya etamiz
              </p>
              <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm transition-colors">
                Parolni o'zgartirish
              </button>
            </div>
          </div>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-purple-600/20 rounded-lg">
              <ShieldCheckIcon className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white mb-2">Faol Sessiyalar</h3>
              <p className="text-slate-400 text-sm mb-4">
                Barcha qurilmalardagi faol sessiyalarni ko'ring
              </p>
              <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm transition-colors">
                Sessiyalarni ko'rish
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
