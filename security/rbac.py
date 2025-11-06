#!/usr/bin/env python3
"""
Role-Based Access Control (RBAC) Tizimi
RBAC System - Advanced Role and Permission Management

Bu fayl ilg'or role-based access control (RBAC) tizimini ta'minlaydi,
foydalanuvchi rollari, huquqlar va ruxsatlarni boshqarish.

Features:
- Role-Based Access Control
- Dynamic Permission Assignment
- Hierarchical Roles
- Context-Aware Access Control
- Time-Based Restrictions
- Resource-Level Permissions
- Audit Trail
- Delegation Management
- Emergency Access Procedures
"""

import os
import sys
import json
import sqlite3
import hashlib
import datetime
import logging
import threading
import uuid
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/orion-starline/logs/rbac.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PermissionType(Enum):
    """Ruxsat turlari"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"
    OWNER = "owner"

class ResourceType(Enum):
    """Resurs turlari"""
    USER = "user"
    ROLE = "role"
    PERMISSION = "permission"
    DATA = "data"
    SYSTEM_CONFIG = "system_config"
    REPORT = "report"
    AUDIT_LOG = "audit_log"
    API_ENDPOINT = "api_endpoint"
    FILE = "file"
    DATABASE = "database"

class AccessDecision(Enum):
    """Kirish qarori"""
    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"

class ContextFactor(Enum):
    """Kontekst omillari"""
    TIME_BASED = "time_based"
    LOCATION_BASED = "location_based"
    DEVICE_BASED = "device_based"
    RISK_LEVEL = "risk_level"
    AUTHENTICATION_STRENGTH = "authentication_strength"

@dataclass
class Permission:
    """Ruxsat"""
    permission_id: str
    name: str
    description: str
    permission_type: PermissionType
    resource_type: ResourceType
    resource_id: Optional[str]
    conditions: Dict[str, Any]
    created_date: str
    metadata: Dict[str, Any]

@dataclass
class Role:
    """Rol"""
    role_id: str
    name: str
    description: str
    parent_role_id: Optional[str]
    permissions: List[str]
    is_system_role: bool
    is_active: bool
    created_date: str
    metadata: Dict[str, Any]

@dataclass
class User:
    """Foydalanuvchi"""
    user_id: str
    username: str
    email: str
    roles: List[str]
    attributes: Dict[str, Any]
    is_active: bool
    created_date: str
    last_login: Optional[str]
    metadata: Dict[str, Any]

@dataclass
class AccessContext:
    """Kirish konteksti"""
    context_id: str
    user_id: str
    resource: str
    action: str
    timestamp: str
    ip_address: str
    user_agent: str
    session_id: str
    factors: Dict[str, Any]

@dataclass
class AccessDecisionLog:
    """Kirish qarori logi"""
    decision_id: str
    context: AccessContext
    decision: AccessDecision
    reason: str
    permissions_checked: List[str]
    additional_conditions: List[str]
    timestamp: str

class PolicyEngine:
    """Siyosat injeni"""
    
    def __init__(self):
        self.policies = []
        self.decision_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def add_policy(self, policy: Dict[str, Any]):
        """Siyosat qo'shish"""
        self.policies.append(policy)
        logger.info(f"Policy added: {policy.get('name', 'Unknown')}")
    
    def evaluate_policies(self, context: AccessContext, user: User, 
                         resource: str, action: str) -> Tuple[AccessDecision, str]:
        """Siyosatlarni baholash"""
        for policy in self.policies:
            decision = self._evaluate_single_policy(policy, context, user, resource, action)
            if decision != AccessDecision.DENY:
                return decision, f"Policy: {policy.get('name', 'Unknown')}"
        
        return AccessDecision.DENY, "No matching policy found"
    
    def _evaluate_single_policy(self, policy: Dict[str, Any], context: AccessContext,
                               user: User, resource: str, action: str) -> AccessDecision:
        """Bitta siyosatni baholash"""
        try:
            # Check user criteria
            if 'user_criteria' in policy:
                if not self._match_user_criteria(policy['user_criteria'], user):
                    return AccessDecision.DENY
            
            # Check resource criteria
            if 'resource_criteria' in policy:
                if not self._match_resource_criteria(policy['resource_criteria'], resource):
                    return AccessDecision.DENY
            
            # Check action criteria
            if 'action_criteria' in policy:
                if not self._match_action_criteria(policy['action_criteria'], action):
                    return AccessDecision.DENY
            
            # Check context criteria
            if 'context_criteria' in policy:
                if not self._match_context_criteria(policy['context_criteria'], context):
                    return AccessDecision.DENY
            
            return AccessDecision.ALLOW if policy.get('effect') == 'allow' else AccessDecision.DENY
            
        except Exception as e:
            logger.error(f"Error evaluating policy: {e}")
            return AccessDecision.DENY
    
    def _match_user_criteria(self, criteria: Dict[str, Any], user: User) -> bool:
        """Foydalanuvchi mezonlarini moslashtirish"""
        if 'roles' in criteria:
            if not any(role in user.roles for role in criteria['roles']):
                return False
        
        if 'attributes' in criteria:
            for attr, value in criteria['attributes'].items():
                if attr not in user.attributes or user.attributes[attr] != value:
                    return False
        
        return True
    
    def _match_resource_criteria(self, criteria: Dict[str, Any], resource: str) -> bool:
        """Resurs mezonlarini moslashtirish"""
        if 'patterns' in criteria:
            import re
            if not any(re.match(pattern, resource) for pattern in criteria['patterns']):
                return False
        
        return True
    
    def _match_action_criteria(self, criteria: Dict[str, Any], action: str) -> bool:
        """Harakat mezonlarini moslashtirish"""
        if 'actions' in criteria:
            if action not in criteria['actions']:
                return False
        
        return True
    
    def _match_context_criteria(self, criteria: Dict[str, Any], context: AccessContext) -> bool:
        """Kontekst mezonlarini moslashtirish"""
        if 'time_restrictions' in criteria:
            if not self._check_time_restrictions(criteria['time_restrictions'], context):
                return False
        
        if 'ip_restrictions' in criteria:
            if context.ip_address not in criteria['ip_restrictions']:
                return False
        
        return True
    
    def _check_time_restrictions(self, restrictions: Dict[str, Any], context: AccessContext) -> bool:
        """Vaqt cheklovlarini tekshirish"""
        current_time = datetime.datetime.fromisoformat(context.timestamp)
        current_hour = current_time.hour
        
        if 'business_hours_only' in restrictions:
            start_hour = restrictions['business_hours_only'].get('start', 9)
            end_hour = restrictions['business_hours_only'].get('end', 17)
            if not (start_hour <= current_hour < end_hour):
                return False
        
        if 'allowed_days' in restrictions:
            allowed_days = restrictions['allowed_days']
            current_day = current_time.strftime('%A').lower()
            if current_day not in [day.lower() for day in allowed_days]:
                return False
        
        return True

