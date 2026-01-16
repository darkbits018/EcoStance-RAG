import { api } from './api';

export type DumpStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
export type CriteriaType = 'LABEL' | 'RECIPIENT';

export interface EmailDumpTask {
    id: string;
    connection_id: string;
    status: DumpStatus;
    criteria_type: CriteriaType;
    criteria_value: string; // e.g., "INBOX" or "bob@example.com"
    started_at: string;
    completed_at?: string;
    total_emails: number;
}

export interface CreateDumpRequest {
    connection_id: string;
    criteria_type: CriteriaType;
    criteria_value: string;
}

export const dumpService = {
    // List all dumps
    getAllDumps: async (): Promise<EmailDumpTask[]> => {
        const response = await api.get<EmailDumpTask[]>('/dumps/');
        return response.data;
    },

    // Get a specific dump
    getDump: async (id: string): Promise<EmailDumpTask> => {
        const response = await api.get<EmailDumpTask>(`/dumps/${id}`);
        return response.data;
    },

    // Trigger a new dump
    createDump: async (data: CreateDumpRequest): Promise<EmailDumpTask> => {
        const response = await api.post<EmailDumpTask>('/dumps/', {
            connection_id: data.connection_id,
            criteria_type: data.criteria_type,
            criteria_value: data.criteria_value
        });
        return response.data;
    },
    deleteDump: async (id: string): Promise<void> => {
        await api.delete(`/dumps/${id}`);
    },
    rerunDump: async (id: string): Promise<EmailDumpTask> => {
        const response = await api.post<EmailDumpTask>(`/dumps/${id}/rerun`);
        return response.data;
    }
};
