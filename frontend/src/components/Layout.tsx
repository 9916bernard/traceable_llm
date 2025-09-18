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
      </Head>
      <div className="min-h-screen bg-gradient-to-br from-navy-50 via-blue-50 to-primary-50 relative overflow-hidden">
        {/* 배경 장식 요소 */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-primary-200/30 to-blue-300/30 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-tr from-navy-200/30 to-primary-200/30 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-blue-100/20 to-primary-100/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
        </div>

        {/* 헤더 */}
        <header className="relative z-10 bg-white/80 backdrop-blur-md border-b border-navy-200 shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-navy-700 rounded-lg flex items-center justify-center shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <div>
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-navy-800 to-primary-700 bg-clip-text text-transparent">
                    LLM Verification System
                  </h1>
                  <p className="text-sm text-navy-600 font-medium">
                    Blockchain-powered AI authenticity verification
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="hidden sm:flex items-center space-x-2 px-3 py-2 bg-gradient-to-r from-success-100 to-success-200 rounded-full border border-success-300">
                  <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
                  <span className="text-xs font-semibold text-success-800">System Online</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* 메인 콘텐츠 */}
        <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="fade-in">
            {children}
          </div>
        </main>

        {/* 푸터 */}
        <footer className="relative z-10 mt-16 bg-navy-900 text-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div>
                <h3 className="text-lg font-semibold mb-4 text-primary-300">About</h3>
                <p className="text-navy-300 text-sm leading-relaxed">
                  Secure, transparent, and reliable LLM output verification using blockchain technology.
                </p>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-4 text-primary-300">Features</h3>
                <ul className="space-y-2 text-navy-300 text-sm">
                  <li className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-primary-400 rounded-full"></div>
                    <span>Real-time verification</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-primary-400 rounded-full"></div>
                    <span>Blockchain security</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-primary-400 rounded-full"></div>
                    <span>Multi-LLM support</span>
                  </li>
                </ul>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-4 text-primary-300">Security</h3>
                <div className="flex items-center space-x-2 text-navy-300 text-sm">
                  <svg className="w-4 h-4 text-success-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                  <span>End-to-end encrypted</span>
                </div>
              </div>
            </div>
            <div className="border-t border-navy-800 mt-8 pt-6 text-center">
              <p className="text-navy-400 text-sm">
                © 2024 LLM Verification System. Built with trust and transparency.
              </p>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}
