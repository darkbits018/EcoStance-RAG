import React, { useState, useMemo } from 'react';
import { Icons } from './icons';
import { Badge } from './ui/Badge';
import { Button } from './ui/Button';
import { Checkbox } from './ui/Checkbox';
import { Select } from './ui/Select';
import { Input } from './ui/Input';
import { DropdownMenu, DropdownMenuItem } from './ui/DropdownMenu';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from './ui/Dialog';
import { cn } from '../lib/utils';
import { knowledgeBaseAPI } from '../services/api';

export interface Document {
  id: string;
  filename: string;
  fileType: "pdf" | "docx" | "txt" | "csv" | "json" | "wav" | "mp3" | "m4a" | "ogg" | "audio" | "md" | "unknown";
  uploadDate: string;
  chunks: number;
  fileSize: string;
  characters: number;
  status: "Processing" | "Indexed" | "Failed";
  filePath?: string;
  processingDate?: string;
  chunkSize?: number;
  embeddingModel?: string;
  processingDuration?: string;
  errorLogs?: string;
  firstChunkPreview?: string;
  chunksList?: string[];
}

interface DocumentsTableProps {
  documents: Document[];
  knowledgeBaseName?: string; // Add KB name for API calls
  onDownload?: (doc: Document) => void;
  onReindex?: (doc: Document) => void;
  onDelete?: (doc: Document) => void;
  onBulkReindex?: (docs: Document[]) => void;
  onBulkDelete?: (docs: Document[]) => void;
  onUpload?: () => void;
}

type SortField = 'filename' | 'fileType' | 'uploadDate' | 'chunks' | 'fileSize' | 'characters' | 'status';
type SortDirection = 'asc' | 'desc';

