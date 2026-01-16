import { useState, useEffect } from 'react';
import { gmailAPI } from '../../services/api';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { Loader2, RefreshCw } from 'lucide-react';

interface GmailScheduleConfigProps {
    onSyncComplete?: () => void;
}

export default function GmailScheduleConfig({ onSyncComplete }: GmailScheduleConfigProps) {
    const [schedules, setSchedules] = useState<any[]>([]);
    const [recipients, setRecipients] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);

    const [newSchedule, setNewSchedule] = useState({
        name: 'Hourly Sync',
        schedule_type: 'interval',
        minutes: 60,
        recipient_ids: [] as string[]
    });
    const [createLoading, setCreateLoading] = useState(false);
    const [syncing, setSyncing] = useState<string | null>(null);

    const handleSync = async (scheduleId: string) => {
        setSyncing(scheduleId);
        try {
            await gmailAPI.schedules.sync(scheduleId);
            alert('Sync completed successfully');
            if (onSyncComplete) onSyncComplete();
        } catch (err: any) {
            console.error(err);
            alert(err.message || 'Sync failed');
        } finally {
            setSyncing(null);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const [schedulesData, recipientsData] = await Promise.all([
                gmailAPI.schedules.list(),
                gmailAPI.recipients.list()
            ]);
            setSchedules(schedulesData || []);
            setRecipients(recipientsData || []);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async () => {
        setCreateLoading(true);
        try {
            const payload = {
                name: newSchedule.name,
                schedule_type: newSchedule.schedule_type,
                schedule_config: { minutes: parseInt(newSchedule.minutes.toString()) },
                recipient_ids: newSchedule.recipient_ids,
                enabled: true
            };
            await gmailAPI.schedules.create(payload);
            setNewSchedule({
                name: 'Hourly Sync',
                schedule_type: 'interval',
                minutes: 60,
                recipient_ids: []
            });
            loadData();
        } catch (err) {
            console.error(err);
            alert('Failed to create schedule');
        } finally {
            setCreateLoading(false);
        }
    };

    const toggleRecipient = (id: string) => {
        const current = newSchedule.recipient_ids;
        if (current.includes(id)) {
            setNewSchedule({ ...newSchedule, recipient_ids: current.filter(r => r !== id) });
        } else {
            setNewSchedule({ ...newSchedule, recipient_ids: [...current, id] });
        }
    };

    if (loading) {
        return <div className="p-4 text-center text-text-secondary">Loading schedules...</div>;
    }

    return (
        <div className="space-y-6">
            <Card className="p-6 bg-surface border-border">
                <h3 className="text-lg font-medium text-text mb-4">Configurations</h3>

                <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="text-sm font-medium text-text-secondary mb-1 block">Schedule Name</label>
                            <Input
                                value={newSchedule.name}
                                onChange={(e) => setNewSchedule({ ...newSchedule, name: e.target.value })}
                            />
                        </div>
                        <div>
                            <label className="text-sm font-medium text-text-secondary mb-1 block">Type</label>
                            <Select
                                value={newSchedule.schedule_type}
                                onChange={(e) => setNewSchedule({ ...newSchedule, schedule_type: e.target.value })}
                            >
                                <option value="interval">Interval (Minutes)</option>
                                <option value="daily">Daily</option>
                            </Select>
                        </div>
                        {newSchedule.schedule_type === 'interval' && (
                            <div>
                                <label className="text-sm font-medium text-text-secondary mb-1 block">Frequency (Minutes)</label>
                                <Input
                                    type="number"
                                    value={newSchedule.minutes}
                                    onChange={(e) => setNewSchedule({ ...newSchedule, minutes: parseInt(e.target.value) })}
                                />
                            </div>
                        )}
                    </div>

                    <div>
                        <label className="text-sm font-medium text-text-secondary mb-2 block">Recipients to Sync</label>
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                            {recipients.map(r => (
                                <label key={r.id} className="flex items-center gap-2 p-2 border border-border rounded hover:bg-surface-hover cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={newSchedule.recipient_ids.includes(r.id)}
                                        onChange={() => toggleRecipient(r.id)}
                                        className="rounded border-gray-300 text-primary focus:ring-primary"
                                    />
                                    <span className="text-sm">{r.email_address}</span>
                                </label>
                            ))}
                            {recipients.length === 0 && (
                                <p className="text-sm text-text-secondary">No recipients available. Add one above.</p>
                            )}
                        </div>
                    </div>

                    <Button onClick={handleCreate} disabled={createLoading || recipients.length === 0}>
                        {createLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                        Create Schedule
                    </Button>
                </div>
            </Card>

            <div className="space-y-4">
                <h3 className="text-lg font-medium text-text">Active Schedules</h3>
                <div className="grid gap-4">
                    {schedules.map(sch => (
                        <Card key={sch.id} className="p-4 bg-surface border-border flex justify-between items-center">
                            <div className="flex justify-between items-center w-full">
                                <div>
                                    <h4 className="font-medium">{sch.name}</h4>
                                    <p className="text-sm text-text-secondary">
                                        Type: {sch.schedule_type}
                                        {sch.schedule_config?.minutes && ` (${sch.schedule_config.minutes} mins)`}
                                    </p>
                                </div>
                                <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => handleSync(sch.id)}
                                    disabled={syncing === sch.id}
                                    title="Run Manual Sync"
                                >
                                    <RefreshCw className={`w-4 h-4 mr-2 ${syncing === sch.id ? 'animate-spin' : ''}`} />
                                    {syncing === sch.id ? 'Syncing...' : 'Run Now'}
                                </Button>
                            </div>
                        </Card>
                    ))}
                    {schedules.length === 0 && (
                        <p className="text-text-secondary">No active schedules.</p>
                    )}
                </div>
            </div>
        </div>
    );
}
