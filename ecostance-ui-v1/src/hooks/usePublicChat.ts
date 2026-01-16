import { useState, useEffect } from 'react';
import { publicChatAPI } from '../services/api';

interface PublicChatConfig {
  enabled: boolean;
  allowed_kbs: string[];
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
  };
}

interface KnowledgeBase {
  kb_name: string;
  document_count: number;
}

export const usePublicChatConfig = () => {
  const [config, setConfig] = useState<PublicChatConfig | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadConfig = async () => {
      try {
        const data = await publicChatAPI.getConfig() as PublicChatConfig;
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

export const usePublicChatAdmin = () => {
  const [config, setConfig] = useState<PublicChatConfig | null>(null);
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [configData, kbsData] = await Promise.all([
          publicChatAPI.admin.getConfig() as Promise<PublicChatConfig>,
          publicChatAPI.admin.getAvailableKBs() as Promise<any>,
        ]);
        
        setConfig(configData);
        
        console.log('Raw KB data from API:', kbsData);
        
        // Transform KB data from the manage/knowledge-bases endpoint
        // The endpoint returns an array of KB names (strings) or objects
        const transformedKBs: KnowledgeBase[] = Array.isArray(kbsData) 
          ? kbsData.map((kb: any) => {
              console.log('Processing KB item:', kb, 'Type:', typeof kb);
              // If it's a string, just use it as the kb_name
              if (typeof kb === 'string') {
                const result = {
                  kb_name: kb,
                  document_count: 0, // We don't have count info from this endpoint
                };
                console.log('Created KB object from string:', result);
                return result;
              }
              // If it's an object, extract the properties
              const result = {
                kb_name: kb.kb_name || kb.name || String(kb),
                document_count: kb.document_count || kb.documents?.length || 0,
              };
              console.log('Created KB object from object:', result);
              return result;
            })
          : [];
        
        console.log('Transformed KBs:', transformedKBs);
        setKnowledgeBases(transformedKBs);
      } catch (err: any) {
        console.error('Error loading data:', err);
        setError(err.message || 'Failed to load configuration');
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  const saveConfig = async (newConfig: PublicChatConfig) => {
    setIsSaving(true);
    setError(null);
    
    try {
      await publicChatAPI.admin.updateConfig(newConfig);
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
    isLoading, 
    isSaving,
    error,
    saveConfig,
  };
};

export const usePublicChatQuery = (sessionId: string) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendQuery = async (
    query: string,
    conversationHistory: Array<{ role: string; content: string }>
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await publicChatAPI.query({
        session_id: sessionId,
        query,
        conversation_history: conversationHistory,
      }) as any;

      return {
        success: true,
        data: response,
      };
    } catch (err: any) {
      console.error('Error sending query:', err);
      setError(err.message || 'Failed to send query');
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
      await publicChatAPI.submitFeedback({
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
    sendQuery,
    submitFeedback,
    isLoading,
    error,
  };
};
