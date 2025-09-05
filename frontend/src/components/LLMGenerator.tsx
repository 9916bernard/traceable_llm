import { useState } from 'react';
import { useMutation } from 'react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { LLMRequest, LLMResponse } from '@/types';
import { llmApi } from '@/services/api';
import { formatResponseTime, copyToClipboard, getEtherscanUrl } from '@/utils';

interface LLMGeneratorProps {
  models?: Record<string, string[]>;
}

interface FormData {
  provider: string;
  model: string;
  prompt: string;
  temperature: number;
  max_tokens: number;
  commit_to_blockchain: boolean;
}

export default function LLMGenerator({ models }: LLMGeneratorProps) {
  const [result, setResult] = useState<LLMResponse | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string; response?: string; error?: string } | null>(null);
  const [isTesting, setIsTesting] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
    reset,
  } = useForm<FormData>({
    defaultValues: {
      provider: 'openai',
      model: 'gpt-3.5-turbo',
      temperature: 0.7,
      max_tokens: 1000,
      commit_to_blockchain: true,
    },
  });

  const selectedProvider = watch('provider');

  // LLM 생성 뮤테이션
  const generateMutation = useMutation(llmApi.generate, {
    onMutate: () => {
      setIsGenerating(true);
      setResult(null);
    },
    onSuccess: (data) => {
      setResult(data);
      toast.success('LLM 응답이 생성되었습니다!');
    },
    onError: (error: any) => {
      toast.error(`생성 실패: ${error.response?.data?.error || error.message}`);
    },
    onSettled: () => {
      setIsGenerating(false);
    },
  });

  // OpenAI API 테스트 뮤테이션
  const testMutation = useMutation(llmApi.testConnection, {
    onMutate: () => {
      setIsTesting(true);
      setTestResult(null);
    },
    onSuccess: (data) => {
      setTestResult(data);
      if (data.success) {
        toast.success('OpenAI API 연결 성공!');
      } else {
        toast.error(`API 연결 실패: ${data.message}`);
      }
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.error || error.message;
      setTestResult({
        success: false,
        message: 'API 연결 실패',
        error: errorMessage
      });
      toast.error(`API 연결 실패: ${errorMessage}`);
    },
    onSettled: () => {
      setIsTesting(false);
    },
  });

  const onSubmit = (data: FormData) => {
    const request: LLMRequest = {
      provider: data.provider,
      model: data.model,
      prompt: data.prompt,
      parameters: {
        temperature: data.temperature,
        max_tokens: data.max_tokens,
      },
      commit_to_blockchain: data.commit_to_blockchain,
    };

    generateMutation.mutate(request);
  };

  const handleCopyHash = async () => {
    if (result?.hash_value) {
      const success = await copyToClipboard(result.hash_value);
      if (success) {
        toast.success('해시값이 클립보드에 복사되었습니다');
      } else {
        toast.error('복사에 실패했습니다');
      }
    }
  };

  const handleCopyResponse = async () => {
    if (result?.content) {
      const success = await copyToClipboard(result.content);
      if (success) {
        toast.success('응답이 클립보드에 복사되었습니다');
      } else {
        toast.error('복사에 실패했습니다');
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* 입력 폼 */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* LLM 제공자 선택 */}
          <div>
            <label className="label">LLM 제공자</label>
            <select
              {...register('provider', { required: 'LLM 제공자를 선택해주세요' })}
              className="select"
            >
              {models && Object.keys(models).map((provider) => (
                <option key={provider} value={provider}>
                  {provider === 'openai' ? 'OpenAI' : provider === 'anthropic' ? 'Anthropic' : provider}
                </option>
              ))}
            </select>
            {errors.provider && (
              <p className="mt-1 text-sm text-error-600">{errors.provider.message}</p>
            )}
          </div>

          {/* 모델 선택 */}
          <div>
            <label className="label">모델</label>
            <select
              {...register('model', { required: '모델을 선택해주세요' })}
              className="select"
            >
              {models && models[selectedProvider]?.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>
            {errors.model && (
              <p className="mt-1 text-sm text-error-600">{errors.model.message}</p>
            )}
          </div>
        </div>

        {/* 프롬프트 입력 */}
        <div>
          <label className="label">프롬프트</label>
          <textarea
            {...register('prompt', { required: '프롬프트를 입력해주세요' })}
            rows={4}
            className="textarea"
            placeholder="LLM에게 전달할 프롬프트를 입력하세요..."
          />
          {errors.prompt && (
            <p className="mt-1 text-sm text-error-600">{errors.prompt.message}</p>
          )}
        </div>

        {/* 파라미터 설정 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="label">Temperature ({watch('temperature')})</label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              {...register('temperature', { valueAsNumber: true })}
              className="w-full"
            />
          </div>

          <div>
            <label className="label">Max Tokens</label>
            <input
              type="number"
              min="1"
              max="4000"
              {...register('max_tokens', { valueAsNumber: true })}
              className="input"
            />
          </div>
        </div>

        {/* 블록체인 커밋 옵션 */}
        <div className="flex items-center">
          <input
            type="checkbox"
            {...register('commit_to_blockchain')}
            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
          <label className="ml-2 block text-sm text-gray-900">
            블록체인에 해시 커밋
          </label>
        </div>

        {/* 제출 버튼 */}
        <div className="flex justify-between">
          <button
            type="button"
            onClick={() => testMutation.mutate()}
            className="btn-outline"
            disabled={isTesting || isGenerating}
          >
            {isTesting ? (
              <div className="flex items-center space-x-2">
                <div className="loading-spinner" />
                <span>테스트 중...</span>
              </div>
            ) : (
              'OpenAI API 테스트'
            )}
          </button>
          
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={() => reset()}
              className="btn-outline"
              disabled={isGenerating || isTesting}
            >
              초기화
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={isGenerating || isTesting}
            >
              {isGenerating ? (
                <div className="flex items-center space-x-2">
                  <div className="loading-spinner" />
                  <span>생성 중...</span>
                </div>
              ) : (
                'LLM 응답 생성'
              )}
            </button>
          </div>
        </div>
      </form>

      {/* 테스트 결과 표시 */}
      {testResult && (
        <div className="space-y-4 fade-in">
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">OpenAI API 테스트 결과</h3>
            
            <div className={`p-4 rounded-lg ${
              testResult.success 
                ? 'bg-green-50 border border-green-200' 
                : 'bg-red-50 border border-red-200'
            }`}>
              <div className="flex items-center space-x-2 mb-2">
                <span className={`w-3 h-3 rounded-full ${
                  testResult.success ? 'bg-green-500' : 'bg-red-500'
                }`} />
                <span className={`font-medium ${
                  testResult.success ? 'text-green-800' : 'text-red-800'
                }`}>
                  {testResult.success ? '연결 성공' : '연결 실패'}
                </span>
              </div>
              
              <p className={`text-sm ${
                testResult.success ? 'text-green-700' : 'text-red-700'
              }`}>
                {testResult.message}
              </p>
              
              {testResult.response && (
                <div className="mt-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    OpenAI 응답:
                  </label>
                  <div className="code-block bg-white">
                    {testResult.response}
                  </div>
                </div>
              )}
              
              {testResult.error && (
                <div className="mt-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    오류 메시지:
                  </label>
                  <div className="code-block bg-white text-red-600">
                    {testResult.error}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 결과 표시 */}
      {result && (
        <div className="space-y-4 fade-in">
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">생성 결과</h3>
            
            {/* 응답 내용 */}
            <div className="mb-4">
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
                {result.content}
              </div>
            </div>

            {/* 해시 정보 */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <label className="label mb-0">검증 해시</label>
                <button
                  onClick={handleCopyHash}
                  className="btn-outline text-xs"
                >
                  복사
                </button>
              </div>
              <div className="hash-display">
                {result.hash_value}
              </div>
            </div>

            {/* 메타 정보 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="font-medium text-gray-700">응답 시간:</span>
                <span className="ml-2">{formatResponseTime(result.response_time)}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">모델:</span>
                <span className="ml-2">{result.model}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">제공자:</span>
                <span className="ml-2">{result.provider}</span>
              </div>
            </div>

            {/* 블록체인 커밋 결과 */}
            {result.blockchain_commit && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">블록체인 커밋 결과</h4>
                {result.blockchain_commit.status === 'success' ? (
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <span className="badge-success">성공</span>
                    </div>
                    {result.blockchain_commit.transaction_hash && (
                      <div>
                        <span className="font-medium text-gray-700">트랜잭션 해시:</span>
                        <a
                          href={getEtherscanUrl(result.blockchain_commit.transaction_hash)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="ml-2 text-primary-600 hover:text-primary-800 font-mono text-sm"
                        >
                          {result.blockchain_commit.transaction_hash.substring(0, 20)}...
                        </a>
                      </div>
                    )}
                    {result.blockchain_commit.block_number && (
                      <div>
                        <span className="font-medium text-gray-700">블록 번호:</span>
                        <span className="ml-2">{result.blockchain_commit.block_number}</span>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <span className="badge-error">실패</span>
                    <span className="text-sm text-gray-600">
                      {result.blockchain_commit.error_message}
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
