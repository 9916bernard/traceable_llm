import { useState } from 'react';
import Head from 'next/head';
import { useQuery, useMutation } from 'react-query';
import toast from 'react-hot-toast';
import Layout from '@/components/Layout';
import LLMGenerator from '@/components/LLMGenerator';
import VerificationChecker from '@/components/VerificationChecker';
import BlockchainStatus from '@/components/BlockchainStatus';
import { llmApi, verificationApi, blockchainApi } from '@/services/api';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'generate' | 'verify' | 'status'>('generate');

  // 블록체인 상태 조회
  const { data: blockchainStatus, isLoading: blockchainLoading } = useQuery(
    'blockchain-status',
    blockchainApi.getStatus,
    {
      refetchInterval: 30000, // 30초마다 갱신
    }
  );

  // LLM 모델 목록 조회
  const { data: models } = useQuery('llm-models', llmApi.getModels);

  return (
    <>
      <Head>
        <title>LLM Verification System</title>
        <meta name="description" content="Blockchain-based system for verifying LLM output authenticity" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <Layout>
        {/* 히어로 섹션 */}
        <div className="relative mb-12">
          <div className="text-center py-12">
            <div className="slide-in-left">
              <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-navy-800 via-primary-700 to-blue-700 bg-clip-text text-transparent mb-6">
                Secure AI Verification
              </h1>
              <p className="text-xl text-navy-600 max-w-3xl mx-auto leading-relaxed">
                Experience the future of AI authenticity with blockchain-powered verification. 
                Every response is cryptographically secured and transparently verifiable.
              </p>
            </div>
            
            {/* 상태 표시 카드 */}
            <div className="slide-in-right mt-8 flex justify-center">
              {blockchainStatus && (
                <div className={`inline-flex items-center space-x-3 px-6 py-3 rounded-full border-2 transition-all duration-300 hover:scale-105 ${
                  blockchainStatus.status === 'connected'
                    ? 'bg-gradient-to-r from-success-100 to-success-200 border-success-300 text-success-800'
                    : 'bg-gradient-to-r from-error-100 to-error-200 border-error-300 text-error-800'
                }`}>
                  <div className={`w-3 h-3 rounded-full ${
                    blockchainStatus.status === 'connected' ? 'bg-success-500 animate-pulse' : 'bg-error-500'
                  }`} />
                  <span className="font-semibold">
                    {blockchainStatus.status === 'connected' ? 'Blockchain Connected' : 'Blockchain Disconnected'}
                  </span>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 탭 네비게이션 */}
        <div className="mb-8">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-2 border border-navy-200 shadow-lg">
            <nav className="flex space-x-2">
              {[
                { id: 'generate', name: 'AI Generation', icon: '🤖', desc: 'Create & Verify' },
                { id: 'verify', name: 'Verification', icon: '🔍', desc: 'Check Authenticity' },
                { id: 'status', name: 'System Status', icon: '📊', desc: 'Network Health' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex-1 relative px-6 py-4 rounded-xl font-semibold text-sm transition-all duration-300 transform hover:scale-105 ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg hover:shadow-xl'
                      : 'text-navy-600 hover:bg-primary-50 hover:text-primary-700'
                  }`}
                >
                  <div className="flex flex-col items-center space-y-1">
                    <span className="text-lg">{tab.icon}</span>
                    <span>{tab.name}</span>
                    <span className={`text-xs ${
                      activeTab === tab.id ? 'text-primary-100' : 'text-navy-400'
                    }`}>
                      {tab.desc}
                    </span>
                  </div>
                  {activeTab === tab.id && (
                    <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-primary-600/20 to-primary-700/20 animate-pulse" />
                  )}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* 메인 컨텐츠 */}
        <div className="space-y-8">
          {activeTab === 'generate' && (
            <div className="fade-in">
              <div className="card hover-glow">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-12 h-12 bg-gradient-to-br from-primary-600 to-navy-700 rounded-xl flex items-center justify-center shadow-lg">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-navy-800">
                      AI Response Generation
                    </h2>
                    <p className="text-navy-600 mt-1">
                      Generate verified AI responses with blockchain security
                    </p>
                  </div>
                </div>
                <LLMGenerator models={models} />
              </div>
            </div>
          )}

          {activeTab === 'verify' && (
            <div className="fade-in">
              <div className="card hover-glow">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-12 h-12 bg-gradient-to-br from-success-600 to-success-700 rounded-xl flex items-center justify-center shadow-lg">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-navy-800">
                      Authenticity Verification
                    </h2>
                    <p className="text-navy-600 mt-1">
                      Verify the authenticity of AI-generated content
                    </p>
                  </div>
                </div>
                <VerificationChecker />
              </div>
            </div>
          )}

          {activeTab === 'status' && (
            <div className="fade-in">
              <div className="card hover-glow">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center shadow-lg">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-navy-800">
                      System Health Monitor
                    </h2>
                    <p className="text-navy-600 mt-1">
                      Real-time blockchain network and system status
                    </p>
                  </div>
                </div>
                <BlockchainStatus status={blockchainStatus} loading={blockchainLoading} />
              </div>
            </div>
          )}
        </div>
      </Layout>
    </>
  );
}
