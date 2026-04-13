import { ReactNode } from 'react';
import Head from 'next/head';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <>
      <Head>
        <title>Traceable LLM</title>
        <meta name="description" content="Blockchain-anchored verification for LLM outputs" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </Head>
      <div className="min-h-screen bg-white flex flex-col">
        {/* Header */}
        <header className="border-b border-[var(--color-border)]">
          <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
            <div>
              <h1 className="text-lg font-semibold text-[var(--color-ink)] tracking-tight">
                Traceable LLM
              </h1>
              <p className="text-xs text-[var(--color-ink-muted)]">
                Consensus-based verification with on-chain anchoring
              </p>
            </div>
            <div className="flex items-center space-x-2 text-xs text-[var(--color-ink-muted)]">
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-[var(--color-safe)]"></span>
              <span>Sepolia Testnet</span>
            </div>
          </div>
        </header>

        {/* Main content */}
        <main className="flex-1 max-w-4xl mx-auto w-full px-6 py-8">
          {children}
        </main>

        {/* Footer */}
        <footer className="border-t border-[var(--color-border)] mt-auto">
          <div className="max-w-4xl mx-auto px-6 py-4 text-xs text-[var(--color-ink-muted)]">
            Traceable LLM &mdash; Multi-model consensus filtering with Ethereum Sepolia anchoring
          </div>
        </footer>
      </div>
    </>
  );
}
