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
    if (result?.verification_record.hash_value) {
      const success = await copyToClipboard(result.verification_record.hash_value);
      if (success) {
        toast.success('해시값이 클립보드에 복사되었습니다');
      } else {
        toast.error('복사에 실패했습니다');
      }
    }
  };

  const handleCopyResponse = async () => {
    if (result?.verification_record.response) {
      const success = await copyToClipboard(result.verification_record.response);
      if (success) {
        toast.success('응답이 클립보드에 복사되었습니다');
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
          <label className="label">검증할 해시값</label>
          <textarea
            {...register('hash_value', { 
              required: '해시값을 입력해주세요',
              minLength: { value: 64, message: '유효한 SHA-256 해시값을 입력해주세요' }
            })}
            rows={3}
            className="textarea font-mono text-sm"
            placeholder="검증할 SHA-256 해시값을 입력하세요..."
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
              
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center space-x-2">
                  <span className={`w-3 h-3 rounded-full ${
                    result.hash_verified ? 'bg-success-500' : 'bg-error-500'
                  }`} />
                  <span className="text-sm text-gray-700">
                    해시 검증: {result.hash_verified ? '성공' : '실패'}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`w-3 h-3 rounded-full ${
                    result.blockchain_verified ? 'bg-success-500' : 'bg-error-500'
                  }`} />
                  <span className="text-sm text-gray-700">
                    블록체인 검증: {result.blockchain_verified ? '성공' : '실패'}
                  </span>
                </div>
              </div>
            </div>

            {/* 검증 기록 정보 */}
            <div className="space-y-4">
              <h4 className="font-medium text-gray-900">검증 기록 정보</h4>
              
              {/* 해시 정보 */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="label mb-0">해시값</label>
                  <button
                    onClick={handleCopyHash}
                    className="btn-outline text-xs"
                  >
                    복사
                  </button>
                </div>
                <div className="hash-display">
                  {result.verification_record.hash_value}
                </div>
              </div>

              {/* 프롬프트 */}
              <div>
                <label className="label">프롬프트</label>
                <div className="code-block">
                  {result.verification_record.prompt}
                </div>
              </div>

              {/* 응답 */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="label mb-0">LLM 응답</label>
                  <button
                    onClick={handleCopyResponse}
                    className="btn-outline text-xs"
                  >
                    복사
                  </button>
                </div>
                <div className="code-block">
                  {result.verification_record.response}
                </div>
              </div>

              {/* 메타 정보 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-700">LLM 제공자:</span>
                  <span className="ml-2">{result.verification_record.llm_provider}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">모델:</span>
                  <span className="ml-2">{result.verification_record.model_name}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">생성 시간:</span>
                  <span className="ml-2">{formatDate(result.verification_record.timestamp)}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">검증 상태:</span>
                  <span className={`ml-2 badge ${
                    result.verification_record.verified ? 'badge-success' : 'badge-error'
                  }`}>
                    {result.verification_record.verified ? '검증됨' : '미검증'}
                  </span>
                </div>
              </div>

              {/* 파라미터 정보 */}
              {result.verification_record.parameters && (
                <div>
                  <label className="label">LLM 파라미터</label>
                  <div className="code-block">
                    <pre>{JSON.stringify(result.verification_record.parameters, null, 2)}</pre>
                  </div>
                </div>
              )}

              {/* 블록체인 정보 */}
              {result.verification_record.transaction_hash && (
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h5 className="font-medium text-gray-900 mb-2">블록체인 정보</h5>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="font-medium text-gray-700">트랜잭션 해시:</span>
                      <a
                        href={getEtherscanUrl(result.verification_record.transaction_hash)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="ml-2 text-primary-600 hover:text-primary-800 font-mono"
                      >
                        {formatHash(result.verification_record.transaction_hash, 10)}
                      </a>
                    </div>
                    {result.verification_record.block_number && (
                      <div>
                        <span className="font-medium text-gray-700">블록 번호:</span>
                        <span className="ml-2">{result.verification_record.block_number}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

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
                    {result.blockchain_info.timestamp && (
                      <div>
                        <span className="font-medium text-gray-700">블록체인 타임스탬프:</span>
                        <span className="ml-2">{formatDate(new Date(result.blockchain_info.timestamp * 1000).toISOString())}</span>
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
