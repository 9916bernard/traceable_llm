// LLM 관련 타입 정의
export interface LLMProvider {
  name: string;
  models: string[];
}

export interface LLMRequest {
  provider: string;
  model: string;
  prompt: string;
  parameters?: {
    temperature?: number;
    max_tokens?: number;
    top_p?: number;
    frequency_penalty?: number;
    presence_penalty?: number;
  };
  commit_to_blockchain?: boolean;
}

export interface LLMResponse {
  request_id: string;
  content: string;
  hash_value: string;
  verification_record_id: number;
  response_time: number;
  model: string;
  provider: string;
  blockchain_commit?: {
    transaction_hash?: string;
    block_number?: number;
    status: string;
    error_message?: string;
  };
}

// 검증 관련 타입 정의
export interface VerificationRecord {
  id: number;
  hash_value: string;
  llm_provider: string;
  model_name: string;
  prompt: string;
  response: string;
  parameters: Record<string, any>;
  timestamp: string;
  transaction_hash?: string;
  block_number?: number;
  verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface VerificationRequest {
  hash_value: string;
}

export interface VerificationResponse {
  verified: boolean;
  transaction_hash: string;
  blockchain_info: {
    exists: boolean;
    transaction_hash?: string;
    block_number?: number;
    gas_used?: number;
    status: string;
    is_success?: boolean;
    from_address?: string;
    to_address?: string;
    value?: string;
    etherscan_url?: string;
    error_message?: string;
  };
  message: string;
}

// 블록체인 관련 타입 정의
export interface BlockchainStatus {
  network_id: number;
  latest_block: number;
  gas_price: string;
  account_balance: string;
  status: string;
  error_message?: string;
  network_name?: string;
  explorer_url?: string;
  faucet_url?: string;
}

export interface BlockchainCommitRequest {
  hash_value: string;
  verification_record_id: number;
}

export interface BlockchainCommitResponse {
  transaction_hash?: string;
  block_number?: number;
  gas_used?: number;
  status: string;
  error_message?: string;
}

// API 응답 타입 정의
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  records: T[];
  total: number;
  pages: number;
  current_page: number;
  per_page: number;
}

// UI 관련 타입 정의
export interface SearchRequest {
  query: string;
  type?: 'prompt' | 'response' | 'both';
}

export interface SearchResponse {
  records: VerificationRecord[];
  total: number;
}
