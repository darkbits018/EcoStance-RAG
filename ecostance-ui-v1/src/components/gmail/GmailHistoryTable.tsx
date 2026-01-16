import { useState, useEffect } from 'react';
import { gmailAPI } from '../../services/api';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/Table';
import { Button } from '../ui/Button';
import { ChevronLeft, ChevronRight, Loader2, RefreshCw, Trash2 } from 'lucide-react';

interface GmailHistoryTableProps {
    refreshTrigger?: number;
}

export default function GmailHistoryTable({ refreshTrigger = 0 }: GmailHistoryTableProps) {
    const [messages, setMessages] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [page, setPage] = useState(0);
    const limit = 50;

    useEffect(() => {
        loadMessages();
    }, [page, refreshTrigger]);

    const loadMessages = async () => {
        setLoading(true);
        try {
            const data = await gmailAPI.messages.list(limit, page * limit);
            setMessages(data || []);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm('Are you sure you want to delete this message and its vectors?')) return;
        try {
            await gmailAPI.messages.delete(id);
            loadMessages();
        } catch (err: any) {
            console.error(err);
            alert(err.message || 'Failed to delete message');
        }
    };

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium text-text">Ingestion History</h3>
                <div className="flex gap-2">
                    <Button variant="ghost" size="sm" onClick={loadMessages} disabled={loading} title="Refresh History">
                        <RefreshCw className={`w-4 h-4 text-text-secondary ${loading ? 'animate-spin' : ''}`} />
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0 || loading}>
                        <ChevronLeft className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => setPage(p => p + 1)} disabled={loading || messages.length < limit}>
                        <ChevronRight className="w-4 h-4" />
                    </Button>
                </div>
            </div>

            {/* Table */}
            <div className="border border-border rounded-lg overflow-hidden">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Subject</TableHead>
                            <TableHead>Sender</TableHead>
                            <TableHead>Received</TableHead>
                            <TableHead>Ingested</TableHead>
                            <TableHead className="text-right">Action</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {loading ? (
                            <TableRow><TableCell colSpan={4} className="text-center py-8"><Loader2 className="w-6 h-6 animate-spin mx-auto text-primary" /></TableCell></TableRow>
                        ) : messages.length === 0 ? (
                            <TableRow><TableCell colSpan={4} className="text-center py-8 text-text-secondary">No messages ingested yet.</TableCell></TableRow>
                        ) : (
                            messages.map((msg) => (
                                <TableRow key={msg.id}>
                                    <TableCell className="font-medium max-w-[200px] truncate" title={msg.subject}>{msg.subject || '(No Subject)'}</TableCell>
                                    <TableCell className="max-w-[200px] truncate" title={msg.sender}>{msg.sender}</TableCell>
                                    <TableCell className="whitespace-nowrap">{new Date(msg.received_at).toLocaleDateString()} {new Date(msg.received_at).toLocaleTimeString()}</TableCell>
                                    <TableCell className="whitespace-nowrap">{new Date(msg.ingested_at).toLocaleDateString()} {new Date(msg.ingested_at).toLocaleTimeString()}</TableCell>
                                    <TableCell className="text-right">
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => handleDelete(msg.id)}
                                            className="text-error hover:text-error hover:bg-error/10"
                                            title="Delete Message"
                                        >
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
