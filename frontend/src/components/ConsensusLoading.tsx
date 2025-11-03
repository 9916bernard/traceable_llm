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
    return (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        {step === 'completed' ? (
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        ) : step === 'error' ? (
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        ) : (
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        )}
      </svg>
    );
  };

  const getStepColor = (step: LoadingStep) => {
    switch (step) {
      case 'completed':
        return 'text-emerald-900';
      case 'error':
        return 'text-red-900';
      case 'idle':
        return 'text-gray-500';
      default:
        return 'text-blue-900';
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
      {/* Current step display */}
      <div className="text-center">
        <div className={`flex items-center justify-center mb-3 ${getStepColor(currentStep)}`}>
          <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-xl flex items-center justify-center shadow-lg">
            {getStepIcon(currentStep)}
          </div>
        </div>
        <h3 className={`text-xl font-bold ${getStepColor(currentStep)}`}>
          {stepMessages[currentStep]}
        </h3>
        <p className="text-sm text-gray-600 mt-2">
          {stepDescriptions[currentStep]}
        </p>
      </div>

      {/* Progress steps */}
      <div className="space-y-3">
        {steps.map((step, index) => {
          const isActive = isStepActive(step.key);
          const isCurrent = currentStep === step.key;
          
          return (
            <div
              key={step.key}
              className={`flex items-center space-x-4 p-4 rounded-xl transition-all duration-300 ${
                isCurrent
                  ? 'bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-300 shadow-md'
                  : isActive
                  ? 'bg-gradient-to-r from-emerald-50 to-emerald-100 border border-emerald-200'
                  : 'bg-white border border-gray-200'
              }`}
            >
              <div className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center text-xs font-bold shadow-sm ${
                isCurrent
                  ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white'
                  : isActive
                  ? 'bg-gradient-to-br from-emerald-500 to-emerald-600 text-white'
                  : 'bg-gray-200 text-gray-600'
              }`}>
                {isActive && !isCurrent ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  index + 1
                )}
              </div>
              <div className="flex-1">
                <div className={`font-semibold ${
                  isCurrent ? 'text-blue-900' : isActive ? 'text-emerald-900' : 'text-gray-600'
                }`}>
                  {step.label}
                </div>
                <div className="text-sm text-gray-500 mt-1">
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

      {/* Consensus results */}
      {consensusResult && (
        <div className="mt-6 p-5 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border-2 border-blue-200 shadow-sm">
          <h4 className="font-bold text-gray-900 mb-4">Consensus Validation Results</h4>
          <div className="grid grid-cols-2 gap-4 text-sm mb-4">
            <div>
              <span className="font-semibold text-gray-700">Safe Votes:</span>
              <span className="ml-2 text-emerald-900 font-bold">
                {consensusResult.safe_votes}/{consensusResult.total_models}
              </span>
            </div>
            <div>
              <span className="font-semibold text-gray-700">Harmful Votes:</span>
              <span className="ml-2 text-red-900 font-bold">
                {consensusResult.harmful_votes}/{consensusResult.total_models}
              </span>
            </div>
            <div>
              <span className="font-semibold text-gray-700">Threshold:</span>
              <span className="ml-2 text-gray-900 font-bold">{consensusResult.threshold} models</span>
            </div>
            <div>
              <span className="font-semibold text-gray-700">Status:</span>
              <span className={`ml-2 font-bold ${
                consensusResult.consensus_passed ? 'text-emerald-900' : 'text-red-900'
              }`}>
                {consensusResult.consensus_passed ? 'PASSED' : 'FAILED'}
              </span>
            </div>
          </div>
          
          {/* Individual model responses */}
          <div className="mt-4">
            <h5 className="font-semibold text-gray-900 mb-3">Individual Model Responses</h5>
            <div className="space-y-2">
              {Object.entries(consensusResult.model_responses).map(([provider, response]) => (
                <div key={provider} className="flex items-center justify-between text-sm p-3 bg-white rounded-lg border border-blue-200 hover:border-blue-300 transition-colors duration-200">
                  <span className="font-semibold text-gray-700 capitalize">{provider}</span>
                  <div className="flex items-center space-x-2">
                    <span className={`px-3 py-1 rounded-lg text-xs font-semibold shadow-sm ${
                      response.is_harmful 
                        ? 'bg-red-100 text-red-800 border border-red-200' 
                        : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                    }`}>
                      {response.is_harmful ? 'Harmful' : 'Safe'}
                    </span>
                    <span className="text-gray-500 text-xs font-medium">
                      {response.response_time.toFixed(2)}s
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Error display */}
      {error && (
        <div className="mt-4 p-5 bg-gradient-to-br from-red-50 to-red-100 border-2 border-red-300 rounded-xl shadow-sm">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-red-500 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <div className="flex-1">
              <div className="font-bold text-red-900 mb-1">Error</div>
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
