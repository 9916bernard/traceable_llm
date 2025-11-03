import { ReactNode } from 'react';
import Head from 'next/head';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <>
      <Head>
        <title>LLM Verification System</title>
        <meta name="description" content="Blockchain-based system for verifying LLM output authenticity" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
      </Head>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
        {/* Header */}
        <header className="bg-gradient-to-r from-[#1E2A38] to-[#2D3E50] shadow-lg border-b border-blue-900/20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-5">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-blue-600 rounded-xl flex items-center justify-center shadow-lg transform hover:scale-105 transition-transform duration-300">
                  <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white tracking-tight">
                    LLM Verification System
                  </h1>
                  <p className="text-sm text-blue-200 font-medium">
                    Blockchain-Powered AI Authenticity
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="hidden sm:flex items-center space-x-2 px-4 py-2 bg-emerald-500/20 rounded-lg border border-emerald-400/30 backdrop-blur-sm">
                  <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse shadow-lg shadow-emerald-400/50"></div>
                  <span className="text-xs font-semibold text-emerald-100">System Online</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Main content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <div className="fade-in">
            {children}
          </div>
        </main>

        {/* Footer */}
        <footer className="mt-20 bg-gradient-to-r from-[#1E2A38] to-[#2D3E50] text-white border-t border-blue-900/20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
              <div>
                <h3 className="text-lg font-bold mb-4 text-blue-200">About</h3>
                <p className="text-blue-100/80 text-sm leading-relaxed">
                  Secure, transparent, and reliable LLM output verification using blockchain technology. Built with trust and technological excellence.
                </p>
              </div>
              <div>
                <h3 className="text-lg font-bold mb-4 text-blue-200">Features</h3>
                <ul className="space-y-2 text-blue-100/80 text-sm">
                  <li className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-blue-400 rounded-full"></div>
                    <span>Real-time verification</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-blue-400 rounded-full"></div>
                    <span>Blockchain security</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-blue-400 rounded-full"></div>
                    <span>Multi-LLM support</span>
                  </li>
                </ul>
              </div>
              <div>
                <h3 className="text-lg font-bold mb-4 text-blue-200">Security</h3>
                <div className="flex items-center space-x-2 text-blue-100/80 text-sm">
                  <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                  <span>End-to-end encrypted</span>
                </div>
              </div>
            </div>
            <div className="border-t border-blue-800/30 mt-10 pt-8 text-center">
              <p className="text-blue-200/60 text-sm">
                © 2024 LLM Verification System. Built with trust and transparency.
              </p>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}
