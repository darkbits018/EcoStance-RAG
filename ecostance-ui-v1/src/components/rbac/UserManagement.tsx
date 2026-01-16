
import { useState, useEffect } from 'react';
import { rbacAPI } from '../../services/api';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Users, UserPlus, Edit, Trash2, Search, AlertCircle, Check, Shield } from 'lucide-react';

interface Role {
    id: string;
    name: string;
    description?: string;
    permissions: string[];
}

interface User {
    id: string;
    email: string;
    full_name?: string; // API uses full_name, local interface might use name
    name?: string;      // Handle both maps
    roles: Role[];
    is_active: boolean;
    created_at: string;
}

export default function UserManagement() {
    const [users, setUsers] = useState<User[]>([]);
    const [roles, setRoles] = useState<Role[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [searchTerm, setSearchTerm] = useState('');

    // Modal states
    const [showModal, setShowModal] = useState(false);
    const [editingUser, setEditingUser] = useState<User | null>(null);
    const [formData, setFormData] = useState({
        email: '',
        full_name: '',
        password: '',
        role_id: '',
        is_active: true
    });

    useEffect(() => {
        loadUsers();
        loadRoles();
    }, []);

    const loadUsers = async () => {
        try {
            const data = await rbacAPI.users.list();
            console.log('🔍 Raw users data:', data);

            let usersArray: User[] = [];
            if (Array.isArray(data)) {
                usersArray = data;
            } else if (data && typeof data === 'object' && 'users' in data && Array.isArray(data.users)) {
                usersArray = data.users;
            } else if (data && typeof data === 'object' && 'data' in data && Array.isArray(data.data)) {
                usersArray = data.data;
            } else {
                usersArray = [];
            }

            setUsers(usersArray);
        } catch (err: any) {
            console.error('❌ Failed to load users:', err);
            setError(err.message || 'Failed to load users');
            setUsers([]);
        }
    };

    const loadRoles = async () => {
        try {
            const data = await rbacAPI.roles.list();
            let rolesArray: Role[] = [];
            if (Array.isArray(data)) {
                rolesArray = data;
            } else if (data && typeof data === 'object' && 'roles' in data && Array.isArray(data.roles)) {
                rolesArray = data.roles;
            } else if (data && typeof data === 'object' && 'data' in data && Array.isArray(data.data)) {
                rolesArray = data.data;
            }
            setRoles(rolesArray);
        } catch (err: any) {
            console.error('❌ Failed to load roles:', err);
        }
    };

    const handleCreateUser = async () => {
        if (!formData.email.trim() || !formData.full_name.trim()) return;

        try {
            setLoading(true);
            setError('');
            await rbacAPI.users.create({
                email: formData.email,
                full_name: formData.full_name,
                password: formData.password,
                role_id: formData.role_id || undefined,
                is_active: formData.is_active
            });
            await loadUsers();
            setSuccess('User invited successfully');
            resetForm();
        } catch (err: any) {
            setError(err.message || 'Failed to invite user');
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateUser = async () => {
        if (!editingUser) return;

        try {
            setLoading(true);
            setError('');
            await rbacAPI.users.update(editingUser.id, {
                full_name: formData.full_name,
                is_active: formData.is_active,
                role_id: formData.role_id || undefined
            });
            await loadUsers();
            setSuccess('User updated successfully');
            resetForm();
        } catch (err: any) {
            setError(err.message || 'Failed to update user');
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteUser = async (userId: string, userEmail: string) => {
        if (!confirm(`Are you sure you want to remove ${userEmail}? This action cannot be undone.`)) return;

        try {
            setLoading(true);
            setError('');
            await rbacAPI.users.delete(userId);
            await loadUsers();
            setSuccess('User removed successfully');
        } catch (err: any) {
            setError(err.message || 'Failed to remove user');
        } finally {
            setLoading(false);
        }
    };

    const resetForm = () => {
        setShowModal(false);
        setEditingUser(null);
        setFormData({
            email: '',
            full_name: '',
            password: '',
            role_id: '',
            is_active: true
        });
    };

    const openEditModal = (user: User) => {
        setEditingUser(user);
        // Find absolute primary role or first role
        const currentRoleId = user.roles && user.roles.length > 0 ? user.roles[0].id : '';

        setFormData({
            email: user.email,
            full_name: user.full_name || user.name || '',
            password: '', // Password not editable here
            role_id: currentRoleId,
            is_active: user.is_active
        });
        setShowModal(true);
    };

    const filteredUsers = Array.isArray(users) ? users.filter(user =>
        user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (user.full_name || user.name || '').toLowerCase().includes(searchTerm.toLowerCase())
    ) : [];

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        });
    };

    return (
        <div className="space-y-6">
            {error && (
                <div className="p-4 bg-error/10 border border-error/20 rounded-lg flex items-start gap-2">
                    <AlertCircle className="w-5 h-5 text-error flex-shrink-0 mt-0.5" />
                    <p className="text-error">{error}</p>
                </div>
            )}

            {success && (
                <div className="p-4 bg-success/10 border border-success/20 rounded-lg flex items-start gap-2">
                    <Check className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
                    <p className="text-success">{success}</p>
                </div>
            )}

            <Card className="p-6 bg-surface border-border">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h2 className="text-lg font-semibold text-text flex items-center gap-2">
                            <Users className="w-5 h-5 text-primary" />
                            User Management
                        </h2>
                        <p className="text-sm text-text-secondary mt-1">
                            Invite and manage users in your organization
                        </p>
                    </div>
                    <Button onClick={() => setShowModal(true)}>
                        <UserPlus className="w-4 h-4 mr-2" />
                        Invite User
                    </Button>
                </div>

                {/* Search */}
                <div className="mb-6">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-text-secondary" />
                        <input
                            type="text"
                            placeholder="Search users by email or name..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 border border-border rounded-lg bg-background text-text placeholder:text-text-secondary focus:border-primary focus:outline-none"
                        />
                    </div>
                </div>

                {/* Users List */}
                <div className="space-y-3">
                    {filteredUsers.map((user) => (
                        <div key={user.id} className="p-4 border border-border rounded-lg bg-background">
                            <div className="flex items-center justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                        <h3 className="font-medium text-text">{user.email}</h3>
                                        {(user.full_name || user.name) && (
                                            <span className="text-sm text-text-secondary">({user.full_name || user.name})</span>
                                        )}
                                        {!user.is_active && (
                                            <span className="px-2 py-0.5 text-xs bg-warning/10 text-warning border border-warning/20 rounded">
                                                Inactive
                                            </span>
                                        )}
                                    </div>

                                    <div className="flex items-center gap-4 text-xs text-text-secondary mt-2">
                                        <span className="flex items-center gap-1">
                                            <Shield className="w-3 h-3" />
                                            {user.roles && user.roles.length > 0
                                                ? user.roles.map(r => r.name).join(', ')
                                                : 'No active roles'}
                                        </span>
                                        <span>Added {formatDate(user.created_at)}</span>
                                    </div>
                                </div>

                                <div className="flex items-center gap-2">
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => openEditModal(user)}
                                    >
                                        <Edit className="w-4 h-4" />
                                    </Button>
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => handleDeleteUser(user.id, user.email)}
                                        className="text-error hover:text-error/80"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </Button>
                                </div>
                            </div>
                        </div>
                    ))}
                    {filteredUsers.length === 0 && (
                        <div className="text-center py-8">
                            <Users className="w-12 h-12 text-text-secondary mx-auto mb-3" />
                            <p className="text-text-secondary">
                                {searchTerm ? 'No users found matching your search' : 'No users found'}
                            </p>
                        </div>
                    )}
                </div>
            </Card>

            {/* Create/Edit Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-surface border border-border rounded-lg p-6 w-full max-w-md mx-4">
                        <h3 className="text-lg font-semibold text-text mb-4">
                            {editingUser ? 'Edit User' : 'Invite New User'}
                        </h3>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-text-secondary mb-1">
                                    Email Address *
                                </label>
                                <input
                                    type="email"
                                    value={formData.email}
                                    onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                                    disabled={!!editingUser} // Cannot change email on edit usually
                                    className={`w-full px-3 py-2 border border-border rounded-lg bg-background text-text focus:border-primary focus:outline-none ${editingUser ? 'opacity-50 cursor-not-allowed' : ''}`}
                                    placeholder="colleague@example.com"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-text-secondary mb-1">
                                    Full Name *
                                </label>
                                <input
                                    type="text"
                                    value={formData.full_name}
                                    onChange={(e) => setFormData(prev => ({ ...prev, full_name: e.target.value }))}
                                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-text focus:border-primary focus:outline-none"
                                    placeholder="e.g. John Doe"
                                />
                            </div>

                            {!editingUser && (
                                <div>
                                    <label className="block text-sm font-medium text-text-secondary mb-1">
                                        Password *
                                    </label>
                                    <input
                                        type="password"
                                        value={formData.password}
                                        onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                                        className="w-full px-3 py-2 border border-border rounded-lg bg-background text-text focus:border-primary focus:outline-none"
                                        placeholder="Enter temporary password"
                                    />
                                </div>
                            )}

                            <div>
                                <label className="block text-sm font-medium text-text-secondary mb-1">
                                    Role
                                </label>
                                <select
                                    value={formData.role_id}
                                    onChange={(e) => setFormData(prev => ({ ...prev, role_id: e.target.value }))}
                                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-text focus:border-primary focus:outline-none"
                                >
                                    <option value="">Select a role...</option>
                                    {roles.map(role => (
                                        <option key={role.id} value={role.id}>
                                            {role.name}
                                        </option>
                                    ))}
                                </select>
                                <p className="text-xs text-text-secondary mt-1">
                                    Assigning a role grants specific permissions to this user.
                                </p>
                            </div>

                            {editingUser && (
                                <div className="flex items-center gap-2">
                                    <input
                                        type="checkbox"
                                        id="is_active"
                                        checked={formData.is_active}
                                        onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
                                        className="w-4 h-4 accent-primary"
                                    />
                                    <label htmlFor="is_active" className="text-sm text-text">Active Account</label>
                                </div>
                            )}
                        </div>

                        <div className="flex justify-end gap-2 mt-6">
                            <Button
                                variant="outline"
                                onClick={resetForm}
                            >
                                Cancel
                            </Button>
                            <Button
                                onClick={editingUser ? handleUpdateUser : handleCreateUser}
                                disabled={loading || !formData.email || !formData.full_name || (!editingUser && !formData.password)}
                            >
                                {editingUser ? 'Save Changes' : 'Send Invite'}
                            </Button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
