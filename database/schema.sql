-- LLM Verification System Database Schema
-- PostgreSQL 데이터베이스 스키마

-- 데이터베이스 생성 (필요시)
-- CREATE DATABASE llm_verification;
-- CREATE DATABASE llm_verification_dev;
-- CREATE DATABASE llm_verification_test;

-- 확장 기능 활성화
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 검증 기록 테이블
CREATE TABLE IF NOT EXISTS verification_records (
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
CREATE TABLE IF NOT EXISTS llm_requests (
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
CREATE INDEX IF NOT EXISTS idx_verification_records_hash_value ON verification_records(hash_value);
CREATE INDEX IF NOT EXISTS idx_verification_records_llm_provider ON verification_records(llm_provider);
CREATE INDEX IF NOT EXISTS idx_verification_records_model_name ON verification_records(model_name);
CREATE INDEX IF NOT EXISTS idx_verification_records_timestamp ON verification_records(timestamp);
CREATE INDEX IF NOT EXISTS idx_verification_records_verified ON verification_records(verified);
CREATE INDEX IF NOT EXISTS idx_verification_records_created_at ON verification_records(created_at);
CREATE INDEX IF NOT EXISTS idx_verification_records_transaction_hash ON verification_records(transaction_hash);

CREATE INDEX IF NOT EXISTS idx_llm_requests_request_id ON llm_requests(request_id);
CREATE INDEX IF NOT EXISTS idx_llm_requests_llm_provider ON llm_requests(llm_provider);
CREATE INDEX IF NOT EXISTS idx_llm_requests_model_name ON llm_requests(model_name);
CREATE INDEX IF NOT EXISTS idx_llm_requests_status ON llm_requests(status);
CREATE INDEX IF NOT EXISTS idx_llm_requests_created_at ON llm_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_llm_requests_verification_record_id ON llm_requests(verification_record_id);

-- 텍스트 검색을 위한 인덱스
CREATE INDEX IF NOT EXISTS idx_verification_records_prompt_gin ON verification_records USING gin(to_tsvector('english', prompt));
CREATE INDEX IF NOT EXISTS idx_verification_records_response_gin ON verification_records USING gin(to_tsvector('english', response));
CREATE INDEX IF NOT EXISTS idx_llm_requests_prompt_gin ON llm_requests USING gin(to_tsvector('english', prompt));

-- 트리그램 인덱스 (부분 문자열 검색용)
CREATE INDEX IF NOT EXISTS idx_verification_records_prompt_trgm ON verification_records USING gin(prompt gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_verification_records_response_trgm ON verification_records USING gin(response gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_llm_requests_prompt_trgm ON llm_requests USING gin(prompt gin_trgm_ops);

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

-- 통계 뷰 생성
CREATE OR REPLACE VIEW verification_stats AS
SELECT 
    llm_provider,
    model_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN verified = true THEN 1 END) as verified_records,
    COUNT(CASE WHEN transaction_hash IS NOT NULL THEN 1 END) as blockchain_committed,
    AVG(CASE WHEN lr.response_time IS NOT NULL THEN lr.response_time END) as avg_response_time,
    MIN(created_at) as first_record,
    MAX(created_at) as last_record
FROM verification_records vr
LEFT JOIN llm_requests lr ON vr.id = lr.verification_record_id
GROUP BY llm_provider, model_name;

-- 일별 통계 뷰
CREATE OR REPLACE VIEW daily_stats AS
SELECT 
    DATE(created_at) as date,
    llm_provider,
    COUNT(*) as records_count,
    COUNT(CASE WHEN verified = true THEN 1 END) as verified_count,
    COUNT(CASE WHEN transaction_hash IS NOT NULL THEN 1 END) as blockchain_count
FROM verification_records
GROUP BY DATE(created_at), llm_provider
ORDER BY date DESC;

-- 검색 함수
CREATE OR REPLACE FUNCTION search_verification_records(
    search_query TEXT,
    search_type VARCHAR DEFAULT 'both'
)
RETURNS TABLE (
    id INTEGER,
    hash_value VARCHAR(64),
    llm_provider VARCHAR(50),
    model_name VARCHAR(100),
    prompt TEXT,
    response TEXT,
    timestamp TIMESTAMP WITH TIME ZONE,
    verified BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        vr.id,
        vr.hash_value,
        vr.llm_provider,
        vr.model_name,
        vr.prompt,
        vr.response,
        vr.timestamp,
        vr.verified,
        vr.created_at,
        CASE 
            WHEN search_type = 'prompt' THEN ts_rank(to_tsvector('english', vr.prompt), plainto_tsquery('english', search_query))
            WHEN search_type = 'response' THEN ts_rank(to_tsvector('english', vr.response), plainto_tsquery('english', search_query))
            ELSE GREATEST(
                ts_rank(to_tsvector('english', vr.prompt), plainto_tsquery('english', search_query)),
                ts_rank(to_tsvector('english', vr.response), plainto_tsquery('english', search_query))
            )
        END as rank
    FROM verification_records vr
    WHERE 
        (search_type = 'prompt' AND to_tsvector('english', vr.prompt) @@ plainto_tsquery('english', search_query))
        OR (search_type = 'response' AND to_tsvector('english', vr.response) @@ plainto_tsquery('english', search_query))
        OR (search_type = 'both' AND (
            to_tsvector('english', vr.prompt) @@ plainto_tsquery('english', search_query)
            OR to_tsvector('english', vr.response) @@ plainto_tsquery('english', search_query)
        ))
    ORDER BY rank DESC, vr.created_at DESC
    LIMIT 100;
END;
$$ LANGUAGE plpgsql;

-- 샘플 데이터 삽입 (개발용)
INSERT INTO verification_records (
    hash_value, llm_provider, model_name, prompt, response, parameters, timestamp, verified
) VALUES (
    'a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456',
    'openai',
    'gpt-3.5-turbo',
    'Hello, how are you?',
    'Hello! I am doing well, thank you for asking. How can I help you today?',
    '{"temperature": 0.7, "max_tokens": 100}',
    NOW() - INTERVAL '1 day',
    true
) ON CONFLICT (hash_value) DO NOTHING;

-- 권한 설정 (필요시)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO llm_verification_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO llm_verification_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO llm_verification_user;
