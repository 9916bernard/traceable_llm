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
        <meta name="description" content="LLM 출력의 진위를 검증하는 블록체인 기반 시스템" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <Layout>
        <div className="min-h-screen bg-gray-50">
          {/* 헤더 */}
          <div className="bg-white shadow">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center py-6">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">
                    LLM Verification System
                  </h1>
                  <p className="mt-2 text-gray-600">
                    LLM 출력의 진위를 블록체인으로 검증하는 시스템
                  </p>
                </div>
                <div className="flex items-center space-x-4">
                  {blockchainStatus && (
                    <div className="flex items-center space-x-2">
                      <div
                        className={`w-3 h-3 rounded-full ${
                          blockchainStatus.status === 'connected'
                            ? 'bg-green-500'
                            : 'bg-red-500'
                        }`}
                      />
                      <span className="text-sm text-gray-600">
                        {blockchainStatus.status === 'connected' ? '블록체인 연결됨' : '블록체인 연결 안됨'}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* 탭 네비게이션 */}
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8">
                {[
                  { id: 'generate', name: 'LLM 생성', icon: '🤖' },
                  { id: 'verify', name: '검증', icon: '🔍' },
                  { id: 'status', name: '상태', icon: '📊' },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`${
                      activeTab === tab.id
                        ? 'border-primary-500 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
                  >
                    <span>{tab.icon}</span>
                    <span>{tab.name}</span>
                  </button>
                ))}
              </nav>
            </div>
          </div>

          {/* 메인 컨텐츠 */}
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
            {activeTab === 'generate' && (
              <div className="space-y-6">
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">
                    LLM 응답 생성 및 검증
                  </h2>
                  <p className="text-gray-600 mb-6">
                    LLM에 프롬프트를 입력하면 응답과 함께 검증 해시가 생성되고 블록체인에 저장됩니다.
                  </p>
                  <LLMGenerator models={models} />
                </div>
              </div>
            )}

            {activeTab === 'verify' && (
              <div className="space-y-6">
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">
                    해시 검증
                  </h2>
                  <p className="text-gray-600 mb-6">
                    해시값을 입력하여 LLM 출력의 진위를 검증할 수 있습니다.
                  </p>
                  <VerificationChecker />
                </div>
              </div>
            )}

            {activeTab === 'status' && (
              <div className="space-y-6">
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">
                    시스템 상태
                  </h2>
                  <p className="text-gray-600 mb-6">
                    블록체인 네트워크와 시스템의 현재 상태를 확인할 수 있습니다.
                  </p>
                  <BlockchainStatus status={blockchainStatus} loading={blockchainLoading} />
                </div>
              </div>
            )}
          </div>
        </div>
      </Layout>
    </>
  );
}
