import { useState } from 'react';
import Head from 'next/head';
import { useQuery, useMutation } from 'react-query';
import toast from 'react-hot-toast';
import Layout from '@/components/Layout';
import LLMGenerator from '@/components/LLMGenerator';
import VerificationChecker from '@/components/VerificationChecker';
import { llmApi, verificationApi, blockchainApi } from '@/services/api';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'generate' | 'verify'>('generate');

  // Blockchain status query
  const { data: blockchainStatus } = useQuery(
    'blockchain-status',
    blockchainApi.getStatus,
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  // LLM models query
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
        {/* Tab navigation */}
        <div className="mb-10">
          <div className="glass-card p-2">
            <nav className="flex space-x-2">
              {[
                { id: 'generate', name: 'AI Generation', desc: 'Create & Verify', icon: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z' },
                { id: 'verify', name: 'Verification', desc: 'Check Authenticity', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex-1 relative px-6 py-4 rounded-xl font-semibold text-sm transition-all duration-300 transform hover:scale-[1.02] ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg'
                      : 'text-gray-600 hover:bg-blue-50 hover:text-blue-700'
                  }`}
                >
                  <div className="flex items-center justify-center space-x-3">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={tab.icon} />
                    </svg>
                    <div className="text-left">
                      <div>{tab.name}</div>
                      <div className={`text-xs font-normal ${
                        activeTab === tab.id ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        {tab.desc}
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Main content */}
        <div className="space-y-8">
          {activeTab === 'generate' && (
            <div className="fade-in">
              <div className="card-gradient">
                <div className="flex items-center space-x-4 mb-8">
                  <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                    <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">
                      AI Response Generation
                    </h2>
                    <p className="text-gray-600 mt-1">
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
              <div className="card-gradient">
                <div className="flex items-center space-x-4 mb-8">
                  <div className="w-14 h-14 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg">
                    <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">
                      Authenticity Verification
                    </h2>
                    <p className="text-gray-600 mt-1">
                      Verify the authenticity of AI-generated content
                    </p>
                  </div>
                </div>
                <VerificationChecker />
              </div>
            </div>
          )}
        </div>
      </Layout>
    </>
  );
}
