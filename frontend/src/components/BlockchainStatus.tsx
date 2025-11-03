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
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="loading-spinner w-6 h-6"></div>
          </div>
          <span className="text-gray-600 font-medium">Checking blockchain status...</span>
        </div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gray-200 rounded-md flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <div className="text-gray-600 font-medium">
          Unable to load blockchain status information.
        </div>
      </div>
    );
  }

  if (status.status === 'not_configured') {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gray-200 rounded-md flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <div className="text-gray-900 font-semibold mb-2">
          Blockchain Configuration Required
        </div>
        <div className="text-gray-600">
          Please configure environment variables to use blockchain features.
        </div>
      </div>
    );
  }

  if (status.status === 'error') {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gray-200 rounded-md flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <div className="text-gray-900 font-semibold mb-2">
          Blockchain Connection Error
        </div>
        <div className="text-gray-600 max-w-md mx-auto">
          {status.error_message}
        </div>
      </div>
    );
  }

  const isConnected = status.status === 'connected';

  return (
    <div className="space-y-6 fade-in">
      {/* Connection status */}
      <div className="flex items-center justify-center">
        <div className={`px-8 py-4 rounded-md border-2 transition-all duration-200 ${
          isConnected 
            ? 'bg-black text-white border-black' 
            : 'bg-gray-200 text-gray-900 border-gray-300'
        }`}>
          <div className="flex items-center space-x-4">
            <div className={`w-3 h-3 rounded-full ${
              isConnected ? 'bg-white' : 'bg-gray-900'
            }`} />
            <span className="font-semibold text-lg">
              {isConnected ? 'Blockchain Connected' : 'Blockchain Disconnected'}
            </span>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Network information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card hover-lift">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-10 h-10 bg-black rounded-md flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0-9v9m0 9c-5 0-9-4-9-9s4-9 9-9" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900">Network Information</h3>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-md border border-gray-200">
              <span className="text-gray-600 font-medium">Network ID:</span>
              <span className="font-mono text-sm">{status.network_id}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-md border border-gray-200">
              <span className="text-gray-600 font-medium">Latest Block:</span>
              <span className="font-mono text-sm">{status.latest_block?.toLocaleString()}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-md border border-gray-200">
              <span className="text-gray-600 font-medium">Gas Price:</span>
              <span className="font-mono text-sm">
                {status.gas_price ? `${(parseInt(status.gas_price) / 1e9).toFixed(2)} Gwei` : 'N/A'}
              </span>
            </div>
          </div>
        </div>

        <div className="card hover-lift">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-10 h-10 bg-black rounded-md flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900">Account Information</h3>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-md border border-gray-200">
              <span className="text-gray-600 font-medium">Balance:</span>
              <span className="font-mono text-sm">
                {status.account_balance ? `${(parseInt(status.account_balance) / 1e18).toFixed(4)} ETH` : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-md border border-gray-200">
              <span className="text-gray-600 font-medium">Status:</span>
              <span className={`px-3 py-1 rounded text-xs font-semibold ${
                isConnected ? 'bg-black text-white' : 'bg-gray-200 text-gray-900'
              }`}>
                {isConnected ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Network details */}
      <div className="card hover-lift">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 bg-black rounded-md flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900">Network Details</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-3 bg-gray-50 rounded-md border border-gray-200">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 font-medium">Network:</span>
              <span className="font-semibold text-gray-900">
                {status.network_id === 1 ? 'Ethereum Mainnet' :
                 status.network_id === 11155111 ? 'Sepolia Testnet' :
                 status.network_id === 5 ? 'Goerli Testnet' :
                 status.network_id === 31337 ? 'Local Network' :
                 `Network ${status.network_id}`}
              </span>
            </div>
          </div>
          <div className="p-3 bg-gray-50 rounded-md border border-gray-200">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 font-medium">Chain ID:</span>
              <span className="font-mono text-sm">{status.network_id}</span>
            </div>
          </div>
          {status.latest_block && (
            <div className="p-3 bg-gray-50 rounded-md border border-gray-200">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 font-medium">Block Height:</span>
                <span className="font-mono text-sm">{status.latest_block.toLocaleString()}</span>
              </div>
            </div>
          )}
          {status.network_id === 11155111 && (
            <div className="p-3 bg-gray-50 rounded-md border border-gray-200">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 font-medium">Explorer:</span>
                <a 
                  href="https://sepolia.etherscan.io" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-gray-900 hover:text-gray-700 font-mono text-sm underline transition-colors duration-200"
                >
                  sepolia.etherscan.io
                </a>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Sepolia testnet info */}
      {status.network_id === 11155111 && (
        <div className="card bg-gray-50 border-2 border-gray-300 hover-lift">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-gray-900 rounded-md flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9v-9m0-9v9m0 9c-5 0-9-4-9-9s4-9 9-9" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900">Sepolia Testnet</h3>
          </div>
          <div className="space-y-2 text-gray-700">
            <p className="flex items-start space-x-2">
              <span className="font-semibold mt-0.5">•</span>
              <span><strong>Testnet Environment</strong> - No real ETH is consumed</span>
            </p>
            <p className="flex items-start space-x-2">
              <span className="font-semibold mt-0.5">•</span>
              <span>Sepolia ETH can be obtained for free from faucets</span>
            </p>
            <p className="flex items-start space-x-2">
              <span className="font-semibold mt-0.5">•</span>
              <span>Get test ETH from <a href="https://sepoliafaucet.com/" target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-900 font-semibold">Sepolia Faucet</a></span>
            </p>
            <p className="flex items-start space-x-2">
              <span className="font-semibold mt-0.5">•</span>
              <span>All transactions can be verified on <a href="https://sepolia.etherscan.io" target="_blank" rel="noopener noreferrer" className="underline hover:text-gray-900 font-semibold">Etherscan</a></span>
            </p>
          </div>
        </div>
      )}

      {/* Usage guide */}
      <div className="card bg-gray-50 border-2 border-gray-300 hover-lift">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 bg-black rounded-md flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900">Usage Guide</h3>
        </div>
        <div className="space-y-2 text-gray-700">
          <p className="flex items-start space-x-2">
            <span className="font-semibold mt-0.5">•</span>
            <span>Hash is automatically stored on blockchain when generating LLM responses</span>
          </p>
          <p className="flex items-start space-x-2">
            <span className="font-semibold mt-0.5">•</span>
            <span>Verify authenticity of LLM outputs through hash verification</span>
          </p>
          <p className="flex items-start space-x-2">
            <span className="font-semibold mt-0.5">•</span>
            <span>All verification records are permanently stored on blockchain</span>
          </p>
          <p className="flex items-start space-x-2">
            <span className="font-semibold mt-0.5">•</span>
            <span>Using testnet environment - no real ETH is consumed</span>
          </p>
        </div>
      </div>
    </div>
  );
}
