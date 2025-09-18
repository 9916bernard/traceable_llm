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

  // 검증 뮤테이션
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
      {/* 검증 폼 */}
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
            <p className="mt-1 text-sm text-error-600">{errors.hash_value.message}</p>
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

      {/* 검증 결과 */}
      {result && (
        <div className="space-y-4 fade-in">
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Verification Result</h3>
            
            {/* 검증 상태 */}
            <div className="mb-6">
              <div className="flex items-center space-x-4">
                <div className={`px-4 py-2 rounded-lg ${
                  result.verified 
                    ? 'bg-success-100 text-success-800 border border-success-200' 
                    : 'bg-error-100 text-error-800 border border-error-200'
                }`}>
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">
                      {result.verified ? '✅' : '❌'}
                    </span>
                    <span className="font-semibold">
                      {result.verified ? 'Verification Success' : 'Verification Failed'}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="mt-4">
                <p className="text-sm text-gray-700">{result.message}</p>
              </div>
            </div>

            {/* 출처 검증 정보 */}
            {result.origin_verification && (
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-3">Origin Verification</h4>
                <div className={`px-4 py-3 rounded-lg border ${
                  result.origin_verification.origin_verified
                    ? 'bg-green-50 border-green-200'
                    : 'bg-red-50 border-red-200'
                }`}>
                  <div className="flex items-center space-x-2 mb-3">
                    <span className="text-lg">
                      {result.origin_verification.origin_verified ? '🏠' : '⚠️'}
                    </span>
                    <span className={`font-semibold ${
                      result.origin_verification.origin_verified ? 'text-green-800' : 'text-red-800'
                    }`}>
                      {result.origin_verification.origin_verified 
                        ? 'Our Website Origin' 
                        : 'Different Origin'
                      }
                    </span>
                  </div>
                  
                  {/* 주소 비교 정보 */}
                  <div className="p-3 bg-white rounded border text-xs">
                    <div className="space-y-1">
                      <div>
                        <span className="font-medium text-gray-600">Etherscan From Address:</span>
                        <span className="ml-2 font-mono text-gray-800">
                          {result.origin_verification.from_address}
                        </span>
                      </div>
                      <div>
                        <span className="font-medium text-gray-600">Our Official Address:</span>
                        <span className="ml-2 font-mono text-gray-800">
                          {result.origin_verification.our_official_address}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-gray-600">Address Match:</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          result.origin_verification.origin_verified
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {result.origin_verification.origin_verified ? 'Match' : 'Mismatch'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* 트랜잭션 정보 */}
            <div className="space-y-4">
              <h4 className="font-medium text-gray-900">Transaction Information</h4>
              
              {/* 트랜잭션 해시 */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="label mb-0">Transaction Hash</label>
                  <button
                    onClick={handleCopyHash}
                    className="btn-outline text-xs"
                  >
                    복사
                  </button>
                </div>
                <div className="hash-display">
                  {result.transaction_hash}
                </div>
              </div>

              {/* 블록체인 검증 상세 정보 */}
              {result.blockchain_info && (
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h5 className="font-medium text-gray-900 mb-2">Blockchain Verification Details</h5>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">Status:</span>
                      <span className={`ml-2 badge ${
                        result.blockchain_info.status === 'success' ? 'badge-success' : 'badge-error'
                      }`}>
                        {result.blockchain_info.status}
                      </span>
                    </div>
                    {result.blockchain_info.block_number && (
                      <div>
                        <span className="font-medium text-gray-700">Block Number:</span>
                        <span className="ml-2">{result.blockchain_info.block_number}</span>
                      </div>
                    )}
                    {result.blockchain_info.gas_used && (
                      <div>
                        <span className="font-medium text-gray-700">Gas Used:</span>
                        <span className="ml-2">{result.blockchain_info.gas_used.toLocaleString()}</span>
                      </div>
                    )}
                    {result.blockchain_info.from_address && (
                      <div>
                        <span className="font-medium text-gray-700">From:</span>
                        <span className="ml-2 font-mono">{result.blockchain_info.from_address}</span>
                      </div>
                    )}
                    {result.blockchain_info.to_address && (
                      <div>
                        <span className="font-medium text-gray-700">To:</span>
                        <span className="ml-2 font-mono">{result.blockchain_info.to_address}</span>
                      </div>
                    )}
                    {result.blockchain_info.etherscan_url && (
                      <div>
                        <span className="font-medium text-gray-700">Etherscan:</span>
                        <a
                          href={result.blockchain_info.etherscan_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="ml-2 text-primary-600 hover:text-primary-800"
                        >
                          View Transaction →
                        </a>
                      </div>
                    )}
                    {result.blockchain_info.error_message && (
                      <div>
                        <span className="font-medium text-gray-700">Error Message:</span>
                        <span className="ml-2 text-error-600">{result.blockchain_info.error_message}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
