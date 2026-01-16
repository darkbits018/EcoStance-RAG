"""
Role-Based Access Control (RBAC) implementation.
Enhanced to support two-tier role architecture.
"""

from typing import Optional, List, Set
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.tenant_user import TenantUser
from app.models.tenant_role import TenantRole
from app.auth.permissions import (
    Permission, Role, SystemRole, 
    get_role_permissions, get_system_role_permissions,
    SYSTEM_ROLE_PERMISSIONS
)


class RBACService:
    """Service for role-based access control operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_permission(
        self,
        tenant_id: str,
        user_id: str,
        permission: Permission
    ) -> bool:
        """
        Check if a user has a specific permission within a tenant.
        Uses enhanced two-tier permission resolution.
        
        Args:
            tenant_id: The tenant ID
            user_id: The user ID
            permission: The permission to check
            
        Returns:
            True if user has permission, False otherwise
        """
        user_permissions = self.get_user_permissions(tenant_id, user_id)
        return permission in user_permissions
    
    def require_permission(
        self,
        tenant_id: str,
        user_id: str,
        permission: Permission
    ) -> None:
        """
        Require a user to have a specific permission, raise exception if not.
        
        Args:
            tenant_id: The tenant ID
            user_id: The user ID
            permission: The required permission
            
        Raises:
            HTTPException: 403 if user doesn't have permission
        """
        if not self.check_permission(tenant_id, user_id, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value} required"
            )
    
    def get_user_permissions(self, tenant_id: str, user_id: str) -> Set[Permission]:
        """
        Get all permissions for a user using two-tier resolution.
        
        Permission resolution order:
        1. If super_admin: ALL permissions
        2. If tenant_admin: All tenant-scoped permissions
        3. If custom tenant role: Role's specific permissions
        4. If legacy role: Legacy role permissions
        5. Default: Empty set (no permissions)
        
        Args:
            tenant_id: The tenant ID
            user_id: The user ID
            
        Returns:
            Set of permissions for the user
        """
        tenant_user = self.db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant_id,
            TenantUser.user_id == user_id
        ).first()
        
        if not tenant_user:
            # If no TenantUser record exists, return empty permissions
            return set()
        
        # Check system role first
        if tenant_user.system_role:
            system_role = SystemRole(tenant_user.system_role)
            return get_system_role_permissions(system_role)
        
        # Check tenant role
        if tenant_user.tenant_role_id and tenant_user.tenant_role:
            if tenant_user.tenant_role.is_active:
                return set(Permission(p) for p in tenant_user.tenant_role.permissions)
        
        # Fall back to legacy role for backward compatibility
        if tenant_user.role:
            try:
                legacy_role = Role(tenant_user.role)
                return get_role_permissions(legacy_role)
            except ValueError:
                # Invalid legacy role
                pass
        
        # Default: no permissions
        return set()
    
    def get_user_role(self, tenant_id: str, user_id: str) -> Optional[Role]:
        """
        Get the legacy role of a user within a tenant.
        Kept for backward compatibility.
        
        Args:
            tenant_id: The tenant ID
            user_id: The user ID
            
        Returns:
            The user's legacy role or None if not found
        """
        tenant_user = self.db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant_id,
            TenantUser.user_id == user_id
        ).first()
        
        if tenant_user and tenant_user.role:
            try:
                return Role(tenant_user.role)
            except ValueError:
                pass
        
        return None
    
    def assign_role(
        self,
        tenant_id: str,
        user_id: str,
        role: Role,
        assigned_by: str
    ) -> TenantUser:
        """
        Assign a role to a user within a tenant.
        
        Args:
            tenant_id: The tenant ID
            user_id: The user ID to assign role to
            role: The role to assign
            assigned_by: The user ID performing the assignment
            
        Returns:
            The updated TenantUser record
            
        Raises:
            HTTPException: If assigner doesn't have permission
        """
        # Check if assigner has permission to manage users
        self.require_permission(
            tenant_id,
            assigned_by,
            Permission.TENANT_MANAGE_USERS
        )
        
        # Check if user already has a role in this tenant
        tenant_user = self.db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant_id,
            TenantUser.user_id == user_id
        ).first()
        
        if tenant_user:
            tenant_user.role = role.value
        else:
            tenant_user = TenantUser(
                tenant_id=tenant_id,
                user_id=user_id,
                role=role.value
            )
            self.db.add(tenant_user)
        
        self.db.commit()
        self.db.refresh(tenant_user)
        return tenant_user
    
    def remove_user_from_tenant(
        self,
        tenant_id: str,
        user_id: str,
        removed_by: str
    ) -> None:
        """
        Remove a user from a tenant.
        
        Args:
            tenant_id: The tenant ID
            user_id: The user ID to remove
            removed_by: The user ID performing the removal
            
        Raises:
            HTTPException: If remover doesn't have permission
        """
        # Check if remover has permission to manage users
        self.require_permission(
            tenant_id,
            removed_by,
            Permission.TENANT_MANAGE_USERS
        )
        
        tenant_user = self.db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant_id,
            TenantUser.user_id == user_id
        ).first()
        
        if tenant_user:
            self.db.delete(tenant_user)
            self.db.commit()
    
    def list_tenant_users(self, tenant_id: str, requester_id: str) -> list[TenantUser]:
        """
        List all users in a tenant.
        
        Args:
            tenant_id: The tenant ID
            requester_id: The user ID requesting the list
            
        Returns:
            List of TenantUser records
            
        Raises:
            HTTPException: If requester doesn't have permission
        """
        # Check if requester has permission to view users
        self.require_permission(
            tenant_id,
            requester_id,
            Permission.TENANT_VIEW
        )
        
        return self.db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant_id
        ).all()
    
    # New methods for two-tier RBAC system
    
    def create_tenant_role(
        self, 
        tenant_id: str, 
        creator_id: str, 
        name: str, 
        permissions: List[Permission], 
        description: str = None
    ) -> TenantRole:
        """
        Create a new tenant role with specified permissions.
        
        Args:
            tenant_id: The tenant ID
            creator_id: The user ID creating the role
            name: The role name
            permissions: List of permissions to assign
            description: Optional role description
            
        Returns:
            The created TenantRole
            
        Raises:
            HTTPException: If creator doesn't have permission or role name exists
        """
        # Check if creator has permission to manage users
        self.require_permission(tenant_id, creator_id, Permission.TENANT_MANAGE_USERS)
        
        # Validate permissions - tenant admins cannot assign admin:* permissions
        creator_permissions = self.get_user_permissions(tenant_id, creator_id)
        invalid_permissions = []
        for permission in permissions:
            if permission not in creator_permissions:
                invalid_permissions.append(permission)
        
        if invalid_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cannot assign permissions you don't have: {[p.value for p in invalid_permissions]}"
            )
        
        # Check if role name already exists in tenant
        existing_role = self.db.query(TenantRole).filter(
            TenantRole.tenant_id == tenant_id,
            TenantRole.name == name
        ).first()
        
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{name}' already exists in this tenant"
            )
        
        # Create the role
        # Resolve internal tenant_user_id for created_by field
        tenant_user = self.db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant_id,
            TenantUser.user_id == creator_id
        ).first()
        
        if not tenant_user:
            # Should not happen if require_permission passed, but good for safety
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found in tenant"
            )

        tenant_role = TenantRole(
            tenant_id=tenant_id,
            name=name,
            description=description,
            permissions=[p.value for p in permissions],
            created_by=tenant_user.id  # Use internal PK
        )
        
        self.db.add(tenant_role)
        self.db.commit()
        self.db.refresh(tenant_role)
        return tenant_role
    
    def update_tenant_role(
        self,
        role_id: str,
        updater_id: str,
        name: str = None,
        permissions: List[Permission] = None,
        description: str = None
    ) -> TenantRole:
        """
        Update an existing tenant role.
        
        Args:
            role_id: The role ID to update
            updater_id: The user ID performing the update
            name: New role name (optional)
            permissions: New permissions list (optional)
            description: New description (optional)
            
        Returns:
            The updated TenantRole
            
        Raises:
            HTTPException: If updater doesn't have permission or role not found
        """
        # Get the role
        tenant_role = self.db.query(TenantRole).filter(TenantRole.id == role_id).first()
        if not tenant_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Check if updater has permission
        self.require_permission(tenant_role.tenant_id, updater_id, Permission.TENANT_MANAGE_USERS)
        
        # Validate permissions if provided
        if permissions is not None:
            updater_permissions = self.get_user_permissions(tenant_role.tenant_id, updater_id)
            invalid_permissions = []
            for permission in permissions:
                if permission not in updater_permissions:
                    invalid_permissions.append(permission)
            
            if invalid_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Cannot assign permissions you don't have: {[p.value for p in invalid_permissions]}"
                )
        
        # Check if new name conflicts
        if name and name != tenant_role.name:
            existing_role = self.db.query(TenantRole).filter(
                TenantRole.tenant_id == tenant_role.tenant_id,
                TenantRole.name == name,
                TenantRole.id != role_id
            ).first()
            
            if existing_role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Role '{name}' already exists in this tenant"
                )
        
        # Update the role
        if name is not None:
            tenant_role.name = name
        if permissions is not None:
            tenant_role.permissions = [p.value for p in permissions]
        if description is not None:
            tenant_role.description = description
        
        self.db.commit()
        self.db.refresh(tenant_role)
        return tenant_role
    
    def delete_tenant_role(self, role_id: str, deleter_id: str) -> None:
        """
        Delete a tenant role (users with this role will lose it).
        
        Args:
            role_id: The role ID to delete
            deleter_id: The user ID performing the deletion
            
        Raises:
            HTTPException: If deleter doesn't have permission or role not found
        """
        # Get the role
        tenant_role = self.db.query(TenantRole).filter(TenantRole.id == role_id).first()
        if not tenant_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        # Check if deleter has permission
        self.require_permission(tenant_role.tenant_id, deleter_id, Permission.TENANT_MANAGE_USERS)
        
        # Remove role from all users first
        self.db.query(TenantUser).filter(
            TenantUser.tenant_role_id == role_id
        ).update({"tenant_role_id": None})
        
        # Delete the role
        self.db.delete(tenant_role)
        self.db.commit()
    
    def list_tenant_roles(self, tenant_id: str, requester_id: str) -> List[TenantRole]:
        """
        List all roles in a tenant.
        
        Args:
            tenant_id: The tenant ID
            requester_id: The user ID requesting the list
            
        Returns:
            List of TenantRole records
            
        Raises:
            HTTPException: If requester doesn't have permission
        """
        # Check if requester has permission to view tenant
        self.require_permission(tenant_id, requester_id, Permission.TENANT_VIEW)
        
        return self.db.query(TenantRole).filter(
            TenantRole.tenant_id == tenant_id,
            TenantRole.is_active == True
        ).all()
    
    def assign_tenant_role(
        self, 
        tenant_id: str, 
        user_id: str, 
        role_id: str, 
        assigned_by: str
    ) -> TenantUser:
        """
        Assign a tenant role to a user.
        
        Args:
            tenant_id: The tenant ID
            user_id: The user ID to assign role to
            role_id: The role ID to assign
            assigned_by: The user ID performing the assignment
            
        Returns:
            The updated TenantUser record
            
        Raises:
            HTTPException: If assigner doesn't have permission
        """
        # Check if assigner has permission to manage users
        self.require_permission(tenant_id, assigned_by, Permission.TENANT_MANAGE_USERS)
        
        # Verify the role exists and belongs to the tenant
        tenant_role = self.db.query(TenantRole).filter(
            TenantRole.id == role_id,
            TenantRole.tenant_id == tenant_id,
            TenantRole.is_active == True
        ).first()
        
        if not tenant_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found or inactive"
            )
        
        # Get or create tenant user
        tenant_user = self.db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant_id,
            TenantUser.user_id == user_id
        ).first()
        
        if not tenant_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in tenant"
            )
        
        # Assign the role
        tenant_user.tenant_role_id = role_id
        tenant_user.system_role = None  # Clear system role when assigning tenant role
        
        self.db.commit()
        self.db.refresh(tenant_user)
        return tenant_user
    
    def assign_system_role(
        self,
        tenant_id: str,
        user_id: str,
        system_role: SystemRole,
        assigned_by: str
    ) -> TenantUser:
        """
        Assign a system role to a user.
        Only super_admin can assign system roles.
        
        Args:
            tenant_id: The tenant ID
            user_id: The user ID to assign role to
            system_role: The system role to assign
            assigned_by: The user ID performing the assignment
            
        Returns:
            The updated TenantUser record
            
        Raises:
            HTTPException: If assigner doesn't have permission
        """
        # Only super_admin can assign system roles
        assigner_permissions = self.get_user_permissions(tenant_id, assigned_by)
        if not (Permission.ADMIN_MANAGE_USERS in assigner_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super admin can assign system roles"
            )
        
        # Get tenant user
        tenant_user = self.db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant_id,
            TenantUser.user_id == user_id
        ).first()
        
        if not tenant_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in tenant"
            )
        
        # Assign the system role
        tenant_user.system_role = system_role.value
        tenant_user.tenant_role_id = None  # Clear tenant role when assigning system role
        
        self.db.commit()
        self.db.refresh(tenant_user)
        return tenant_user
    
    # Legacy methods (kept for backward compatibility)
    
    def assign_role(
        self,
        tenant_id: str,
        user_id: str,
        role: Role,
        assigned_by: str
    ) -> TenantUser:
        """
        Assign a legacy role to a user within a tenant.
        Kept for backward compatibility.
        
        Args:
            tenant_id: The tenant ID
            user_id: The user ID to assign role to
            role: The legacy role to assign
            assigned_by: The user ID performing the assignment
            
        Returns:
            The updated TenantUser record
            
        Raises:
            HTTPException: If assigner doesn't have permission
        """
        # Check if assigner has permission to manage users
        self.require_permission(
            tenant_id,
            assigned_by,
            Permission.TENANT_MANAGE_USERS
        )
        
        # Check if user already has a role in this tenant
        tenant_user = self.db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant_id,
            TenantUser.user_id == user_id
        ).first()
        
        if tenant_user:
            tenant_user.role = role.value
            # Clear new role fields when using legacy role
            tenant_user.system_role = None
            tenant_user.tenant_role_id = None
        else:
            tenant_user = TenantUser(
                tenant_id=tenant_id,
                user_id=user_id,
                role=role.value
            )
            self.db.add(tenant_user)
        
        self.db.commit()
        self.db.refresh(tenant_user)
        return tenant_user
    
    def remove_user_from_tenant(
        self,
        tenant_id: str,
        user_id: str,
        removed_by: str
    ) -> None:
        """
        Remove a user from a tenant.
        
        Args:
            tenant_id: The tenant ID
            user_id: The user ID to remove
            removed_by: The user ID performing the removal
            
        Raises:
            HTTPException: If remover doesn't have permission
        """
        # Check if remover has permission to manage users
        self.require_permission(
            tenant_id,
            removed_by,
            Permission.TENANT_MANAGE_USERS
        )
        
        tenant_user = self.db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant_id,
            TenantUser.user_id == user_id
        ).first()
        
        if tenant_user:
            self.db.delete(tenant_user)
            self.db.commit()
    
    def list_tenant_users(self, tenant_id: str, requester_id: str) -> List[TenantUser]:
        """
        List all users in a tenant.
        
        Args:
            tenant_id: The tenant ID
            requester_id: The user ID requesting the list
            
        Returns:
            List of TenantUser records
            
        Raises:
            HTTPException: If requester doesn't have permission
        """
        # Check if requester has permission to view users
        self.require_permission(
            tenant_id,
            requester_id,
            Permission.TENANT_VIEW
        )
        
        return self.db.query(TenantUser).filter(
            TenantUser.tenant_id == tenant_id
        ).all()