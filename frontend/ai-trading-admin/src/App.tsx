import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
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
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <ThemeProvider>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </ThemeProvider>
    </Router>
  );
}

export default App;
