import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib

class ConnectionManager:
    def __init__(self, config_file: str = "data/saved_connections.json"):
        self.config_file = config_file
        self.connections = self._load_connections()
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(config_file), exist_ok=True)

    def _load_connections(self) -> Dict[str, Any]:
        """Load saved connections from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}

    def _save_connections(self):
        """Save connections to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.connections, f, indent=2)

    def _generate_connection_id(self, config: Dict[str, Any]) -> str:
        """Generate a unique ID for a connection"""
        id_data = {
            'type': config.get('type'),
            'host': config.get('host'),
            'port': config.get('port'),
            'database': config.get('database'),
            'username': config.get('username')
        }
        id_string = json.dumps(id_data, sort_keys=True)
        return hashlib.md5(id_string.encode()).hexdigest()[:8]

    def save_connection(self, config: Dict[str, Any], name: str = None, save_password: bool = False) -> str:
        """Save a database connection configuration"""
        connection_id = self._generate_connection_id(config)
        
        connection_entry = {
            'id': connection_id,
            'name': name or f"{config.get('type', 'Unknown')} - {config.get('database', 'Unknown')}",
            'type': config.get('type'),
            'host': config.get('host'),
            'port': config.get('port'),
            'database': config.get('database'),
            'username': config.get('username'),
            'created_at': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat(),
            'use_count': self.connections.get(connection_id, {}).get('use_count', 0) + 1
        }
        
        if save_password and config.get('password'):
            connection_entry['password'] = config.get('password')
            connection_entry['password_saved'] = True
        else:
            connection_entry['password_saved'] = False
        
        self.connections[connection_id] = connection_entry
        self._save_connections()
        
        return connection_id

    def get_connections_by_type(self, db_type: str) -> List[Dict[str, Any]]:
        """Get all saved connections for a specific database type"""
        connections = []
        for conn_id, conn_data in self.connections.items():
            if conn_data.get('type', '').lower() == db_type.lower():
                safe_conn = conn_data.copy()
                if 'password' in safe_conn:
                    safe_conn.pop('password')
                connections.append(safe_conn)
        
        connections.sort(key=lambda x: x.get('last_used', ''), reverse=True)
        return connections

    def get_connection(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific connection by ID"""
        return self.connections.get(connection_id)

    def update_last_used(self, connection_id: str):
        """Update the last used timestamp for a connection"""
        if connection_id in self.connections:
            self.connections[connection_id]['last_used'] = datetime.now().isoformat()
            self.connections[connection_id]['use_count'] = self.connections[connection_id].get('use_count', 0) + 1
            self._save_connections()

    def delete_connection(self, connection_id: str) -> bool:
        """Delete a saved connection"""
        if connection_id in self.connections:
            del self.connections[connection_id]
            self._save_connections()
            return True
        return False

    def rename_connection(self, connection_id: str, new_name: str) -> bool:
        """Rename a saved connection"""
        if connection_id in self.connections:
            self.connections[connection_id]['name'] = new_name
            self._save_connections()
            return True
        return False

    def get_connection_config(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get connection configuration for database connection"""
        conn_data = self.get_connection(connection_id)
        if not conn_data:
            return None
        
        config = {
            'type': conn_data.get('type'),
            'database': conn_data.get('database')
        }
        
        if conn_data.get('type', '').lower() != 'sqlite':
            config.update({
                'host': conn_data.get('host'),
                'port': conn_data.get('port'),
                'username': conn_data.get('username')
            })
            
            if conn_data.get('password_saved') and conn_data.get('password'):
                config['password'] = conn_data.get('password')
        
        return config
