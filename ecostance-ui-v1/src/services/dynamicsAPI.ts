import { apiClient } from './api';

export interface DynamicsConfig {
    tenant_id: string;
    client_id: string;
    resource_url: string;
    is_configured: boolean;
    last_sync: string | null;
}

export interface DynamicsConfigPayload {
    tenant_id: string;
    client_id: string;
    client_secret: string;
    resource_url: string;
}

export interface TestConnectionResponse {
    success: boolean;
    message: string;
}

export interface SyncResponse {
    message: string;
    emails_found: number;
    chunks_created: number;
}

export const dynamicsAPI = {
    getConfig: async () => {
        return apiClient.get<DynamicsConfig>('/dynamics/config');
    },

    saveConfig: async (config: DynamicsConfigPayload) => {
        return apiClient.post('/dynamics/config', config);
    },

    testConnection: async () => {
        return apiClient.post<TestConnectionResponse>('/dynamics/test');
    },

    syncNow: async (lookbackMinutes: number = 60) => {
        return apiClient.post<SyncResponse>(`/dynamics/sync/now?lookback_minutes=${lookbackMinutes}`);
    },
};
