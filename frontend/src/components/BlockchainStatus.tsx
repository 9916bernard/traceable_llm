import { BlockchainStatus as BlockchainStatusType } from '@/types';
import { formatDate } from '@/utils';

interface BlockchainStatusProps {
  status?: BlockchainStatusType;
  loading?: boolean;
}

export default function BlockchainStatus({ status, loading }: BlockchainStatusProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="flex items-center space-x-2">
          <div className="loading-spinner" />
          <span className="text-gray-600">블록체인 상태를 확인하는 중...</span>
        </div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-500">
          블록체인 상태 정보를 불러올 수 없습니다.
        </div>
      </div>
    );
  }

  if (status.status === 'not_configured') {
    return (
      <div className="text-center py-8">
        <div className="text-warning-600 mb-2">
          ⚠️ 블록체인 설정이 완료되지 않았습니다
        </div>
        <div className="text-gray-600">
          블록체인 기능을 사용하려면 환경 변수를 설정해주세요.
        </div>
      </div>
    );
  }

  if (status.status === 'error') {
    return (
      <div className="text-center py-8">
        <div className="text-error-600 mb-2">
          ❌ 블록체인 연결 오류
        </div>
        <div className="text-gray-600">
          {status.error_message}
        </div>
      </div>
    );
  }

  const isConnected = status.status === 'connected';

  return (
    <div className="space-y-6">
      {/* 연결 상태 */}
      <div className="flex items-center justify-center">
        <div className={`px-6 py-3 rounded-lg border-2 ${
          isConnected 
            ? 'bg-success-50 border-success-200 text-success-800' 
            : 'bg-error-50 border-error-200 text-error-800'
        }`}>
          <div className="flex items-center space-x-3">
            <div className={`w-4 h-4 rounded-full ${
              isConnected ? 'bg-success-500' : 'bg-error-500'
            }`} />
            <span className="font-semibold">
              {isConnected ? '블록체인 연결됨' : '블록체인 연결 안됨'}
            </span>
          </div>
        </div>
      </div>

      {/* 네트워크 정보 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">네트워크 정보</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">네트워크 ID:</span>
              <span className="font-mono text-sm">{status.network_id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">최신 블록:</span>
              <span className="font-mono text-sm">{status.latest_block?.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">가스 가격:</span>
              <span className="font-mono text-sm">
                {status.gas_price ? `${(parseInt(status.gas_price) / 1e9).toFixed(2)} Gwei` : 'N/A'}
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">계정 정보</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">잔액:</span>
              <span className="font-mono text-sm">
                {status.account_balance ? `${(parseInt(status.account_balance) / 1e18).toFixed(4)} ETH` : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">상태:</span>
              <span className={`badge ${
                isConnected ? 'badge-success' : 'badge-error'
              }`}>
                {isConnected ? '활성' : '비활성'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 네트워크별 정보 */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">네트워크 상세</h3>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">네트워크:</span>
            <span className="font-semibold">
              {status.network_id === 1 ? 'Ethereum Mainnet' :
               status.network_id === 11155111 ? 'Sepolia Testnet' :
               status.network_id === 5 ? 'Goerli Testnet' :
               status.network_id === 31337 ? 'Local Network' :
               `Network ${status.network_id}`}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">체인 ID:</span>
            <span className="font-mono text-sm">{status.network_id}</span>
          </div>
          {status.latest_block && (
            <div className="flex justify-between">
              <span className="text-gray-600">블록 높이:</span>
              <span className="font-mono text-sm">{status.latest_block.toLocaleString()}</span>
            </div>
          )}
        </div>
      </div>

      {/* 사용 가이드 */}
      <div className="card bg-blue-50 border border-blue-200">
        <h3 className="text-lg font-semibold text-blue-900 mb-4">💡 사용 가이드</h3>
        <div className="space-y-2 text-blue-800">
          <p>• LLM 응답 생성 시 자동으로 해시가 블록체인에 저장됩니다</p>
          <p>• 해시 검증을 통해 LLM 출력의 진위를 확인할 수 있습니다</p>
          <p>• 모든 검증 기록은 블록체인에 영구적으로 저장됩니다</p>
          <p>• 테스트넷을 사용하므로 실제 ETH가 소모되지 않습니다</p>
        </div>
      </div>
    </div>
  );
}
