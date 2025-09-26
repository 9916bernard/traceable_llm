import React from 'react';
import { LoadingStep, ConsensusResult } from '@/types';

interface ConsensusLoadingProps {
  currentStep: LoadingStep;
  consensusResult?: ConsensusResult;
  error?: string;
}

const stepMessages: Record<LoadingStep, string> = {
  idle: 'Ready to start',
  consensus_validation: 'Running consensus validation with 5 LLM models...',
  llm_generation: 'Generating LLM response...',
  hash_creation: 'Creating verification hash...',
  blockchain_commit: 'Committing to blockchain...',
  completed: 'Process completed successfully!',
  error: 'An error occurred'
};

const stepDescriptions: Record<LoadingStep, string> = {
  idle: 'Ready to start processing',
  consensus_validation: 'Asking 5 different LLM models to evaluate prompt safety',
  llm_generation: 'Generating response from selected LLM model',
  hash_creation: 'Creating cryptographic hash for verification',
  blockchain_commit: 'Storing hash on Ethereum blockchain',
  completed: 'All steps completed successfully',
  error: 'Process failed'
};

export default function ConsensusLoading({ currentStep, consensusResult, error }: ConsensusLoadingProps) {
  const getStepIcon = (step: LoadingStep) => {
    switch (step) {
      case 'idle':
        return '⏳';
      case 'consensus_validation':
        return '🤖';
      case 'llm_generation':
        return '⚡';
      case 'hash_creation':
        return '🔐';
      case 'blockchain_commit':
        return '⛓️';
      case 'completed':
        return '✅';
      case 'error':
        return '❌';
      default:
        return '⏳';
    }
  };

  const getStepColor = (step: LoadingStep) => {
    switch (step) {
      case 'completed':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
      case 'idle':
        return 'text-gray-500';
      default:
        return 'text-blue-600';
    }
  };

  const isStepActive = (step: LoadingStep) => {
    const stepOrder = ['idle', 'consensus_validation', 'llm_generation', 'hash_creation', 'blockchain_commit', 'completed'];
    const currentIndex = stepOrder.indexOf(currentStep);
    const stepIndex = stepOrder.indexOf(step);
    return stepIndex <= currentIndex;
  };

  const steps = [
    { key: 'consensus_validation', label: 'Consensus Validation' },
    { key: 'llm_generation', label: 'LLM Generation' },
    { key: 'hash_creation', label: 'Hash Creation' },
    { key: 'blockchain_commit', label: 'Blockchain Commit' }
  ] as const;

  return (
    <div className="space-y-6">
      {/* 현재 단계 표시 */}
      <div className="text-center">
        <div className={`text-4xl mb-2 ${getStepColor(currentStep)}`}>
          {getStepIcon(currentStep)}
        </div>
        <h3 className={`text-lg font-semibold ${getStepColor(currentStep)}`}>
          {stepMessages[currentStep]}
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          {stepDescriptions[currentStep]}
        </p>
      </div>

      {/* 진행 단계 표시 */}
      <div className="space-y-3">
        {steps.map((step, index) => {
          const isActive = isStepActive(step.key);
          const isCurrent = currentStep === step.key;
          
          return (
            <div
              key={step.key}
              className={`flex items-center space-x-3 p-3 rounded-lg transition-all duration-300 ${
                isCurrent
                  ? 'bg-blue-50 border border-blue-200'
                  : isActive
                  ? 'bg-green-50 border border-green-200'
                  : 'bg-gray-50 border border-gray-200'
              }`}
            >
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                isCurrent
                  ? 'bg-blue-500 text-white'
                  : isActive
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-300 text-gray-600'
              }`}>
                {isCurrent ? '⏳' : isActive ? '✓' : index + 1}
              </div>
              <div className="flex-1">
                <div className={`font-medium ${
                  isCurrent ? 'text-blue-800' : isActive ? 'text-green-800' : 'text-gray-600'
                }`}>
                  {step.label}
                </div>
                <div className="text-sm text-gray-500">
                  {stepDescriptions[step.key]}
                </div>
              </div>
              {isCurrent && (
                <div className="flex-shrink-0">
                  <div className="loading-spinner" />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Consensus 결과 표시 */}
      {consensusResult && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium text-gray-900 mb-3">Consensus Validation Results</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium text-gray-700">Safe Votes:</span>
              <span className="ml-2 text-green-600 font-semibold">
                {consensusResult.safe_votes}/{consensusResult.total_models}
              </span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Harmful Votes:</span>
              <span className="ml-2 text-red-600 font-semibold">
                {consensusResult.harmful_votes}/{consensusResult.total_models}
              </span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Threshold:</span>
              <span className="ml-2">{consensusResult.threshold} models</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Status:</span>
              <span className={`ml-2 font-semibold ${
                consensusResult.consensus_passed ? 'text-green-600' : 'text-red-600'
              }`}>
                {consensusResult.consensus_passed ? 'PASSED' : 'FAILED'}
              </span>
            </div>
          </div>
          
          {/* 개별 모델 응답 */}
          <div className="mt-4">
            <h5 className="font-medium text-gray-900 mb-2">Individual Model Responses</h5>
            <div className="space-y-2">
              {Object.entries(consensusResult.model_responses).map(([provider, response]) => (
                <div key={provider} className="flex items-center justify-between text-sm">
                  <span className="font-medium text-gray-700 capitalize">{provider}</span>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      response.is_harmful 
                        ? 'bg-red-100 text-red-800' 
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {response.is_harmful ? 'Harmful' : 'Safe'}
                    </span>
                    <span className="text-gray-500">
                      {response.response_time.toFixed(2)}s
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 에러 표시 */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <span className="text-red-500">❌</span>
            <span className="font-medium text-red-800">Error</span>
          </div>
          <p className="text-sm text-red-700 mt-1">{error}</p>
        </div>
      )}
    </div>
  );
}
