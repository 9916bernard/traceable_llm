import { useState } from 'react';
import { useMutation } from 'react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { LLMRequest, LLMResponse, TestResponse, PromptFilterResponse } from '@/types';
import { llmApi } from '@/services/api';
import { formatResponseTime, copyToClipboard, getEtherscanUrl } from '@/utils';

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
  const [testResult, setTestResult] = useState<TestResponse | null>(null);
  const [isTesting, setIsTesting] = useState(false);
  const [filterResult, setFilterResult] = useState<PromptFilterResponse | null>(null);
  const [isFiltering, setIsFiltering] = useState(false);
  const [showCommitButton, setShowCommitButton] = useState(false);

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

  // 프롬프트 필터링 뮤테이션
  const filterMutation = useMutation(
    (prompt: string) => llmApi.filterPrompt({ prompt }),
    {
      onMutate: () => {
        setIsFiltering(true);
        setFilterResult(null);
        setShowCommitButton(false);
      },
      onSuccess: (data) => {
        setFilterResult(data);
        if (data.success && !data.filtered) {
          setShowCommitButton(true);
          toast.success('프롬프트가 적합합니다!');
        } else {
          setShowCommitButton(false);
          toast.error(data.message);
        }
      },
      onError: (error: any) => {
        const errorMessage = error.response?.data?.error || error.message;
        setFilterResult({
          success: false,
          filtered: true,
          message: `필터링 오류: ${errorMessage}`,
          error: errorMessage
        });
        setShowCommitButton(false);
        toast.error(`필터링 실패: ${errorMessage}`);
      },
      onSettled: () => {
        setIsFiltering(false);
      },
    }
  );

  // OpenRouter API 테스트 뮤테이션
  const testMutation = useMutation(
    (testData: { prompt: string; provider: string; model: string }) => 
      llmApi.testConnection(testData),
    {
      onMutate: () => {
        setIsTesting(true);
        setTestResult(null);
      },
      onSuccess: (data) => {
        setTestResult(data);
        if (data.success) {
          toast.success('OpenRouter API 연결 성공!');
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
    }
  );

  const onSubmit = (data: FormData) => {
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
        {/* 프롬프트 입력 */}
        <div>
          <label className="label">프롬프트</label>
          <textarea
            {...register('prompt', { required: '프롬프트를 입력해주세요' })}
            rows={4}
            className={`textarea ${showCommitButton ? 'bg-gray-50 cursor-not-allowed' : ''}`}
            placeholder="LLM에게 전달할 프롬프트를 입력하세요..."
            disabled={showCommitButton}
          />
          {errors.prompt && (
            <p className="mt-1 text-sm text-error-600">{errors.prompt.message}</p>
          )}
        </div>

        {/* LLM 설정 섹션 - 필터 통과 후에만 표시 */}
        {showCommitButton && (
          <div className="border-t pt-6 space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">LLM 설정</h3>
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
                      {provider === 'openai' ? 'OpenAI' : 
                       provider === 'grok' ? 'Llama' :
                       provider === 'claude' ? 'Claude' :
                       provider === 'gemini' ? 'Gemini' :
                       provider === 'deepseek' ? 'DeepSeek' : provider}
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
          </div>
        )}


        {/* 제출 버튼 */}
        <div className="flex justify-between">
          {!showCommitButton ? (
            <button
              type="button"
              onClick={() => {
                const currentData = watch();
                if (!currentData.prompt) {
                  toast.error('테스트를 위해 프롬프트를 입력해주세요');
                  return;
                }
                testMutation.mutate({
                  prompt: currentData.prompt,
                  provider: currentData.provider,
                  model: currentData.model
                });
              }}
              className="btn-outline"
              disabled={isTesting || isGenerating || isFiltering}
            >
              {isTesting ? (
                <div className="flex items-center space-x-2">
                  <div className="loading-spinner" />
                  <span>테스트 중...</span>
                </div>
              ) : (
                'OpenRouter API 테스트'
              )}
            </button>
          ) : (
            <div className="text-sm text-gray-500 flex items-center">
              <span className="mr-2">✓</span>
              프롬프트가 승인되었습니다. 다른 프롬프트를 사용하려면 초기화 버튼을 클릭하세요.
            </div>
          )}
          
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={() => {
                reset();
                setFilterResult(null);
                setShowCommitButton(false);
              }}
              className="btn-outline"
              disabled={isGenerating || isTesting || isFiltering}
            >
              {showCommitButton ? '새 프롬프트 입력' : '초기화'}
            </button>
            
            {!showCommitButton ? (
              <button
                type="button"
                onClick={() => {
                  const currentData = watch();
                  if (!currentData.prompt) {
                    toast.error('프롬프트를 입력해주세요');
                    return;
                  }
                  filterMutation.mutate(currentData.prompt);
                }}
                className="btn-primary"
                disabled={isGenerating || isTesting || isFiltering}
              >
                {isFiltering ? (
                  <div className="flex items-center space-x-2">
                    <div className="loading-spinner" />
                    <span>필터링 중...</span>
                  </div>
                ) : (
                  '프롬프트 필터링'
                )}
              </button>
            ) : (
              <button
                type="submit"
                className="btn-primary"
                disabled={isGenerating || isTesting || isFiltering}
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
            )}
          </div>
        </div>
      </form>

      {/* 프롬프트 필터링 결과 표시 */}
      {filterResult && (
        <div className="space-y-4 fade-in">
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">프롬프트 필터링 결과</h3>
            
            <div className={`p-4 rounded-lg ${
              filterResult.success && !filterResult.filtered
                ? 'bg-green-50 border border-green-200' 
                : 'bg-red-50 border border-red-200'
            }`}>
              <div className="flex items-center space-x-2 mb-2">
                <span className={`w-3 h-3 rounded-full ${
                  filterResult.success && !filterResult.filtered ? 'bg-green-500' : 'bg-red-500'
                }`} />
                <span className={`font-medium ${
                  filterResult.success && !filterResult.filtered ? 'text-green-800' : 'text-red-800'
                }`}>
                  {filterResult.success && !filterResult.filtered ? '프롬프트 승인' : '프롬프트 거부'}
                </span>
                {filterResult.category && (
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    filterResult.category === 'APPROPRIATE' 
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {filterResult.category}
                  </span>
                )}
              </div>
              
              <p className={`text-sm ${
                filterResult.success && !filterResult.filtered ? 'text-green-700' : 'text-red-700'
              }`}>
                {filterResult.message}
              </p>
              
              {filterResult.reason && (
                <div className="mt-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    필터링 이유:
                  </label>
                  <div className="text-sm text-gray-600">
                    {filterResult.reason}
                  </div>
                </div>
              )}
              
              {filterResult.confidence && (
                <div className="mt-2">
                  <span className="text-sm text-gray-600">
                    신뢰도: {(filterResult.confidence * 100).toFixed(1)}%
                  </span>
                </div>
              )}
              
              {filterResult.error && (
                <div className="mt-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    오류 메시지:
                  </label>
                  <div className="code-block bg-white text-red-600">
                    {filterResult.error}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 테스트 결과 표시 */}
      {testResult && (
        <div className="space-y-4 fade-in">
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">OpenRouter API 테스트 결과</h3>
            
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
                    LLM 응답:
                  </label>
                  <div className="code-block bg-white max-h-96 overflow-y-auto">
                    {testResult.response}
                  </div>
                </div>
              )}
              
              {testResult.prompt && (
                <div className="mt-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    테스트 프롬프트:
                  </label>
                  <div className="code-block bg-white max-h-32 overflow-y-auto">
                    {testResult.prompt}
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
              <div className="code-block max-h-96 overflow-y-auto">
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
