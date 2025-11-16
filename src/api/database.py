from supabase import create_client, Client
from .config import settings
import hashlib
import secrets
from typing import Optional, Dict, Any


class Database:
    """Supabase database client wrapper."""
    
    def __init__(self):
        self.client: Client = create_client(settings.supabase_url, settings.supabase_key)
    
    def get_or_create_user(self, email: str) -> Dict[str, Any]:
        """Get existing user or create a new one."""
        # Try to get existing user
        result = self.client.table("users").select("*").eq("email", email).execute()
        
        if result.data:
            return result.data[0]
        
        # Create new user
        result = self.client.table("users").insert({"email": email}).execute()
        return result.data[0]
    
    def create_api_key(self, user_id: str) -> tuple[str, str]:
        """Create a new API key for a user. Returns (api_key, key_hash)."""
        # Generate API key
        api_key = f"ctx_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        key_prefix = api_key[:12]  # First 12 chars for display
        
        # Store in database
        self.client.table("api_keys").insert({
            "user_id": user_id,
            "key_hash": key_hash,
            "key_prefix": key_prefix
        }).execute()
        
        return api_key, key_hash
    
    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Verify an API key and return user info if valid."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        result = self.client.table("api_keys").select("*, users(*)").eq("key_hash", key_hash).execute()
        
        if result.data:
            api_key_data = result.data[0]
            return {
                "user_id": api_key_data["user_id"],
                "email": api_key_data["users"]["email"]
            }
        
        return None
    
    def store_trace_metadata(self, user_id: str, trace_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Store trace metadata in Supabase."""
        result = self.client.table("trace_metadata").insert({
            "user_id": user_id,
            "trace_id": trace_id,
            "provider": metadata.get("provider"),
            "model": metadata.get("model"),
            "success": metadata.get("success", True),
            "tokens_used": metadata.get("tokens_used"),
            "latency_ms": metadata.get("latency_ms")
        }).execute()
        
        return result.data[0] if result.data else {}


db = Database()