export const DocumentsTable: React.FC<DocumentsTableProps> = ({
  documents,
  knowledgeBaseName,
  onDownload,
  onReindex,
  onDelete,
  onBulkReindex,
  onBulkDelete,
  onUpload,
}) => {
  const [selectedDocs, setSelectedDocs] = useState<Set<string>>(new Set());
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [sortField, setSortField] = useState<SortField>('uploadDate');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [jumpToPage, setJumpToPage] = useState('');

  // File details state
  const [fileDetails, setFileDetails] = useState<Record<string, any>>({});
  const [loadingDetails, setLoadingDetails] = useState<Set<string>>(new Set());

  // Modals
  const [deleteConfirmDoc, setDeleteConfirmDoc] = useState<Document | null>(null);
  const [bulkDeleteConfirm, setBulkDeleteConfirm] = useState(false);
  const [viewChunksDoc, setViewChunksDoc] = useState<Document | null>(null);

  // Sort documents
  const sortedDocuments = useMemo(() => {
    const sorted = [...documents].sort((a, b) => {
      let aVal: any = a[sortField];
      let bVal: any = b[sortField];

      if (sortField === 'uploadDate') {
        aVal = new Date(aVal).getTime();
        bVal = new Date(bVal).getTime();
      } else if (sortField === 'fileSize') {
        aVal = parseFloat(aVal);
        bVal = parseFloat(bVal);
      }

      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
    return sorted;
  }, [documents, sortField, sortDirection]);

  // Pagination
  const totalPages = Math.ceil(sortedDocuments.length / itemsPerPage);
  const paginatedDocuments = sortedDocuments.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const toggleSelectAll = () => {
    if (selectedDocs.size === paginatedDocuments.length) {
      setSelectedDocs(new Set());
    } else {
      setSelectedDocs(new Set(paginatedDocuments.map(doc => doc.id)));
    }
  };

  const toggleSelectDoc = (docId: string) => {
    const newSelected = new Set(selectedDocs);
    if (newSelected.has(docId)) {
      newSelected.delete(docId);
    } else {
      newSelected.add(docId);
    }
    setSelectedDocs(newSelected);
  };

  const toggleExpandRow = async (docId: string) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(docId)) {
      newExpanded.delete(docId);
      setExpandedRows(newExpanded);
    } else {
      newExpanded.add(docId);
      setExpandedRows(newExpanded);

      // Fetch file details if not already loaded and KB name is provided
      if (!fileDetails[docId] && knowledgeBaseName) {
        const doc = documents.find(d => d.id === docId);
        if (doc) {
          setLoadingDetails(prev => new Set(prev).add(docId));
          try {
            const details = await knowledgeBaseAPI.getFileDetails(knowledgeBaseName, doc.filename);
            setFileDetails(prev => ({ ...prev, [docId]: details }));
          } catch (error) {
            console.error('Failed to fetch file details:', error);
          } finally {
            setLoadingDetails(prev => {
              const newSet = new Set(prev);
              newSet.delete(docId);
              return newSet;
            });
          }
        }
      }
    }
  };

  const handleJumpToPage = () => {
    const page = parseInt(jumpToPage);
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
      setJumpToPage('');
    }
  };

  const getFileTypeIcon = (fileType: Document['fileType']) => {
    switch (fileType) {
      case "pdf":
        return <Icons.FileText className="h-4 w-4 text-red-500" />;
      case "docx":
        return <Icons.FileText className="h-4 w-4 text-blue-500" />;
      case "txt":
        return <Icons.FileText className="h-4 w-4 text-text-secondary" />;
      case "csv":
        return <Icons.FileText className="h-4 w-4 text-green-500" />;
      case "json":
        return <Icons.FileText className="h-4 w-4 text-purple-500" />;
      case "wav":
      case "mp3":
      case "m4a":
      case "ogg":
      case "audio":
        return <Icons.FileAudio className="h-4 w-4 text-yellow-500" />;
      case "md":
        return <Icons.FileText className="h-4 w-4 text-gray-500" />;
      case "unknown":
      default:
        return <Icons.FileText className="h-4 w-4 text-text-secondary" />;
    }
  };

  const getFileTypeBadgeColor = (fileType: Document['fileType']) => {
    const colors = {
      pdf: 'bg-red-500/20 text-red-400 border border-red-500/30',
      docx: 'bg-blue-500/20 text-blue-400 border border-blue-500/30',
      txt: 'bg-surface text-text-secondary border border-border',
      csv: 'bg-green-500/20 text-green-400 border border-green-500/30',
      json: 'bg-purple-500/20 text-purple-400 border border-purple-500/30',
      wav: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30',
      mp3: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30',
      m4a: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30',
      ogg: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30',
      audio: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30',
      md: 'bg-gray-500/20 text-gray-400 border border-gray-500/30',
      unknown: 'bg-surface text-text-secondary border border-border',
    };
    return colors[fileType] || 'bg-surface text-text-secondary border border-border';
  };

  const getStatusBadgeVariant = (status: Document['status']) => {
    switch (status) {
      case "Indexed":
        return "default";
      case "Processing":
        return "secondary";
      case "Failed":
        return "destructive";
      default:
        return "outline";
    }
  };

  const formatNumber = (num: number) => num.toLocaleString();

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const selectedDocuments = documents.filter(doc => selectedDocs.has(doc.id));

  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-4 bg-surface rounded-lg border border-border">
        <Icons.FileStack className="h-16 w-16 text-text-secondary mb-4" />
        <h3 className="text-xl font-semibold text-text mb-2">No documents yet</h3>
        <p className="text-text-secondary mb-6">Upload your first document to get started</p>
        <Button onClick={onUpload}>
          <Icons.Upload className="h-4 w-4 mr-2" />
          Upload Document
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Bulk Actions Bar */}
      {selectedDocs.size > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-center justify-between">
          <span className="text-sm font-medium text-blue-900">
            {selectedDocs.size} document{selectedDocs.size > 1 ? 's' : ''} selected
          </span>
          <div className="flex space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onBulkReindex?.(selectedDocuments)}
            >
              <Icons.RefreshCw className="h-4 w-4 mr-2" />
              Reindex Selected
            </Button>
            <Button
              variant="destructive"
              size="sm"
              onClick={() => setBulkDeleteConfirm(true)}
            >
              <Icons.Trash className="h-4 w-4 mr-2" />
              Delete Selected
            </Button>
          </div>
        </div>
      )}

      {/* Table */}
      <div className="bg-surface rounded-lg shadow overflow-hidden border border-border">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-background border-b border-border">
              <tr>
                <th className="px-4 py-3 text-left w-12">
                  <Checkbox
                    checked={selectedDocs.size === paginatedDocuments.length && paginatedDocuments.length > 0}
                    onChange={toggleSelectAll}
                  />
                </th>
                <th className="px-4 py-3 text-left w-8"></th>
                <th
                  className="px-4 py-3 text-left cursor-pointer hover:bg-surface-hover"
                  onClick={() => handleSort('filename')}
                >
                  <div className="flex items-center space-x-1">
                    <span className="text-sm font-medium text-text">Filename</span>
                    {sortField === 'filename' && (
                      sortDirection === 'asc' ? <Icons.ArrowUp className="h-3 w-3" /> : <Icons.ArrowDown className="h-3 w-3" />
                    )}
                  </div>
                </th>
                <th
                  className="px-4 py-3 text-left cursor-pointer hover:bg-surface-hover"
                  onClick={() => handleSort('fileType')}
                >
                  <div className="flex items-center space-x-1">
                    <span className="text-sm font-medium text-text">File Type</span>
                    {sortField === 'fileType' && (
                      sortDirection === 'asc' ? <Icons.ArrowUp className="h-3 w-3" /> : <Icons.ArrowDown className="h-3 w-3" />
                    )}
                  </div>
                </th>
                <th
                  className="px-4 py-3 text-left cursor-pointer hover:bg-surface-hover"
                  onClick={() => handleSort('uploadDate')}
                >
                  <div className="flex items-center space-x-1">
                    <span className="text-sm font-medium text-text">Upload Date</span>
                    {sortField === 'uploadDate' && (
                      sortDirection === 'asc' ? <Icons.ArrowUp className="h-3 w-3" /> : <Icons.ArrowDown className="h-3 w-3" />
                    )}
                  </div>
                </th>
                <th
                  className="px-4 py-3 text-left cursor-pointer hover:bg-surface-hover"
                  onClick={() => handleSort('chunks')}
                >
                  <div className="flex items-center space-x-1">
                    <span className="text-sm font-medium text-text">Chunks</span>
                    {sortField === 'chunks' && (
                      sortDirection === 'asc' ? <Icons.ArrowUp className="h-3 w-3" /> : <Icons.ArrowDown className="h-3 w-3" />
                    )}
                  </div>
                </th>
                <th className="px-4 py-3 text-left">
                  <span className="text-sm font-medium text-text">File Size</span>
                </th>
                <th
                  className="px-4 py-3 text-left cursor-pointer hover:bg-surface-hover"
                  onClick={() => handleSort('characters')}
                >
                  <div className="flex items-center space-x-1">
                    <span className="text-sm font-medium text-text">Characters</span>
                    {sortField === 'characters' && (
                      sortDirection === 'asc' ? <Icons.ArrowUp className="h-3 w-3" /> : <Icons.ArrowDown className="h-3 w-3" />
                    )}
                  </div>
                </th>
                <th
                  className="px-4 py-3 text-left cursor-pointer hover:bg-surface-hover"
                  onClick={() => handleSort('status')}
                >
                  <div className="flex items-center space-x-1">
                    <span className="text-sm font-medium text-text">Status</span>
                    {sortField === 'status' && (
                      sortDirection === 'asc' ? <Icons.ArrowUp className="h-3 w-3" /> : <Icons.ArrowDown className="h-3 w-3" />
                    )}
                  </div>
                </th>
                <th className="px-4 py-3 text-left">
                  <span className="text-sm font-medium text-text">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {paginatedDocuments.map((doc) => (
                <React.Fragment key={doc.id}>
                  <tr className="hover:bg-surface-hover">
                    <td className="px-4 py-3">
                      <Checkbox
                        checked={selectedDocs.has(doc.id)}
                        onChange={() => toggleSelectDoc(doc.id)}
                      />
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => toggleExpandRow(doc.id)}
                        className="text-text-secondary hover:text-text"
                      >
                        {expandedRows.has(doc.id) ? (
                          <Icons.ChevronUp className="h-4 w-4" />
                        ) : (
                          <Icons.ChevronDown className="h-4 w-4" />
                        )}
                      </button>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center space-x-2">
                        {getFileTypeIcon(doc.fileType)}
                        <span className="text-sm text-text">{doc.filename}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={cn('px-2 py-1 text-xs font-medium rounded', getFileTypeBadgeColor(doc.fileType))}>
                        {doc.fileType.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-text-secondary">
                      {formatDate(doc.uploadDate)}
                    </td>
                    <td className="px-4 py-3 text-sm text-text">
                      {formatNumber(doc.chunks)}
                    </td>
                    <td className="px-4 py-3 text-sm text-text-secondary">
                      {doc.fileSize}
                    </td>
                    <td className="px-4 py-3 text-sm text-text">
                      {formatNumber(doc.characters)}
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={getStatusBadgeVariant(doc.status)}>
                        {doc.status}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <DropdownMenu
                        trigger={
                          <button className="p-1 hover:bg-surface rounded">
                            <Icons.MoreHorizontal className="h-4 w-4 text-text-secondary" />
                          </button>
                        }
                      >
                        <DropdownMenuItem onClick={() => onDownload?.(doc)}>
                          <Icons.Download className="h-4 w-4" />
                          <span>Download</span>
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onReindex?.(doc)}>
                          <Icons.RefreshCw className="h-4 w-4" />
                          <span>Reindex</span>
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => setViewChunksDoc(doc)}>
                          <Icons.Eye className="h-4 w-4" />
                          <span>View Chunks</span>
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => setDeleteConfirmDoc(doc)}
                          variant="destructive"
                        >
                          <Icons.Trash className="h-4 w-4" />
                          <span>Delete</span>
                        </DropdownMenuItem>
                      </DropdownMenu>
                    </td>
                  </tr>
                  {expandedRows.has(doc.id) && (
                    <tr className="bg-background">
                      <td colSpan={10} className="px-4 py-4">
                        {loadingDetails.has(doc.id) ? (
                          <div className="flex items-center justify-center py-8">
                            <Icons.Loader2 className="h-6 w-6 animate-spin text-text-secondary" />
                            <span className="ml-2 text-text-secondary">Loading file details...</span>
                          </div>
                        ) : (
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            {(() => {
                              const details = fileDetails[doc.id];
                              return (
                                <>
                                  <div>
                                    <span className="font-medium text-text">Collection Name:</span>
                                    <p className="text-text-secondary mt-1">{details?.collection_name || 'N/A'}</p>
                                  </div>
                                  <div>
                                    <span className="font-medium text-text">Processing Date:</span>
                                    <p className="text-text-secondary mt-1">{details?.processing_date || formatDate(doc.uploadDate)}</p>
                                  </div>
                                  <div>
                                    <span className="font-medium text-text">File Size:</span>
                                    <p className="text-text-secondary mt-1">{details?.file_size_mb || doc.fileSize}</p>
                                  </div>
                                  <div>
                                    <span className="font-medium text-text">Embedding Model:</span>
                                    <p className="text-text-secondary mt-1">{details?.embedding_model || 'N/A'}</p>
                                  </div>
                                  <div>
                                    <span className="font-medium text-text">Embedding Dimension:</span>
                                    <p className="text-text-secondary mt-1">{details?.embedding_dimension || 'N/A'}</p>
                                  </div>
                                  <div>
                                    <span className="font-medium text-text">Processing Version:</span>
                                    <p className="text-text-secondary mt-1">{details?.processing_version || 'N/A'}</p>
                                  </div>
                                  <div>
                                    <span className="font-medium text-text">Extraction Method:</span>
                                    <p className="text-text-secondary mt-1">{details?.extraction_method || 'N/A'}</p>
                                  </div>
                                  <div>
                                    <span className="font-medium text-text">Total Pages:</span>
                                    <p className="text-text-secondary mt-1">{details?.total_pages || 'N/A'}</p>
                                  </div>
                                  {details?.multilingual_processed && (
                                    <>
                                      <div>
                                        <span className="font-medium text-text">Languages Detected:</span>
                                        <div className="mt-1 flex flex-wrap gap-1">
                                          {details.languages?.distribution && Object.entries(details.languages.distribution).map(([lang, count]) => (
                                            <span key={lang} className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                                              {lang.toUpperCase()}: {count}
                                            </span>
                                          ))}
                                        </div>
                                      </div>
                                      <div>
                                        <span className="font-medium text-text">Primary Language:</span>
                                        <p className="text-text-secondary mt-1">{details.languages?.primary_language?.toUpperCase() || 'N/A'}</p>
                                      </div>
                                    </>
                                  )}
                                  {doc.status === 'Failed' && doc.errorLogs && (
                                    <div className="col-span-2">
                                      <span className="font-medium text-red-700">Error Logs:</span>
                                      <p className="text-red-600 mt-1 bg-red-50 p-2 rounded">{doc.errorLogs}</p>
                                    </div>
                                  )}
                                  <div className="col-span-2">
                                    <span className="font-medium text-text">First Chunk Preview:</span>
                                    <p className="text-text-secondary mt-1 bg-background p-3 rounded border border-border text-xs">
                                      {details?.chunks?.[0]?.text?.substring(0, 200) + '...' || 'No preview available'}
                                    </p>
                                  </div>
                                </>
                              );
                            })()}
                          </div>
                        )}
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="bg-background px-4 py-3 border-t border-border flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-text">Items per page:</span>
              <Select
                value={itemsPerPage.toString()}
                onChange={(e) => {
                  setItemsPerPage(Number(e.target.value));
                  setCurrentPage(1);
                }}
                className="w-20"
              >
                <option value="10">10</option>
                <option value="25">25</option>
                <option value="50">50</option>
                <option value="100">100</option>
              </Select>
            </div>
            <span className="text-sm text-text">
              Showing {(currentPage - 1) * itemsPerPage + 1}-{Math.min(currentPage * itemsPerPage, sortedDocuments.length)} of {sortedDocuments.length} documents
            </span>
          </div>

          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
            >
              <Icons.ChevronLeft className="h-4 w-4" />
            </Button>

            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let pageNum: number;
              if (totalPages <= 5) {
                pageNum = i + 1;
              } else if (currentPage <= 3) {
                pageNum = i + 1;
              } else if (currentPage >= totalPages - 2) {
                pageNum = totalPages - 4 + i;
              } else {
                pageNum = currentPage - 2 + i;
              }

              return (
                <Button
                  key={pageNum}
                  variant={currentPage === pageNum ? "default" : "outline"}
                  size="sm"
                  onClick={() => setCurrentPage(pageNum)}
                  className="w-10"
                >
                  {pageNum}
                </Button>
              );
            })}

            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
            >
              <Icons.ChevronRight className="h-4 w-4" />
            </Button>

            <div className="flex items-center space-x-2 ml-4">
              <span className="text-sm text-text">Jump to:</span>
              <Input
                type="number"
                min="1"
                max={totalPages}
                value={jumpToPage}
                onChange={(e) => setJumpToPage(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleJumpToPage()}
                className="w-16"
                placeholder="Page"
              />
              <Button size="sm" onClick={handleJumpToPage}>Go</Button>
            </div>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteConfirmDoc} onOpenChange={() => setDeleteConfirmDoc(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Document</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{deleteConfirmDoc?.filename}"? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteConfirmDoc(null)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                if (deleteConfirmDoc) {
                  onDelete?.(deleteConfirmDoc);
                  setDeleteConfirmDoc(null);
                }
              }}
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Bulk Delete Confirmation Dialog */}
      <Dialog open={bulkDeleteConfirm} onOpenChange={setBulkDeleteConfirm}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Multiple Documents</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete {selectedDocs.size} document{selectedDocs.size > 1 ? 's' : ''}? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setBulkDeleteConfirm(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                onBulkDelete?.(selectedDocuments);
                setBulkDeleteConfirm(false);
                setSelectedDocs(new Set());
              }}
            >
              Delete All
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View Chunks Dialog */}
      <Dialog open={!!viewChunksDoc} onOpenChange={() => setViewChunksDoc(null)}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>Document Chunks - {viewChunksDoc?.filename}</DialogTitle>
            <DialogDescription>
              Viewing all {viewChunksDoc?.chunks} text chunks from this document
            </DialogDescription>
          </DialogHeader>
          <div className="max-h-96 overflow-y-auto space-y-3">
            {(() => {
              const details = viewChunksDoc ? fileDetails[viewChunksDoc.id] : null;
              const chunks = details?.chunks || Array.from({ length: viewChunksDoc?.chunks || 0 }, (_, i) => ({
                text: `Chunk ${i + 1}: This is sample text content for chunk ${i + 1}. In a real implementation, this would contain the actual text extracted from the document.`,
                language: 'en',
                page_number: 1,
                token_count: 50
              }));

              return chunks.map((chunk: any, index: number) => (
                <div key={index} className="bg-background p-3 rounded border border-border">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-medium text-text-secondary">Chunk {index + 1}</span>
                      {chunk.language && (
                        <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                          {chunk.language.toUpperCase()}
                        </span>
                      )}
                      {chunk.page_number && (
                        <span className="text-xs text-text-secondary">Page {chunk.page_number}</span>
                      )}
                    </div>
                    <div className="flex items-center space-x-2 text-xs text-text-secondary">
                      <span>{chunk.text?.length || 0} characters</span>
                      {chunk.token_count && <span>{chunk.token_count} tokens</span>}
                    </div>
                  </div>
                  <p className="text-sm text-text">{chunk.text}</p>
                </div>
              ));
            })()}
          </div>
          <DialogFooter>
            <Button onClick={() => setViewChunksDoc(null)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
