import { useState, useEffect } from 'react';
import { publicAgentAPI } from '../services/api';

interface PublicAgentConfig {
  enabled: boolean;
  allowed_kbs: string[];
  allowed_dbs: string[];
  welcome_message: string;
  suggested_questions: string[];
  branding: {
    logo_url?: string;
    primary_color: string;
    company_name: string;
  };
  rate_limit: {
    queries_per_minute: number;
    max_messages_per_session: number;
  };
  features: {
    show_sources: boolean;
    allow_feedback: boolean;
    show_suggested_questions: boolean;
    enable_database_tools: boolean;
    enable_knowledge_base: boolean;
  };
}

interface KnowledgeBase {
  kb_name: string;
  document_count: number;
}

interface DatabaseConnection {
  name: string;
  type: string;
}

export const usePublicAgentConfig = () => {
  const [config, setConfig] = useState<PublicAgentConfig | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadConfig = async () => {
      try {
        const data = await publicAgentAPI.getConfig() as PublicAgentConfig;
        setConfig(data);
      } catch (err: any) {
        console.error('Error loading config:', err);
        setError(err.message || 'Failed to load configuration');
      } finally {
        setIsLoading(false);
      }
    };

    loadConfig();
  }, []);

  return { config, isLoading, error };
};

export const usePublicAgentAdmin = () => {
  const [config, setConfig] = useState<PublicAgentConfig | null>(null);
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [databases, setDatabases] = useState<DatabaseConnection[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [configData, kbsData, dbsData] = await Promise.all([
          publicAgentAPI.admin.getConfig() as Promise<PublicAgentConfig>,
          publicAgentAPI.admin.getAvailableKBs() as Promise<any>,
          publicAgentAPI.admin.getAvailableDBs() as Promise<any>,
        ]);
        
        setConfig(configData);
        
        // Transform KB data
        const transformedKBs: KnowledgeBase[] = Array.isArray(kbsData) 
          ? kbsData.map((kb: any) => {
              if (typeof kb === 'string') {
                return {
                  kb_name: kb,
                  document_count: 0,
                };
              }
              return {
                kb_name: kb.kb_name || kb.name || String(kb),
                document_count: kb.document_count || kb.documents?.length || 0,
              };
            })
          : [];
        
        setKnowledgeBases(transformedKBs);
        setDatabases(Array.isArray(dbsData) ? dbsData : []);
      } catch (err: any) {
        console.error('Error loading data:', err);
        setError(err.message || 'Failed to load configuration');
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  const saveConfig = async (newConfig: PublicAgentConfig) => {
    setIsSaving(true);
    setError(null);
    
    try {
      await publicAgentAPI.admin.updateConfig(newConfig);
      setConfig(newConfig);
      return { success: true };
    } catch (err: any) {
      console.error('Error saving config:', err);
      setError(err.message || 'Failed to save configuration');
      return { success: false, error: err.message };
    } finally {
      setIsSaving(false);
    }
  };

  return { 
    config, 
    setConfig,
    knowledgeBases,
    databases,
    isLoading, 
    isSaving,
    error,
    saveConfig,
  };
};

export const usePublicAgentChat = (sessionId: string) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async (
    message: string,
    conversationHistory: Array<{ role: string; content: string }>
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await publicAgentAPI.chat({
        session_id: sessionId,
        message,
        conversation_history: conversationHistory,
      }) as any;

      return {
        success: true,
        data: response,
      };
    } catch (err: any) {
      console.error('Error sending message:', err);
      setError(err.message || 'Failed to send message');
      return {
        success: false,
        error: err.message,
      };
    } finally {
      setIsLoading(false);
    }
  };

  const submitFeedback = async (
    messageId: string,
    feedbackType: 'positive' | 'negative',
    comment?: string
  ) => {
    try {
      await publicAgentAPI.submitFeedback({
        session_id: sessionId,
        message_id: messageId,
        feedback_type: feedbackType,
        comment,
      });
      return { success: true };
    } catch (err: any) {
      console.error('Error submitting feedback:', err);
      return { success: false, error: err.message };
    }
  };

  return {
    sendMessage,
    submitFeedback,
    isLoading,
    error,
  };
};
