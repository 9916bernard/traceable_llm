-- Migration: 003_add_views_and_functions.sql
-- Description: 통계 뷰와 검색 함수 추가
-- Created: 2024-01-03

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
