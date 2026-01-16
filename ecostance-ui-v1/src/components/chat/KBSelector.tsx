import React, { useState, useMemo } from 'react';
import { Input } from '../ui/Input';
import { Checkbox } from '../ui/Checkbox';
import { Button } from '../ui/Button';
import { Icons } from '../icons';
import { Badge } from '../ui/Badge';

export interface KnowledgeBase {
  id: string;
  name: string;
  documentCount: number;
  status: 'Ready' | 'Processing' | 'Error';
}

interface KBSelectorProps {
  knowledgeBases: KnowledgeBase[];
  selectedKBs: string[];
  onSelectionChange: (selectedIds: string[]) => void;
  onClose?: () => void;
}

export const KBSelector: React.FC<KBSelectorProps> = ({
  knowledgeBases,
  selectedKBs,
  onSelectionChange,
  onClose,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredKBs = useMemo(() => {
    return knowledgeBases.filter((kb) =>
      kb?.name?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [knowledgeBases, searchTerm]);

  const toggleKB = (kbId: string) => {
    if (selectedKBs.includes(kbId)) {
      onSelectionChange(selectedKBs.filter((id) => id !== kbId));
    } else {
      onSelectionChange([...selectedKBs, kbId]);
    }
  };

  const selectAll = () => {
    onSelectionChange(filteredKBs.map((kb) => kb.id));
  };

  const clearAll = () => {
    onSelectionChange([]);
  };

  const getStatusBadgeVariant = (status: KnowledgeBase['status']) => {
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

  return (
    <div className="bg-surface rounded-lg shadow-lg border border-border p-4 w-96">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-text">
          Select Knowledge Bases
        </h3>
        {onClose && (
          <button
            onClick={onClose}
            className="text-text-secondary hover:text-text"
          >
            <Icons.X className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Search */}
      <div className="mb-4">
        <Input
          type="search"
          placeholder="Search knowledge bases..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full"
        />
      </div>

      {/* Selection info */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-text-secondary">
          {selectedKBs.length} selected
        </span>
        <div className="flex space-x-2">
          <button
            onClick={selectAll}
            className="text-xs text-primary hover:underline"
          >
            Select All
          </button>
          <span className="text-border">|</span>
          <button
            onClick={clearAll}
            className="text-xs text-primary hover:underline"
          >
            Clear All
          </button>
        </div>
      </div>

      {/* KB List */}
      <div className="max-h-96 overflow-y-auto space-y-2">
        {filteredKBs.length === 0 ? (
          <div className="text-center py-8 text-text-secondary">
            <p className="text-sm">No knowledge bases found</p>
          </div>
        ) : (
          filteredKBs.map((kb) => (
            <div
              key={kb.id}
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-surface-hover cursor-pointer border border-border bg-background"
              onClick={() => toggleKB(kb.id)}
            >
              <Checkbox
                checked={selectedKBs.includes(kb.id)}
                onChange={() => toggleKB(kb.id)}
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  <p className="text-sm font-medium text-text truncate">
                    {kb.name}
                  </p>
                  <Badge variant={getStatusBadgeVariant(kb.status)} className="text-xs">
                    {kb.status}
                  </Badge>
                </div>
                <p className="text-xs text-text-secondary">
                  {kb.documentCount} document{kb.documentCount !== 1 ? 's' : ''}
                </p>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Actions */}
      <div className="mt-4 flex justify-end space-x-2">
        {onClose && (
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
        )}
        <Button
          onClick={onClose}
          disabled={selectedKBs.length === 0}
        >
          Query {selectedKBs.length > 0 && `(${selectedKBs.length})`} KB
          {selectedKBs.length !== 1 ? 's' : ''}
        </Button>
      </div>
    </div>
  );
};
