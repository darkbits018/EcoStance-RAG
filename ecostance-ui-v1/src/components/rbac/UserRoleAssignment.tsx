import { useState, useEffect } from 'react';
import { rbacAPI } from '../../services/api';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Users, UserCheck, UserX, Search, AlertCircle, Check } from 'lucide-react';

interface User {
  id: string;
  email: string;
  name?: string;
  roles: Role[];
  is_active: boolean;
  created_at: string;
}

interface Role {
  id: string;
  name: string;
  description?: string;
  permissions: string[];
}

export default function UserRoleAssignment() {
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showAssignModal, setShowAssignModal] = useState(false);

  useEffect(() => {
    loadUsers();
    loadRoles();
  }, []);

  const loadUsers = async () => {
    try {
      const data = await rbacAPI.users.list();
      console.log('🔍 Raw users data from API:', data);
      
      // Handle different response formats
      let usersArray: User[] = [];
      if (Array.isArray(data)) {
        usersArray = data;
      } else if (data && typeof data === 'object' && 'users' in data && Array.isArray(data.users)) {
        usersArray = data.users;
      } else if (data && typeof data === 'object' && 'data' in data && Array.isArray(data.data)) {
        usersArray = data.data;
      } else {
        console.warn('⚠️ Unexpected users data format:', data);
        usersArray = [];
      }
      
      console.log('🔍 Processed users array:', usersArray);
      setUsers(usersArray);
    } catch (err: any) {
      console.error('❌ Failed to load users:', err);
      setError(err.message || 'Failed to load users');
      setUsers([]); // Ensure users is always an array
    }
  };

  const loadRoles = async () => {
    try {
      const data = await rbacAPI.roles.list();
      console.log('🔍 Raw roles data from API (UserRoleAssignment):', data);
      
      // Handle different response formats
      let rolesArray: Role[] = [];
      if (Array.isArray(data)) {
        rolesArray = data;
      } else if (data && typeof data === 'object' && 'roles' in data && Array.isArray(data.roles)) {
        rolesArray = data.roles;
      } else if (data && typeof data === 'object' && 'data' in data && Array.isArray(data.data)) {
        rolesArray = data.data;
      } else {
        console.warn('⚠️ Unexpected roles data format:', data);
        rolesArray = [];
      }
      
      console.log('🔍 Processed roles array (UserRoleAssignment):', rolesArray);
      setRoles(rolesArray);
    } catch (err: any) {
      console.error('❌ Failed to load roles:', err);
      setError(err.message || 'Failed to load roles');
      setRoles([]); // Ensure roles is always an array
    }
  };

  const handleAssignRole = async (userId: string, roleId: string) => {
    try {
      setLoading(true);
      setError('');
      await rbacAPI.users.assignRole(userId, roleId);
      await loadUsers();
      setSuccess('Role assigned successfully');
      setShowAssignModal(false);
      setSelectedUser(null);
    } catch (err: any) {
      setError(err.message || 'Failed to assign role');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveRole = async (userId: string, roleId: string, roleName: string) => {
    if (!confirm(`Remove role "${roleName}" from this user?`)) return;
    try {
      setLoading(true);
      setError('');
      await rbacAPI.users.removeRole(userId, roleId);
      await loadUsers();
      setSuccess('Role removed successfully');
    } catch (err: any) {
      setError(err.message || 'Failed to remove role');
    } finally {
      setLoading(false);
    }
  };

  const filteredUsers = Array.isArray(users) ? users.filter(user =>
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (user.name && user.name.toLowerCase().includes(searchTerm.toLowerCase()))
  ) : [];

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getAvailableRoles = (user: User) => {
    if (!Array.isArray(user.roles) || !Array.isArray(roles)) {
      return [];
    }
    const userRoleIds = user.roles.map(role => role.id);
    return roles.filter(role => !userRoleIds.includes(role.id));
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
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-text flex items-center gap-2 mb-2">
            <Users className="w-5 h-5 text-primary" />
            User Role Assignment
          </h2>
          <p className="text-sm text-text-secondary">
            Assign and manage roles for users in your organization
          </p>
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
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-medium text-text">{user.email}</h3>
                    {user.name && (
                      <span className="text-sm text-text-secondary">({user.name})</span>
                    )}
                    {!user.is_active && (
                      <span className="px-2 py-0.5 text-xs bg-warning/10 text-warning border border-warning/20 rounded">
                        Inactive
                      </span>
                    )}
                  </div>
                  
                  <div className="mb-3">
                    <p className="text-xs text-text-secondary mb-2">Current Roles:</p>
                    {Array.isArray(user.roles) && user.roles.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {user.roles.map((role) => (
                          <div key={role.id} className="flex items-center gap-1 px-2 py-1 bg-primary/10 text-primary border border-primary/20 rounded text-xs">
                            <span>{role.name}</span>
                            <button
                              onClick={() => handleRemoveRole(user.id, role.id, role.name)}
                              className="ml-1 text-primary hover:text-primary/80"
                              title="Remove role"
                            >
                              <UserX className="w-3 h-3" />
                            </button>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-text-secondary italic">No roles assigned</p>
                    )}
                  </div>

                  <p className="text-xs text-text-secondary">
                    Member since {formatDate(user.created_at)}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    onClick={() => {
                      setSelectedUser(user);
                      setShowAssignModal(true);
                    }}
                    disabled={getAvailableRoles(user).length === 0}
                  >
                    <UserCheck className="w-4 h-4 mr-1" />
                    Assign Role
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

      {/* Assign Role Modal */}
      {showAssignModal && selectedUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-surface border border-border rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold text-text mb-4">
              Assign Role to {selectedUser.email}
            </h3>
            
            <div className="space-y-3 mb-6">
              {Array.isArray(roles) && getAvailableRoles(selectedUser).map((role) => (
                <div key={role.id} className="p-3 border border-border rounded-lg bg-background">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-text">{role.name}</h4>
                      {role.description && (
                        <p className="text-sm text-text-secondary mt-1">{role.description}</p>
                      )}
                      <p className="text-xs text-text-secondary mt-1">
                        {role.permissions.length} permissions
                      </p>
                    </div>
                    <Button
                      size="sm"
                      onClick={() => handleAssignRole(selectedUser.id, role.id)}
                      disabled={loading}
                    >
                      Assign
                    </Button>
                  </div>
                </div>
              ))}
              {Array.isArray(roles) && getAvailableRoles(selectedUser).length === 0 && (
                <p className="text-center text-text-secondary py-4">
                  No additional roles available for this user
                </p>
              )}
            </div>

            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => {
                  setShowAssignModal(false);
                  setSelectedUser(null);
                }}
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}