import React, { useState, useEffect } from 'react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/ui/Card';
import { Icons } from '../components/icons';
import { cn } from '../lib/utils';
import CreateKBModal from '../components/modals/CreateKBModal';
import { useNavigate } from 'react-router-dom';
import { Badge } from '../components/ui/Badge';
import { SkeletonCard, SkeletonRow } from '../components/ui/Skeleton';
import { Select } from '../components/ui/Select';
import { useKnowledgeBase } from '../hooks/useKnowledgeBase';

// Type definition for Knowledge Base
type KnowledgeBase = {
  id: string;
  name: string;
  documentCount: number;
  totalVectors: number;
  lastUpdated: Date;
  sizeGB: number;
  status: 'Ready' | 'Processing' | 'Error';
};

// Mock Data for Knowledge Bases
const mockKnowledgeBases: KnowledgeBase[] = [
  {
    id: 'kb-1',
    name: 'company-policies',
    documentCount: 25,
    totalVectors: 5000,
    lastUpdated: new Date('2024-07-20T10:00:00Z'),
    sizeGB: 1.2,
    status: 'Ready' as const,
  },
  {
    id: 'kb-2',
    name: 'product-documentation',
    documentCount: 150,
    totalVectors: 30000,
    lastUpdated: new Date('2024-07-25T14:30:00Z'),
    sizeGB: 15.5,
    status: 'Ready' as const,
  },
  {
    id: 'kb-3',
    name: 'marketing-materials',
    documentCount: 75,
    totalVectors: 15000,
    lastUpdated: new Date('2024-07-22T09:15:00Z'),
    sizeGB: 8.0,
    status: 'Processing' as const,
  },
  {
    id: 'kb-4',
    name: 'technical-support-faqs',
    documentCount: 50,
    totalVectors: 10000,
    lastUpdated: new Date('2024-07-26T11:00:00Z'),
    sizeGB: 5.2,
    status: 'Ready' as const,
  },
  {
    id: 'kb-5',
    name: 'customer-feedback',
    documentCount: 30,
    totalVectors: 6000,
    lastUpdated: new Date('2024-07-24T15:00:00Z'),
    sizeGB: 2.8,
    status: 'Error' as const,
  },
];

// Helper function for status badge
const getStatusBadgeVariant = (status: 'Ready' | 'Processing' | 'Error') => {
  switch (status) {
    case 'Ready':
      return 'default';
    case 'Processing':
      return 'secondary';
    case 'Error':
      return 'destructive';
    default:
      return 'outline';
  }
};

// Mock component for a single Knowledge Base Card
const KnowledgeBaseCard = ({ kb, onDelete }: { kb: KnowledgeBase; onDelete: (kbId: string) => void }) => {
  const [isHovered, setIsHovered] = useState(false);
  const navigate = useNavigate();

  const handleView = () => navigate(`/knowledge-base/${kb.id}`);
  const handleQuery = () => navigate(`/chat?kb=${kb.id}`);
  const handleDelete = () => {
    if (window.confirm(`Are you sure you want to delete "${kb.name}"? This action cannot be undone.`)) {
      onDelete(kb.id);
    }
  };

  return (
    <Card
      className="w-full max-w-sm h-56 flex flex-col justify-between bg-surface border-none shadow-md relative cursor-pointer"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleView}
    >
      <div className="absolute top-2 right-2 z-10">
        <Badge variant={getStatusBadgeVariant(kb.status)}>{kb.status}</Badge>
      </div>
      <CardHeader className="p-4 pb-2">
        <CardTitle className="text-lg font-bold text-primary truncate">{kb.name}</CardTitle>
        <CardDescription className="text-xs text-text-secondary">
          Last updated: {kb.lastUpdated.toLocaleDateString()}
        </CardDescription>
      </CardHeader>
      <CardContent className="p-4 pt-0 flex-grow flex flex-col justify-center">
        <div className="text-sm text-text mb-1">
          Documents: <span className="font-medium">{kb.documentCount}</span>
        </div>
        <div className="text-sm text-text mb-2">
          Total Vectors: <span className="font-medium">{kb.totalVectors.toLocaleString()}</span>
        </div>
        <div className="text-sm text-text">
          Size: <span className="font-medium">{kb.sizeGB.toFixed(2)} GB</span>
        </div>
      </CardContent>
      {isHovered && (
        <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center space-x-2 rounded-lg transition-opacity duration-300">
          <Button variant="ghost" size="icon" onClick={(e) => { e.stopPropagation(); handleView(); }} aria-label="View Knowledge Base">
            <Icons.Eye className="h-5 w-5 text-white" />
          </Button>
          <Button variant="ghost" size="icon" onClick={(e) => { e.stopPropagation(); handleQuery(); }} aria-label="Query Knowledge Base">
            <Icons.Search className="h-5 w-5 text-white" />
          </Button>
          <Button variant="ghost" size="icon" onClick={(e) => { e.stopPropagation(); handleDelete(); }} aria-label="Delete Knowledge Base">
            <Icons.Trash className="h-5 w-5 text-red-500" />
          </Button>
        </div>
      )}
    </Card>
  );
};

