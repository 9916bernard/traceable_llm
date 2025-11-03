import { useState } from 'react';
import { useMutation } from 'react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { VerificationRequest, VerificationResponse } from '@/types';
import { verificationApi } from '@/services/api';
import { formatDate, formatHash, copyToClipboard, getEtherscanUrl } from '@/utils';

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

  // Verification mutation
  const verifyMutation = useMutation(verificationApi.verify, {
    onMutate: () => {
      setIsVerifying(true);
      setResult(null);
    },
    onSuccess: (data) => {
      setResult(data);
      if (data.verified) {
        toast.success('Verification completed!');
      } else {
        toast.error('Verification failed.');
      }
    },
    onError: (error: any) => {
      toast.error(`Verification failed: ${error.response?.data?.error || error.message}`);
    },
    onSettled: () => {
      setIsVerifying(false);
    },
  });

  const onSubmit = (data: FormData) => {
    const request: VerificationRequest = {
      hash_value: data.hash_value.trim(),
    };

    verifyMutation.mutate(request);
  };

  const handleCopyHash = async () => {
    if (result?.transaction_hash) {
      const success = await copyToClipboard(result.transaction_hash);
      if (success) {
        toast.success('Transaction hash copied to clipboard');
      } else {
        toast.error('Copy failed');
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Verification form */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="label">Transaction Hash to Verify</label>
          <textarea
            {...register('hash_value', { 
              required: 'Please enter a transaction hash',
              minLength: { value: 64, message: 'Please enter a valid transaction hash' }
            })}
            rows={3}
            className="textarea font-mono text-sm"
            placeholder="Enter a Sepolia transaction hash to verify..."
          />
          {errors.hash_value && (
            <p className="mt-1 text-sm text-red-600">{errors.hash_value.message}</p>
          )}
        </div>

        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => reset()}
            className="btn-outline"
            disabled={isVerifying}
          >
            Reset
          </button>
          <button
            type="submit"
            className="btn-primary"
            disabled={isVerifying}
          >
            {isVerifying ? (
              <div className="flex items-center space-x-2">
                <div className="loading-spinner" />
                <span>Verifying...</span>
              </div>
            ) : (
              'Verify'
            )}
          </button>
        </div>
      </form>

      {/* Verification results */}
      {result && (
        <div className="space-y-6 fade-in">
          <div className="border-t border-slate-200 pt-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-6">Verification Result</h3>
            
            {/* Overall status card */}
            <div className={`card mb-8 ${
              result.verified 
                ? 'bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-300 shadow-lg' 
                : 'bg-gradient-to-br from-red-50 to-red-100 border-red-300 shadow-lg'
            }`}>
              <div className="flex items-center space-x-5">
                <div className={`flex-shrink-0 w-20 h-20 rounded-xl flex items-center justify-center shadow-lg ${
                  result.verified 
                    ? 'bg-gradient-to-br from-emerald-500 to-emerald-600 text-white' 
                    : 'bg-gradient-to-br from-red-500 to-red-600 text-white'
                }`}>
                  <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    {result.verified ? (
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                    ) : (
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                    )}
                  </svg>
                </div>
                <div className="flex-1">
                  <div className={`text-2xl font-bold mb-2 ${
                    result.verified ? 'text-emerald-900' : 'text-red-900'
                  }`}>
                      {result.verified ? 'Verification Success' : 'Verification Failed'}
                  </div>
                  <div className="text-sm text-gray-600">
                    {result.message}
                  </div>
                </div>
              </div>
            </div>

            {/* Three separate verification cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              
              {/* Card 1: Hash Existence Check */}
              <div className="card bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200 hover-lift">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <h4 className="font-bold text-gray-900">Hash Existence</h4>
                </div>
                <div className="space-y-3">
                  <div className={`inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-semibold shadow-sm ${
                    result.verified 
                      ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' 
                      : 'bg-red-100 text-red-800 border border-red-300'
                  }`}>
                    {result.verified ? 'Found on Blockchain' : 'Not Found'}
                  </div>
                  <p className="text-xs text-gray-600 leading-relaxed">
                    {result.verified 
                      ? 'The transaction hash exists on the blockchain and has been confirmed.'
                      : 'The provided hash was not found on the blockchain network.'}
                  </p>
                </div>
              </div>

              {/* Card 2: Re-calculate Verification */}
              <div className="card bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200 hover-lift">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <h4 className="font-bold text-gray-900">Re-calculate Check</h4>
                </div>
                <div className="space-y-3">
                  <div className={`inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-semibold shadow-sm ${
                    result.verified 
                      ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' 
                      : 'bg-gray-200 text-gray-700 border border-gray-300'
                  }`}>
                    {result.verified ? 'Match' : 'N/A'}
                  </div>
                  <p className="text-xs text-gray-600 leading-relaxed">
                    {result.verified 
                      ? 'Hash recalculation from blockchain data matches the original.'
                      : 'Cannot recalculate as hash was not found.'}
                  </p>
                </div>
              </div>

              {/* Card 3: Origin Verification */}
              <div className="card bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200 hover-lift">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                    </svg>
                  </div>
                  <h4 className="font-bold text-gray-900">Origin Check</h4>
                </div>
                <div className="space-y-3">
                  {result.origin_verification ? (
                    <>
                      <div className={`inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-semibold shadow-sm ${
                        result.origin_verification.origin_verified 
                          ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' 
                          : 'bg-amber-100 text-amber-800 border border-amber-300'
                      }`}>
                        {result.origin_verification.origin_verified ? 'Our Website' : 'External Source'}
                      </div>
                      <p className="text-xs text-gray-600 leading-relaxed">
                        {result.origin_verification.origin_verified 
                          ? 'Transaction originated from our official address.'
                          : 'Transaction came from a different address.'}
                      </p>
                    </>
                  ) : (
                    <>
                      <div className="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-semibold bg-gray-200 text-gray-700 border border-gray-300 shadow-sm">
                        N/A
                      </div>
                      <p className="text-xs text-gray-600 leading-relaxed">
                        Origin information not available.
                      </p>
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* Detailed origin verification information */}
            {result.origin_verification && (
              <div className="card bg-slate-50 mb-6">
                <h4 className="font-semibold text-slate-900 mb-4">Origin Verification Details</h4>
                <div className="space-y-3">
                  <div>
                    <div className="text-xs font-medium text-slate-600 mb-1">Transaction From Address</div>
                    <div className="font-mono text-sm text-slate-900 bg-white px-3 py-2 rounded border border-slate-200">
                      {result.origin_verification.from_address}
                    </div>
                  </div>
                      <div>
                    <div className="text-xs font-medium text-slate-600 mb-1">Our Official Address</div>
                    <div className="font-mono text-sm text-slate-900 bg-white px-3 py-2 rounded border border-slate-200">
                      {result.origin_verification.our_official_address}
                    </div>
                      </div>
                      <div>
                    <div className="text-xs font-medium text-slate-600 mb-1">Match Status</div>
                    <div className={`inline-flex items-center px-3 py-1.5 rounded font-medium text-sm ${
                          result.origin_verification.origin_verified
                        ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                        : 'bg-amber-100 text-amber-800 border border-amber-200'
                        }`}>
                      {result.origin_verification.origin_verified ? 'Addresses Match' : 'Addresses Do Not Match'}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Transaction information */}
            <div className="card">
              <h4 className="font-semibold text-slate-900 mb-4">Transaction Information</h4>
              
              {/* Transaction hash */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-slate-700">Transaction Hash</label>
                  <button
                    onClick={handleCopyHash}
                    className="btn-outline text-xs"
                  >
                    Copy
                  </button>
                </div>
                <div className="hash-display">
                  {result.transaction_hash}
                </div>
              </div>

              {/* Input Data (Transaction Details) */}
              {result.input_data && (
                <div className="mb-6 p-5 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
                  <h5 className="font-bold text-gray-900 mb-4 flex items-center space-x-2">
                    <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span>Transaction Data</span>
                  </h5>
                  <div className="space-y-4">
                    {/* Model Info */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-xs font-semibold text-gray-600 mb-1">LLM Provider</div>
                        <div className="text-sm font-medium text-gray-900 bg-white px-3 py-2 rounded-lg border border-blue-100">
                          {result.input_data.llm_provider}
                        </div>
                      </div>
                      <div>
                        <div className="text-xs font-semibold text-gray-600 mb-1">Model Name</div>
                        <div className="text-sm font-medium text-gray-900 bg-white px-3 py-2 rounded-lg border border-blue-100">
                          {result.input_data.model_name}
                        </div>
                      </div>
                    </div>

                    {/* Timestamp */}
                    {result.input_data.timestamp && (
                      <div>
                        <div className="text-xs font-semibold text-gray-600 mb-1">Timestamp</div>
                        <div className="text-sm font-mono text-gray-900 bg-white px-3 py-2 rounded-lg border border-blue-100">
                          {result.input_data.timestamp}
                        </div>
                      </div>
                    )}

                    {/* Consensus Votes */}
                    {result.input_data.consensus_votes && (
                      <div>
                        <div className="text-xs font-semibold text-gray-600 mb-1">Consensus Votes</div>
                        <div className="text-sm font-medium text-gray-900 bg-white px-3 py-2 rounded-lg border border-blue-100">
                          {result.input_data.consensus_votes}
                        </div>
                      </div>
                    )}

                    {/* Prompt */}
                    <div>
                      <div className="text-xs font-semibold text-gray-600 mb-1">Prompt</div>
                      <div className="text-sm text-gray-900 bg-white px-4 py-3 rounded-lg border border-blue-100 max-h-32 overflow-y-auto custom-scrollbar">
                        {result.input_data.prompt}
                      </div>
                    </div>

                    {/* Response */}
                    <div>
                      <div className="text-xs font-semibold text-gray-600 mb-1">Response</div>
                      <div className="text-sm text-gray-900 bg-white px-4 py-3 rounded-lg border border-blue-100 max-h-40 overflow-y-auto custom-scrollbar">
                        {result.input_data.response}
                      </div>
                    </div>

                    {/* Hash */}
                    <div>
                      <div className="text-xs font-semibold text-gray-600 mb-1">Hash</div>
                      <div className="text-xs font-mono text-gray-700 bg-white px-3 py-2 rounded-lg border border-blue-100 break-all">
                        {result.input_data.hash}
                      </div>
                    </div>

                    {/* Parameters */}
                    {result.input_data.parameters && (
                      <div>
                        <div className="text-xs font-semibold text-gray-600 mb-1">Parameters</div>
                        <div className="text-xs font-mono text-gray-700 bg-white px-3 py-2 rounded-lg border border-blue-100">
                          {result.input_data.parameters}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Blockchain verification details */}
              {result.blockchain_info && (
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-xs font-medium text-slate-600 mb-1">Status</div>
                      <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                        result.blockchain_info.status === 'success' 
                          ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' 
                          : 'bg-red-100 text-red-800 border border-red-200'
                      }`}>
                        {result.blockchain_info.status}
                      </span>
                    </div>
                    {result.blockchain_info.block_number && (
                      <div>
                        <div className="text-xs font-medium text-slate-600 mb-1">Block Number</div>
                        <div className="text-sm text-slate-900">{result.blockchain_info.block_number}</div>
                      </div>
                    )}
                  </div>
                  
                    {result.blockchain_info.gas_used && (
                      <div>
                      <div className="text-xs font-medium text-slate-600 mb-1">Gas Used</div>
                      <div className="text-sm text-slate-900">{result.blockchain_info.gas_used.toLocaleString()}</div>
                      </div>
                    )}
                  
                    {result.blockchain_info.from_address && (
                      <div>
                      <div className="text-xs font-medium text-slate-600 mb-1">From Address</div>
                      <div className="font-mono text-sm text-slate-900 bg-slate-50 px-3 py-2 rounded">
                        {result.blockchain_info.from_address}
                      </div>
                      </div>
                    )}
                  
                    {result.blockchain_info.to_address && (
                      <div>
                      <div className="text-xs font-medium text-slate-600 mb-1">To Address</div>
                      <div className="font-mono text-sm text-slate-900 bg-slate-50 px-3 py-2 rounded">
                        {result.blockchain_info.to_address}
                      </div>
                      </div>
                    )}
                  
                    {result.blockchain_info.etherscan_url && (
                      <div>
                        <a
                          href={result.blockchain_info.etherscan_url}
                          target="_blank"
                          rel="noopener noreferrer"
                        className="inline-flex items-center text-sm font-medium text-slate-900 hover:text-slate-700 underline"
                        >
                        View on Etherscan
                        <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                        </a>
                      </div>
                    )}
                  
                    {result.blockchain_info.error_message && (
                    <div className="p-3 bg-slate-100 rounded border border-slate-300">
                      <div className="text-xs font-medium text-slate-700 mb-1">Error Message</div>
                      <div className="text-sm text-slate-900">{result.blockchain_info.error_message}</div>
                      </div>
                    )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
