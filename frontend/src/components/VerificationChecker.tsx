import { useState } from 'react';
import { useMutation } from 'react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { VerificationRequest, VerificationResponse } from '@/types';
import { verificationApi } from '@/services/api';
import { copyToClipboard, getEtherscanUrl } from '@/utils';

interface FormData {
  hash_value: string;
}

export default function VerificationChecker() {
  const [result, setResult] = useState<VerificationResponse | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<FormData>();

  const verifyMutation = useMutation(verificationApi.verify, {
    onMutate: () => {
      setIsVerifying(true);
      setResult(null);
    },
    onSuccess: (data) => {
      setResult(data);
      toast[data.verified ? 'success' : 'error'](
        data.verified ? 'Record verified.' : 'Verification failed.'
      );
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.response?.data?.error || error.message}`);
    },
    onSettled: () => {
      setIsVerifying(false);
    },
  });

  const onSubmit = (data: FormData) => {
    verifyMutation.mutate({ hash_value: data.hash_value.trim() });
  };

  return (
    <div className="space-y-6">
      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="label">Transaction Hash</label>
          <textarea
            {...register('hash_value', {
              required: 'Enter a transaction hash',
              minLength: { value: 64, message: 'Invalid hash length' },
            })}
            rows={2}
            className="textarea font-mono text-xs"
            placeholder="0x..."
          />
          {errors.hash_value && (
            <p className="mt-1 text-xs text-[var(--color-danger)]">{errors.hash_value.message}</p>
          )}
        </div>

        <div className="flex justify-end space-x-2">
          <button type="button" onClick={() => reset()} className="btn-secondary" disabled={isVerifying}>
            Clear
          </button>
          <button type="submit" className="btn-primary" disabled={isVerifying}>
            {isVerifying ? (
              <span className="flex items-center space-x-2">
                <span className="loading-spinner" />
                <span>Verifying...</span>
              </span>
            ) : 'Verify'}
          </button>
        </div>
      </form>

      {/* Results */}
      {result && (
        <div className="fade-in">
          <div className="divider" />

          {/* Status */}
          <div className="flex items-center space-x-3 mb-6 p-4 rounded border border-[var(--color-border)] bg-[var(--color-surface-dim)]">
            <span className={`inline-block w-2 h-2 rounded-full ${
              result.verified ? 'bg-[var(--color-safe)]' : 'bg-[var(--color-danger)]'
            }`}></span>
            <div>
              <span className={`text-sm font-semibold ${
                result.verified ? 'text-[var(--color-safe)]' : 'text-[var(--color-danger)]'
              }`}>
                {result.verified ? 'Verified' : 'Not Verified'}
              </span>
              <span className="text-sm text-[var(--color-ink-light)] ml-2">{result.message}</span>
            </div>
          </div>

          {/* Three-check summary */}
          <div className="grid grid-cols-3 gap-3 mb-6">
            <CheckCard
              label="Hash Exists"
              status={result.verified}
              detail={result.verified ? 'Found on-chain' : 'Not found'}
            />
            <CheckCard
              label="Hash Match"
              status={result.verified}
              detail={result.verified ? 'Recalculation matches' : 'N/A'}
            />
            <CheckCard
              label="Origin"
              status={result.origin_verification?.origin_verified ?? null}
              detail={
                result.origin_verification
                  ? result.origin_verification.origin_verified ? 'Verified sender' : 'External sender'
                  : 'N/A'
              }
            />
          </div>

          {/* Origin details */}
          {result.origin_verification && (
            <div className="card mb-4">
              <span className="label">Origin Details</span>
              <div className="space-y-2 mt-2">
                <div>
                  <span className="text-xs text-[var(--color-ink-muted)]">From</span>
                  <div className="mono-display">{result.origin_verification.from_address}</div>
                </div>
                <div>
                  <span className="text-xs text-[var(--color-ink-muted)]">Expected</span>
                  <div className="mono-display">{result.origin_verification.our_official_address}</div>
                </div>
              </div>
            </div>
          )}

          {/* Transaction hash */}
          <div className="card mb-4">
            <div className="flex items-center justify-between mb-1.5">
              <span className="label mb-0">Transaction Hash</span>
              <button
                onClick={() => result.transaction_hash && copyToClipboard(result.transaction_hash).then(ok => ok && toast.success('Copied'))}
                className="text-xs text-[var(--color-ink-muted)] hover:text-[var(--color-ink)]"
              >
                Copy
              </button>
            </div>
            <div className="mono-display">{result.transaction_hash}</div>
          </div>

          {/* Decoded input data */}
          {result.input_data && (
            <div className="card mb-4">
              <span className="label">Anchored Record</span>
              <div className="space-y-3 mt-2">
                <div className="grid grid-cols-2 gap-3">
                  <Field label="Provider" value={result.input_data.llm_provider} />
                  <Field label="Model" value={result.input_data.model_name} />
                </div>
                {result.input_data.timestamp && (
                  <Field label="Timestamp" value={result.input_data.timestamp} mono />
                )}
                {result.input_data.consensus_votes && (
                  <Field label="Consensus Votes" value={result.input_data.consensus_votes} />
                )}
                <Field label="Prompt" value={result.input_data.prompt} />
                <Field label="Response" value={result.input_data.response} />
                <Field label="Hash" value={result.input_data.hash} mono />
                {result.input_data.parameters && (
                  <Field label="Parameters" value={result.input_data.parameters} mono />
                )}
              </div>
            </div>
          )}

          {/* Blockchain info */}
          {result.blockchain_info && (
            <div className="card">
              <span className="label">Blockchain Details</span>
              <div className="space-y-2 mt-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-[var(--color-ink-muted)]">Status</span>
                  <span className={result.blockchain_info.status === 'success' ? 'badge-safe' : 'badge-danger'}>
                    {result.blockchain_info.status}
                  </span>
                </div>
                {result.blockchain_info.block_number && (
                  <div className="flex justify-between">
                    <span className="text-[var(--color-ink-muted)]">Block</span>
                    <span className="font-mono text-xs">{result.blockchain_info.block_number}</span>
                  </div>
                )}
                {result.blockchain_info.gas_used && (
                  <div className="flex justify-between">
                    <span className="text-[var(--color-ink-muted)]">Gas Used</span>
                    <span className="font-mono text-xs">{result.blockchain_info.gas_used.toLocaleString()}</span>
                  </div>
                )}
                {result.blockchain_info.from_address && (
                  <div>
                    <span className="text-[var(--color-ink-muted)] text-xs">From</span>
                    <div className="mono-display mt-1">{result.blockchain_info.from_address}</div>
                  </div>
                )}
                {result.blockchain_info.to_address && (
                  <div>
                    <span className="text-[var(--color-ink-muted)] text-xs">To</span>
                    <div className="mono-display mt-1">{result.blockchain_info.to_address}</div>
                  </div>
                )}
                {result.blockchain_info.etherscan_url && (
                  <a
                    href={result.blockchain_info.etherscan_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-[var(--color-accent)] hover:underline"
                  >
                    View on Etherscan
                  </a>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function CheckCard({ label, status, detail }: { label: string; status: boolean | null; detail: string }) {
  return (
    <div className="p-3 bg-[var(--color-surface-dim)] rounded border border-[var(--color-border)] text-center">
      <div className="text-xs text-[var(--color-ink-muted)] mb-1">{label}</div>
      <div className={`text-sm font-semibold ${
        status === true ? 'text-[var(--color-safe)]' :
        status === false ? 'text-[var(--color-danger)]' :
        'text-[var(--color-ink-muted)]'
      }`}>
        {status === true ? '\u2713' : status === false ? '\u2717' : '\u2014'}
      </div>
      <div className="text-xs text-[var(--color-ink-muted)] mt-0.5">{detail}</div>
    </div>
  );
}

function Field({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <span className="text-xs text-[var(--color-ink-muted)]">{label}</span>
      <div className={`text-sm mt-0.5 ${mono ? 'mono-display' : 'text-[var(--color-ink)] bg-[var(--color-surface-dim)] px-3 py-2 rounded border border-[var(--color-border)]'}`}>
        {value}
      </div>
    </div>
  );
}