// Mock component for a single row in the list view
const KnowledgeBaseRow = ({ kb, onDelete }: { kb: KnowledgeBase; onDelete: (kbId: string) => void }) => {
  const navigate = useNavigate();

  const handleView = () => navigate(`/knowledge-base/${kb.id}`);
  const handleQuery = () => navigate(`/chat?kb=${kb.id}`);
  const handleDelete = () => {
    if (window.confirm(`Are you sure you want to delete "${kb.name}"? This action cannot be undone.`)) {
      onDelete(kb.id);
    }
  };

  return (
    <tr className="border-b border-border hover:bg-surface-hover transition-colors duration-200">
      <td className="py-3 px-4 text-sm text-text font-medium truncate cursor-pointer hover:underline" onClick={handleView}>{kb.name}</td>
      <td className="py-3 px-4 text-sm text-text">{kb.documentCount}</td>
      <td className="py-3 px-4 text-sm text-text">{kb.totalVectors.toLocaleString()}</td>
      <td className="py-3 px-4 text-sm text-text">{kb.sizeGB.toFixed(2)} GB</td>
      <td className="py-3 px-4 text-sm text-text">{kb.lastUpdated.toLocaleString()}</td>
      <td className="py-3 px-4">
        <Badge variant={getStatusBadgeVariant(kb.status)}>{kb.status}</Badge>
      </td>
      <td className="py-3 px-4 flex items-center space-x-2">
        <Button variant="ghost" size="icon" onClick={handleView} aria-label="View Knowledge Base">
          <Icons.Eye className="h-4 w-4 text-primary" />
        </Button>
        <Button variant="ghost" size="icon" onClick={handleQuery} aria-label="Query Knowledge Base">
          <Icons.Search className="h-4 w-4 text-primary" />
        </Button>
        <Button variant="ghost" size="icon" onClick={handleDelete} aria-label="Delete Knowledge Base">
          <Icons.Trash className="h-4 w-4 text-red-500" />
        </Button>
      </td>
    </tr>
  );
};

