import { useState, useEffect } from 'react';
import { Dialog } from '../ui/Dialog';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { Brain, X, Loader2 } from 'lucide-react';
import { publicAgentAPI } from '../../services/api';

interface AgentAssignmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  tenantName: string;
  tenantId: string;
  onAssign: (tenantId: string, agentType: string) => Promise<void>;
}

const FALLBACK_AGENTS = [
  { value: 'generic', label: 'Generic Assistant', description: 'General-purpose AI assistant', color: 'bg-gray-500', features: ['Q&A', 'Search'] },
  { value: 'ecommerce', label: 'E-commerce Agent', description: 'Retail-focused assistant', color: 'bg-blue-500', features: ['Products', 'Support'] },
  { value: 'ecostance', label: 'EcoStance Agent', description: 'Sustainability-focused assistant', color: 'bg-green-500', features: ['Sustainability', 'Certificates'] },
  { value: 'quickship', label: 'QuickShip Agent', description: 'Logistics-focused assistant', color: 'bg-purple-500', features: ['Tracking', 'Logistics'] }
];

export default function AgentAssignmentModal({
  isOpen,
  onClose,
  tenantName,
  tenantId,
  onAssign
}: AgentAssignmentModalProps) {
  const [selectedAgent, setSelectedAgent] = useState<string>('generic');
  const [isAssigning, setIsAssigning] = useState(false);
  const [availableAgents, setAvailableAgents] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadAgents();
    }
  }, [isOpen]);

  const loadAgents = async () => {
    try {
      setIsLoading(true);
      const data = await publicAgentAPI.admin.getAvailableAgents() as any;
      setAvailableAgents(Array.isArray(data) ? data : (data.agents || []));
    } catch (error) {
      console.error('Failed to load agents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAssign = async () => {
    setIsAssigning(true);
    try {
      await onAssign(tenantId, selectedAgent);
      onClose();
    } catch (error) {
      console.error('Failed to assign agent:', error);
    } finally {
      setIsAssigning(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
        <div className="bg-surface border border-border rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-border">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <Brain className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-text">Assign AI Agent</h2>
                <p className="text-sm text-text-secondary">Configure AI agent for {tenantName}</p>
              </div>
            </div>
            <Button variant="outline" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-text mb-4">Select Agent Type</h3>
              <div className="space-y-3">
                {isLoading ? (
                  <div className="flex flex-col items-center justify-center py-12 text-text-secondary">
                    <Loader2 className="w-8 h-8 animate-spin mb-3 text-primary" />
                    <p>Loading available agents...</p>
                  </div>
                ) : (availableAgents.length > 0 ? availableAgents : FALLBACK_AGENTS).map((agent) => (
                  <div
                    key={agent.value || agent.id}
                    className={`p-4 border rounded-lg cursor-pointer transition-all ${selectedAgent === (agent.value || agent.id)
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:border-primary/50 hover:bg-surface-hover'
                      }`}
                    onClick={() => setSelectedAgent(agent.value || agent.id)}
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex items-center gap-3 flex-1">
                        <div className={`w-4 h-4 rounded-full ${agent.color || 'bg-gray-400'}`} />
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h4 className="font-semibold text-text">{agent.label || agent.name}</h4>
                            {selectedAgent === (agent.value || agent.id) && (
                              <Badge variant="success" className="text-xs">Selected</Badge>
                            )}
                          </div>
                          <p className="text-sm text-text-secondary mb-3">{agent.description}</p>
                          <div className="flex flex-wrap gap-1">
                            {(agent.features || []).map((feature: string) => (
                              <Badge key={feature} variant="outline" className="text-xs">
                                {feature}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${selectedAgent === (agent.value || agent.id)
                        ? 'border-primary bg-primary'
                        : 'border-border'
                        }`}>
                        {selectedAgent === (agent.value || agent.id) && (
                          <div className="w-2 h-2 bg-white rounded-full" />
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 p-6 border-t border-border">
            <Button variant="outline" onClick={onClose} disabled={isAssigning}>
              Cancel
            </Button>
            <Button onClick={handleAssign} disabled={isAssigning} className="bg-primary hover:bg-primary/90">
              {isAssigning ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Assigning...
                </>
              ) : (
                'Assign Agent'
              )}
            </Button>
          </div>
        </div>
      </div>
    </Dialog>
  );
}