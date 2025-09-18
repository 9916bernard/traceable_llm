import { BlockchainStatus as BlockchainStatusType } from '@/types';
import { formatDate } from '@/utils';

interface BlockchainStatusProps {
  status?: BlockchainStatusType;
  loading?: boolean;
}

export default function BlockchainStatus({ status, loading }: BlockchainStatusProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="loading-container mb-4">
            <div className="loading-pulse"></div>
            <div className="loading-pulse"></div>
            <div className="loading-pulse"></div>
          </div>
          <span className="text-navy-600 font-medium">Checking blockchain status...</span>
        </div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gradient-to-br from-error-100 to-error-200 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-error-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <div className="text-navy-600 font-medium">
          Unable to load blockchain status information.
        </div>
      </div>
    );
  }

  if (status.status === 'not_configured') {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gradient-to-br from-warning-100 to-warning-200 rounded-full flex items-center justify-center mx-auto mb-4 bounce-gentle">
          <svg className="w-8 h-8 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <div className="text-warning-700 font-semibold mb-2">
          Blockchain Configuration Required
        </div>
        <div className="text-navy-600">
          Please configure environment variables to use blockchain features.
        </div>
      </div>
    );
  }

  if (status.status === 'error') {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gradient-to-br from-error-100 to-error-200 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-error-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <div className="text-error-700 font-semibold mb-2">
          Blockchain Connection Error
        </div>
        <div className="text-navy-600 max-w-md mx-auto">
          {status.error_message}
        </div>
      </div>
    );
  }

  const isConnected = status.status === 'connected';

  return (
    <div className="space-y-8 fade-in">
      {/* 연결 상태 */}
      <div className="flex items-center justify-center">
        <div className={`px-8 py-4 rounded-2xl border-2 transition-all duration-300 hover:scale-105 ${
          isConnected 
            ? 'bg-gradient-to-r from-success-100 to-success-200 border-success-300 text-success-800 shadow-lg hover:shadow-xl' 
            : 'bg-gradient-to-r from-error-100 to-error-200 border-error-300 text-error-800 shadow-lg hover:shadow-xl'
        }`}>
          <div className="flex items-center space-x-4">
            <div className={`w-5 h-5 rounded-full ${
              isConnected ? 'bg-success-500 animate-pulse' : 'bg-error-500'
            }`} />
            <span className="font-bold text-lg">
              {isConnected ? 'Blockchain Connected' : 'Blockchain Disconnected'}
            </span>
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
        </div>
      </div>

      {/* 네트워크 정보 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card hover-lift slide-in-left">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0-9v9m0 9c-5 0-9-4-9-9s4-9 9-9" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-navy-800">Network Information</h3>
          </div>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-navy-50 rounded-lg">
              <span className="text-navy-600 font-medium">Network ID:</span>
              <span className="font-mono text-sm bg-white px-2 py-1 rounded border">{status.network_id}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-navy-50 rounded-lg">
              <span className="text-navy-600 font-medium">Latest Block:</span>
              <span className="font-mono text-sm bg-white px-2 py-1 rounded border">{status.latest_block?.toLocaleString()}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-navy-50 rounded-lg">
              <span className="text-navy-600 font-medium">Gas Price:</span>
              <span className="font-mono text-sm bg-white px-2 py-1 rounded border">
                {status.gas_price ? `${(parseInt(status.gas_price) / 1e9).toFixed(2)} Gwei` : 'N/A'}
              </span>
            </div>
          </div>
        </div>

        <div className="card hover-lift slide-in-right">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-primary-700 rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-navy-800">Account Information</h3>
          </div>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-navy-50 rounded-lg">
              <span className="text-navy-600 font-medium">Balance:</span>
              <span className="font-mono text-sm bg-white px-2 py-1 rounded border">
                {status.account_balance ? `${(parseInt(status.account_balance) / 1e18).toFixed(4)} ETH` : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-navy-50 rounded-lg">
              <span className="text-navy-600 font-medium">Status:</span>
              <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                isConnected ? 'bg-success-100 text-success-800' : 'bg-error-100 text-error-800'
              }`}>
                {isConnected ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 네트워크별 정보 */}
      <div className="card hover-lift">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 bg-gradient-to-br from-navy-600 to-navy-700 rounded-xl flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-xl font-bold text-navy-800">Network Details</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-3 bg-navy-50 rounded-lg">
            <div className="flex justify-between items-center">
              <span className="text-navy-600 font-medium">Network:</span>
              <span className="font-semibold text-navy-800">
                {status.network_id === 1 ? 'Ethereum Mainnet' :
                 status.network_id === 11155111 ? 'Sepolia Testnet' :
                 status.network_id === 5 ? 'Goerli Testnet' :
                 status.network_id === 31337 ? 'Local Network' :
                 `Network ${status.network_id}`}
              </span>
            </div>
          </div>
          <div className="p-3 bg-navy-50 rounded-lg">
            <div className="flex justify-between items-center">
              <span className="text-navy-600 font-medium">Chain ID:</span>
              <span className="font-mono text-sm bg-white px-2 py-1 rounded border">{status.network_id}</span>
            </div>
          </div>
          {status.latest_block && (
            <div className="p-3 bg-navy-50 rounded-lg">
              <div className="flex justify-between items-center">
                <span className="text-navy-600 font-medium">Block Height:</span>
                <span className="font-mono text-sm bg-white px-2 py-1 rounded border">{status.latest_block.toLocaleString()}</span>
              </div>
            </div>
          )}
          {status.network_id === 11155111 && (
            <div className="p-3 bg-navy-50 rounded-lg">
              <div className="flex justify-between items-center">
                <span className="text-navy-600 font-medium">Explorer:</span>
                <a 
                  href="https://sepolia.etherscan.io" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:text-primary-800 font-mono text-sm hover:underline transition-colors duration-200"
                >
                  sepolia.etherscan.io
                </a>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Sepolia Testnet 전용 안내 */}
      {status.network_id === 11155111 && (
        <div className="card bg-gradient-to-r from-warning-50 to-warning-100 border-2 border-warning-300 hover-lift">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-gradient-to-br from-warning-500 to-warning-600 rounded-xl flex items-center justify-center">
              <span className="text-white text-lg">🌐</span>
            </div>
            <h3 className="text-xl font-bold text-warning-900">Sepolia Testnet</h3>
          </div>
          <div className="space-y-3 text-warning-800">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-warning-500 rounded-full"></div>
              <p><strong>Testnet Environment</strong> - No real ETH is consumed</p>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-warning-500 rounded-full"></div>
              <p>Sepolia ETH can be obtained for free from faucets</p>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-warning-500 rounded-full"></div>
              <p>Get test ETH from <a href="https://sepoliafaucet.com/" target="_blank" rel="noopener noreferrer" className="underline hover:text-warning-900 font-semibold">Sepolia Faucet</a></p>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-warning-500 rounded-full"></div>
              <p>All transactions can be verified on <a href="https://sepolia.etherscan.io" target="_blank" rel="noopener noreferrer" className="underline hover:text-warning-900 font-semibold">Etherscan</a></p>
            </div>
          </div>
        </div>
      )}

      {/* 사용 가이드 */}
      <div className="card bg-gradient-to-r from-blue-50 to-primary-50 border-2 border-blue-300 hover-lift">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-primary-600 rounded-xl flex items-center justify-center">
            <span className="text-white text-lg">💡</span>
          </div>
          <h3 className="text-xl font-bold text-blue-900">Usage Guide</h3>
        </div>
        <div className="space-y-3 text-blue-800">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <p>Hash is automatically stored on blockchain when generating LLM responses</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <p>Verify authenticity of LLM outputs through hash verification</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <p>All verification records are permanently stored on blockchain</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <p>Using testnet environment - no real ETH is consumed</p>
          </div>
        </div>
      </div>
    </div>
  );
}
