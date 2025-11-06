import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { Web3Provider } from './contexts/Web3Context';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import PositionsPage from './pages/PositionsPage';
import StrategiesPage from './pages/StrategiesPage';
import UsersPage from './pages/UsersPage';
import MonitoringPage from './pages/MonitoringPage';
import SettingsPage from './pages/SettingsPage';
import CopyTradingPage from './pages/CopyTradingPage';
import SubscriptionPage from './pages/SubscriptionPage';
import ReferralPage from './pages/ReferralPage';
import SecurityPage from './pages/SecurityPage';
import NewsTradingPage from './pages/NewsTradingPage';
import SocialSentimentPage from './pages/SocialSentimentPage';
import RiskAnalyticsPage from './pages/RiskAnalyticsPage';
import GPTAssistantPage from './pages/GPTAssistantPage';
import VoiceCommandsPage from './pages/VoiceCommandsPage';
import AutoStrategyPage from './pages/AutoStrategyPage';
import MarketPredictionsPage from './pages/MarketPredictionsPage';
import KYCPage from './pages/KYCPage';
import AuditLogsPage from './pages/AuditLogsPage';
import AdvancedSecurityPage from './pages/AdvancedSecurityPage';
import CryptoPaymentPage from './pages/CryptoPaymentPage';
import MarketplacePage from './pages/MarketplacePage';
import DeviceSettingsPage from './pages/DeviceSettingsPage';
import MediaCapturePage from './pages/MediaCapturePage';
import SocialTradingPage from './pages/SocialTradingPage';
import RiskManagementPage from './pages/RiskManagementPage';
import DeFiTradingPage from './pages/DeFiTradingPage';
import AIMarketPredictorPage from './pages/AIMarketPredictorPage';
import AIBotsPage from './pages/AIBotsPage';
import StrategyBuilderPage from './pages/StrategyBuilderPage';
import AITradingBotsMainPage from './pages/AITradingBotsMainPage';
import MLPredictionPage from './pages/MLPredictionPage';
import DeFiDashboardPage from './pages/DeFiDashboardPage';
import DeFiBridgePage from './pages/DeFiBridgePage';
import DeFiYieldFarmingPage from './pages/DeFiYieldFarmingPage';
import DeFiArbitragePage from './pages/DeFiArbitragePage';
import DeFiWalletPage from './pages/DeFiWalletPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Yuklanmoqda...</div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="positions" element={<PositionsPage />} />
        <Route path="strategies" element={<StrategiesPage />} />
        <Route path="ai-bots" element={<AIBotsPage />} />
        <Route path="ai-trading-bots" element={<AITradingBotsMainPage />} />
        <Route path="ml-predictions" element={<MLPredictionPage />} />
        <Route path="strategy-builder" element={<StrategyBuilderPage />} />
        <Route path="social-trading" element={<SocialTradingPage />} />
        <Route path="risk-management" element={<RiskManagementPage />} />
        <Route path="defi-trading" element={<DeFiTradingPage />} />
        <Route path="defi" element={<DeFiDashboardPage />} />
        <Route path="defi/dashboard" element={<DeFiDashboardPage />} />
        <Route path="defi/bridge" element={<DeFiBridgePage />} />
        <Route path="defi/yield" element={<DeFiYieldFarmingPage />} />
        <Route path="defi/arbitrage" element={<DeFiArbitragePage />} />
        <Route path="defi/wallet" element={<DeFiWalletPage />} />
        <Route path="ai-market-predictor" element={<AIMarketPredictorPage />} />
        <Route path="copy-trading" element={<CopyTradingPage />} />
        <Route path="subscription" element={<SubscriptionPage />} />
        <Route path="referral" element={<ReferralPage />} />
        <Route path="security" element={<SecurityPage />} />
        <Route path="news-trading" element={<NewsTradingPage />} />
        <Route path="social-sentiment" element={<SocialSentimentPage />} />
        <Route path="risk-analytics" element={<RiskAnalyticsPage />} />
        <Route path="gpt-assistant" element={<GPTAssistantPage />} />
        <Route path="voice-commands" element={<VoiceCommandsPage />} />
        <Route path="auto-strategy" element={<AutoStrategyPage />} />
        <Route path="market-predictions" element={<MarketPredictionsPage />} />
        <Route path="kyc" element={<KYCPage />} />
        <Route path="audit-logs" element={<AuditLogsPage />} />
        <Route path="advanced-security" element={<AdvancedSecurityPage />} />
        <Route path="crypto-payment" element={<CryptoPaymentPage />} />
        <Route path="marketplace" element={<MarketplacePage />} />
        <Route path="users" element={<UsersPage />} />
        <Route path="monitoring" element={<MonitoringPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="device-settings" element={<DeviceSettingsPage />} />
        <Route path="media-capture" element={<MediaCapturePage />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <ThemeProvider>
        <Web3Provider>
          <AuthProvider>
            <AppRoutes />
          </AuthProvider>
        </Web3Provider>
      </ThemeProvider>
    </Router>
  );
}

export default App;
