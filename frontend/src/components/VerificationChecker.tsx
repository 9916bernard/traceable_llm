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
        toast.success('검증이 완료되었습니다!');
      } else {
        toast.error('검증에 실패했습니다.');
      }
    },
    onError: (error: any) => {
      toast.error(`검증 실패: ${error.response?.data?.error || error.message}`);
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
        toast.success('트랜잭션 해시가 클립보드에 복사되었습니다');
      } else {
        toast.error('복사에 실패했습니다');
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* 검증 폼 */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="label">검증할 트랜잭션 해시</label>
          <textarea
            {...register('hash_value', { 
              required: '트랜잭션 해시를 입력해주세요',
              minLength: { value: 64, message: '유효한 트랜잭션 해시를 입력해주세요' }
            })}
            rows={3}
            className="textarea font-mono text-sm"
            placeholder="검증할 Sepolia 트랜잭션 해시를 입력하세요..."
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
            초기화
          </button>
          <button
            type="submit"
            className="btn-primary"
            disabled={isVerifying}
          >
            {isVerifying ? (
              <div className="flex items-center space-x-2">
                <div className="loading-spinner" />
                <span>검증 중...</span>
              </div>
            ) : (
              '검증하기'
            )}
          </button>
        </div>
      </form>

      {/* 검증 결과 */}
      {result && (
        <div className="space-y-4 fade-in">
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">검증 결과</h3>
            
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
                      {result.verified ? '검증 성공' : '검증 실패'}
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
                <h4 className="font-medium text-gray-900 mb-3">출처 검증</h4>
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
                        ? '우리 웹사이트 출처' 
                        : '다른 출처'
                      }
                    </span>
                  </div>
                  
                  {/* 주소 비교 정보 */}
                  <div className="p-3 bg-white rounded border text-xs">
                    <div className="space-y-1">
                      <div>
                        <span className="font-medium text-gray-600">Etherscan From 주소:</span>
                        <span className="ml-2 font-mono text-gray-800">
                          {result.origin_verification.from_address}
                        </span>
                      </div>
                      <div>
                        <span className="font-medium text-gray-600">우리 공식 주소:</span>
                        <span className="ml-2 font-mono text-gray-800">
                          {result.origin_verification.our_official_address}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-gray-600">주소 일치:</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          result.origin_verification.origin_verified
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {result.origin_verification.origin_verified ? '일치' : '불일치'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* 트랜잭션 정보 */}
            <div className="space-y-4">
              <h4 className="font-medium text-gray-900">트랜잭션 정보</h4>
              
              {/* 트랜잭션 해시 */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="label mb-0">트랜잭션 해시</label>
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
                  <h5 className="font-medium text-gray-900 mb-2">블록체인 검증 상세</h5>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">상태:</span>
                      <span className={`ml-2 badge ${
                        result.blockchain_info.status === 'success' ? 'badge-success' : 'badge-error'
                      }`}>
                        {result.blockchain_info.status}
                      </span>
                    </div>
                    {result.blockchain_info.block_number && (
                      <div>
                        <span className="font-medium text-gray-700">블록 번호:</span>
                        <span className="ml-2">{result.blockchain_info.block_number}</span>
                      </div>
                    )}
                    {result.blockchain_info.gas_used && (
                      <div>
                        <span className="font-medium text-gray-700">사용된 가스:</span>
                        <span className="ml-2">{result.blockchain_info.gas_used.toLocaleString()}</span>
                      </div>
                    )}
                    {result.blockchain_info.from_address && (
                      <div>
                        <span className="font-medium text-gray-700">발신자:</span>
                        <span className="ml-2 font-mono">{result.blockchain_info.from_address}</span>
                      </div>
                    )}
                    {result.blockchain_info.to_address && (
                      <div>
                        <span className="font-medium text-gray-700">수신자:</span>
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
                          트랜잭션 보기 →
                        </a>
                      </div>
                    )}
                    {result.blockchain_info.error_message && (
                      <div>
                        <span className="font-medium text-gray-700">에러 메시지:</span>
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
