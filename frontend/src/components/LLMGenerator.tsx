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
      toast.success('LLM response has been generated!');
    },
    onError: (error: any) => {
      toast.error(`Generation failed: ${error.response?.data?.error || error.message}`);
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
          toast.success('Prompt is appropriate!');
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
          message: `Filtering error: ${errorMessage}`,
          error: errorMessage
        });
        setShowCommitButton(false);
        toast.error(`Filtering failed: ${errorMessage}`);
      },
      onSettled: () => {
        setIsFiltering(false);
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
          <label className="label">Prompt</label>
          <textarea
            {...register('prompt', { required: 'Please enter a prompt' })}
            rows={4}
            className={`textarea ${showCommitButton ? 'bg-gray-50 cursor-not-allowed' : ''}`}
            placeholder="Enter a prompt to send to the LLM..."
            disabled={showCommitButton}
          />
          {errors.prompt && (
            <p className="mt-1 text-sm text-error-600">{errors.prompt.message}</p>
          )}
        </div>

        {/* LLM 설정 섹션 - 필터 통과 후에만 표시 */}
        {showCommitButton && (
          <div className="border-t pt-6 space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">LLM Settings</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* LLM 제공자 선택 */}
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
                  <p className="mt-1 text-sm text-error-600">{errors.provider.message}</p>
                )}
              </div>

              {/* 모델 선택 */}
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
                  <p className="mt-1 text-sm text-error-600">{errors.model.message}</p>
                )}
              </div>
            </div>
          </div>
        )}


        {/* 제출 버튼 */}
        <div className="flex justify-between">
          {!showCommitButton ? (
            <div className="text-sm text-gray-500">
              Please enter a prompt and proceed with filtering.
            </div>
          ) : (
            <div className="text-sm text-gray-500 flex items-center">
              <span className="mr-2">✓</span>
              Prompt has been approved. Click the reset button to use a different prompt.
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
              disabled={isGenerating || isFiltering}
            >
              {showCommitButton ? 'New Prompt' : 'Reset'}
            </button>
            
            {!showCommitButton ? (
              <button
                type="button"
                onClick={() => {
                  const currentData = watch();
                  if (!currentData.prompt) {
                    toast.error('Please enter a prompt');
                    return;
                  }
                  filterMutation.mutate(currentData.prompt);
                }}
                className="btn-primary"
                disabled={isGenerating || isFiltering}
              >
                {isFiltering ? (
                  <div className="flex items-center space-x-2">
                    <div className="loading-spinner" />
                    <span>Filtering...</span>
                  </div>
                ) : (
                  'Filter Prompt'
                )}
              </button>
            ) : (
              <button
                type="submit"
                className="btn-primary"
                disabled={isGenerating || isFiltering}
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
            )}
          </div>
        </div>
      </form>

      {/* 프롬프트 필터링 결과 표시 */}
      {filterResult && (
        <div className="space-y-4 fade-in">
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Prompt Filtering Result</h3>
            
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
                      {filterResult.success && !filterResult.filtered ? 'Prompt Approved' : 'Prompt Rejected'}
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
                    Filtering Reason:
                  </label>
                  <div className="text-sm text-gray-600">
                    {filterResult.reason}
                  </div>
                </div>
              )}
              
              {filterResult.confidence && (
                <div className="mt-2">
                  <span className="text-sm text-gray-600">
                    Confidence: {(filterResult.confidence * 100).toFixed(1)}%
                  </span>
                </div>
              )}
              
              {filterResult.error && (
                <div className="mt-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Error Message:
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


      {/* 결과 표시 */}
      {result && (
        <div className="space-y-4 fade-in">
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Generation Result</h3>
            
            {/* 응답 내용 */}
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

            {/* 해시 정보 */}
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
            </div>

            {/* 메타 정보 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="font-medium text-gray-700">Response Time:</span>
                <span className="ml-2">{formatResponseTime(result.response_time)}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Model:</span>
                <span className="ml-2">{result.model}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Provider:</span>
                <span className="ml-2">{result.provider}</span>
              </div>
            </div>

            {/* 블록체인 커밋 결과 */}
            {result.blockchain_commit && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Blockchain Commit Result</h4>
                {result.blockchain_commit.status === 'success' ? (
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <span className="badge-success">Success</span>
                    </div>
                    {result.blockchain_commit.transaction_hash && (
                      <div>
                        <span className="font-medium text-gray-700">Transaction Hash:</span>
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
                        <span className="font-medium text-gray-700">Block Number:</span>
                        <span className="ml-2">{result.blockchain_commit.block_number}</span>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <span className="badge-error">Failed</span>
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
