import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Web3Provider } from './contexts/Web3Context';
import { MarketplaceProvider } from './contexts/MarketplaceContext';
import { Navbar } from './components/Navbar';
import { HomePage } from './pages/HomePage';
import { MarketplacePage } from './pages/MarketplacePage';
import { PortfolioPage } from './pages/PortfolioPage';
import { CreateListingPage } from './pages/CreateListingPage';
import { AuctionPage } from './pages/AuctionPage';
import { CertificationPage } from './pages/CertificationPage';
import { MetalDetailsPage } from './pages/MetalDetailsPage';
import { Footer } from './components/Footer';

function App() {
  return (
    <Web3Provider>
      <MarketplaceProvider>
        <Router>
          <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            <Navbar />
            <main className="container mx-auto px-4 py-8">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/marketplace" element={<MarketplacePage />} />
                <Route path="/portfolio" element={<PortfolioPage />} />
                <Route path="/create-listing" element={<CreateListingPage />} />
                <Route path="/auction/:id" element={<AuctionPage />} />
                <Route path="/certification/:id" element={<CertificationPage />} />
                <Route path="/metal/:id" element={<MetalDetailsPage />} />
              </Routes>
            </main>
            <Footer />
          </div>
        </Router>
      </MarketplaceProvider>
    </Web3Provider>
  );
}

export default App;
