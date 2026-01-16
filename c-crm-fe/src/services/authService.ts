import { api } from './api';

export interface GmailConnection {
    id: string;
    email_address: string;
    is_active: boolean;
    token_expiry: string;
}

export const authService = {
    // Get the login URL for Google OAuth
    getLoginUrl: async (): Promise<string> => {
        const response = await api.get<string>('/auth/login'); // Keep as is, auth usually okay
        return response.data;
    },

    // Check current connection status
    listConnections: async (): Promise<GmailConnection[]> => {
        const response = await api.get<GmailConnection[]>('/connections/'); // Added slash
        return response.data;
    },
};
