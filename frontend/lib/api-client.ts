import { fetchAuthSession } from 'aws-amplify/auth';

const API_ENDPOINT = process.env.NEXT_PUBLIC_API_ENDPOINT;

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function getAuthToken(): Promise<string> {
  try {
    const session = await fetchAuthSession();
    const token = session.tokens?.idToken?.toString();
    if (!token) {
      throw new Error('No authentication token available');
    }
    return token;
  } catch (error) {
    console.error('Error getting auth token:', error);
    throw new Error('Authentication required');
  }
}

export async function apiCall<T = any>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getAuthToken();

  const response = await fetch(`${API_ENDPOINT}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new ApiError(response.status, error.error || `HTTP ${response.status}`);
  }

  return response.json();
}

// Request API functions
export const requestsApi = {
  list: () => apiCall('/requests'),
  
  get: (id: string) => apiCall(`/requests/${id}`),
  
  create: (data: { title: string; description: string }) =>
    apiCall('/requests', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  update: (id: string, data: any) =>
    apiCall(`/requests/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  
  classify: (id: string) =>
    apiCall(`/requests/${id}/classify`, {
      method: 'POST',
    }),
  
  executeAction: (id: string, action: string, parameters?: any) =>
    apiCall(`/requests/${id}/action`, {
      method: 'POST',
      body: JSON.stringify({ action, parameters }),
    }),
  
  chat: (id: string, message: string, history?: any[]) =>
    apiCall(`/requests/${id}/chat`, {
      method: 'POST',
      body: JSON.stringify({ message, history }),
    }),
  
  resolve: (id: string, resolution: string) =>
    apiCall(`/requests/${id}/resolve`, {
      method: 'POST',
      body: JSON.stringify({ resolution }),
    }),
};
