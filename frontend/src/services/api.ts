import axios, { AxiosResponse } from 'axios';
import {
  LLMRequest,
  LLMResponse,
  VerificationRequest,
  VerificationResponse,
  VerificationRecord,
  BlockchainStatus,
  BlockchainCommitRequest,
  BlockchainCommitResponse,
  SearchRequest,
  SearchResponse,
  PaginatedResponse,
  TestResponse,
} from '@/types';

// API 기본 설정
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(`API Error: ${error.response?.status} ${error.config?.url}`, error.response?.data);
    return Promise.reject(error);
  }
);

// LLM API 서비스
export const llmApi = {
  // LLM 응답 생성
  generate: async (request: LLMRequest): Promise<LLMResponse> => {
    const response: AxiosResponse<LLMResponse> = await api.post('/llm/generate', request);
    return response.data;
  },

  // 사용 가능한 모델 목록 조회
  getModels: async (): Promise<Record<string, string[]>> => {
    const response: AxiosResponse<Record<string, string[]>> = await api.get('/llm/models');
    return response.data;
  },

  // LLM 서비스 상태 확인
  healthCheck: async (): Promise<{ status: string; test_response?: string; error?: string }> => {
    const response = await api.get('/llm/health');
    return response.data;
  },

  // OpenRouter API 연결 테스트
  testConnection: async (data?: { prompt?: string; provider?: string; model?: string }): Promise<TestResponse> => {
    const response = await api.post('/llm/test', data || {});
    return response.data;
  },
};

// 검증 API 서비스
export const verificationApi = {
  // 해시 검증
  verify: async (request: VerificationRequest): Promise<VerificationResponse> => {
    const response: AxiosResponse<VerificationResponse> = await api.post('/verification/verify', request);
    return response.data;
  },

  // 검증 기록 조회
  getRecord: async (recordId: number): Promise<VerificationRecord> => {
    const response: AxiosResponse<VerificationRecord> = await api.get(`/verification/record/${recordId}`);
    return response.data;
  },

  // 검증 기록 목록 조회
  getRecords: async (params?: {
    page?: number;
    per_page?: number;
    provider?: string;
    verified?: boolean;
  }): Promise<PaginatedResponse<VerificationRecord>> => {
    const response: AxiosResponse<PaginatedResponse<VerificationRecord>> = await api.get('/verification/records', {
      params,
    });
    return response.data;
  },

  // 내용으로 검색
  search: async (request: SearchRequest): Promise<SearchResponse> => {
    const response: AxiosResponse<SearchResponse> = await api.post('/verification/search', request);
    return response.data;
  },
};

// 블록체인 API 서비스
export const blockchainApi = {
  // 블록체인 상태 조회
  getStatus: async (): Promise<BlockchainStatus> => {
    const response: AxiosResponse<BlockchainStatus> = await api.get('/blockchain/status');
    return response.data;
  },

  // 블록체인에서 해시 검증
  verifyHash: async (hashValue: string): Promise<{ exists: boolean; timestamp?: number; status: string; error_message?: string }> => {
    const response = await api.get(`/blockchain/verify/${hashValue}`);
    return response.data;
  },

  // 해시를 블록체인에 커밋
  commitHash: async (request: BlockchainCommitRequest): Promise<BlockchainCommitResponse> => {
    const response: AxiosResponse<BlockchainCommitResponse> = await api.post('/blockchain/commit', request);
    return response.data;
  },
};

export default api;