class PermissionManager:
    """Ruxsatlar boshqaruvchisi"""
    
    def __init__(self, db_path: str = "/workspace/orion-starline/data/rbac_permissions.db"):
        self.db_path = db_path
        self.permissions_cache = {}
        self.init_database()
        
        logger.info("Permission Manager initialized")
    
    def init_database(self):
        """Ma'lumotlar bazasini ishga tushirish"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permissions (
                permission_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                permission_type TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id TEXT,
                conditions TEXT NOT NULL,
                created_date TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_permission(self, permission: Permission) -> bool:
        """Yangi ruxsat yaratish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO permissions 
                (permission_id, name, description, permission_type, resource_type, resource_id, 
                 conditions, created_date, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                permission.permission_id, permission.name, permission.description,
                permission.permission_type.value, permission.resource_type.value,
                permission.resource_id, json.dumps(permission.conditions),
                permission.created_date, json.dumps(permission.metadata)
            ))
            
            conn.commit()
            conn.close()
            
            # Update cache
            self.permissions_cache[permission.permission_id] = permission
            
            logger.info(f"Permission created: {permission.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create permission: {e}")
            return False
    
    def get_permission(self, permission_id: str) -> Optional[Permission]:
        """Ruxsatni olish"""
        if permission_id in self.permissions_cache:
            return self.permissions_cache[permission_id]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM permissions WHERE permission_id = ?', (permission_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            permission = Permission(
                permission_id=row[0],
                name=row[1],
                description=row[2],
                permission_type=PermissionType(row[3]),
                resource_type=ResourceType(row[4]),
                resource_id=row[5],
                conditions=json.loads(row[6]),
                created_date=row[7],
                metadata=json.loads(row[8])
            )
            self.permissions_cache[permission_id] = permission
            return permission
        
        return None
    
    def list_permissions(self, resource_type: ResourceType = None,
                        permission_type: PermissionType = None) -> List[Permission]:
        """Ruxsatlarni ro'yxatini olish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM permissions WHERE 1=1"
        params = []
        
        if resource_type:
            query += " AND resource_type = ?"
            params.append(resource_type.value)
        
        if permission_type:
            query += " AND permission_type = ?"
            params.append(permission_type.value)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        permissions = []
        for row in rows:
            permission = Permission(
                permission_id=row[0],
                name=row[1],
                description=row[2],
                permission_type=PermissionType(row[3]),
                resource_type=ResourceType(row[4]),
                resource_id=row[5],
                conditions=json.loads(row[6]),
                created_date=row[7],
                metadata=json.loads(row[8])
            )
            permissions.append(permission)
        
        return permissions

class RoleManager:
    """Rol boshqaruvchisi"""
    
    def __init__(self, db_path: str = "/workspace/orion-starline/data/rbac_roles.db"):
        self.db_path = db_path
        self.roles_cache = {}
        self.role_hierarchy = {}
        self.init_database()
        
        logger.info("Role Manager initialized")
    
    def init_database(self):
        """Ma'lumotlar bazasini ishga tushirish"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                role_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                parent_role_id TEXT,
                permissions TEXT NOT NULL,
                is_system_role BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                created_date TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_role(self, role: Role) -> bool:
        """Yangi rol yaratish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO roles 
                (role_id, name, description, parent_role_id, permissions, is_system_role, 
                 is_active, created_date, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                role.role_id, role.name, role.description, role.parent_role_id,
                json.dumps(role.permissions), role.is_system_role, role.is_active,
                role.created_date, json.dumps(role.metadata)
            ))
            
            conn.commit()
            conn.close()
            
            # Update cache and hierarchy
            self.roles_cache[role.role_id] = role
            if role.parent_role_id:
                self.role_hierarchy[role.role_id] = role.parent_role_id
            
            logger.info(f"Role created: {role.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create role: {e}")
            return False
    
    def get_role(self, role_id: str) -> Optional[Role]:
        """Rulni olish"""
        if role_id in self.roles_cache:
            return self.roles_cache[role_id]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM roles WHERE role_id = ?', (role_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            role = Role(
                role_id=row[0],
                name=row[1],
                description=row[2],
                parent_role_id=row[3],
                permissions=json.loads(row[4]),
                is_system_role=bool(row[5]),
                is_active=bool(row[6]),
                created_date=row[7],
                metadata=json.loads(row[8])
            )
            self.roles_cache[role_id] = role
            return role
        
        return None
    
    def get_user_permissions(self, user_id: str, user_manager) -> Set[str]:
        """Foydalanuvchining barcha ruxsatlarini olish"""
        user = user_manager.get_user(user_id)
        if not user:
            return set()
        
        all_permissions = set()
        
        for role_id in user.roles:
            role = self.get_role(role_id)
            if role and role.is_active:
                all_permissions.update(role.permissions)
                
                # Get permissions from parent roles
                parent_permissions = self._get_inherited_permissions(role_id)
                all_permissions.update(parent_permissions)
        
        return all_permissions
    
    def _get_inherited_permissions(self, role_id: str) -> Set[str]:
        """Ota-rol ruxsatlarini olish"""
        inherited = set()
        
        def get_parent_permissions(rid):
            role = self.get_role(rid)
            if role and role.parent_role_id:
                parent_role = self.get_role(role.parent_role_id)
                if parent_role:
                    inherited.update(parent_role.permissions)
                    get_parent_permissions(role.parent_role_id)
        
        get_parent_permissions(role_id)
        return inherited
    
    def list_roles(self, include_inactive: bool = False) -> List[Role]:
        """Rullar ro'yxatini olish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if include_inactive:
            cursor.execute('SELECT * FROM roles')
        else:
            cursor.execute('SELECT * FROM roles WHERE is_active = TRUE')
        
        rows = cursor.fetchall()
        conn.close()
        
        roles = []
        for row in rows:
            role = Role(
                role_id=row[0],
                name=row[1],
                description=row[2],
                parent_role_id=row[3],
                permissions=json.loads(row[4]),
                is_system_role=bool(row[5]),
                is_active=bool(row[6]),
                created_date=row[7],
                metadata=json.loads(row[8])
            )
            roles.append(role)
        
        return roles

