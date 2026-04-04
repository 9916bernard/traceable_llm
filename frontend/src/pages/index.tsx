import { useState } from 'react';
import Head from 'next/head';
import { useQuery } from 'react-query';
import Layout from '@/components/Layout';
import LLMGenerator from '@/components/LLMGenerator';
import VerificationChecker from '@/components/VerificationChecker';
import { llmApi, blockchainApi } from '@/services/api';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'generate' | 'verify'>('generate');

  const { data: blockchainStatus } = useQuery(
    'blockchain-status',
    blockchainApi.getStatus,
    { refetchInterval: 30000 }
  );

  const { data: models } = useQuery('llm-models', llmApi.getModels);

  return (
    <>
      <Head>
        <title>Traceable LLM</title>
        <meta name="description" content="Blockchain-anchored verification for LLM outputs" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <Layout>
        {/* Tab navigation */}
        <div className="flex border-b border-[var(--color-border)] mb-8">
          <button
            onClick={() => setActiveTab('generate')}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors duration-150 -mb-px ${
              activeTab === 'generate'
                ? 'border-[var(--color-ink)] text-[var(--color-ink)]'
                : 'border-transparent text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]'
            }`}
          >
            Generate
          </button>
          <button
            onClick={() => setActiveTab('verify')}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors duration-150 -mb-px ${
              activeTab === 'verify'
                ? 'border-[var(--color-ink)] text-[var(--color-ink)]'
                : 'border-transparent text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]'
            }`}
          >
            Verify
          </button>
        </div>

        {/* Content */}
        <div className="fade-in">
          {activeTab === 'generate' && (
            <div>
              <div className="mb-6">
                <h2 className="text-base font-semibold text-[var(--color-ink)]">
                  Generate &amp; Anchor
                </h2>
                <p className="text-sm text-[var(--color-ink-muted)] mt-1">
                  Submit a prompt for consensus validation, LLM generation, and blockchain anchoring.
                </p>
              </div>
              <LLMGenerator models={models} />
            </div>
          )}

          {activeTab === 'verify' && (
            <div>
              <div className="mb-6">
                <h2 className="text-base font-semibold text-[var(--color-ink)]">
                  Verify Record
                </h2>
                <p className="text-sm text-[var(--color-ink-muted)] mt-1">
                  Look up a transaction hash to verify the integrity of a previously anchored LLM output.
                </p>
              </div>
              <VerificationChecker />
            </div>
          )}
        </div>
      </Layout>
    </>
  );
}
