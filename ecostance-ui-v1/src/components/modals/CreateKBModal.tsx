import React, { useState, useEffect, useCallback } from 'react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/Card';
import { Icons } from '../icons';
import { cn } from '../../lib/utils';
import { useKnowledgeBase } from '../../hooks/useKnowledgeBase';
import { knowledgeBaseAPI } from '../../services/api';

const validateKBName = (name: string, existingNames: string[]): string | undefined => {
  if (!name) return 'Knowledge Base Name is required.';
  if (name.length < 3 || name.length > 50) return 'Name must be between 3 and 50 characters.';
  if (!/^[a-z0-9_-]+$/.test(name)) return 'Only lowercase letters, numbers, hyphens, and underscores are allowed.';
  if (existingNames.includes(name)) return 'This name is already taken.';
  return undefined;
};

interface CreateKBModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (kbName: string) => void;
}

const CreateKBModal: React.FC<CreateKBModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [kbName, setKbName] = useState('');
  const [kbNameError, setKbNameError] = useState<string | undefined>(undefined);
  const [isKbNameTouched, setIsKbNameTouched] = useState(false);
  const [existingKBNames, setExistingKBNames] = useState<string[]>([]);

  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | undefined>(undefined);

  const { listKnowledgeBases } = useKnowledgeBase();
  const isFormValid = !kbNameError && kbName.length > 0;

  // Fetch existing KB names when modal opens
  useEffect(() => {
    if (isOpen) {
      const fetchKBNames = async () => {
        try {
          const response = await listKnowledgeBases();
          if (response && Array.isArray(response)) {
            const names = response.map((kb: any) => kb.name);
            setExistingKBNames(names);
          }
        } catch (error) {
          console.error('Failed to fetch KB names:', error);
        }
      };
      fetchKBNames();
    }
  }, [isOpen, listKnowledgeBases]);

  // Reset form when modal opens
  useEffect(() => {
    if (isOpen) {
      setKbName('');
      setKbNameError(undefined);
      setIsKbNameTouched(false);
      setDescription('');
      setIsSubmitting(false);
      setSubmitError(undefined);
    }
  }, [isOpen]);

  const handleNameBlur = useCallback(() => {
    setIsKbNameTouched(true);
    const error = validateKBName(kbName, existingKBNames);
    setKbNameError(error);
  }, [kbName, existingKBNames]);

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setKbName(e.target.value);
    // Clear error on typing if touched
    if (isKbNameTouched) {
      const error = validateKBName(e.target.value, existingKBNames);
      setKbNameError(error);
    }
  };

  const handleDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setDescription(e.target.value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isFormValid) return;

    setIsSubmitting(true);
    setSubmitError(undefined);

    try {
      // Create the knowledge base using the backend API
      await knowledgeBaseAPI.create(kbName);
      
      onSuccess(kbName);
      onClose(); // Close modal on success
    } catch (error) {
      console.error('Error creating KB:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to create knowledge base. Please try again.';
      setSubmitError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm">
      <Card className="w-full max-w-md bg-background border border-border shadow-xl">
        <CardHeader className="flex flex-row justify-between items-center p-5 pb-2">
          <div>
            <CardTitle className="text-2xl font-bold text-primary">Create New Knowledge Base</CardTitle>
            <CardDescription className="text-sm text-text-secondary">
              Choose a name for your KB. Upload documents to it to start building your knowledge base.
            </CardDescription>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close modal">
            <Icons.X className="h-6 w-6 text-text-secondary hover:text-primary" />
          </Button>
        </CardHeader>
        <CardContent className="p-5 pt-4">
          <form onSubmit={handleSubmit}>
            <div className="space-y-5">
              <div>
                <Input
                  label="Knowledge Base Name*"
                  type="text"
                  placeholder="e.g., product-documentation"
                  value={kbName}
                  onChange={handleNameChange}
                  onBlur={handleNameBlur}
                  error={isKbNameTouched ? kbNameError : undefined}
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Use lowercase letters, numbers, hyphens, and underscores
                </p>
              </div>
              <div className="flex flex-col space-y-1.5">
                <label htmlFor="description" className="text-sm font-medium text-primary">
                  Description (Optional)
                </label>
                <textarea
                  id="description"
                  placeholder="Brief description of this knowledge base..."
                  value={description}
                  onChange={handleDescriptionChange}
                  maxLength={500}
                  rows={4}
                  className={cn(
                    `flex min-h-[80px] w-full rounded-md border border-border bg-background px-3 py-2 text-sm
                     text-text ring-offset-background placeholder:text-text-secondary/70
                     focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary/50
                     focus-visible:ring-offset-0 transition-colors duration-200 resize-none`,
                    // Add error styling if needed, though description is optional
                  )}
                />
              </div>

              {submitError && (
                <p className="text-sm text-red-500 text-center">{submitError}</p>
              )}

              <div className="flex justify-end space-x-3 pt-2">
                <Button variant="outline" onClick={onClose} type="button" disabled={isSubmitting}>
                  Cancel
                </Button>
                <Button variant="primary" onClick={handleSubmit} type="submit" disabled={!isFormValid || isSubmitting}>
                  {isSubmitting ? (
                    <>
                      <Icons.Spinner className="mr-2 h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    'Create Knowledge Base'
                  )}
                </Button>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default CreateKBModal;
