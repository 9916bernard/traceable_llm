import React from 'react';
import { LoadingStep, ConsensusResult } from '@/types';

interface ConsensusLoadingProps {
  currentStep: LoadingStep;
  consensusResult?: ConsensusResult;
  error?: string;
}

const steps = [
  { key: 'consensus_validation' as const, label: 'Consensus validation', desc: '5-model safety vote' },
  { key: 'llm_generation' as const, label: 'LLM generation', desc: 'Response from selected model' },
  { key: 'hash_creation' as const, label: 'Hash creation', desc: 'HMAC-SHA256 canonicalization' },
  { key: 'ipfs_pin' as const, label: 'IPFS pin', desc: 'Pin record to IPFS via Pinata' },
  { key: 'blockchain_commit' as const, label: 'Blockchain commit', desc: 'Anchor hash + CID to Sepolia' },
];

const stepOrder = ['idle', 'consensus_validation', 'llm_generation', 'hash_creation', 'ipfs_pin', 'blockchain_commit', 'completed'];

export default function ConsensusLoading({ currentStep, consensusResult, error }: ConsensusLoadingProps) {
  const currentIndex = stepOrder.indexOf(currentStep);

  return (
    <div className="space-y-4">
      {/* Step list */}
      <div className="space-y-2">
        {steps.map((step, i) => {
          const stepIndex = stepOrder.indexOf(step.key);
          const isDone = stepIndex < currentIndex;
          const isActive = currentStep === step.key;

          return (
            <div
              key={step.key}
              className={`flex items-center space-x-3 px-3 py-2.5 rounded text-sm ${
                isActive
                  ? 'bg-[var(--color-surface-dim)] border border-[var(--color-border)]'
                  : isDone
                  ? 'text-[var(--color-ink-muted)]'
                  : 'text-[var(--color-ink-muted)] opacity-50'
              }`}
            >
              <div className="flex-shrink-0 w-5 h-5 flex items-center justify-center">
                {isDone ? (
                  <svg className="w-4 h-4 text-[var(--color-safe)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : isActive ? (
                  <span className="loading-spinner" style={{ width: 14, height: 14 }} />
                ) : (
                  <span className="text-xs font-mono text-[var(--color-ink-muted)]">{i + 1}</span>
                )}
              </div>
              <div className="flex-1">
                <span className={`font-medium ${isActive ? 'text-[var(--color-ink)]' : ''}`}>
                  {step.label}
                </span>
                <span className="text-xs text-[var(--color-ink-muted)] ml-2">{step.desc}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Inline consensus result during loading */}
      {consensusResult && (
        <div className="p-3 bg-[var(--color-surface-dim)] rounded border border-[var(--color-border)] text-sm">
          <span className="font-medium text-[var(--color-ink)]">Consensus: </span>
          <span className={consensusResult.consensus_passed ? 'text-[var(--color-safe)]' : 'text-[var(--color-danger)]'}>
            {consensusResult.safe_votes}/{consensusResult.total_models} safe
          </span>
          <span className="text-[var(--color-ink-muted)]"> &mdash; {consensusResult.consensus_passed ? 'passed' : 'blocked'}</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-[var(--color-danger)]">
          {error}
        </div>
      )}
    </div>
  );
}
