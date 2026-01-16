import { useState, useEffect } from 'react';
import { gmailAPI } from '../../services/api';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/Table';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/Dialog';
import { Trash2, Plus } from 'lucide-react';
import { Badge } from '../ui/Badge';

export default function GmailRecipientTable() {
    const [recipients, setRecipients] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [isAdding, setIsAdding] = useState(false);
    const [newRecipient, setNewRecipient] = useState({ email_address: '', display_name: '', group_name: 'Default' });
    const [addLoading, setAddLoading] = useState(false);

    useEffect(() => {
        loadRecipients();
    }, []);

    const loadRecipients = async () => {
        setLoading(true);
        try {
            const data = await gmailAPI.recipients.list();
            setRecipients(data || []);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleAdd = async () => {
        setAddLoading(true);
        try {
            await gmailAPI.recipients.add(newRecipient);
            setIsAdding(false);
            setNewRecipient({ email_address: '', display_name: '', group_name: 'Default' });
            loadRecipients();
        } catch (err) {
            console.error(err);
            alert('Failed to add recipient');
        } finally {
            setAddLoading(false);
        }
    };

    const handleRemove = async (id: string) => {
        if (!confirm('Are you sure?')) return;
        try {
            await gmailAPI.recipients.remove(id);
            loadRecipients();
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium text-text">Recipients</h3>
                <Button size="sm" className="flex items-center gap-2" onClick={() => setIsAdding(true)}>
                    <Plus className="w-4 h-4" /> Add Recipient
                </Button>
            </div>

            <Dialog open={isAdding} onOpenChange={setIsAdding}>
                <DialogContent className="max-w-md">
                    <DialogHeader>
                        <DialogTitle>Add New Recipient</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4 py-4 text-text">
                        <div>
                            <label className="text-sm font-medium mb-1 block">Email Address</label>
                            <Input
                                value={newRecipient.email_address}
                                onChange={(e) => setNewRecipient({ ...newRecipient, email_address: e.target.value })}
                                placeholder="user@example.com"
                            />
                        </div>
                        <div>
                            <label className="text-sm font-medium mb-1 block">Display Name</label>
                            <Input
                                value={newRecipient.display_name}
                                onChange={(e) => setNewRecipient({ ...newRecipient, display_name: e.target.value })}
                                placeholder="John Doe"
                            />
                        </div>
                        <div>
                            <label className="text-sm font-medium mb-1 block">Group</label>
                            <Input
                                value={newRecipient.group_name}
                                onChange={(e) => setNewRecipient({ ...newRecipient, group_name: e.target.value })}
                                placeholder="Sales"
                            />
                        </div>
                        <div className="flex justify-end gap-2 pt-2">
                            <Button variant="outline" onClick={() => setIsAdding(false)}>Cancel</Button>
                            <Button onClick={handleAdd} disabled={addLoading}>
                                {addLoading ? 'Adding...' : 'Add'}
                            </Button>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>

            <div className="border border-border rounded-lg overflow-hidden">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Email</TableHead>
                            <TableHead>Name</TableHead>
                            <TableHead>Group</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {loading ? (
                            <TableRow>
                                <TableCell colSpan={5} className="text-center text-text-secondary py-8">
                                    Loading...
                                </TableCell>
                            </TableRow>
                        ) : recipients.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={5} className="text-center text-text-secondary py-8">
                                    No recipients configured
                                </TableCell>
                            </TableRow>
                        ) : (
                            recipients.map((r) => (
                                <TableRow key={r.id}>
                                    <TableCell>{r.email_address}</TableCell>
                                    <TableCell>{r.display_name || '-'}</TableCell>
                                    <TableCell>{r.group_name || '-'}</TableCell>
                                    <TableCell>
                                        <Badge variant={r.enabled ? 'default' : 'secondary'}>
                                            {r.enabled ? 'Active' : 'Disabled'}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <Button variant="ghost" size="sm" onClick={() => handleRemove(r.id)} className="text-error hover:text-error hover:bg-error/10">
                                            <Trash2 className="w-4 h-4" />
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
}
