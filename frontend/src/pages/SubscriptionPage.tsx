import { useEffect, useState } from 'react';
import { CheckIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface Plan {
  id: string;
  name: string;
  display_name: string;
  description: string;
  price_monthly: number;
  price_yearly: number;
  features: string[];
  limits: {
    positions: number;
    api_calls: number;
    copy_traders: number;
  };
  popular?: boolean;
}

export default function SubscriptionPage() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [billing, setBilling] = useState<'monthly' | 'yearly'>('monthly');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPlans();
  }, []);

  async function loadPlans() {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/subscription-manage`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ action: 'get_plans' })
        }
      );
      const data = await response.json();
      setPlans(data.plans || []);
    } catch (error) {
      console.error('Error loading plans:', error);
    } finally {
      setLoading(false);
    }
  }

  async function subscribe(planId: string) {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/subscription-manage`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            action: 'subscribe',
            plan_id: planId,
            billing_cycle: billing
          })
        }
      );
      const data = await response.json();
      if (data.success) {
        alert('Obuna muvaffaqiyatli faollashtirildi!');
      }
    } catch (error) {
      console.error('Error subscribing:', error);
      alert('Xatolik yuz berdi');
    }
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
      <div className="text-center">
        <h2 className="text-4xl font-bold text-white mb-3">Obuna Rejalari</h2>
        <p className="text-slate-400 text-lg mb-6">
          Sizga mos rejani tanlang va professional trading boshilang
        </p>

        {/* Billing Toggle */}
        <div className="inline-flex items-center bg-slate-800 rounded-lg p-1">
          <button
            onClick={() => setBilling('monthly')}
            className={`px-6 py-2 rounded-md font-medium transition-colors ${
              billing === 'monthly'
                ? 'bg-blue-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Oylik
          </button>
          <button
            onClick={() => setBilling('yearly')}
            className={`px-6 py-2 rounded-md font-medium transition-colors ${
              billing === 'yearly'
                ? 'bg-blue-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Yillik
            <span className="ml-2 px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded">
              20% chegirma
            </span>
          </button>
        </div>
      </div>

      {/* Plans Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-7xl mx-auto">
        {plans.map((plan) => {
          const price = billing === 'monthly' ? plan.price_monthly : plan.price_yearly;
          const pricePerMonth = billing === 'yearly' ? price / 12 : price;

          return (
            <div
              key={plan.id}
              className={`relative bg-slate-800/50 backdrop-blur-xl rounded-2xl border-2 p-8 ${
                plan.popular
                  ? 'border-blue-500 shadow-xl shadow-blue-500/20'
                  : 'border-slate-700'
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="px-4 py-1 bg-blue-600 text-white text-sm font-medium rounded-full">
                    Mashhur
                  </span>
                </div>
              )}

              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold text-white mb-2">{plan.display_name}</h3>
                <p className="text-slate-400 mb-4">{plan.description}</p>
                <div className="text-5xl font-bold text-white mb-2">
                  ${price.toFixed(0)}
                  {price > 0 && (
                    <span className="text-lg text-slate-400 font-normal">
                      /{billing === 'monthly' ? 'oy' : 'yil'}
                    </span>
                  )}
                </div>
                {billing === 'yearly' && price > 0 && (
                  <p className="text-slate-400 text-sm">
                    ${pricePerMonth.toFixed(2)}/oy
                  </p>
                )}
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <CheckIcon className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    <span className="text-slate-300">{feature}</span>
                  </li>
                ))}
              </ul>

              <div className="border-t border-slate-700 pt-6 mb-6">
                <p className="text-slate-400 text-sm mb-2">Limitlar:</p>
                <ul className="space-y-2">
                  <li className="flex justify-between text-sm">
                    <span className="text-slate-400">Pozitsiyalar:</span>
                    <span className="text-white font-medium">
                      {plan.limits.positions === -1 ? 'Cheksiz' : plan.limits.positions}
                    </span>
                  </li>
                  <li className="flex justify-between text-sm">
                    <span className="text-slate-400">API Chaqiruvlar:</span>
                    <span className="text-white font-medium">
                      {plan.limits.api_calls === -1 ? 'Cheksiz' : plan.limits.api_calls.toLocaleString()}
                    </span>
                  </li>
                  <li className="flex justify-between text-sm">
                    <span className="text-slate-400">Copy Treyderlar:</span>
                    <span className="text-white font-medium">
                      {plan.limits.copy_traders === -1 ? 'Cheksiz' : plan.limits.copy_traders || 'Yo\'q'}
                    </span>
                  </li>
                </ul>
              </div>

              <button
                onClick={() => subscribe(plan.id)}
                className={`w-full py-3 rounded-lg font-medium transition-colors ${
                  plan.popular
                    ? 'bg-blue-600 hover:bg-blue-700 text-white'
                    : 'bg-slate-700 hover:bg-slate-600 text-white'
                }`}
              >
                {price === 0 ? 'Boshlanish' : 'Obuna bolish'}
              </button>
            </div>
          );
        })}
      </div>

      {/* FAQ Section */}
      <div className="mt-12 bg-slate-800/30 rounded-xl p-8 max-w-4xl mx-auto">
        <h3 className="text-2xl font-bold text-white mb-6 text-center">Tez-tez So'raladigan Savollar</h3>
        <div className="space-y-4">
          <div>
            <h4 className="text-white font-medium mb-2">Obunani bekor qilsam nima bo'ladi?</h4>
            <p className="text-slate-400 text-sm">
              Obunani istalgan vaqt bekor qilishingiz mumkin. Obuna davri tugaguncha barcha xususiyatlardan foydalanasiz.
            </p>
          </div>
          <div>
            <h4 className="text-white font-medium mb-2">To'lov usullari qanday?</h4>
            <p className="text-slate-400 text-sm">
              Biz kredit karta, PayPal va cryptocurrency (BTC, ETH, USDT) orqali to'lovni qabul qilamiz.
            </p>
          </div>
          <div>
            <h4 className="text-white font-medium mb-2">Rejani o'zgartirish mumkinmi?</h4>
            <p className="text-slate-400 text-sm">
              Ha, istalgan vaqt rejangizni yangilashingiz yoki pasaytirishingiz mumkin.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