const KnowledgeBaseListPage: React.FC = () => {
  const navigate = useNavigate();
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState<{ key: keyof KnowledgeBase | '', direction: 'ascending' | 'descending' }>({ key: '', direction: 'ascending' });
  const [isCreateKBModalOpen, setIsCreateKBModalOpen] = useState(false);
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(9);
  
  const { listKnowledgeBases, getKBDetails, deleteKB, loading: isLoading, error } = useKnowledgeBase();

  // Fetch knowledge bases on component mount
  useEffect(() => {
    const fetchKnowledgeBases = async () => {
      try {
        console.log('Fetching knowledge bases...');
        const response = await listKnowledgeBases();
        console.log('KB API Response:', response);
        
        // Transform API response to match our KnowledgeBase type
        if (response && Array.isArray(response)) {
          console.log(`Found ${response.length} knowledge bases`);
          
          // Fetch details for each KB
          const detailedKBs = await Promise.all(
            response.map(async (kb: any) => {
              const kbName = typeof kb === 'string' ? kb : (kb.name || kb.id);
              
              try {
                // Fetch detailed information for this KB
                const details = await getKBDetails(kbName);
                console.log(`Details for ${kbName}:`, details);
                
                if (details) {
                  return {
                    id: kbName,
                    name: kbName,
                    documentCount: details.files_count || 0,
                    totalVectors: details.vectors_count || details.total_points || 0,
                    lastUpdated: new Date(),
                    sizeGB: 0, // Size calculation would need to be added to backend
                    status: 'Ready' as const,
                  };
                }
              } catch (err) {
                console.warn(`Failed to fetch details for ${kbName}:`, err);
              }
              
              // Fallback if details fetch fails
              return {
                id: kbName,
                name: kbName,
                documentCount: 0,
                totalVectors: 0,
                lastUpdated: new Date(),
                sizeGB: 0,
                status: 'Ready' as const,
              };
            })
          );
          
          console.log('Detailed KBs:', detailedKBs);
          setKnowledgeBases(detailedKBs);
        } else {
          console.warn('Response is not an array:', response);
          setKnowledgeBases([]);
        }
      } catch (err) {
        console.error('Failed to fetch knowledge bases:', err);
        setKnowledgeBases([]);
      }
    };

    fetchKnowledgeBases();
  }, [listKnowledgeBases, getKBDetails]);

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const handleSort = (key: keyof KnowledgeBase) => {
    let direction: 'ascending' | 'descending' = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  // Filter, sort, and paginate
  const sortedAndFilteredKbs = React.useMemo(() => {
    let processedKbs = knowledgeBases.filter(kb =>
      kb?.name?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (sortConfig.key) {
      processedKbs.sort((a, b) => {
        const aValue = a[sortConfig.key as keyof typeof a];
        const bValue = b[sortConfig.key as keyof typeof b];

        if (aValue < bValue) {
          return sortConfig.direction === 'ascending' ? -1 : 1;
        }
        if (aValue > bValue) {
          return sortConfig.direction === 'ascending' ? 1 : -1;
        }
        return 0;
      });
    }
    return processedKbs;
  }, [searchTerm, sortConfig, knowledgeBases]);

  // Pagination
  const totalPages = Math.ceil(sortedAndFilteredKbs.length / itemsPerPage);
  const paginatedKbs = sortedAndFilteredKbs.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handleCreateKB = () => {
    setIsCreateKBModalOpen(true);
  };

  const handleCloseCreateKBModal = () => {
    setIsCreateKBModalOpen(false);
  };

  const handleKBSuccess = (newKbName: string) => {
    console.log('KB name reserved:', newKbName);
    
    // Add the KB to local state (it will be created on backend when first document is uploaded)
    const newKB: KnowledgeBase = {
      id: newKbName,
      name: newKbName,
      documentCount: 0,
      totalVectors: 0,
      lastUpdated: new Date(),
      sizeGB: 0,
      status: 'Ready',
    };
    setKnowledgeBases(prev => [...prev, newKB]);
    
    // Navigate to the KB details page where user can upload documents
    navigate(`/knowledge-base/${newKbName}`);
  };

  const handleRefresh = async () => {
    try {
      console.log('Refreshing knowledge bases...');
      const response = await listKnowledgeBases();
      console.log('Refresh KB API Response:', response);
      
      if (response && Array.isArray(response)) {
        console.log(`Found ${response.length} knowledge bases on refresh`);
        
        // Fetch details for each KB
        const detailedKBs = await Promise.all(
          response.map(async (kb: any) => {
            const kbName = typeof kb === 'string' ? kb : (kb.name || kb.id);
            
            try {
              // Fetch detailed information for this KB
              const details = await getKBDetails(kbName);
              
              if (details) {
                return {
                  id: kbName,
                  name: kbName,
                  documentCount: details.files_count || 0,
                  totalVectors: details.vectors_count || details.total_points || 0,
                  lastUpdated: new Date(),
                  sizeGB: 0,
                  status: 'Ready' as const,
                };
              }
            } catch (err) {
              console.warn(`Failed to fetch details for ${kbName}:`, err);
            }
            
            // Fallback if details fetch fails
            return {
              id: kbName,
              name: kbName,
              documentCount: 0,
              totalVectors: 0,
              lastUpdated: new Date(),
              sizeGB: 0,
              status: 'Ready' as const,
            };
          })
        );
        
        setKnowledgeBases(detailedKBs);
      } else {
        console.warn('Refresh response is not an array:', response);
        setKnowledgeBases([]);
      }
    } catch (err) {
      console.error('Failed to refresh knowledge bases:', err);
    }
  };

  const handleDeleteKB = async (kbId: string) => {
    try {
      console.log('Deleting knowledge base:', kbId);
      await deleteKB(kbId);
      
      // Remove the KB from local state
      setKnowledgeBases(prev => prev.filter(kb => kb.id !== kbId));
      
      console.log('Knowledge base deleted successfully');
    } catch (err) {
      console.error('Failed to delete knowledge base:', err);
      alert(`Failed to delete knowledge base: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6">
      <div className="flex flex-col md:flex-row justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-primary mb-4 md:mb-0">Knowledge Bases</h1>
        <div className="flex items-center space-x-4">
          <Button onClick={handleRefresh} variant="outline" className="h-10 px-5" disabled={isLoading}>
            <Icons.RefreshCw className={cn("mr-2 h-4 w-4", isLoading && "animate-spin")} />
            Refresh
          </Button>
          <Button onClick={handleCreateKB} className="h-10 px-5">
            <Icons.PlusCircle className="mr-2 h-4 w-4" />
            Create New KB
          </Button>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-text-secondary hidden md:inline">View:</span>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setViewMode('grid')}
              className={cn('p-2', viewMode === 'grid' ? 'bg-primary text-white' : 'text-text-secondary hover:bg-surface-hover')}
              aria-label="Switch to Grid View"
            >
              <Icons.LayoutGrid className="h-5 w-5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setViewMode('list')}
              className={cn('p-2', viewMode === 'list' ? 'bg-primary text-white' : 'text-text-secondary hover:bg-surface-hover')}
              aria-label="Switch to List View"
            >
              <Icons.List className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4" role="alert">
          <span className="block sm:inline">Error loading knowledge bases: {error.message}</span>
        </div>
      )}

      <div className="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
        <div className="flex-1 w-full md:w-auto">
          <Input
            type="search"
            placeholder="Search knowledge bases by name..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="h-12"
          />
        </div>
      </div>

      {/* Knowledge Base Display Area */}
      {isLoading ? (
        viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        ) : (
          <Card className="w-full bg-surface border-none shadow-md">
            <CardContent className="p-0">
              <table className="min-w-full divide-y divide-border">
                <thead className="bg-surface">
                  <tr>
                    <th className="py-3 px-4"></th>
                    <th className="py-3 px-4 text-left text-xs font-semibold text-primary">Name</th>
                    <th className="py-3 px-4 text-left text-xs font-semibold text-primary">Documents</th>
                    <th className="py-3 px-4 text-left text-xs font-semibold text-primary">Vectors</th>
                    <th className="py-3 px-4 text-left text-xs font-semibold text-primary">Size</th>
                    <th className="py-3 px-4 text-left text-xs font-semibold text-primary">Last Updated</th>
                    <th className="py-3 px-4 text-left text-xs font-semibold text-primary">Status</th>
                    <th className="py-3 px-4 text-left text-xs font-semibold text-primary">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-surface divide-y divide-border">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <SkeletonRow key={i} />
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        )
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {paginatedKbs.length > 0 ? (
            paginatedKbs.map(kb => <KnowledgeBaseCard key={kb.id} kb={kb} onDelete={handleDeleteKB} />)
          ) : (
            <div className="col-span-full text-center py-10 text-text-secondary">
              No knowledge bases found.
            </div>
          )}
        </div>
      ) : (
        <Card className="w-full bg-surface border-none shadow-md">
          <CardContent className="p-0">
            <table className="min-w-full divide-y divide-border">
              <thead className="bg-surface">
                <tr>
                  <th scope="col" className="py-3 px-4 text-left text-xs font-semibold text-primary uppercase tracking-wider cursor-pointer hover:text-primary/80" onClick={() => handleSort('name')}>
                    Name {sortConfig.key === 'name' && (sortConfig.direction === 'ascending' ? <Icons.ArrowUp className="inline h-3 w-3" /> : <Icons.ArrowDown className="inline h-3 w-3" />)}
                  </th>
                  <th scope="col" className="py-3 px-4 text-left text-xs font-semibold text-primary uppercase tracking-wider cursor-pointer hover:text-primary/80" onClick={() => handleSort('documentCount')}>
                    Documents {sortConfig.key === 'documentCount' && (sortConfig.direction === 'ascending' ? <Icons.ArrowUp className="inline h-3 w-3" /> : <Icons.ArrowDown className="inline h-3 w-3" />)}
                  </th>
                  <th scope="col" className="py-3 px-4 text-left text-xs font-semibold text-primary uppercase tracking-wider cursor-pointer hover:text-primary/80" onClick={() => handleSort('totalVectors')}>
                    Vectors {sortConfig.key === 'totalVectors' && (sortConfig.direction === 'ascending' ? <Icons.ArrowUp className="inline h-3 w-3" /> : <Icons.ArrowDown className="inline h-3 w-3" />)}
                  </th>
                  <th scope="col" className="py-3 px-4 text-left text-xs font-semibold text-primary uppercase tracking-wider cursor-pointer hover:text-primary/80" onClick={() => handleSort('sizeGB')}>
                    Size {sortConfig.key === 'sizeGB' && (sortConfig.direction === 'ascending' ? <Icons.ArrowUp className="inline h-3 w-3" /> : <Icons.ArrowDown className="inline h-3 w-3" />)}
                  </th>
                  <th scope="col" className="py-3 px-4 text-left text-xs font-semibold text-primary uppercase tracking-wider cursor-pointer hover:text-primary/80" onClick={() => handleSort('lastUpdated')}>
                    Last Updated {sortConfig.key === 'lastUpdated' && (sortConfig.direction === 'ascending' ? <Icons.ArrowUp className="inline h-3 w-3" /> : <Icons.ArrowDown className="inline h-3 w-3" />)}
                  </th>
                  <th scope="col" className="py-3 px-4 text-left text-xs font-semibold text-primary uppercase tracking-wider cursor-pointer hover:text-primary/80" onClick={() => handleSort('status')}>
                    Status {sortConfig.key === 'status' && (sortConfig.direction === 'ascending' ? <Icons.ArrowUp className="inline h-3 w-3" /> : <Icons.ArrowDown className="inline h-3 w-3" />)}
                  </th>
                  <th scope="col" className="py-3 px-4 text-left text-xs font-semibold text-primary uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-surface divide-y divide-border">
                {paginatedKbs.length > 0 ? (
                  paginatedKbs.map(kb => <KnowledgeBaseRow key={kb.id} kb={kb} onDelete={handleDeleteKB} />)
                ) : (
                  <tr>
                    <td colSpan={7} className="text-center py-10 text-text-secondary">
                      No knowledge bases found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}

      {/* Pagination */}
      {!isLoading && sortedAndFilteredKbs.length > 0 && (
        <div className="mt-6 flex items-center justify-between">
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
              <option value="9">9</option>
              <option value="18">18</option>
              <option value="27">27</option>
              <option value="50">50</option>
            </Select>
            <span className="text-sm text-text ml-4">
              Showing {(currentPage - 1) * itemsPerPage + 1}-{Math.min(currentPage * itemsPerPage, sortedAndFilteredKbs.length)} of {sortedAndFilteredKbs.length}
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
          </div>
        </div>
      )}

      <CreateKBModal
        isOpen={isCreateKBModalOpen}
        onClose={handleCloseCreateKBModal}
        onSuccess={handleKBSuccess}
      />
    </div>
  );
};

export default KnowledgeBaseListPage;
