import { Link, Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ThemeToggle from './ThemeToggle';
import {
  HomeIcon,
  ChartBarIcon,
  CpuChipIcon,
  UsersIcon,
  ComputerDesktopIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  BellIcon,
  UserGroupIcon,
  CreditCardIcon,
  GiftIcon,
  ShieldCheckIcon,
  NewspaperIcon,
  ChatBubbleBottomCenterTextIcon,
  ExclamationTriangleIcon,
  SparklesIcon,
  MicrophoneIcon,
  CommandLineIcon,
  ChartPieIcon,
  IdentificationIcon,
  DocumentTextIcon,
  LockClosedIcon,
  CurrencyDollarIcon,
  ShoppingBagIcon,
  Bars3Icon,
  XMarkIcon,
  ArrowsRightLeftIcon,
  FireIcon,
  BoltIcon,
  WalletIcon,
  LinkIcon
} from '@heroicons/react/24/outline';
import { useState } from 'react';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Pozitsiyalar', href: '/positions', icon: ChartBarIcon },
  { name: 'Strategiyalar', href: '/strategies', icon: CpuChipIcon },
  
  // Phase 4.1: AI Trading Bots V2
  { name: 'AI Trading Bots V2', href: '/ai-trading-bots', icon: CpuChipIcon },
  { name: 'ML Price Predictions', href: '/ml-predictions', icon: ChartPieIcon },
  { name: 'AI Bots (Legacy)', href: '/ai-bots', icon: CpuChipIcon },
  { name: 'Strategiya Yaratuvchi', href: '/strategy-builder', icon: SparklesIcon },
  
  // Phase 2 & 3 Features
  { name: 'Sosyal Trading', href: '/social-trading', icon: UserGroupIcon },
  { name: 'Risk Yönetimi', href: '/risk-management', icon: ExclamationTriangleIcon },
  { name: 'DeFi Trading', href: '/defi-trading', icon: SparklesIcon },
  
  // Phase 4.2: DeFi 2.0 Integration
  { name: 'DeFi Dashboard', href: '/defi', icon: LinkIcon },
  { name: 'Cross-Chain Bridge', href: '/defi/bridge', icon: ArrowsRightLeftIcon },
  { name: 'Yield Farming', href: '/defi/yield', icon: FireIcon },
  { name: 'Arbitrage Scanner', href: '/defi/arbitrage', icon: BoltIcon },
  { name: 'Multi-Chain Wallet', href: '/defi/wallet', icon: WalletIcon },
  
  { name: 'AI Market Tahmini', href: '/ai-market-predictor', icon: ChartPieIcon },
  
  // Original Features
  { name: 'Copy Trading', href: '/copy-trading', icon: UserGroupIcon },
  { name: 'Obuna', href: '/subscription', icon: CreditCardIcon },
  { name: 'Referral', href: '/referral', icon: GiftIcon },
  { name: 'Xavfsizlik', href: '/security', icon: ShieldCheckIcon },
  
  // Advanced Trading Features
  { name: 'News Trading', href: '/news-trading', icon: NewspaperIcon },
  { name: 'Social Sentiment', href: '/social-sentiment', icon: ChatBubbleBottomCenterTextIcon },
  { name: 'Risk Analytics', href: '/risk-analytics', icon: ExclamationTriangleIcon },
  
  // AI Assistants
  { name: 'GPT Assistant', href: '/gpt-assistant', icon: SparklesIcon },
  { name: 'Voice Commands', href: '/voice-commands', icon: MicrophoneIcon },
  
  // Device & Media Management
  { name: 'Qurilma Sozlamalari', href: '/device-settings', icon: ComputerDesktopIcon },
  { name: 'Media Capture', href: '/media-capture', icon: MicrophoneIcon },
  { name: 'Auto Strategy', href: '/auto-strategy', icon: CommandLineIcon },
  { name: 'Market Predictions', href: '/market-predictions', icon: ChartPieIcon },
  
  // Security & Compliance
  { name: 'KYC Verification', href: '/kyc', icon: IdentificationIcon },
  { name: 'Audit Logs', href: '/audit-logs', icon: DocumentTextIcon },
  { name: 'Advanced Security', href: '/advanced-security', icon: LockClosedIcon },
  
  // Monetization
  { name: 'Crypto Payment', href: '/crypto-payment', icon: CurrencyDollarIcon },
  { name: 'Marketplace', href: '/marketplace', icon: ShoppingBagIcon },
  
  // Admin
  { name: 'Foydalanuvchilar', href: '/users', icon: UsersIcon },
  { name: 'Monitoring', href: '/monitoring', icon: ComputerDesktopIcon },
  { name: 'Sozlamalar', href: '/settings', icon: Cog6ToothIcon },
];

export default function Layout() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleSignOut = async () => {
    await signOut();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-neutral-900 transition-colors duration-300">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 glass-dark border-b border-neutral-200 dark:border-neutral-800 shadow-lg">
        <div className="flex items-center justify-between px-4 sm:px-6 py-3">
          {/* Left Section */}
          <div className="flex items-center gap-4">
            {/* Mobile Menu Button */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
            >
              {sidebarOpen ? (
                <XMarkIcon className="w-6 h-6 text-neutral-700 dark:text-neutral-300" />
              ) : (
                <Bars3Icon className="w-6 h-6 text-neutral-700 dark:text-neutral-300" />
              )}
            </button>

            {/* Logo & Title */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center shadow-md">
                <span className="text-white font-bold text-xl">AI</span>
              </div>
              <h1 className="hidden sm:block text-xl font-bold text-neutral-900 dark:text-white font-display">
                Orion Starline
              </h1>
            </div>
          </div>
          
          {/* Right Section */}
          <div className="flex items-center gap-3">
            {/* Notifications */}
            <button className="relative p-2.5 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-all">
              <BellIcon className="w-6 h-6 text-neutral-600 dark:text-neutral-400" />
              <span className="absolute top-2 right-2 w-2 h-2 bg-danger-500 rounded-full ring-2 ring-white dark:ring-neutral-900"></span>
            </button>

            {/* Theme Toggle */}
            <ThemeToggle />
            
            {/* User Menu */}
            <div className="flex items-center gap-3 pl-3 border-l border-neutral-200 dark:border-neutral-700">
              <div className="hidden sm:block text-right">
                <p className="text-sm font-semibold text-neutral-900 dark:text-white">{user?.email}</p>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">Administrator</p>
              </div>
              <button
                onClick={handleSignOut}
                className="p-2.5 rounded-lg hover:bg-danger-50 dark:hover:bg-danger-900/20 
                  text-neutral-600 dark:text-neutral-400 hover:text-danger-600 dark:hover:text-danger-400 
                  transition-all"
                title="Chiqish"
              >
                <ArrowRightOnRectangleIcon className="w-6 h-6" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed top-16 left-0 bottom-0 z-40 w-72 bg-white dark:bg-neutral-900 
        border-r border-neutral-200 dark:border-neutral-800 overflow-y-auto
        transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <nav className="p-4 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                onClick={() => setSidebarOpen(false)}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm
                  transition-all duration-200 group
                  ${
                    isActive
                      ? 'bg-gradient-primary text-white shadow-lg hover:shadow-xl'
                      : 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800'
                  }
                `}
              >
                <item.icon className={`
                  w-5 h-5 flex-shrink-0 transition-transform duration-200
                  ${isActive ? 'scale-110' : 'group-hover:scale-110'}
                `} />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="pt-16 lg:pl-72 min-h-screen">
        <div className="p-4 sm:p-6 lg:p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
