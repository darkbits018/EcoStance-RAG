import { api } from './api';

export interface Email {
    id: string; // Gmail Message ID
    thread_id: string;
    sender: string;
    recipients: string;
    subject: string;
    snippet: string;
    body_text?: string;
    body_html?: string;
    received_at: string;
    labels: string[];
}

export interface EmailListingParams {
    page?: number;
    limit?: number;
    search?: string;
    sort_by?: string;
}

export const emailService = {
    // List emails
    getEmails: async (params: EmailListingParams = {}): Promise<Email[]> => {
        const response = await api.get<Email[]>('/emails/', { params });
        return response.data;
    },

    // Get single email details
    getEmail: async (id: string): Promise<Email> => {
        const response = await api.get<Email>(`/emails/${id}`);
        return response.data;
    },
};
