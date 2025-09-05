-- Migration: 002_add_search_indexes.sql
-- Description: 텍스트 검색을 위한 인덱스 추가
-- Created: 2024-01-02

-- 텍스트 검색을 위한 GIN 인덱스
CREATE INDEX idx_verification_records_prompt_gin ON verification_records USING gin(to_tsvector('english', prompt));
CREATE INDEX idx_verification_records_response_gin ON verification_records USING gin(to_tsvector('english', response));
CREATE INDEX idx_llm_requests_prompt_gin ON llm_requests USING gin(to_tsvector('english', prompt));

-- 트리그램 인덱스 (부분 문자열 검색용)
CREATE INDEX idx_verification_records_prompt_trgm ON verification_records USING gin(prompt gin_trgm_ops);
CREATE INDEX idx_verification_records_response_trgm ON verification_records USING gin(response gin_trgm_ops);
CREATE INDEX idx_llm_requests_prompt_trgm ON llm_requests USING gin(prompt gin_trgm_ops);
