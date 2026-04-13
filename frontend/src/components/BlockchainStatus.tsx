import { BlockchainStatus as BlockchainStatusType } from '@/types';

interface BlockchainStatusProps {
  status?: BlockchainStatusType;
  loading?: boolean;
}

export default function BlockchainStatus({ status, loading }: BlockchainStatusProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <span className="loading-spinner mr-2" />
        <span className="text-sm text-[var(--color-ink-muted)]">Checking blockchain status...</span>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="text-center py-8 text-sm text-[var(--color-ink-muted)]">
        Unable to load blockchain status.
      </div>
    );
  }

  if (status.status === 'not_configured') {
    return (
      <div className="text-center py-8">
        <p className="text-sm font-medium text-[var(--color-ink)]">Configuration Required</p>
        <p className="text-xs text-[var(--color-ink-muted)] mt-1">Set blockchain environment variables to continue.</p>
      </div>
    );
  }

  if (status.status === 'error') {
    return (
      <div className="text-center py-8">
        <p className="text-sm font-medium text-[var(--color-danger)]">Connection Error</p>
        <p className="text-xs text-[var(--color-ink-muted)] mt-1">{status.error_message}</p>
      </div>
    );
  }

  const isConnected = status.status === 'connected';

  return (
    <div className="space-y-4 fade-in">
      {/* Status indicator */}
      <div className="flex items-center space-x-2 mb-4">
        <span className={`inline-block w-2 h-2 rounded-full ${isConnected ? 'bg-[var(--color-safe)]' : 'bg-[var(--color-danger)]'}`}></span>
        <span className="text-sm font-medium text-[var(--color-ink)]">
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
        <span className="text-xs text-[var(--color-ink-muted)]">
          {status.network_id === 11155111 ? 'Sepolia Testnet' :
           status.network_id === 1 ? 'Ethereum Mainnet' :
           status.network_id === 31337 ? 'Local Network' :
           `Network ${status.network_id}`}
        </span>
      </div>

      {/* Info grid */}
      <div className="grid grid-cols-2 gap-3">
        <InfoRow label="Network ID" value={String(status.network_id)} />
        <InfoRow label="Latest Block" value={status.latest_block?.toLocaleString() ?? 'N/A'} />
        <InfoRow
          label="Gas Price"
          value={status.gas_price ? `${(parseInt(status.gas_price) / 1e9).toFixed(2)} Gwei` : 'N/A'}
        />
        <InfoRow
          label="Balance"
          value={status.account_balance ? `${(parseInt(status.account_balance) / 1e18).toFixed(4)} ETH` : 'N/A'}
        />
      </div>

      {status.network_id === 11155111 && (
        <p className="text-xs text-[var(--color-ink-muted)]">
          Sepolia testnet &mdash; no real ETH consumed.{' '}
          <a href="https://sepolia.etherscan.io" target="_blank" rel="noopener noreferrer" className="text-[var(--color-accent)] hover:underline">
            Explorer
          </a>
        </p>
      )}
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center p-2.5 bg-[var(--color-surface-dim)] rounded border border-[var(--color-border)]">
      <span className="text-xs text-[var(--color-ink-muted)]">{label}</span>
      <span className="font-mono text-xs text-[var(--color-ink)]">{value}</span>
    </div>
  );
}
