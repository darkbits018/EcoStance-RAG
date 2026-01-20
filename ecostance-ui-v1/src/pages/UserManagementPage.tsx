import React, { useState, useEffect } from 'react';
import { tenantUsersAPI, tenantRolesAPI } from '../services/api';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Label } from '../components/ui/Label';
import { Icons } from '../components/icons';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '../components/ui/Table';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from '../components/ui/Dialog';

interface User {
    id: string;
    email: string;
    full_name: string;
    role: {
        id: string;
        name: string;
    };
    is_active: boolean;
    created_at: string;
}

interface Role {
    id: string;
    name: string;
}

const UserManagementPage: React.FC = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [roles, setRoles] = useState<Role[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isInviteOpen, setIsInviteOpen] = useState(false);
    const [isEditOpen, setIsEditOpen] = useState(false);
    const [currentUser, setCurrentUser] = useState<User | null>(null);

    // Invite Form State (Bulk)
    const [inviteEmails, setInviteEmails] = useState('');
    const [inviteRole, setInviteRole] = useState('');
    const [inviteLoading, setInviteLoading] = useState(false);

    // Edit Form State
    const [editName, setEditName] = useState('');
    const [editRole, setEditRole] = useState('');
    const [editActive, setEditActive] = useState(false);
    const [editLoading, setEditLoading] = useState(false);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setIsLoading(true);
        try {
            const [usersData, rolesData] = await Promise.all([
                tenantUsersAPI.list(),
                tenantRolesAPI.list(),
            ]);

            // Handle nested user data
            let usersArray: User[] = [];
            if (Array.isArray(usersData)) {
                usersArray = usersData as User[];
            } else if (usersData && typeof usersData === 'object') {
                if ('users' in usersData && Array.isArray((usersData as any).users)) {
                    usersArray = (usersData as any).users;
                } else if ('data' in usersData && Array.isArray((usersData as any).data)) {
                    usersArray = (usersData as any).data;
                }
            }
            setUsers(usersArray);

            // Handle nested role data
            let rolesArray: Role[] = [];
            if (Array.isArray(rolesData)) {
                rolesArray = rolesData as Role[];
            } else if (rolesData && typeof rolesData === 'object') {
                if ('roles' in rolesData && Array.isArray((rolesData as any).roles)) {
                    rolesArray = (rolesData as any).roles;
                } else if ('data' in rolesData && Array.isArray((rolesData as any).data)) {
                    rolesArray = (rolesData as any).data;
                }
            }
            setRoles(rolesArray);

        } catch (error) {
            console.error("Failed to fetch data:", error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleInvite = async (e: React.FormEvent) => {
        e.preventDefault();
        setInviteLoading(true);

        const emailList = inviteEmails
            .split(/[\s,]+/)
            .map(e => e.trim())
            .filter(e => e && e.includes('@'));

        if (emailList.length === 0) {
            alert('Please enter at least one valid email address.');
            setInviteLoading(false);
            return;
        }

        try {
            const result: any = await tenantUsersAPI.inviteBulk({
                emails: emailList,
                role_id: inviteRole,
            });

            setIsInviteOpen(false);
            setInviteEmails('');
            setInviteRole('');
            fetchData();

            const successCount = result.successful ? result.successful.length : 0;
            const failedCount = result.failed ? result.failed.length : 0;
            let msg = `Invited ${successCount} user(s) successfully.`;
            if (failedCount > 0) {
                msg += ` Failed: ${failedCount}. Check console.`;
                console.warn(result.failed);
            }
            alert(msg);

        } catch (error: any) {
            alert(error.message || "Failed to invite users");
        } finally {
            setInviteLoading(false);
        }
    };

    const openEdit = (user: User) => {
        setCurrentUser(user);
        setEditName(user.full_name);
        setEditRole(user.role?.id || '');
        setEditActive(user.is_active);
        setIsEditOpen(true);
    };

    const handleEdit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!currentUser) return;
        setEditLoading(true);
        try {
            await tenantUsersAPI.update(currentUser.id, {
                full_name: editName,
                role_id: editRole,
                is_active: editActive,
            });
            setIsEditOpen(false);
            fetchData();
        } catch (error: any) {
            alert(error.message || "Failed to update user");
        } finally {
            setEditLoading(false);
        }
    };

    const handleDelete = async (userId: string) => {
        if (!window.confirm("Are you sure you want to remove this user? This action cannot be undone.")) return;
        try {
            await tenantUsersAPI.remove(userId);
            fetchData();
        } catch (error: any) {
            // If user is already gone (404), treat as success and refresh
            const errorMsg = (error.message || '').toLowerCase();
            if (errorMsg.includes('user not found') || errorMsg.includes('not found')) {
                fetchData();
                alert('User entry cleared (already deleted)');
            } else {
                alert(error.message || "Failed to delete user");
            }
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-primary">User Management</h1>
                    <p className="text-text-secondary">Manage access and roles for your team members.</p>
                </div>
                <Button onClick={() => setIsInviteOpen(true)}>
                    <Icons.Plus className="h-4 w-4 mr-2" />
                    Invite Users
                </Button>
            </div>

            <div className="bg-surface rounded-lg border border-border overflow-hidden">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>User</TableHead>
                            <TableHead>Role</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Joined</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {isLoading ? (
                            <TableRow>
                                <TableCell colSpan={5} className="text-center py-8">
                                    <Icons.Spinner className="h-6 w-6 animate-spin mx-auto text-primary" />
                                </TableCell>
                            </TableRow>
                        ) : users.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={5} className="text-center py-8 text-text-secondary">
                                    No users found. Invite your first team member!
                                </TableCell>
                            </TableRow>
                        ) : (
                            users.map((user) => (
                                <TableRow key={user.id}>
                                    <TableCell>
                                        <div>
                                            <div className="font-medium text-text">{user.full_name || 'N/A'}</div>
                                            <div className="text-xs text-text-secondary">{user.email}</div>
                                        </div>
                                    </TableCell>
                                    <TableCell>
                                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-secondary text-secondary-foreground">
                                            {user.role?.name || 'Unknown'}
                                        </span>
                                    </TableCell>
                                    <TableCell>
                                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${user.is_active
                                            ? 'bg-green-100 text-green-700'
                                            : 'bg-yellow-100 text-yellow-700'
                                            }`}>
                                            {user.is_active ? 'Active' : 'Pending/Inactive'}
                                        </span>
                                    </TableCell>
                                    <TableCell className="text-text-secondary text-sm">
                                        {new Date(user.created_at).toLocaleDateString()}
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <Button variant="ghost" size="icon" onClick={() => openEdit(user)}>
                                            <Icons.Pencil className="h-4 w-4 text-text-secondary hover:text-primary" />
                                        </Button>
                                        <Button variant="ghost" size="icon" onClick={() => handleDelete(user.id)} className="hover:text-red-600">
                                            <Icons.Trash className="h-4 w-4 text-text-secondary hover:text-red-600" />
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>

            {/* Invite Modal */}
            <Dialog open={isInviteOpen} onOpenChange={setIsInviteOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Invite New Users</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={handleInvite} className="space-y-4">
                        <div>
                            <Label htmlFor="emails">Email Addresses (Bulk)</Label>
                            <textarea
                                id="emails"
                                value={inviteEmails}
                                onChange={(e) => setInviteEmails(e.target.value)}
                                required
                                className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                placeholder="colleague1@example.com, colleague2@example.com"
                            />
                            <p className="text-xs text-text-secondary mt-1">
                                Enter multiple emails separated by commas, spaces, or new lines.
                            </p>
                        </div>
                        <div>
                            <Label htmlFor="role">Role</Label>
                            <select
                                id="role"
                                value={inviteRole}
                                onChange={(e) => setInviteRole(e.target.value)}
                                required
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                            >
                                <option value="">Select a role...</option>
                                {roles.map((role) => (
                                    <option key={role.id} value={role.id}>{role.name}</option>
                                ))}
                            </select>
                        </div>
                        <DialogFooter>
                            <Button type="button" variant="ghost" onClick={() => setIsInviteOpen(false)}>Cancel</Button>
                            <Button type="submit" disabled={inviteLoading}>
                                {inviteLoading ? <Icons.Spinner className="h-4 w-4 animate-spin" /> : 'Send Invites'}
                            </Button>
                        </DialogFooter>
                    </form>
                </DialogContent>
            </Dialog>

            {/* Edit Modal */}
            <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Edit User</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={handleEdit} className="space-y-4">
                        <div>
                            <Label htmlFor="edit-name">Full Name</Label>
                            <Input
                                id="edit-name"
                                type="text"
                                value={editName}
                                onChange={(e) => setEditName(e.target.value)}
                            />
                        </div>
                        <div>
                            <Label htmlFor="edit-role">Role</Label>
                            <select
                                id="edit-role"
                                value={editRole}
                                onChange={(e) => setEditRole(e.target.value)}
                                required
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                            >
                                {roles.map((role) => (
                                    <option key={role.id} value={role.id}>{role.name}</option>
                                ))}
                            </select>
                        </div>
                        <div className="flex items-center space-x-2">
                            <input
                                type="checkbox"
                                id="edit-active"
                                checked={editActive}
                                onChange={(e) => setEditActive(e.target.checked)}
                                className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                            />
                            <Label htmlFor="edit-active">User is Active</Label>
                        </div>
                        <DialogFooter>
                            <Button type="button" variant="ghost" onClick={() => setIsEditOpen(false)}>Cancel</Button>
                            <Button type="submit" disabled={editLoading}>
                                {editLoading ? <Icons.Spinner className="h-4 w-4 animate-spin" /> : 'Save Changes'}
                            </Button>
                        </DialogFooter>
                    </form>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default UserManagementPage;