class UserManager:
    """Foydalanuvchi boshqaruvchisi"""
    
    def __init__(self, db_path: str = "/workspace/orion-starline/data/rbac_users.db"):
        self.db_path = db_path
        self.users_cache = {}
        self.init_database()
        
        logger.info("User Manager initialized")
    
    def init_database(self):
        """Ma'lumotlar bazasini ishga tushirish"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                roles TEXT NOT NULL,
                attributes TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_date TEXT NOT NULL,
                last_login TEXT,
                metadata TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, user: User) -> bool:
        """Yangi foydalanuvchi yaratish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users 
                (user_id, username, email, roles, attributes, is_active, created_date, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user.user_id, user.username, user.email, json.dumps(user.roles),
                json.dumps(user.attributes), user.is_active, user.created_date,
                json.dumps(user.metadata)
            ))
            
            conn.commit()
            conn.close()
            
            # Update cache
            self.users_cache[user.user_id] = user
            
            logger.info(f"User created: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Foydalanuvchini olish"""
        if user_id in self.users_cache:
            return self.users_cache[user_id]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            user = User(
                user_id=row[0],
                username=row[1],
                email=row[2],
                roles=json.loads(row[3]),
                attributes=json.loads(row[4]),
                is_active=bool(row[5]),
                created_date=row[6],
                last_login=row[7],
                metadata=json.loads(row[8])
            )
            self.users_cache[user_id] = user
            return user
        
        return None
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Foydalanuvchini yangilash"""
        user = self.get_user(user_id)
        if not user:
            return False
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users 
                SET username = ?, email = ?, roles = ?, attributes = ?, is_active = ?, last_login = ?, metadata = ?
                WHERE user_id = ?
            ''', (
                user.username, user.email, json.dumps(user.roles), json.dumps(user.attributes),
                user.is_active, user.last_login, json.dumps(user.metadata), user_id
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"User updated: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            return False

class AccessControlEngine:
    """Kirish boshqaruv injeni"""
    
    def __init__(self, user_manager: UserManager, role_manager: RoleManager,
                 permission_manager: PermissionManager, policy_engine: PolicyEngine):
        self.user_manager = user_manager
        self.role_manager = role_manager
        self.permission_manager = permission_manager
        self.policy_engine = policy_engine
        self.decision_cache = {}
        self.audit_log = []
        
        logger.info("Access Control Engine initialized")
    
    def check_access(self, user_id: str, resource: str, action: str,
                    context: AccessContext) -> Tuple[AccessDecision, str, List[str]]:
        """Kirish ruxsatini tekshirish"""
        # Get user
        user = self.user_manager.get_user(user_id)
        if not user:
            return AccessDecision.DENY, "User not found", []
        
        if not user.is_active:
            return AccessDecision.DENY, "User is inactive", []
        
        # Get user permissions
        user_permissions = self.role_manager.get_user_permissions(user_id, self.user_manager)
        
        # Check specific permission for resource and action
        required_permission = f"{action}_{resource}"
        has_permission = any(required_permission in perm or perm in required_permission 
                           for perm in user_permissions)
        
        if not has_permission:
            # Check policy engine
            policy_decision, policy_reason = self.policy_engine.evaluate_policies(
                context, user, resource, action
            )
            
            if policy_decision == AccessDecision.ALLOW:
                return policy_decision, policy_reason, list(user_permissions)
            else:
                return AccessDecision.DENY, "Access denied by policy", list(user_permissions)
        
        # Evaluate policies for additional context
        policy_decision, policy_reason = self.policy_engine.evaluate_policies(
            context, user, resource, action
        )
        
        # Log access decision
        decision_log = AccessDecisionLog(
            decision_id=str(uuid.uuid4()),
            context=context,
            decision=policy_decision,
            reason=policy_reason,
            permissions_checked=list(user_permissions),
            additional_conditions=[],
            timestamp=datetime.datetime.now().isoformat()
        )
        
        self.audit_log.append(decision_log)
        
        logger.info(f"Access decision: {user_id} -> {action} {resource} = {policy_decision.value}")
        
        return policy_decision, policy_reason, list(user_permissions)
    
    def delegate_permission(self, delegator_id: str, delegatee_id: str,
                          permission: str, expires_in_days: int = 7) -> bool:
        """Ruxsatni topshirish"""
        try:
            # Check if delegator has the permission
            delegator = self.user_manager.get_user(delegator_id)
            if not delegator:
                return False
            
            delegator_permissions = self.role_manager.get_user_permissions(delegator_id, self.user_manager)
            if permission not in delegator_permissions:
                return False
            
            # Create temporary role for delegation
            delegation_role = Role(
                role_id=str(uuid.uuid4()),
                name=f"delegation_{delegator_id}_{delegatee_id}_{permission}",
                description=f"Temporary delegation of {permission} from {delegator_id} to {delegatee_id}",
                parent_role_id=None,
                permissions=[permission],
                is_system_role=False,
                is_active=True,
                created_date=datetime.datetime.now().isoformat(),
                metadata={
                    'delegator_id': delegator_id,
                    'delegatee_id': delegatee_id,
                    'delegated_permission': permission,
                    'expires_at': (datetime.datetime.now() + datetime.timedelta(days=expires_in_days)).isoformat(),
                    'type': 'delegation'
                }
            )
            
            # Add temporary role to delegatee
            delegatee = self.user_manager.get_user(delegatee_id)
            if not delegatee:
                return False
            
            delegatee.roles.append(delegation_role.role_id)
            self.user_manager.update_user(delegatee_id, {'roles': delegatee.roles})
            self.role_manager.create_role(delegation_role)
            
            logger.info(f"Permission delegated: {delegator_id} -> {delegatee_id} ({permission})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delegate permission: {e}")
            return False
    
    def revoke_delegation(self, delegation_role_id: str) -> bool:
        """Topshirilgan ruxsatni bekor qilish"""
        try:
            delegation_role = self.role_manager.get_role(delegation_role_id)
            if not delegation_role or delegation_role.metadata.get('type') != 'delegation':
                return False
            
            # Remove role from delegatee
            delegatee_id = delegation_role.metadata['delegatee_id']
            delegatee = self.user_manager.get_user(delegatee_id)
            
            if delegatee and delegation_role_id in delegatee.roles:
                delegatee.roles.remove(delegation_role_id)
                self.user_manager.update_user(delegatee_id, {'roles': delegatee.roles})
            
            # Deactivate delegation role
            self.role_manager.create_role(
                Role(
                    role_id=delegation_role_id,
                    name=delegation_role.name,
                    description=delegation_role.description,
                    parent_role_id=delegation_role.parent_role_id,
                    permissions=delegation_role.permissions,
                    is_system_role=delegation_role.is_system_role,
                    is_active=False,  # Deactivate
                    created_date=delegation_role.created_date,
                    metadata=delegation_role.metadata
                )
            )
            
            logger.info(f"Delegation revoked: {delegation_role_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke delegation: {e}")
            return False

class EmergencyAccess:
    """Favqulodda kirish"""
    
    def __init__(self, access_engine: AccessControlEngine):
        self.access_engine = access_engine
        self.emergency_users = set()
        self.emergency_permissions = set()
        self.break_glass_used = False
        self.audit_trail = []
        
        logger.info("Emergency Access initialized")
    
    def activate_break_glass(self, user_id: str, reason: str, context: AccessContext) -> bool:
        """Break glass rejimini faollashtirish"""
        try:
            # Log the emergency access
            self.audit_trail.append({
                'action': 'break_glass_activated',
                'user_id': user_id,
                'reason': reason,
                'context': asdict(context),
                'timestamp': datetime.datetime.now().isoformat()
            })
            
            self.break_glass_used = True
            
            # Grant emergency access to critical resources
            emergency_resources = ['system_config', 'audit_log', 'user_management']
            emergency_actions = ['read', 'write']
            
            for resource in emergency_resources:
                for action in emergency_actions:
                    # This would normally involve creating a temporary emergency role
                    # and granting it to the user
                    pass
            
            logger.critical(f"BREAK GLASS activated by {user_id}: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to activate break glass: {e}")
            return False
    
    def grant_temporary_access(self, user_id: str, permissions: List[str],
                             duration_hours: int = 1) -> bool:
        """Vaqtinchalik kirish berish"""
        try:
            # Create temporary role with specified permissions
            temp_role = Role(
                role_id=str(uuid.uuid4()),
                name=f"temp_access_{user_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                description=f"Temporary access for {user_id}",
                parent_role_id=None,
                permissions=permissions,
                is_system_role=False,
                is_active=True,
                created_date=datetime.datetime.now().isoformat(),
                metadata={
                    'type': 'temporary_access',
                    'user_id': user_id,
                    'expires_at': (datetime.datetime.now() + datetime.timedelta(hours=duration_hours)).isoformat(),
                    'duration_hours': duration_hours
                }
            )
            
            # Add role to user
            user = self.access_engine.user_manager.get_user(user_id)
            if not user:
                return False
            
            user.roles.append(temp_role.role_id)
            success = self.access_engine.user_manager.update_user(user_id, {'roles': user.roles})
            
            if success:
                self.access_engine.role_manager.create_role(temp_role)
                logger.warning(f"Temporary access granted: {user_id} for {duration_hours} hours")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to grant temporary access: {e}")
            return False

# Main RBAC System
class RBACSystem:
    """Asosiy RBAC tizimi"""
    
    def __init__(self):
        self.user_manager = UserManager()
        self.role_manager = RoleManager()
        self.permission_manager = PermissionManager()
        self.policy_engine = PolicyEngine()
        self.access_engine = AccessControlEngine(
            self.user_manager, self.role_manager, self.permission_manager, self.policy_engine
        )
        self.emergency_access = EmergencyAccess(self.access_engine)
        
        # Initialize default permissions and roles
        self._init_default_permissions()
        self._init_default_roles()
        self._init_default_policies()
        
        logger.info("RBAC System initialized")
    
    def _init_default_permissions(self):
        """Standart ruxsatlarni yaratish"""
        default_permissions = [
            Permission(
                permission_id="read_user_profile",
                name="Read User Profile",
                description="Can read user profile information",
                permission_type=PermissionType.READ,
                resource_type=ResourceType.USER,
                resource_id=None,
                conditions={},
                created_date=datetime.datetime.now().isoformat(),
                metadata={}
            ),
            Permission(
                permission_id="write_user_profile",
                name="Write User Profile",
                description="Can modify user profile information",
                permission_type=PermissionType.WRITE,
                resource_type=ResourceType.USER,
                resource_id=None,
                conditions={},
                created_date=datetime.datetime.now().isoformat(),
                metadata={}
            ),
            Permission(
                permission_id="admin_system_config",
                name="Admin System Config",
                description="Can modify system configuration",
                permission_type=PermissionType.ADMIN,
                resource_type=ResourceType.SYSTEM_CONFIG,
                resource_id=None,
                conditions={},
                created_date=datetime.datetime.now().isoformat(),
                metadata={}
            ),
            Permission(
                permission_id="read_audit_logs",
                name="Read Audit Logs",
                description="Can read audit logs",
                permission_type=PermissionType.READ,
                resource_type=ResourceType.AUDIT_LOG,
                resource_id=None,
                conditions={},
                created_date=datetime.datetime.now().isoformat(),
                metadata={}
            )
        ]
        
        for permission in default_permissions:
            self.permission_manager.create_permission(permission)
    
    def _init_default_roles(self):
        """Standart rullarni yaratish"""
        admin_role = Role(
            role_id="admin",
            name="Administrator",
            description="System administrator with full access",
            parent_role_id=None,
            permissions=["read_user_profile", "write_user_profile", "admin_system_config", "read_audit_logs"],
            is_system_role=True,
            is_active=True,
            created_date=datetime.datetime.now().isoformat(),
            metadata={'level': 'system'}
        )
        
        user_role = Role(
            role_id="user",
            name="Regular User",
            description="Regular system user",
            parent_role_id=None,
            permissions=["read_user_profile"],
            is_system_role=True,
            is_active=True,
            created_date=datetime.datetime.now().isoformat(),
            metadata={'level': 'standard'}
        )
        
        auditor_role = Role(
            role_id="auditor",
            name="Auditor",
            description="System auditor with read-only access to logs",
            parent_role_id=None,
            permissions=["read_audit_logs", "read_user_profile"],
            is_system_role=True,
            is_active=True,
            created_date=datetime.datetime.now().isoformat(),
            metadata={'level': 'auditing'}
        )
        
        self.role_manager.create_role(admin_role)
        self.role_manager.create_role(user_role)
        self.role_manager.create_role(auditor_role)
    
    def _init_default_policies(self):
        """Standart siyosatlarni yaratish"""
        # Time-based access policy
        self.policy_engine.add_policy({
            'name': 'business_hours_access',
            'effect': 'allow',
            'user_criteria': {'roles': ['admin']},
            'resource_criteria': {'patterns': ['/api/admin/*']},
            'action_criteria': {'actions': ['read', 'write']},
            'context_criteria': {
                'time_restrictions': {
                    'business_hours_only': {'start': 8, 'end': 18},
                    'allowed_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                }
            }
        })
        
        # IP restriction policy
        self.policy_engine.add_policy({
            'name': 'internal_ip_access',
            'effect': 'allow',
            'user_criteria': {'roles': ['admin', 'user']},
            'resource_criteria': {'patterns': ['/api/internal/*']},
            'action_criteria': {'actions': ['read']},
            'context_criteria': {
                'ip_restrictions': ['192.168.1.0/24', '10.0.0.0/8']
            }
        })
    
    def create_user_with_role(self, username: str, email: str, roles: List[str],
                            attributes: Dict[str, Any] = None) -> User:
        """Rol bilan foydalanuvchi yaratish"""
        user = User(
            user_id=str(uuid.uuid4()),
            username=username,
            email=email,
            roles=roles,
            attributes=attributes or {},
            is_active=True,
            created_date=datetime.datetime.now().isoformat(),
            last_login=None,
            metadata={}
        )
        
        self.user_manager.create_user(user)
        return user
    
    def check_user_access(self, user_id: str, resource: str, action: str,
                         context_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Foydalanuvchi kirish huquqini tekshirish"""
        context = AccessContext(
            context_id=str(uuid.uuid4()),
            user_id=user_id,
            resource=resource,
            action=action,
            timestamp=datetime.datetime.now().isoformat(),
            ip_address=context_data.get('ip_address', '0.0.0.0'),
            user_agent=context_data.get('user_agent', 'unknown'),
            session_id=context_data.get('session_id', 'unknown'),
            factors=context_data.get('factors', {})
        )
        
        decision, reason, permissions = self.access_engine.check_access(
            user_id, resource, action, context
        )
        
        return decision == AccessDecision.ALLOW, reason
    
    def get_user_permissions(self, user_id: str) -> List[str]:
        """Foydalanuvchi ruxsatlarini olish"""
        return list(self.role_manager.get_user_permissions(user_id, self.user_manager))
    
    def generate_access_report(self, user_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Kirish hisobotini yaratish"""
        user = self.user_manager.get_user(user_id)
        if not user:
            return {'error': 'User not found'}
        
        # Get user permissions
        permissions = self.get_user_permissions(user_id)
        
        # Get user roles
        roles = []
        for role_id in user.roles:
            role = self.role_manager.get_role(role_id)
            if role:
                roles.append({
                    'role_id': role.role_id,
                    'role_name': role.name,
                    'description': role.description,
                    'parent_role_id': role.parent_role_id,
                    'permissions': role.permissions
                })
        
        return {
            'user_id': user_id,
            'username': user.username,
            'email': user.email,
            'roles': roles,
            'permissions': permissions,
            'is_active': user.is_active,
            'created_date': user.created_date,
            'last_login': user.last_login,
            'report_period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'generated_at': datetime.datetime.now().isoformat()
        }

# Flask API for RBAC system
from flask import Flask, request, jsonify, g

app = Flask(__name__)
rbac_system = RBACSystem()

@app.route('/api/rbac/user/create', methods=['POST'])
def create_user():
    """Foydalanuvchi yaratish API"""
    try:
        data = request.get_json()
        user = rbac_system.create_user_with_role(
            username=data['username'],
            email=data['email'],
            roles=data.get('roles', ['user']),
            attributes=data.get('attributes', {})
        )
        
        return jsonify({
            'user_id': user.user_id,
            'username': user.username,
            'roles': user.roles
        })
        
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rbac/access/check', methods=['POST'])
def check_access():
    """Kirish huquqini tekshirish API"""
    try:
        data = request.get_json()
        user_id = data['user_id']
        resource = data['resource']
        action = data['action']
        
        context_data = {
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'unknown'),
            'session_id': request.headers.get('X-Session-ID', 'unknown'),
            'factors': data.get('factors', {})
        }
        
        allowed, reason = rbac_system.check_user_access(user_id, resource, action, context_data)
        
        return jsonify({
            'allowed': allowed,
            'reason': reason,
            'user_id': user_id,
            'resource': resource,
            'action': action
        })
        
    except Exception as e:
        logger.error(f"Error checking access: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rbac/user/<user_id>/permissions')
def get_user_permissions(user_id):
    """Foydalanuvchi ruxsatlarini olish API"""
    try:
        permissions = rbac_system.get_user_permissions(user_id)
        return jsonify({'user_id': user_id, 'permissions': permissions})
    except Exception as e:
        logger.error(f"Error getting user permissions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rbac/user/<user_id>/report')
def get_access_report(user_id):
    """Foydalanuvchi kirish hisoboti API"""
    try:
        start_date = request.args.get('start_date', 
                                    (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat())
        end_date = request.args.get('end_date', datetime.datetime.now().isoformat())
        
        report = rbac_system.generate_access_report(user_id, start_date, end_date)
        return jsonify(report)
    except Exception as e:
        logger.error(f"Error generating access report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rbac/roles/list')
def list_roles():
    """Rullar ro'yxati API"""
    try:
        roles = rbac_system.role_manager.list_roles()
        roles_data = [{
            'role_id': role.role_id,
            'name': role.name,
            'description': role.description,
            'parent_role_id': role.parent_role_id,
            'permissions': role.permissions,
            'is_system_role': role.is_system_role,
            'is_active': role.is_active
        } for role in roles]
        
        return jsonify({'roles': roles_data})
    except Exception as e:
        logger.error(f"Error listing roles: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rbac/permissions/list')
def list_permissions():
    """Ruxsatlar ro'yxati API"""
    try:
        resource_type = request.args.get('resource_type')
        permission_type = request.args.get('permission_type')
        
        rt = ResourceType(resource_type) if resource_type else None
        pt = PermissionType(permission_type) if permission_type else None
        
        permissions = rbac_system.permission_manager.list_permissions(rt, pt)
        permissions_data = [{
            'permission_id': perm.permission_id,
            'name': perm.name,
            'description': perm.description,
            'permission_type': perm.permission_type.value,
            'resource_type': perm.resource_type.value
        } for perm in permissions]
        
        return jsonify({'permissions': permissions_data})
    except Exception as e:
        logger.error(f"Error listing permissions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/rbac/emergency/break-glass', methods=['POST'])
def activate_emergency_access():
    """Favqulodda kirish API"""
    try:
        data = request.get_json()
        user_id = data['user_id']
        reason = data['reason']
        
        context = AccessContext(
            context_id=str(uuid.uuid4()),
            user_id=user_id,
            resource='emergency_access',
            action='activate',
            timestamp=datetime.datetime.now().isoformat(),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', 'unknown'),
            session_id=request.headers.get('X-Session-ID', 'unknown'),
            factors={}
        )
        
        success = rbac_system.emergency_access.activate_break_glass(user_id, reason, context)
        
        return jsonify({
            'success': success,
            'break_glass_activated': success,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error activating emergency access: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs('/workspace/orion-starline/data', exist_ok=True)
    os.makedirs('/workspace/orion-starline/logs', exist_ok=True)
    
    # Run RBAC system
    app.run(host='0.0.0.0', port=5004, debug=False)
