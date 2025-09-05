#!/bin/bash

# LLM Verification System AWS Lightsail 배포 스크립트
# AWS Lightsail에서 Docker Compose를 사용한 배포

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
    
    required_vars=(
        "DB_PASSWORD"
        "SECRET_KEY"
        "OPENAI_API_KEY"
        "ANTHROPIC_API_KEY"
        "ETHEREUM_RPC_URL"
        "PRIVATE_KEY"
        "CONTRACT_ADDRESS"
        "CORS_ORIGINS"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log_error "환경 변수 $var가 설정되지 않았습니다."
            exit 1
        fi
    done
    
    log_success "모든 환경 변수가 설정되었습니다."
}

# Docker 및 Docker Compose 설치 확인
check_docker() {
    log_info "Docker 설치 확인 중..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker가 설치되지 않았습니다."
        log_info "Docker 설치를 진행합니다..."
        
        # Ubuntu/Debian용 Docker 설치
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        sudo usermod -aG docker $USER
        
        log_success "Docker 설치 완료. 시스템을 재시작한 후 다시 실행해주세요."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose가 설치되지 않았습니다."
        log_info "Docker Compose 설치를 진행합니다..."
        
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
        log_success "Docker Compose 설치 완료"
    fi
    
    log_success "Docker 환경 확인 완료"
}

# SSL 인증서 설정
setup_ssl() {
    log_info "SSL 인증서 설정 중..."
    
    if [ ! -d "ssl" ]; then
        mkdir -p ssl
    fi
    
    if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
        log_warning "SSL 인증서가 없습니다. 자체 서명 인증서를 생성합니다."
        
        # 자체 서명 인증서 생성 (개발용)
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ssl/key.pem \
            -out ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"
        
        log_success "자체 서명 SSL 인증서 생성 완료"
        log_warning "프로덕션 환경에서는 유효한 SSL 인증서를 사용하세요."
    else
        log_success "SSL 인증서가 이미 존재합니다."
    fi
}

# 방화벽 설정
setup_firewall() {
    log_info "방화벽 설정 중..."
    
    # UFW가 설치되어 있는지 확인
    if command -v ufw &> /dev/null; then
        # 필요한 포트 열기
        sudo ufw allow 22/tcp   # SSH
        sudo ufw allow 80/tcp   # HTTP
        sudo ufw allow 443/tcp  # HTTPS
        
        # UFW 활성화 (비활성화된 경우)
        if ! sudo ufw status | grep -q "Status: active"; then
            sudo ufw --force enable
        fi
        
        log_success "방화벽 설정 완료"
    else
        log_warning "UFW가 설치되지 않았습니다. 수동으로 방화벽을 설정해주세요."
    fi
}

# Docker Compose 서비스 시작
start_services() {
    log_info "Docker Compose 서비스를 시작합니다..."
    
    # 기존 컨테이너 정리
    docker-compose down --remove-orphans
    
    # 이미지 빌드 및 서비스 시작
    docker-compose up -d --build
    
    log_success "서비스 시작 완료"
}

# 서비스 상태 확인
check_services() {
    log_info "서비스 상태 확인 중..."
    
    # 컨테이너 상태 확인
    docker-compose ps
    
    # 로그 확인
    log_info "최근 로그 확인:"
    docker-compose logs --tail=20
    
    # 헬스체크
    log_info "헬스체크 수행 중..."
    
    # 백엔드 헬스체크
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        log_success "백엔드 서비스가 정상적으로 실행 중입니다."
    else
        log_error "백엔드 서비스에 문제가 있습니다."
    fi
    
    # 데이터베이스 연결 확인
    if docker-compose exec -T postgres pg_isready -U llm_user -d llm_verification > /dev/null 2>&1; then
        log_success "데이터베이스가 정상적으로 실행 중입니다."
    else
        log_error "데이터베이스에 문제가 있습니다."
    fi
}

# 모니터링 설정
setup_monitoring() {
    log_info "모니터링 설정 중..."
    
    # 로그 로테이션 설정
    cat << EOF | sudo tee /etc/logrotate.d/docker-compose
/var/lib/docker/containers/*/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
EOF
    
    # 시스템 모니터링 스크립트 생성
    cat << 'EOF' > monitor.sh
#!/bin/bash
# 시스템 모니터링 스크립트

echo "=== 시스템 리소스 사용량 ==="
echo "CPU 사용률:"
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1

echo "메모리 사용률:"
free -h

echo "디스크 사용률:"
df -h

echo "=== Docker 컨테이너 상태 ==="
docker-compose ps

echo "=== 최근 에러 로그 ==="
docker-compose logs --tail=10 | grep -i error
EOF
    
    chmod +x monitor.sh
    
    log_success "모니터링 설정 완료"
}

# 백업 설정
setup_backup() {
    log_info "백업 설정 중..."
    
    # 데이터베이스 백업 스크립트 생성
    cat << 'EOF' > backup.sh
#!/bin/bash
# 데이터베이스 백업 스크립트

BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="llm_verification_backup_$DATE.sql"

mkdir -p $BACKUP_DIR

# 데이터베이스 백업
docker-compose exec -T postgres pg_dump -U llm_user llm_verification > $BACKUP_DIR/$BACKUP_FILE

# 압축
gzip $BACKUP_DIR/$BACKUP_FILE

# 7일 이상 된 백업 파일 삭제
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "백업 완료: $BACKUP_DIR/$BACKUP_FILE.gz"
EOF
    
    chmod +x backup.sh
    
    # 크론 작업 추가 (매일 새벽 2시에 백업)
    (crontab -l 2>/dev/null; echo "0 2 * * * /home/ubuntu/backup.sh") | crontab -
    
    log_success "백업 설정 완료"
}

# 메인 실행 함수
main() {
    log_info "LLM Verification System AWS Lightsail 배포를 시작합니다..."
    
    check_env_vars
    check_docker
    setup_ssl
    setup_firewall
    start_services
    
    # 서비스 시작 대기
    log_info "서비스 시작을 기다리는 중..."
    sleep 30
    
    check_services
    setup_monitoring
    setup_backup
    
    log_success "배포가 완료되었습니다!"
    log_info "서비스 접속 정보:"
    log_info "  - HTTP: http://your-domain.com"
    log_info "  - HTTPS: https://your-domain.com"
    log_info "  - API: https://your-domain.com/api"
    log_info ""
    log_info "유용한 명령어:"
    log_info "  - 서비스 상태 확인: docker-compose ps"
    log_info "  - 로그 확인: docker-compose logs -f"
    log_info "  - 서비스 재시작: docker-compose restart"
    log_info "  - 서비스 중지: docker-compose down"
    log_info "  - 시스템 모니터링: ./monitor.sh"
    log_info "  - 데이터베이스 백업: ./backup.sh"
}

# 스크립트 실행
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
