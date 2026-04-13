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

  const generateMutation = useMutation(llmApi.generate, {
    onMutate: () => {
      setIsGenerating(true);
      setResult(null);
      setError(null);
      setConsensusResult(null);
      setCurrentStep('consensus_validation');
    },
    onSuccess: (data) => {
      if (data.consensus_only) {
        setConsensusResult(data.consensus_result || null);
        setCurrentStep('completed');
        return;
      }
      setResult(data);
      setConsensusResult(data.consensus_result || null);
      setCurrentStep('completed');
      toast.success('Response generated and anchored.');
    },
    onError: (error: any) => {
      setCurrentStep('error');
      setError(error.response?.data?.error || error.message);
      toast.error(`Failed: ${error.response?.data?.error || error.message}`);
    },
    onSettled: () => {
      setIsGenerating(false);
    },
  });

  const simulateLoadingSteps = async () => {
    setCurrentStep('consensus_validation');
    await new Promise(resolve => setTimeout(resolve, 2000));
    setCurrentStep('llm_generation');
    await new Promise(resolve => setTimeout(resolve, 1500));
    setCurrentStep('hash_creation');
    await new Promise(resolve => setTimeout(resolve, 500));
    setCurrentStep('ipfs_pin');
    await new Promise(resolve => setTimeout(resolve, 500));
    setCurrentStep('blockchain_commit');
    await new Promise(resolve => setTimeout(resolve, 1000));
  };

  const onSubmit = async (data: FormData) => {
    const request: LLMRequest = {
      provider: data.provider,
      model: data.model,
      prompt: data.prompt,
      parameters: { temperature: 0.2, max_tokens: 200 },
      commit_to_blockchain: true,
    };
    simulateLoadingSteps();
    generateMutation.mutate(request);
  };

  return (
    <div className="space-y-6">
      {/* Input form */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="label">Prompt</label>
          <textarea
            {...register('prompt', { required: 'Please enter a prompt' })}
            rows={4}
            className="textarea"
            placeholder="Enter a prompt to send to the LLM..."
          />
          {errors.prompt && (
            <p className="mt-1 text-xs text-[var(--color-danger)]">{errors.prompt.message}</p>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">Provider</label>
            <select {...register('provider')} className="select">
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
          </div>
          <div>
            <label className="label">Model</label>
            <select {...register('model')} className="select">
              {models && models[selectedProvider]?.map((model) => (
                <option key={model} value={model}>{model}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex justify-end space-x-2 pt-2">
          <button
            type="button"
            onClick={() => {
              reset();
              setResult(null);
              setCurrentStep('idle');
              setConsensusResult(null);
              setError(null);
            }}
            className="btn-secondary"
            disabled={isGenerating}
          >
            Clear
          </button>
          <button type="submit" className="btn-primary" disabled={isGenerating}>
            {isGenerating ? (
              <span className="flex items-center space-x-2">
                <span className="loading-spinner" />
                <span>Processing...</span>
              </span>
            ) : (
              'Submit'
            )}
          </button>
        </div>
      </form>

      {/* Processing status */}
      {isGenerating && (
        <div className="fade-in">
          <div className="divider" />
          <ConsensusLoading
            currentStep={currentStep}
            consensusResult={consensusResult || undefined}
            error={error || undefined}
          />
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="fade-in">
          <div className="divider" />
          <h3 className="text-sm font-semibold text-[var(--color-ink)] mb-4">Result</h3>

          {/* LLM Response */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-1.5">
              <span className="label mb-0">Response</span>
              <button
                onClick={() => result.content && copyToClipboard(result.content).then(ok => ok && toast.success('Copied'))}
                className="text-xs text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
              >
                Copy
              </button>
            </div>
            <div className="mono-display max-h-64 overflow-y-auto whitespace-pre-wrap text-sm">
              {result.content}
            </div>
          </div>

          {/* Hash */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-1.5">
              <span className="label mb-0">Verification Hash</span>
              <button
                onClick={() => result.hash_value && copyToClipboard(result.hash_value).then(ok => ok && toast.success('Copied'))}
                className="text-xs text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
              >
                Copy
              </button>
            </div>
            <div className="mono-display">{result.hash_value}</div>
            <p className="text-xs text-[var(--color-ink-muted)] mt-1">
              Allow 10-30s before verifying a newly anchored record.
            </p>
          </div>

          {/* IPFS CID (V2) */}
          {result.ipfs_cid && (
            <div className="mb-4">
              <div className="flex items-center justify-between mb-1.5">
                <span className="label mb-0">IPFS CID</span>
                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => result.ipfs_cid && copyToClipboard(result.ipfs_cid).then(ok => ok && toast.success('Copied'))}
                    className="text-xs text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
                  >
                    Copy
                  </button>
                  {result.ipfs_gateway_url && (
                    <a
                      href={result.ipfs_gateway_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-[var(--color-accent)] hover:underline"
                    >
                      View on IPFS
                    </a>
                  )}
                </div>
              </div>
              <div className="mono-display">{result.ipfs_cid}</div>
            </div>
          )}

          {/* Metadata row */}
          <div className="grid grid-cols-3 gap-4 text-sm mb-6">
            <div>
              <span className="label">Time</span>
              <span className="block text-[var(--color-ink)]">{formatResponseTime(result.response_time)}</span>
            </div>
            <div>
              <span className="label">Model</span>
              <span className="block text-[var(--color-ink)]">{result.model}</span>
            </div>
            <div>
              <span className="label">Provider</span>
              <span className="block text-[var(--color-ink)]">{result.provider}</span>
            </div>
          </div>

          {/* Consensus results */}
          {result.consensus_result && (
            <ConsensusResultDisplay data={result.consensus_result} />
          )}

          {/* Blockchain commit */}
          {result.blockchain_commit && (
            <div className="card mt-4">
              <h4 className="text-sm font-semibold text-[var(--color-ink)] mb-3">Blockchain Anchor</h4>
              {result.blockchain_commit.status === 'success' || result.blockchain_commit.status === 'pending' ? (
                <div className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <span className="inline-block w-1.5 h-1.5 rounded-full bg-[var(--color-safe)]"></span>
                    <span className="text-sm font-medium text-[var(--color-ink)]">Transaction submitted</span>
                  </div>
                  {result.blockchain_commit.transaction_hash && (
                    <div>
                      <span className="label">Transaction Hash</span>
                      <div className="mono-display flex items-center justify-between gap-2">
                        <span className="break-all">{result.blockchain_commit.transaction_hash}</span>
                        <a
                          href={getEtherscanUrl(result.blockchain_commit.transaction_hash)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-[var(--color-accent)] hover:underline whitespace-nowrap"
                        >
                          Etherscan
                        </a>
                      </div>
                    </div>
                  )}
                  {result.blockchain_commit.block_number && (
                    <div className="text-xs text-[var(--color-ink-muted)]">
                      Block #{result.blockchain_commit.block_number}
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <span className="inline-block w-1.5 h-1.5 rounded-full bg-[var(--color-danger)]"></span>
                  <span className="text-sm text-[var(--color-danger)]">
                    {result.blockchain_commit.error_message || 'Transaction failed'}
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Consensus-only result (validation blocked generation) */}
      {!result && consensusResult && !isGenerating && (
        <div className="fade-in">
          <div className="divider" />
          <h3 className="text-sm font-semibold text-[var(--color-ink)] mb-4">Consensus Result</h3>
          <ConsensusResultDisplay data={consensusResult} />
          {!consensusResult.consensus_passed && (
            <div className="mt-4 p-3 bg-[var(--color-surface-dim)] border border-[var(--color-border)] rounded text-sm text-[var(--color-ink-light)]">
              The consensus system classified this prompt as potentially harmful.
              Generation was not performed. Modify the prompt and try again.
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ConsensusResultDisplay({ data }: { data: ConsensusResult }) {
  return (
    <div className="card">
      <h4 className="text-sm font-semibold text-[var(--color-ink)] mb-3">Consensus Validation</h4>

      {/* Vote summary */}
      <div className="grid grid-cols-4 gap-3 mb-4">
        <div className="text-center p-3 bg-[var(--color-surface-dim)] rounded">
          <div className="text-lg font-semibold text-[var(--color-safe)]">
            {data.safe_votes}
          </div>
          <div className="text-xs text-[var(--color-ink-muted)]">Safe</div>
        </div>
        <div className="text-center p-3 bg-[var(--color-surface-dim)] rounded">
          <div className="text-lg font-semibold text-[var(--color-danger)]">
            {data.harmful_votes}
          </div>
          <div className="text-xs text-[var(--color-ink-muted)]">Harmful</div>
        </div>
        <div className="text-center p-3 bg-[var(--color-surface-dim)] rounded">
          <div className="text-lg font-semibold text-[var(--color-ink)]">
            {data.threshold}
          </div>
          <div className="text-xs text-[var(--color-ink-muted)]">Threshold</div>
        </div>
        <div className="flex flex-col items-center justify-center p-3 bg-[var(--color-surface-dim)] rounded">
          <span className={data.consensus_passed ? 'badge-safe' : 'badge-danger'}>
            {data.consensus_passed ? 'Pass' : 'Fail'}
          </span>
          <div className="text-xs text-[var(--color-ink-muted)] mt-1">Result</div>
        </div>
      </div>

      {/* Message */}
      <p className="text-sm text-[var(--color-ink-light)] mb-4">{data.consensus_message}</p>

      {/* Individual votes */}
      {data.model_responses && (
        <div>
          <span className="label">Individual Votes</span>
          <div className="space-y-1.5 mt-1">
            {Object.entries(data.model_responses).map(([provider, response]) => (
              <div key={provider} className="flex items-center justify-between text-sm py-2 px-3 bg-[var(--color-surface-dim)] rounded">
                <span className="font-medium capitalize text-[var(--color-ink)]">{provider}</span>
                <div className="flex items-center space-x-3">
                  <span className={response.is_harmful ? 'badge-danger' : 'badge-safe'}>
                    {response.is_harmful ? 'Harmful' : 'Safe'}
                  </span>
                  <span className="text-xs text-[var(--color-ink-muted)] font-mono">
                    {response.response_time.toFixed(2)}s
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
