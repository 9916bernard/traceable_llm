#!/bin/bash

# LLM Verification System Database Setup Script
# PostgreSQL 데이터베이스 설정 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 환경 변수 확인
check_env_vars() {
    log_info "환경 변수 확인 중..."
    
    if [ -z "$DB_HOST" ]; then
        DB_HOST="localhost"
        log_warning "DB_HOST가 설정되지 않았습니다. 기본값(localhost)을 사용합니다."
    fi
    
    if [ -z "$DB_PORT" ]; then
        DB_PORT="5432"
        log_warning "DB_PORT가 설정되지 않았습니다. 기본값(5432)을 사용합니다."
    fi
    
    if [ -z "$DB_USER" ]; then
        log_error "DB_USER 환경 변수가 필요합니다."
        exit 1
    fi
    
    if [ -z "$DB_PASSWORD" ]; then
        log_error "DB_PASSWORD 환경 변수가 필요합니다."
        exit 1
    fi
    
    if [ -z "$DB_NAME" ]; then
        DB_NAME="llm_verification"
        log_warning "DB_NAME이 설정되지 않았습니다. 기본값(llm_verification)을 사용합니다."
    fi
    
    log_success "환경 변수 확인 완료"
}

# PostgreSQL 연결 테스트
test_connection() {
    log_info "PostgreSQL 연결 테스트 중..."
    
    if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
        log_success "PostgreSQL 연결 성공"
    else
        log_error "PostgreSQL 연결 실패. 설정을 확인해주세요."
        exit 1
    fi
}

# 데이터베이스 생성
create_database() {
    log_info "데이터베이스 생성 중..."
    
    # 데이터베이스 존재 여부 확인
    if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        log_warning "데이터베이스 '$DB_NAME'이 이미 존재합니다."
        read -p "기존 데이터베이스를 삭제하고 다시 생성하시겠습니까? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
            log_success "기존 데이터베이스 삭제 완료"
        else
            log_info "기존 데이터베이스를 사용합니다."
            return 0
        fi
    fi
    
    # 데이터베이스 생성
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME;"
    log_success "데이터베이스 '$DB_NAME' 생성 완료"
}

# 스키마 적용
apply_schema() {
    log_info "데이터베이스 스키마 적용 중..."
    
    # 메인 스키마 적용
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f schema.sql
    log_success "메인 스키마 적용 완료"
    
    # 마이그레이션 적용
    log_info "마이그레이션 적용 중..."
    for migration in migrations/*.sql; do
        if [ -f "$migration" ]; then
            log_info "마이그레이션 적용: $(basename "$migration")"
            PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$migration"
        fi
    done
    log_success "모든 마이그레이션 적용 완료"
}

# 샘플 데이터 삽입
insert_sample_data() {
    log_info "샘플 데이터 삽입 중..."
    
    # 샘플 데이터 SQL
    cat << EOF | PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"
-- 샘플 검증 기록
INSERT INTO verification_records (
    hash_value, llm_provider, model_name, prompt, response, parameters, timestamp, verified
) VALUES 
(
    'a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456',
    'openai',
    'gpt-3.5-turbo',
    'Hello, how are you?',
    'Hello! I am doing well, thank you for asking. How can I help you today?',
    '{"temperature": 0.7, "max_tokens": 100}',
    NOW() - INTERVAL '1 day',
    true
),
(
    'b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234567',
    'anthropic',
    'claude-3-sonnet-20240229',
    'What is artificial intelligence?',
    'Artificial intelligence (AI) is a branch of computer science that aims to create machines capable of intelligent behavior.',
    '{"temperature": 0.5, "max_tokens": 200}',
    NOW() - INTERVAL '2 hours',
    true
),
(
    'c3d4e5f6789012345678901234567890abcdef1234567890abcdef12345678',
    'openai',
    'gpt-4',
    'Explain quantum computing',
    'Quantum computing is a type of computation that harnesses quantum mechanical phenomena to process information.',
    '{"temperature": 0.3, "max_tokens": 300}',
    NOW() - INTERVAL '30 minutes',
    false
)
ON CONFLICT (hash_value) DO NOTHING;

-- 샘플 LLM 요청 로그
INSERT INTO llm_requests (
    llm_provider, model_name, prompt, parameters, response, response_time, status, verification_record_id
) VALUES 
(
    'openai',
    'gpt-3.5-turbo',
    'Hello, how are you?',
    '{"temperature": 0.7, "max_tokens": 100}',
    'Hello! I am doing well, thank you for asking. How can I help you today?',
    1.234,
    'success',
    1
),
(
    'anthropic',
    'claude-3-sonnet-20240229',
    'What is artificial intelligence?',
    '{"temperature": 0.5, "max_tokens": 200}',
    'Artificial intelligence (AI) is a branch of computer science that aims to create machines capable of intelligent behavior.',
    2.456,
    'success',
    2
),
(
    'openai',
    'gpt-4',
    'Explain quantum computing',
    '{"temperature": 0.3, "max_tokens": 300}',
    'Quantum computing is a type of computation that harnesses quantum mechanical phenomena to process information.',
    3.789,
    'success',
    3
);
EOF
    
    log_success "샘플 데이터 삽입 완료"
}

# 데이터베이스 상태 확인
check_database_status() {
    log_info "데이터베이스 상태 확인 중..."
    
    # 테이블 목록 확인
    log_info "생성된 테이블:"
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\dt"
    
    # 인덱스 목록 확인
    log_info "생성된 인덱스:"
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\di"
    
    # 뷰 목록 확인
    log_info "생성된 뷰:"
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\dv"
    
    # 샘플 데이터 확인
    log_info "샘플 데이터 확인:"
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT COUNT(*) as verification_records FROM verification_records;"
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT COUNT(*) as llm_requests FROM llm_requests;"
    
    log_success "데이터베이스 상태 확인 완료"
}

# 메인 실행 함수
main() {
    log_info "LLM Verification System 데이터베이스 설정을 시작합니다..."
    
    check_env_vars
    test_connection
    create_database
    apply_schema
    insert_sample_data
    check_database_status
    
    log_success "데이터베이스 설정이 완료되었습니다!"
    log_info "연결 정보:"
    log_info "  Host: $DB_HOST"
    log_info "  Port: $DB_PORT"
    log_info "  Database: $DB_NAME"
    log_info "  User: $DB_USER"
    log_info ""
    log_info "Flask 애플리케이션에서 다음 연결 문자열을 사용하세요:"
    log_info "postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
}

# 스크립트 실행
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
