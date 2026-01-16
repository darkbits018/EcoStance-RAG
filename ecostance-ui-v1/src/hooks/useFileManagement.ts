import { useState, useCallback } from 'react';
import { filesAPI } from '../services/api';
import type { FileInfo, UploadFileResponse, StorageUsage, QuotaCheckResponse } from '../services/api.types';

export function useFileManagement() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const uploadFile = useCallback(async (file: File): Promise<UploadFileResponse | null> => {
    try {
      setLoading(true);
      setError(null);
      setUploadProgress(0);
      
      const response = await filesAPI.upload(file) as UploadFileResponse;
      setUploadProgress(100);
      
      return response;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to upload file');
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const listFiles = useCallback(async (): Promise<FileInfo[] | null> => {
    try {
      setLoading(true);
      setError(null);
      return await filesAPI.list() as FileInfo[];
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to list files');
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const downloadFile = useCallback(async (filename: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const blob = await filesAPI.download(filename);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      return true;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to download file');
      setError(error);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteFile = useCallback(async (filename: string) => {
    try {
      setLoading(true);
      setError(null);
      return await filesAPI.delete(filename);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to delete file');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const getStorageUsage = useCallback(async (): Promise<StorageUsage | null> => {
    try {
      setLoading(true);
      setError(null);
      return await filesAPI.getStorageUsage() as StorageUsage;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to get storage usage');
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const checkQuota = useCallback(async (fileSizeMb: number): Promise<QuotaCheckResponse | null> => {
    try {
      return await filesAPI.checkQuota(fileSizeMb) as QuotaCheckResponse;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to check quota');
      setError(error);
      return null;
    }
  }, []);

  const deleteAllFiles = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      return await filesAPI.deleteAll();
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to delete all files');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    uploadProgress,
    uploadFile,
    listFiles,
    downloadFile,
    deleteFile,
    getStorageUsage,
    checkQuota,
    deleteAllFiles,
  };
}
