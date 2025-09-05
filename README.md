# LLM Verification System

LLM 출력의 진위를 검증하기 위한 블록체인 기반 인증 시스템

## 프로젝트 개요

대형 언어 모델(LLM)이 더욱 신뢰할 수 있게 됨에 따라, 그들의 출력이 LLM에서 나온다는 이유만으로 진실로 받아들여질 수 있습니다. 이는 정치를 포함한 사회의 다양한 분야에서 악용될 수 있으므로, 주어진 답변이 실제로 LLM에서 나온 것인지 검증할 수 있는 인증 시스템이 필요합니다.

## 기술 스택

### Backend
- **언어**: Python
- **프레임워크**: Flask
- **데이터베이스**: PostgreSQL
- **배포**: AWS Lightsail

### Frontend
- **언어**: TypeScript
- **프레임워크**: React
- **배포**: Vercel

### Blockchain
- **네트워크**: Ethereum Public Testnet
- **스마트 컨트랙트**: Solidity
- **로컬 테스트**: Hardhat

## 프로젝트 구조

```
llm_verification/
├── backend/                 # Flask 백엔드 서버
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models/         # 데이터베이스 모델
│   │   ├── routes/         # API 라우트
│   │   ├── services/       # 비즈니스 로직
│   │   └── utils/          # 유틸리티 함수
│   ├── requirements.txt
│   └── config.py
├── frontend/               # React 프론트엔드
│   ├── src/
│   │   ├── components/     # React 컴포넌트
│   │   ├── pages/          # 페이지 컴포넌트
│   │   ├── services/       # API 서비스
│   │   ├── types/          # TypeScript 타입 정의
│   │   └── utils/          # 유틸리티 함수
│   ├── package.json
│   └── tsconfig.json
├── smart-contracts/        # Solidity 스마트 컨트랙트
│   ├── contracts/
│   ├── scripts/
│   ├── test/
│   └── hardhat.config.js
├── database/              # 데이터베이스 스키마 및 마이그레이션
│   ├── migrations/
│   └── schema.sql
├── docs/                  # 문서
└── deployment/            # 배포 설정
    ├── vercel/
    └── aws/
```

## 주요 기능

1. **LLM API 연동**: OpenAI, Anthropic 등의 LLM API 호출
2. **해시 생성**: LLM 파라미터와 타임스탬프를 이용한 SHA-256 해시 생성
3. **블록체인 커밋**: 생성된 해시를 이더리움 테스트넷에 저장
4. **검증 시스템**: 해시를 통한 LLM 출력의 진위 검증
5. **웹 인터페이스**: 사용자 친화적인 검증 인터페이스

## 설치 및 실행

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Smart Contracts
```bash
cd smart-contracts
npm install
npx hardhat compile
npx hardhat test
```

## 라이선스

MIT License
