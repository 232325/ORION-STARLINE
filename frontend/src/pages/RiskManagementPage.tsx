import { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { 
  ShieldExclamationIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  ArrowTrendingDownIcon,
  BellAlertIcon
} from '@heroicons/react/24/outline';

interface RiskAssessment {
  portfolio_id: string;
  risk_score: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  value_at_risk: number;
  conditional_var: number;
  max_drawdown: number;
  sharpe_ratio: number;
  volatility: number;
  beta: number;
  recommendations: string[];
}

interface StressTestResult {
  scenario: string;
  impact: number;
  description: string;
  probability: number;
}

interface StopLossConfig {
  position_id: string;
  symbol: string;
  atr_multiplier: number;
  trailing_percentage: number;
  current_price: number;
  stop_loss_price: number;
}

export default function RiskManagementPage() {
  const [assessment, setAssessment] = useState<RiskAssessment | null>(null);
  const [stressTests, setStressTests] = useState<StressTestResult[]>([]);
  const [stopLosses, setStopLosses] = useState<StopLossConfig[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRiskData();
  }, []);

  const fetchRiskData = async () => {
    try {
      setLoading(true);

      // Portfolio risk assessment
      const assessmentResponse = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/risk-management-system`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`
          },
          body: JSON.stringify({
            action: 'assess_portfolio_risk',
            portfolio_id: 'user-portfolio-1',
            confidence_level: 0.95
          })
        }
      );

      const assessmentData = await assessmentResponse.json();
      if (assessmentData.data) {
        setAssessment(assessmentData.data);
      }

      // Stress testing
      const stressResponse = await fetch(
        `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/risk-management-system`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${import.meta.env.VITE_SUPABASE_ANON_KEY}`
          },
          body: JSON.stringify({
            action: 'run_stress_test',
            portfolio_id: 'user-portfolio-1',
            scenarios: ['market_crash', 'volatility_spike', 'liquidity_crisis', 'black_swan']
          })
        }
      );

      const stressData = await stressResponse.json();
      if (stressData.data) {
        setStressTests(stressData.data.scenarios);
      }

    } catch (error) {
      console.error('Risk verileri yüklenirken hata:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'text-green-400';
      case 'medium': return 'text-yellow-400';
      case 'high': return 'text-orange-400';
      case 'critical': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  const getRiskBadgeVariant = (level: string): 'success' | 'warning' | 'danger' | 'default' => {
    switch (level) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'danger';
      case 'critical': return 'danger';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-slate-700 rounded w-1/4"></div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-64 bg-slate-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <ShieldExclamationIcon className="h-8 w-8 text-orange-400" />
            Risk Yönetimi
          </h1>
          <p className="text-slate-400 mt-2">
            Portföy riski analizi ve koruma stratejileri
          </p>
        </div>
        <Button onClick={fetchRiskData} disabled={loading}>
          Yenile
        </Button>
      </div>

      {/* Risk Score Overview */}
      {assessment && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card variant="glass" className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Risk Skoru</p>
                <div className="flex items-baseline gap-2 mt-2">
                  <h3 className={`text-3xl font-bold ${getRiskColor(assessment.risk_level)}`}>
                    {assessment.risk_score.toFixed(1)}
                  </h3>
                  <span className="text-slate-500">/100</span>
                </div>
                <Badge variant={getRiskBadgeVariant(assessment.risk_level)} className="mt-2">
                  {assessment.risk_level.toUpperCase()}
                </Badge>
              </div>
              <ShieldExclamationIcon className={`h-12 w-12 ${getRiskColor(assessment.risk_level)}`} />
            </div>
          </Card>

          <Card variant="glass" className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Value at Risk (95%)</p>
                <h3 className="text-3xl font-bold text-red-400 mt-2">
                  ${assessment.value_at_risk.toFixed(2)}
                </h3>
                <p className="text-xs text-slate-500 mt-1">Potansiyel kayıp</p>
              </div>
              <ArrowTrendingDownIcon className="h-12 w-12 text-red-400" />
            </div>
          </Card>

          <Card variant="glass" className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Sharpe Ratio</p>
                <h3 className={`text-3xl font-bold mt-2 ${
                  assessment.sharpe_ratio >= 1.5 ? 'text-green-400' :
                  assessment.sharpe_ratio >= 1 ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  {assessment.sharpe_ratio.toFixed(2)}
                </h3>
                <p className="text-xs text-slate-500 mt-1">Risk/getiri oranı</p>
              </div>
              <ChartBarIcon className="h-12 w-12 text-blue-400" />
            </div>
          </Card>

          <Card variant="glass" className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Volatilite</p>
                <h3 className="text-3xl font-bold text-purple-400 mt-2">
                  {(assessment.volatility * 100).toFixed(1)}%
                </h3>
                <p className="text-xs text-slate-500 mt-1">Yıllık volatilite</p>
              </div>
              <ExclamationTriangleIcon className="h-12 w-12 text-purple-400" />
            </div>
          </Card>
        </div>
      )}

      {/* Detailed Metrics */}
      {assessment && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Risk Metrics */}
          <Card variant="glass" className="p-6">
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <ChartBarIcon className="h-6 w-6 text-blue-400" />
              Risk Metrikleri
            </h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center py-3 border-b border-slate-700">
                <span className="text-slate-400">Conditional VaR (CVaR)</span>
                <span className="text-red-400 font-semibold">
                  ${assessment.conditional_var.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-slate-700">
                <span className="text-slate-400">Maksimum Drawdown</span>
                <span className="text-orange-400 font-semibold">
                  {(assessment.max_drawdown * 100).toFixed(2)}%
                </span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-slate-700">
                <span className="text-slate-400">Beta (Piyasa Korelasyonu)</span>
                <span className="text-blue-400 font-semibold">
                  {assessment.beta.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between items-center py-3">
                <span className="text-slate-400">Risk Seviyesi</span>
                <Badge variant={getRiskBadgeVariant(assessment.risk_level)}>
                  {assessment.risk_level.toUpperCase()}
                </Badge>
              </div>
            </div>
          </Card>

          {/* Recommendations */}
          <Card variant="glass" className="p-6">
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <BellAlertIcon className="h-6 w-6 text-yellow-400" />
              Öneriler
            </h2>
            <div className="space-y-3">
              {assessment.recommendations.map((rec, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-slate-800/50 rounded-lg">
                  <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400 mt-0.5 flex-shrink-0" />
                  <p className="text-slate-300 text-sm">{rec}</p>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Stress Test Results */}
      <Card variant="glass" className="p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <ExclamationTriangleIcon className="h-6 w-6 text-red-400" />
          Stres Testi Sonuçları
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {stressTests.map((test, index) => (
            <div key={index} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-semibold text-white">{test.scenario}</h3>
                  <p className="text-xs text-slate-400 mt-1">{test.description}</p>
                </div>
                <Badge variant={test.impact > -10 ? 'warning' : 'danger'}>
                  {test.probability.toFixed(0)}% olasılık
                </Badge>
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <span className="text-sm text-slate-400">Potansiyel etki:</span>
                <span className={`text-xl font-bold ${test.impact >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {test.impact >= 0 ? '+' : ''}{test.impact.toFixed(2)}%
                </span>
              </div>
              <div className="mt-2 w-full bg-slate-700 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${test.impact >= 0 ? 'bg-green-500' : 'bg-red-500'}`}
                  style={{ width: `${Math.min(Math.abs(test.impact), 100)}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Dynamic Stop-Loss Configuration */}
      <Card variant="glass" className="p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <ShieldExclamationIcon className="h-6 w-6 text-green-400" />
          Dinamik Stop-Loss Ayarları
        </h2>
        <div className="space-y-4">
          <p className="text-slate-400 text-sm mb-4">
            ATR (Average True Range) tabanlı dinamik stop-loss seviyeleri. Pozisyonlarınız otomatik olarak korunur.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-slate-800/50 rounded-lg">
              <label className="text-sm text-slate-400">ATR Çarpanı</label>
              <input 
                type="number" 
                step="0.1"
                defaultValue="2.0"
                className="w-full mt-2 px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              />
            </div>
            <div className="p-4 bg-slate-800/50 rounded-lg">
              <label className="text-sm text-slate-400">Trailing %</label>
              <input 
                type="number" 
                step="0.5"
                defaultValue="3.0"
                className="w-full mt-2 px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              />
            </div>
            <div className="p-4 bg-slate-800/50 rounded-lg flex items-end">
              <Button className="w-full">
                Ayarları Uygula
              </Button>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
