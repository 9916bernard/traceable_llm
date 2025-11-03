import { useState } from 'react';
import { useMutation } from 'react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { LLMRequest, LLMResponse, LoadingStep, ConsensusResult } from '@/types';
import { llmApi } from '@/services/api';
import { formatResponseTime, copyToClipboard, getEtherscanUrl } from '@/utils';
import ConsensusLoading from './ConsensusLoading';

interface LLMGeneratorProps {
  models?: Record<string, string[]>;
}

interface FormData {
  provider: string;
  model: string;
  prompt: string;
}

export default function LLMGenerator({ models }: LLMGeneratorProps) {
  const [result, setResult] = useState<LLMResponse | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentStep, setCurrentStep] = useState<LoadingStep>('idle');
  const [consensusResult, setConsensusResult] = useState<ConsensusResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
    reset,
  } = useForm<FormData>({
    defaultValues: {
      provider: 'openai',
      model: 'gpt-5-mini',
    },
  });

  const selectedProvider = watch('provider');

  // LLM generation mutation (with Consensus stage)
  const generateMutation = useMutation(llmApi.generate, {
    onMutate: () => {
      setIsGenerating(true);
      setResult(null);
      setError(null);
      setConsensusResult(null);
      setCurrentStep('consensus_validation');
    },
    onSuccess: (data) => {
      // Consensus only result (validation failed, no LLM generation)
      if (data.consensus_only) {
        setConsensusResult(data.consensus_result || null);
        setCurrentStep('completed');
        // Don't show error toast, just display the consensus result
        return;
      }
      
      // Normal success with LLM generation
      setResult(data);
      setConsensusResult(data.consensus_result || null);
      setCurrentStep('completed');
      toast.success('LLM response has been generated with consensus validation!');
    },
    onError: (error: any) => {
      setCurrentStep('error');
      setError(error.response?.data?.error || error.message);
      toast.error(`Generation failed: ${error.response?.data?.error || error.message}`);
    },
    onSettled: () => {
      setIsGenerating(false);
    },
  });

  // Simulate loading steps
  const simulateLoadingSteps = async () => {
    setCurrentStep('consensus_validation');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setCurrentStep('llm_generation');
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    setCurrentStep('hash_creation');
    await new Promise(resolve => setTimeout(resolve, 500));
    
    setCurrentStep('blockchain_commit');
    await new Promise(resolve => setTimeout(resolve, 1000));
  };

  const onSubmit = async (data: FormData) => {
    const request: LLMRequest = {
      provider: data.provider,
      model: data.model,
      prompt: data.prompt,
      parameters: {
        temperature: 0.2,
        max_tokens: 200,
      },
      commit_to_blockchain: true,
    };

    // Start loading steps simulation
    simulateLoadingSteps();
    
    // Actual API call
    generateMutation.mutate(request);
  };

  const handleCopyHash = async () => {
    if (result?.hash_value) {
      const success = await copyToClipboard(result.hash_value);
      if (success) {
        toast.success('Hash copied to clipboard');
      } else {
        toast.error('Copy failed');
      }
    }
  };

  const handleCopyResponse = async () => {
    if (result?.content) {
      const success = await copyToClipboard(result.content);
      if (success) {
        toast.success('Response copied to clipboard');
      } else {
        toast.error('Copy failed');
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Input form */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Prompt input */}
        <div>
          <label className="label">Prompt</label>
          <textarea
            {...register('prompt', { required: 'Please enter a prompt' })}
            rows={4}
            className="textarea"
            placeholder="Enter a prompt to send to the LLM..."
          />
          {errors.prompt && (
            <p className="mt-1 text-sm text-red-600">{errors.prompt.message}</p>
          )}
        </div>

        {/* LLM settings section */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-slate-900">LLM Settings</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* LLM provider selection */}
            <div>
              <label className="label">LLM Provider</label>
              <select
                {...register('provider', { required: 'Please select an LLM provider' })}
                className="select"
              >
                {models && Object.keys(models).map((provider) => (
                  <option key={provider} value={provider}>
                    {provider === 'openai' ? 'OpenAI' : 
                     provider === 'grok' ? 'Llama' :
                     provider === 'claude' ? 'Claude' :
                     provider === 'gemini' ? 'Gemini' :
                     provider === 'deepseek' ? 'DeepSeek' : provider}
                  </option>
                ))}
              </select>
              {errors.provider && (
                <p className="mt-1 text-sm text-red-600">{errors.provider.message}</p>
              )}
            </div>

            {/* Model selection */}
            <div>
              <label className="label">Model</label>
              <select
                {...register('model', { required: 'Please select a model' })}
                className="select"
              >
                {models && models[selectedProvider]?.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
              {errors.model && (
                <p className="mt-1 text-sm text-red-600">{errors.model.message}</p>
              )}
            </div>
          </div>
        </div>

        {/* Submit buttons */}
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => {
              reset();
              setResult(null);
              setCurrentStep('idle');
              setConsensusResult(null);
              setError(null);
            }}
            className="btn-outline"
            disabled={isGenerating}
          >
            Reset
          </button>
          
          <button
            type="submit"
            className="btn-primary"
            disabled={isGenerating}
          >
            {isGenerating ? (
              <div className="flex items-center space-x-2">
                <div className="loading-spinner" />
                <span>Generating...</span>
              </div>
            ) : (
              'Generate LLM Response'
            )}
          </button>
        </div>
      </form>


      {/* Loading status */}
      {isGenerating && (
        <div className="space-y-4 fade-in">
          <div className="border-t border-slate-200 pt-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Processing Request</h3>
            <ConsensusLoading 
              currentStep={currentStep}
              consensusResult={consensusResult || undefined}
              error={error || undefined}
            />
          </div>
        </div>
      )}

      {/* Result display */}
      {result && (
        <div className="space-y-6 fade-in">
          <div className="border-t border-slate-200 pt-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-4">Generation Result</h3>
            
            {/* Response content */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <label className="label mb-0">LLM Response</label>
                <button
                  onClick={handleCopyResponse}
                  className="btn-outline text-xs"
                >
                  Copy
                </button>
              </div>
              <div className="code-block max-h-96 overflow-y-auto">
                {result.content}
              </div>
            </div>

            {/* Hash information */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <label className="label mb-0">Verification Hash</label>
                <button
                  onClick={handleCopyHash}
                  className="btn-outline text-xs"
                >
                  Copy
                </button>
              </div>
              <div className="hash-display">
                {result.hash_value}
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Please wait 10-30 seconds if verification fails right after generation
              </p>
            </div>

            {/* Meta information */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm mb-6">
              <div>
                <span className="font-medium text-slate-700">Response Time:</span>
                <span className="ml-2 text-slate-900">{formatResponseTime(result.response_time)}</span>
              </div>
              <div>
                <span className="font-medium text-slate-700">Model:</span>
                <span className="ml-2 text-slate-900">{result.model}</span>
              </div>
              <div>
                <span className="font-medium text-slate-700">Provider:</span>
                <span className="ml-2 text-slate-900">{result.provider}</span>
              </div>
            </div>

            {/* Consensus results - detailed card layout */}
            {result.consensus_result && (
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-slate-900 mb-4">Consensus Validation Results</h4>
                
                {/* Summary cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  <div className="card bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200 hover-lift">
                    <div className="text-sm text-emerald-700 font-semibold mb-2">Safe Votes</div>
                    <div className="text-3xl font-bold text-emerald-900">
                      {result.consensus_result.safe_votes}/{result.consensus_result.total_models}
                    </div>
                  </div>
                  <div className="card bg-gradient-to-br from-red-50 to-red-100 border-red-200 hover-lift">
                    <div className="text-sm text-red-700 font-semibold mb-2">Harmful Votes</div>
                    <div className="text-3xl font-bold text-red-900">
                      {result.consensus_result.harmful_votes}/{result.consensus_result.total_models}
                    </div>
                  </div>
                  <div className="card bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200 hover-lift">
                    <div className="text-sm text-blue-700 font-semibold mb-2">Threshold</div>
                    <div className="text-3xl font-bold text-blue-900">
                      {result.consensus_result.threshold}
                    </div>
                  </div>
                  <div className={`card hover-lift ${
                    result.consensus_result.consensus_passed 
                      ? 'bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200' 
                      : 'bg-gradient-to-br from-red-50 to-red-100 border-red-200'
                  }`}>
                    <div className={`text-sm font-semibold mb-2 ${
                      result.consensus_result.consensus_passed ? 'text-emerald-700' : 'text-red-700'
                    }`}>Status</div>
                    <div className={`text-3xl font-bold ${
                      result.consensus_result.consensus_passed ? 'text-emerald-900' : 'text-red-900'
                    }`}>
                      {result.consensus_result.consensus_passed ? 'PASSED' : 'FAILED'}
                    </div>
                  </div>
                </div>

                {/* Detailed message */}
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-md">
                  <div className="text-sm text-slate-700">
                    {result.consensus_result.consensus_message}
                  </div>
                </div>

                {/* Individual model responses */}
                {result.consensus_result.model_responses && (
                  <div className="mt-4">
                    <h5 className="text-sm font-semibold text-slate-900 mb-3">Individual Model Votes</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {Object.entries(result.consensus_result.model_responses).map(([provider, response]) => (
                        <div key={provider} className="card bg-slate-50">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium text-slate-900 capitalize">{provider}</span>
                            <span className={`px-2 py-1 text-xs font-medium rounded ${
                              response.is_harmful 
                                ? 'bg-red-100 text-red-800 border border-red-200' 
                                : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                            }`}>
                              {response.is_harmful ? 'Harmful' : 'Safe'}
                            </span>
                          </div>
                          <div className="text-xs text-slate-600">
                            Response time: {response.response_time.toFixed(2)}s
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Blockchain commit result */}
            {result.blockchain_commit && (
              <div className="card bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
                <h4 className="text-lg font-bold text-gray-900 mb-6">Blockchain Commit Result</h4>
                {result.blockchain_commit.status === 'success' || result.blockchain_commit.status === 'pending' ? (
                  <div className="space-y-5">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0">
                        <div className="w-14 h-14 bg-gradient-to-br from-emerald-500 to-emerald-600 text-white rounded-xl flex items-center justify-center shadow-lg">
                          <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                      </div>
                      <div>
                        <div className="text-xl font-bold text-emerald-900">Success</div>
                        <div className="text-sm text-gray-600">
                          Transaction has been submitted to the blockchain
                        </div>
                      </div>
                    </div>

                    {result.blockchain_commit.transaction_hash && (
                      <div className="p-5 bg-white border-2 border-blue-200 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200">
                        <div className="text-sm font-semibold text-gray-700 mb-3">Transaction Hash</div>
                        <div className="flex items-center justify-between gap-3">
                          <span className="font-mono text-xs text-gray-900 break-all">
                            {result.blockchain_commit.transaction_hash}
                          </span>
                          <a
                            href={getEtherscanUrl(result.blockchain_commit.transaction_hash)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="ml-2 inline-flex items-center px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg transition-colors duration-200 flex-shrink-0"
                          >
                            View on Etherscan
                            <svg className="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                          </a>
                        </div>
                      </div>
                    )}

                    {result.blockchain_commit.block_number && (
                      <div className="text-sm text-slate-600">
                        <span className="font-medium">Block Number:</span>
                        <span className="ml-2">{result.blockchain_commit.block_number}</span>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex items-center space-x-4 p-5 bg-white border-2 border-red-300 rounded-xl">
                    <div className="flex-shrink-0">
                      <div className="w-14 h-14 bg-gradient-to-br from-red-500 to-red-600 text-white rounded-xl flex items-center justify-center shadow-lg">
                        <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </div>
                    </div>
                    <div>
                      <div className="text-xl font-bold text-red-900">Failed</div>
                      <div className="text-sm text-gray-600">
                        {result.blockchain_commit.error_message}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Consensus-only result (validation failed, no LLM generation) */}
      {!result && consensusResult && !isGenerating && (
        <div className="space-y-6 fade-in">
          <div className="border-t border-slate-200 pt-6">
            <h3 className="text-lg font-bold text-gray-900 mb-6">Consensus Validation Result</h3>
            
            {/* Summary cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="card bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200 hover-lift">
                <div className="text-sm text-emerald-700 font-semibold mb-2">Safe Votes</div>
                <div className="text-3xl font-bold text-emerald-900">
                  {consensusResult.safe_votes}/{consensusResult.total_models}
                </div>
              </div>
              <div className="card bg-gradient-to-br from-red-50 to-red-100 border-red-200 hover-lift">
                <div className="text-sm text-red-700 font-semibold mb-2">Harmful Votes</div>
                <div className="text-3xl font-bold text-red-900">
                  {consensusResult.harmful_votes}/{consensusResult.total_models}
                </div>
              </div>
              <div className="card bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200 hover-lift">
                <div className="text-sm text-blue-700 font-semibold mb-2">Threshold</div>
                <div className="text-3xl font-bold text-blue-900">
                  {consensusResult.threshold}
                </div>
              </div>
              <div className={`card hover-lift ${
                consensusResult.consensus_passed 
                  ? 'bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200' 
                  : 'bg-gradient-to-br from-red-50 to-red-100 border-red-200'
              }`}>
                <div className={`text-sm font-semibold mb-2 ${
                  consensusResult.consensus_passed ? 'text-emerald-700' : 'text-red-700'
                }`}>Status</div>
                <div className={`text-3xl font-bold ${
                  consensusResult.consensus_passed ? 'text-emerald-900' : 'text-red-900'
                }`}>
                  {consensusResult.consensus_passed ? 'PASSED' : 'FAILED'}
                </div>
              </div>
            </div>

            {/* Detailed message */}
            <div className={`p-5 rounded-xl border-2 mb-6 ${
              consensusResult.consensus_passed
                ? 'bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200'
                : 'bg-gradient-to-br from-red-50 to-red-100 border-red-200'
            }`}>
              <div className="flex items-start space-x-4">
                <div className={`flex-shrink-0 w-12 h-12 rounded-lg flex items-center justify-center ${
                  consensusResult.consensus_passed
                    ? 'bg-emerald-500 text-white'
                    : 'bg-red-500 text-white'
                }`}>
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    {consensusResult.consensus_passed ? (
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    ) : (
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    )}
                  </svg>
                </div>
                <div className="flex-1">
                  <h4 className={`font-bold text-lg mb-1 ${
                    consensusResult.consensus_passed ? 'text-emerald-900' : 'text-red-900'
                  }`}>
                    {consensusResult.consensus_passed ? 'Validation Passed' : 'Validation Failed'}
                  </h4>
                  <p className={`text-sm ${
                    consensusResult.consensus_passed ? 'text-emerald-800' : 'text-red-800'
                  }`}>
                    {consensusResult.consensus_message}
                  </p>
                </div>
              </div>
            </div>

            {/* Individual model responses */}
            {consensusResult.model_responses && (
              <div>
                <h5 className="text-sm font-semibold text-gray-900 mb-4">Individual Model Votes</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(consensusResult.model_responses).map(([provider, response]) => (
                    <div key={provider} className="card bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200 hover-lift">
                      <div className="flex items-center justify-between mb-3">
                        <span className="font-semibold text-gray-900 capitalize">{provider}</span>
                        <span className={`px-3 py-1 text-xs font-semibold rounded-lg ${
                          response.is_harmful 
                            ? 'bg-red-100 text-red-800 border border-red-200' 
                            : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                        }`}>
                          {response.is_harmful ? 'Harmful' : 'Safe'}
                        </span>
                      </div>
                      <div className="text-xs text-gray-600">
                        <span className="font-medium">Model:</span> {response.model}
                      </div>
                      <div className="text-xs text-gray-600 mt-1">
                        <span className="font-medium">Response Time:</span> {response.response_time.toFixed(2)}s
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {!consensusResult.consensus_passed && (
              <div className="mt-6 p-5 bg-blue-50 border border-blue-200 rounded-xl">
                <div className="flex items-start space-x-3">
                  <svg className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <h5 className="font-semibold text-blue-900 mb-1">What does this mean?</h5>
                    <p className="text-sm text-blue-800">
                      The consensus validation system detected that your prompt may contain inappropriate or harmful content. 
                      The LLM generation was not performed to ensure safety. Please review and modify your prompt if you believe this was a mistake.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
