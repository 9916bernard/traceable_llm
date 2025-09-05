-- Migration: 001_initial_schema.sql
-- Description: 초기 데이터베이스 스키마 생성
-- Created: 2024-01-01

-- 확장 기능 활성화
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 검증 기록 테이블
CREATE TABLE verification_records (
    id SERIAL PRIMARY KEY,
    hash_value VARCHAR(64) UNIQUE NOT NULL,
    llm_provider VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    parameters JSONB,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    transaction_hash VARCHAR(66),
    block_number BIGINT,
    verified BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- LLM 요청 로그 테이블
CREATE TABLE llm_requests (
    id SERIAL PRIMARY KEY,
    request_id UUID UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
    llm_provider VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    prompt TEXT NOT NULL,
    parameters JSONB,
    response TEXT,
    response_time DECIMAL(10, 3),
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    error_message TEXT,
    verification_record_id INTEGER REFERENCES verification_records(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 인덱스 생성
CREATE INDEX idx_verification_records_hash_value ON verification_records(hash_value);
CREATE INDEX idx_verification_records_llm_provider ON verification_records(llm_provider);
CREATE INDEX idx_verification_records_model_name ON verification_records(model_name);
CREATE INDEX idx_verification_records_timestamp ON verification_records(timestamp);
CREATE INDEX idx_verification_records_verified ON verification_records(verified);
CREATE INDEX idx_verification_records_created_at ON verification_records(created_at);
CREATE INDEX idx_verification_records_transaction_hash ON verification_records(transaction_hash);

CREATE INDEX idx_llm_requests_request_id ON llm_requests(request_id);
CREATE INDEX idx_llm_requests_llm_provider ON llm_requests(llm_provider);
CREATE INDEX idx_llm_requests_model_name ON llm_requests(model_name);
CREATE INDEX idx_llm_requests_status ON llm_requests(status);
CREATE INDEX idx_llm_requests_created_at ON llm_requests(created_at);
CREATE INDEX idx_llm_requests_verification_record_id ON llm_requests(verification_record_id);

-- 업데이트 시간 자동 갱신을 위한 트리거 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 생성
CREATE TRIGGER update_verification_records_updated_at 
    BEFORE UPDATE ON verification_records 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_llm_requests_updated_at 
    BEFORE UPDATE ON llm_requests 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
