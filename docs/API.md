# LLM Verification System API 문서

이 문서는 LLM Verification System의 REST API 엔드포인트를 설명합니다.

## 📋 목차

1. [기본 정보](#기본-정보)
2. [인증](#인증)
3. [LLM API](#llm-api)
4. [검증 API](#검증-api)
5. [블록체인 API](#블록체인-api)
6. [에러 코드](#에러-코드)
7. [예제](#예제)

## 🔧 기본 정보

### Base URL
```
개발 환경: http://localhost:5000/api
프로덕션: https://your-domain.com/api
```

### 응답 형식
모든 API 응답은 JSON 형식으로 반환됩니다.

### HTTP 상태 코드
- `200`: 성공
- `400`: 잘못된 요청
- `404`: 리소스를 찾을 수 없음
- `500`: 서버 내부 오류

## 🔐 인증

현재 버전에서는 API 키 인증을 사용하지 않습니다. 향후 버전에서 추가될 예정입니다.

## 🤖 LLM API

### 1. LLM 응답 생성

**POST** `/llm/generate`

LLM에 프롬프트를 전송하고 응답을 생성하며, 검증 해시를 블록체인에 저장합니다.

#### 요청 본문
```json
{
  "provider": "openai",
  "model": "gpt-3.5-turbo",
  "prompt": "Hello, how are you?",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "commit_to_blockchain": true
}
```

#### 요청 필드
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `provider` | string | ✅ | LLM 제공자 (`openai`, `anthropic`) |
| `model` | string | ✅ | 모델 이름 |
| `prompt` | string | ✅ | 입력 프롬프트 |
| `parameters` | object | ❌ | LLM 파라미터 |
| `commit_to_blockchain` | boolean | ❌ | 블록체인 커밋 여부 (기본값: true) |

#### 응답
```json
{
  "request_id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "Hello! I am doing well, thank you for asking. How can I help you today?",
  "hash_value": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
  "verification_record_id": 1,
  "response_time": 1.234,
  "model": "gpt-3.5-turbo",
  "provider": "openai",
  "blockchain_commit": {
    "transaction_hash": "0x1234567890abcdef...",
    "block_number": 12345678,
    "status": "success"
  }
}
```

### 2. 사용 가능한 모델 조회

**GET** `/llm/models`

사용 가능한 LLM 모델 목록을 반환합니다.

#### 응답
```json
{
  "openai": [
    "gpt-4",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k"
  ],
  "anthropic": [
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307"
  ]
}
```

### 3. LLM 서비스 상태 확인

**GET** `/llm/health`

LLM 서비스의 상태를 확인합니다.

#### 응답
```json
{
  "status": "healthy",
  "test_response": "Hello! I am doing well, thank you for asking..."
}
```

## 🔍 검증 API

### 1. 해시 검증

**POST** `/verification/verify`

해시값을 통해 LLM 출력의 진위를 검증합니다.

#### 요청 본문
```json
{
  "hash_value": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
}
```

#### 응답
```json
{
  "verified": true,
  "hash_verified": true,
  "blockchain_verified": true,
  "verification_record": {
    "id": 1,
    "hash_value": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
    "llm_provider": "openai",
    "model_name": "gpt-3.5-turbo",
    "prompt": "Hello, how are you?",
    "response": "Hello! I am doing well, thank you for asking. How can I help you today?",
    "parameters": {
      "temperature": 0.7,
      "max_tokens": 1000
    },
    "timestamp": "2024-01-01T12:00:00Z",
    "transaction_hash": "0x1234567890abcdef...",
    "block_number": 12345678,
    "verified": true,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  },
  "blockchain_info": {
    "exists": true,
    "timestamp": 1704110400,
    "status": "success"
  }
}
```

### 2. 검증 기록 조회

**GET** `/verification/record/{record_id}`

특정 검증 기록의 상세 정보를 조회합니다.

#### URL 파라미터
| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `record_id` | integer | 검증 기록 ID |

#### 응답
검증 API의 `verification_record` 객체와 동일한 형식

### 3. 검증 기록 목록 조회

**GET** `/verification/records`

검증 기록 목록을 페이지네이션으로 조회합니다.

#### 쿼리 파라미터
| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `page` | integer | 1 | 페이지 번호 |
| `per_page` | integer | 20 | 페이지당 항목 수 |
| `provider` | string | - | LLM 제공자 필터 |
| `verified` | boolean | - | 검증 상태 필터 |

#### 응답
```json
{
  "records": [
    {
      "id": 1,
      "hash_value": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
      "llm_provider": "openai",
      "model_name": "gpt-3.5-turbo",
      "prompt": "Hello, how are you?",
      "response": "Hello! I am doing well, thank you for asking. How can I help you today?",
      "parameters": {
        "temperature": 0.7,
        "max_tokens": 1000
      },
      "timestamp": "2024-01-01T12:00:00Z",
      "transaction_hash": "0x1234567890abcdef...",
      "block_number": 12345678,
      "verified": true,
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 100,
  "pages": 5,
  "current_page": 1,
  "per_page": 20
}
```

### 4. 내용으로 검색

**POST** `/verification/search`

프롬프트나 응답 내용으로 검증 기록을 검색합니다.

#### 요청 본문
```json
{
  "query": "artificial intelligence",
  "type": "both"
}
```

#### 요청 필드
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `query` | string | ✅ | 검색 쿼리 |
| `type` | string | ❌ | 검색 타입 (`prompt`, `response`, `both`) |

#### 응답
```json
{
  "records": [
    {
      "id": 2,
      "hash_value": "b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234567",
      "llm_provider": "anthropic",
      "model_name": "claude-3-sonnet-20240229",
      "prompt": "What is artificial intelligence?",
      "response": "Artificial intelligence (AI) is a branch of computer science...",
      "parameters": {
        "temperature": 0.5,
        "max_tokens": 200
      },
      "timestamp": "2024-01-01T13:00:00Z",
      "transaction_hash": "0x2345678901bcdef...",
      "block_number": 12345679,
      "verified": true,
      "created_at": "2024-01-01T13:00:00Z",
      "updated_at": "2024-01-01T13:00:00Z"
    }
  ],
  "total": 1
}
```

## ⛓️ 블록체인 API

### 1. 블록체인 상태 조회

**GET** `/blockchain/status`

블록체인 네트워크의 현재 상태를 조회합니다.

#### 응답
```json
{
  "network_id": 11155111,
  "latest_block": 12345678,
  "gas_price": "20000000000",
  "account_balance": "1000000000000000000",
  "status": "connected"
}
```

### 2. 블록체인에서 해시 검증

**GET** `/blockchain/verify/{hash_value}`

블록체인에서 특정 해시의 존재 여부를 확인합니다.

#### URL 파라미터
| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `hash_value` | string | 검증할 해시값 |

#### 응답
```json
{
  "exists": true,
  "timestamp": 1704110400,
  "status": "success"
}
```

### 3. 해시를 블록체인에 커밋

**POST** `/blockchain/commit`

해시를 블록체인에 수동으로 커밋합니다.

#### 요청 본문
```json
{
  "hash_value": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
  "verification_record_id": 1
}
```

#### 응답
```json
{
  "transaction_hash": "0x1234567890abcdef...",
  "block_number": 12345678,
  "gas_used": 150000,
  "status": "success"
}
```

## ❌ 에러 코드

### 일반적인 에러 응답 형식
```json
{
  "error": "에러 메시지",
  "code": "ERROR_CODE",
  "details": "상세 정보"
}
```

### 주요 에러 코드
| 코드 | HTTP 상태 | 설명 |
|------|-----------|------|
| `INVALID_HASH_LENGTH` | 400 | 해시 길이가 올바르지 않음 |
| `HASH_NOT_FOUND` | 404 | 해시를 찾을 수 없음 |
| `LLM_API_ERROR` | 500 | LLM API 호출 실패 |
| `BLOCKCHAIN_ERROR` | 500 | 블록체인 연결 오류 |
| `DATABASE_ERROR` | 500 | 데이터베이스 오류 |
| `INVALID_PARAMETERS` | 400 | 잘못된 파라미터 |

## 📝 예제

### cURL 예제

#### LLM 응답 생성
```bash
curl -X POST http://localhost:5000/api/llm/generate \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "prompt": "What is the capital of France?",
    "parameters": {
      "temperature": 0.7,
      "max_tokens": 100
    }
  }'
```

#### 해시 검증
```bash
curl -X POST http://localhost:5000/api/verification/verify \
  -H "Content-Type: application/json" \
  -d '{
    "hash_value": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
  }'
```

#### 검증 기록 목록 조회
```bash
curl "http://localhost:5000/api/verification/records?page=1&per_page=10&provider=openai"
```

### JavaScript 예제

```javascript
// LLM 응답 생성
const response = await fetch('/api/llm/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    provider: 'openai',
    model: 'gpt-3.5-turbo',
    prompt: 'Hello, how are you?',
    parameters: {
      temperature: 0.7,
      max_tokens: 1000
    }
  })
});

const result = await response.json();
console.log('Generated hash:', result.hash_value);

// 해시 검증
const verifyResponse = await fetch('/api/verification/verify', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    hash_value: result.hash_value
  })
});

const verification = await verifyResponse.json();
console.log('Verification result:', verification.verified);
```

### Python 예제

```python
import requests

# LLM 응답 생성
response = requests.post('http://localhost:5000/api/llm/generate', json={
    'provider': 'openai',
    'model': 'gpt-3.5-turbo',
    'prompt': 'What is machine learning?',
    'parameters': {
        'temperature': 0.7,
        'max_tokens': 200
    }
})

result = response.json()
print(f"Generated hash: {result['hash_value']}")

# 해시 검증
verify_response = requests.post('http://localhost:5000/api/verification/verify', json={
    'hash_value': result['hash_value']
})

verification = verify_response.json()
print(f"Verification result: {verification['verified']}")
```

---

**참고**: 모든 API 엔드포인트는 CORS를 지원하며, 프론트엔드 애플리케이션에서 직접 호출할 수 있습니다.
