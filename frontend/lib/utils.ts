import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

export function getSeverityColor(severity: number): string {
  switch (severity) {
    case 1:
      return 'text-red-600 bg-red-50';
    case 2:
      return 'text-orange-600 bg-orange-50';
    case 3:
      return 'text-yellow-600 bg-yellow-50';
    case 4:
      return 'text-blue-600 bg-blue-50';
    default:
      return 'text-gray-600 bg-gray-50';
  }
}

export function getStatusColor(status: string): string {
  switch (status) {
    case 'submitted':
      return 'text-blue-600 bg-blue-50';
    case 'classified':
      return 'text-purple-600 bg-purple-50';
    case 'in_progress':
      return 'text-yellow-600 bg-yellow-50';
    case 'resolved':
      return 'text-green-600 bg-green-50';
    case 'classification_failed':
      return 'text-red-600 bg-red-50';
    default:
      return 'text-gray-600 bg-gray-50';
  }
}
