import { ReactNode } from 'react';
import Head from 'next/head';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <>
      <Head>
        <title>LLM Verification System</title>
        <meta name="description" content="LLM 출력의 진위를 검증하는 블록체인 기반 시스템" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className="min-h-screen bg-gray-50">
        {children}
      </div>
    </>
  );
}
