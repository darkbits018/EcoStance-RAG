import { useState } from 'react';
import {
  useAuth,
  useKnowledgeBase,
  useFileManagement,
  useQuota,
  useMetrics,
  useAdmin,
} from '../hooks';

/**
 * Example component demonstrating API integration
 * This shows how to use the various hooks to interact with the backend API
 */
export function APIIntegrationExample() {
  const [selectedKB, setSelectedKB] = useState('default');
  const [query, setQuery] = useState('');

  // Authentication
  const { isAuthenticated, login, logout } = useAuth();

  // Knowledge Base operations
  const {
    loading: kbLoading,
    error: kbError,
    listKnowledgeBases,
    getKBDetails,
    queryKB,
  } = useKnowledgeBase();

  // File management
  const {
    loading: fileLoading,
    uploadFile,
    listFiles,
    downloadFile,
    deleteFile,
  } = useFileManagement();

  // Quota monitoring
  const {
    status: quotaStatus,
    isStorageWarning,
    isQueryWarning,
  } = useQuota();

  // Metrics
  const {
    getTenantMetrics,
    getQueryMetrics,
    exportMetrics,
  } = useMetrics();

  // Admin operations (if user has admin role)
  const {
    getSystemHealth,
    getDashboardSummary,
    searchTenants,
  } = useAdmin();

  // Example: Handle file upload
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const result = await uploadFile(file);
    if (result) {
      console.log('File uploaded successfully:', result);
      // Optionally refresh file list
      await listFiles();
    }
  };

  // Example: Query knowledge base
  const handleQuery = async () => {
    if (!query.trim()) return;

    const result = await queryKB(selectedKB, query);
    if (result) {
      console.log('Query result:', result.answer);
    }
  };

  // Example: Export metrics
  const handleExportMetrics = async () => {
    await exportMetrics('csv', 30);
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">API Integration Example</h1>

      {/* Authentication Status */}
      <div className="border rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-2">Authentication</h2>
        <p>Status: {isAuthenticated ? 'Authenticated' : 'Not authenticated'}</p>
        {isAuthenticated && (
          <button
            onClick={logout}
            className="mt-2 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
          >
            Logout
          </button>
        )}
      </div>

      {/* Quota Status */}
      {quotaStatus && (
        <div className="border rounded-lg p-4">
          <h2 className="text-lg font-semibold mb-2">Quota Status</h2>
          <div className="space-y-2">
            <div>
              <p className="text-sm text-gray-600">Storage Usage</p>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      isStorageWarning() ? 'bg-red-500' : 'bg-blue-500'
                    }`}
                    style={{ width: `${quotaStatus.data.storage.usage_percent}%` }}
                  />
                </div>
                <span className="text-sm">
                  {quotaStatus.data.storage.usage_percent.toFixed(1)}%
                </span>
              </div>
            </div>
            <div>
              <p className="text-sm text-gray-600">Daily Queries</p>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      isQueryWarning() ? 'bg-red-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${quotaStatus.data.queries.daily_percent}%` }}
                  />
                </div>
                <span className="text-sm">
                  {quotaStatus.data.queries.daily_used} / {quotaStatus.data.queries.daily_limit}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* File Upload */}
      <div className="border rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-2">File Upload</h2>
        <input
          type="file"
          onChange={handleFileUpload}
          disabled={fileLoading}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
        {fileLoading && <p className="mt-2 text-sm text-gray-600">Uploading...</p>}
      </div>

      {/* Knowledge Base Query */}
      <div className="border rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-2">Query Knowledge Base</h2>
        <div className="space-y-2">
          <input
            type="text"
            value={selectedKB}
            onChange={(e) => setSelectedKB(e.target.value)}
            placeholder="Knowledge base name"
            className="w-full px-3 py-2 border rounded"
          />
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your question..."
            rows={3}
            className="w-full px-3 py-2 border rounded"
          />
          <button
            onClick={handleQuery}
            disabled={kbLoading || !query.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-300"
          >
            {kbLoading ? 'Querying...' : 'Query'}
          </button>
          {kbError && <p className="text-sm text-red-600">{kbError.message}</p>}
        </div>
      </div>

      {/* Metrics Export */}
      <div className="border rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-2">Export Metrics</h2>
        <button
          onClick={handleExportMetrics}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
        >
          Export Last 30 Days (CSV)
        </button>
      </div>

      {/* API Usage Examples */}
      <div className="border rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-2">More API Examples</h2>
        <div className="space-y-2 text-sm">
          <button
            onClick={() => listKnowledgeBases()}
            className="block w-full text-left px-3 py-2 bg-gray-100 rounded hover:bg-gray-200"
          >
            List Knowledge Bases
          </button>
          <button
            onClick={() => getTenantMetrics('daily', 7)}
            className="block w-full text-left px-3 py-2 bg-gray-100 rounded hover:bg-gray-200"
          >
            Get Tenant Metrics (7 days)
          </button>
          <button
            onClick={() => getQueryMetrics(7)}
            className="block w-full text-left px-3 py-2 bg-gray-100 rounded hover:bg-gray-200"
          >
            Get Query Performance Metrics
          </button>
          <button
            onClick={() => getSystemHealth()}
            className="block w-full text-left px-3 py-2 bg-gray-100 rounded hover:bg-gray-200"
          >
            Get System Health (Admin)
          </button>
        </div>
      </div>
    </div>
  );
}
