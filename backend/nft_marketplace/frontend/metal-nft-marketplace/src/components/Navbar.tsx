import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useWeb3 } from '../contexts/Web3Context';
import { Wallet, Coins, TrendingUp, User, Plus, Shield } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { account, isConnected, connectWallet, disconnectWallet } = useWeb3();
  const location = useLocation();

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const navItems = [
    { path: '/', label: 'Bosh sahifa', icon: Coins },
    { path: '/marketplace', label: 'Bozor', icon: TrendingUp },
    { path: '/portfolio', label: 'Portfel', icon: User },
    { path: '/certification', label: 'Sertifikat', icon: Shield },
  ];

  return (
    <nav className="bg-slate-900/95 backdrop-blur-sm border-b border-slate-700 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center">
              <Coins className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
              MetalNFT
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-6">
            {navItems.map(({ path, label, icon: Icon }) => (
              <Link
                key={path}
                to={path}
                className={`flex items-center space-x-1 px-3 py-2 rounded-lg transition-colors ${
                  location.pathname === path
                    ? 'bg-slate-800 text-yellow-400'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{label}</span>
              </Link>
            ))}
          </div>

          {/* Create Listing Button */}
          <Link
            to="/create-listing"
            className="hidden md:flex items-center space-x-2 bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-4 py-2 rounded-lg hover:from-yellow-600 hover:to-orange-600 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Listing yaratish</span>
          </Link>

          {/* Wallet Connection */}
          <div className="flex items-center space-x-4">
            {isConnected ? (
              <div className="flex items-center space-x-2">
                <div className="hidden md:flex items-center space-x-2 bg-slate-800 px-3 py-2 rounded-lg">
                  <Wallet className="w-4 h-4 text-green-400" />
                  <span className="text-sm text-green-400">
                    {formatAddress(account!)}
                  </span>
                </div>
                <button
                  onClick={disconnectWallet}
                  className="text-sm text-slate-400 hover:text-white transition-colors"
                >
                  Uzilish
                </button>
              </div>
            ) : (
              <button
                onClick={connectWallet}
                className="flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-colors"
              >
                <Wallet className="w-4 h-4" />
                <span>Wallet ulash</span>
              </button>
            )}
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden border-t border-slate-700 pt-4 pb-4">
          <div className="flex items-center justify-around">
            {navItems.map(({ path, label, icon: Icon }) => (
              <Link
                key={path}
                to={path}
                className={`flex flex-col items-center space-y-1 px-2 py-1 rounded-lg transition-colors ${
                  location.pathname === path
                    ? 'text-yellow-400'
                    : 'text-slate-400'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="text-xs">{label}</span>
              </Link>
            ))}
            <Link
              to="/create-listing"
              className="flex flex-col items-center space-y-1 px-2 py-1 text-slate-400"
            >
              <Plus className="w-5 h-5" />
              <span className="text-xs">Yaratish</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};