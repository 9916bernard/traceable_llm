# LLM Verification System 설정 가이드

이 문서는 LLM Verification System을 설정하고 실행하는 방법을 설명합니다.

## 📋 목차

1. [시스템 요구사항](#시스템-요구사항)
2. [환경 설정](#환경-설정)
3. [데이터베이스 설정](#데이터베이스-설정)
4. [스마트 컨트랙트 배포](#스마트-컨트랙트-배포)
5. [백엔드 서버 실행](#백엔드-서버-실행)
6. [프론트엔드 실행](#프론트엔드-실행)
7. [배포](#배포)
8. [문제 해결](#문제-해결)

## 🔧 시스템 요구사항

### 필수 소프트웨어
- **Node.js** 18.x 이상
- **Python** 3.11 이상
- **PostgreSQL** 15 이상
- **Docker** 및 **Docker Compose** (배포용)
- **Git**

### API 키 및 계정
- **OpenAI API Key** (GPT 모델 사용)
- **Anthropic API Key** (Claude 모델 사용)
- **Infura Project ID** (이더리움 네트워크 접근)
- **Etherscan API Key** (컨트랙트 검증용)

## ⚙️ 환경 설정

### 1. 저장소 클론
```bash
git clone <repository-url>
cd llm_verification
```

### 2. 환경 변수 설정

#### 백엔드 환경 변수 (`backend/env.example` → `backend/.env`)
```bash
# Flask 설정
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# 데이터베이스 설정
DATABASE_URL=postgresql://username:password@localhost:5432/llm_verification
DEV_DATABASE_URL=postgresql://username:password@localhost:5432/llm_verification_dev

# LLM API 키
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# 블록체인 설정
ETHEREUM_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
PRIVATE_KEY=your-private-key-without-0x-prefix
CONTRACT_ADDRESS=your-deployed-contract-address

# CORS 설정
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

#### 스마트 컨트랙트 환경 변수 (`smart-contracts/env.example` → `smart-contracts/.env`)
```bash
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
PRIVATE_KEY=your-private-key-without-0x-prefix
ETHERSCAN_API_KEY=your-etherscan-api-key
```

#### 프론트엔드 환경 변수 (`frontend/.env.local`)
```bash
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

## 🗄️ 데이터베이스 설정

### 1. PostgreSQL 설치 및 설정
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS (Homebrew)
brew install postgresql
brew services start postgresql

# Windows
# PostgreSQL 공식 웹사이트에서 설치
```

### 2. 데이터베이스 및 사용자 생성
```sql
-- PostgreSQL에 접속
sudo -u postgres psql

-- 데이터베이스 생성
CREATE DATABASE llm_verification;
CREATE DATABASE llm_verification_dev;

-- 사용자 생성
CREATE USER llm_user WITH PASSWORD 'your_password';

-- 권한 부여
GRANT ALL PRIVILEGES ON DATABASE llm_verification TO llm_user;
GRANT ALL PRIVILEGES ON DATABASE llm_verification_dev TO llm_user;
```

### 3. 스키마 적용
```bash
# 자동 설정 스크립트 실행
cd database
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=llm_user
export DB_PASSWORD=your_password
export DB_NAME=llm_verification

./setup.sh
```

또는 수동으로:
```bash
psql -h localhost -U llm_user -d llm_verification -f schema.sql
```

## 🔗 스마트 컨트랙트 배포

### 1. 의존성 설치
```bash
cd smart-contracts
npm install
```

### 2. 컨트랙트 컴파일
```bash
npx hardhat compile
```

### 3. 테스트 실행
```bash
npx hardhat test
```

### 4. 로컬 네트워크에서 배포 (개발용)
```bash
# Hardhat 노드 시작 (새 터미널)
npx hardhat node

# 컨트랙트 배포 (다른 터미널)
npx hardhat run scripts/deploy.js --network localhost
```

### 5. Sepolia 테스트넷에 배포
```bash
npx hardhat run scripts/deploy.js --network sepolia
```

### 6. Etherscan에서 검증
```bash
npx hardhat verify --network sepolia <CONTRACT_ADDRESS>
```

## 🚀 백엔드 서버 실행

### 1. 의존성 설치
```bash
cd backend
pip install -r requirements.txt
```

### 2. 데이터베이스 마이그레이션
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 3. 서버 실행
```bash
# 개발 모드
python app.py

# 프로덕션 모드
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

### 4. API 테스트
```bash
# 헬스체크
curl http://localhost:5000/api/llm/health

# 사용 가능한 모델 조회
curl http://localhost:5000/api/llm/models
```

## 🎨 프론트엔드 실행

### 1. 의존성 설치
```bash
cd frontend
npm install
```

### 2. 개발 서버 실행
```bash
npm run dev
```

### 3. 프로덕션 빌드
```bash
npm run build
npm start
```

### 4. 접속 확인
브라우저에서 `http://localhost:3000` 접속

## 🚀 배포

### Vercel (프론트엔드)
1. Vercel 계정 생성 및 GitHub 연동
2. 프로젝트 import
3. 환경 변수 설정
4. 자동 배포

### AWS Lightsail (백엔드)
1. Lightsail 인스턴스 생성
2. Docker 설치
3. 환경 변수 설정
4. 배포 스크립트 실행

```bash
# AWS Lightsail 인스턴스에서
cd deployment/aws
export DB_PASSWORD=your_password
export SECRET_KEY=your_secret_key
# ... 기타 환경 변수들

./deploy.sh
```

## 🔧 문제 해결

### 일반적인 문제들

#### 1. 데이터베이스 연결 오류
```bash
# PostgreSQL 서비스 상태 확인
sudo systemctl status postgresql

# 연결 테스트
psql -h localhost -U llm_user -d llm_verification -c "SELECT 1;"
```

#### 2. 블록체인 연결 오류
- Infura 프로젝트 ID 확인
- 네트워크 상태 확인
- 가스비 충분한지 확인

#### 3. LLM API 오류
- API 키 유효성 확인
- 사용량 한도 확인
- 네트워크 연결 확인

#### 4. CORS 오류
- 백엔드 CORS_ORIGINS 설정 확인
- 프론트엔드 도메인이 허용 목록에 있는지 확인

### 로그 확인
```bash
# 백엔드 로그
tail -f backend/logs/app.log

# Docker 로그
docker-compose logs -f

# 시스템 로그
journalctl -u your-service-name -f
```

### 성능 최적화
1. **데이터베이스 인덱스** 확인
2. **API 응답 시간** 모니터링
3. **메모리 사용량** 확인
4. **가스비 최적화** (블록체인)

## 📞 지원

문제가 지속되면 다음을 확인하세요:
1. [GitHub Issues](https://github.com/your-repo/issues)
2. 시스템 로그
3. 네트워크 연결 상태
4. API 키 유효성

---

**참고**: 이 시스템은 테스트넷을 사용하므로 실제 ETH가 소모되지 않습니다. 프로덕션 환경에서는 메인넷 사용을 고려하세요.
