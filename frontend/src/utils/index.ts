import { clsx, type ClassValue } from 'clsx';
import { format, formatDistanceToNow } from 'date-fns';
import { ko } from 'date-fns/locale';

// 클래스명 유틸리티
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

// 날짜 포맷팅 유틸리티
export const formatDate = (dateString: string, formatString: string = 'yyyy-MM-dd HH:mm:ss') => {
  try {
    return format(new Date(dateString), formatString, { locale: ko });
  } catch (error) {
    return 'Invalid Date';
  }
};

export const formatRelativeTime = (dateString: string) => {
  try {
    return formatDistanceToNow(new Date(dateString), { addSuffix: true, locale: ko });
  } catch (error) {
    return 'Invalid Date';
  }
};

// 해시값 포맷팅
export const formatHash = (hash: string, length: number = 8) => {
  if (!hash) return '';
  return `${hash.substring(0, length)}...${hash.substring(hash.length - length)}`;
};

// 트랜잭션 해시 포맷팅
export const formatTransactionHash = (txHash: string) => {
  if (!txHash) return '';
  return `${txHash.substring(0, 10)}...${txHash.substring(txHash.length - 8)}`;
};

// Etherscan 링크 생성
export const getEtherscanUrl = (txHash: string, network: string = 'sepolia') => {
  const baseUrl = network === 'mainnet' ? 'https://etherscan.io' : 'https://sepolia.etherscan.io';
  return `${baseUrl}/tx/${txHash}`;
};

// 응답 시간 포맷팅
export const formatResponseTime = (timeInSeconds: number) => {
  if (timeInSeconds < 1) {
    return `${Math.round(timeInSeconds * 1000)}ms`;
  }
  return `${timeInSeconds.toFixed(2)}s`;
};

// 텍스트 자르기
export const truncateText = (text: string, maxLength: number = 100) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
};

// 에러 메시지 추출
export const getErrorMessage = (error: any): string => {
  if (typeof error === 'string') return error;
  if (error?.response?.data?.error) return error.response.data.error;
  if (error?.response?.data?.message) return error.response.data.message;
  if (error?.message) return error.message;
  return '알 수 없는 오류가 발생했습니다.';
};

// 로컬 스토리지 유틸리티
export const storage = {
  get: (key: string) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch (error) {
      console.error('Storage get error:', error);
      return null;
    }
  },
  set: (key: string, value: any) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Storage set error:', error);
    }
  },
  remove: (key: string) => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Storage remove error:', error);
    }
  },
};

// 복사 기능
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    console.error('Copy to clipboard error:', error);
    return false;
  }
};

// 다운로드 기능
export const downloadAsFile = (content: string, filename: string, type: string = 'text/plain') => {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};
