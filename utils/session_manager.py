from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
import uuid
import threading
import time
from utils.config_manager import config_manager

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._start_cleanup_thread()
        self.session_stats = {
            "created_total": 0,
            "expired_total": 0,
            "cleared_total": 0
        }
        
    def create_session(self, model_type: str) -> Optional[str]:
        """Creates new session if under limit"""
        with self._lock:
            if len(self.sessions) >= config_manager.get('MAX_SESSIONS'):
                return None
                
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = {
                "model_type": model_type,
                "created_at": datetime.now(),
                "last_accessed": datetime.now(),
                "conversation": [],
                "client": None,
                "session_id": session_id
            }
            self.session_stats["created_total"] += 1
            return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session if exists and not expired"""
        with self._lock:
            session = self.sessions.get(session_id)
            if not session:
                return None
                
            timeout = timedelta(minutes=config_manager.get('SESSION_TIMEOUT_MINUTES'))
            if datetime.now() - session["last_accessed"] > timeout:
                del self.sessions[session_id]
                return None
                
            session["last_accessed"] = datetime.now()
            return session

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get info for all active sessions"""
        with self._lock:
            return [{
                "session_id": sid,
                "model_type": session["model_type"],
                "created_at": session["created_at"].isoformat(),
                "last_accessed": session["last_accessed"].isoformat(),
                "conversation_length": len(session.get("conversation", []))
            } for sid, session in self.sessions.items()]

    def clear_all_sessions(self) -> int:
        """Clear all active sessions and return count of cleared sessions"""
        with self._lock:
            count = len(self.sessions)
            self.sessions.clear()
            self.session_stats["cleared_total"] += count
            return count

    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        with self._lock:
            return {
                **self.session_stats,
                "active_count": len(self.sessions),
                "active_by_model": self._get_model_distribution()
            }

    def _get_model_distribution(self) -> Dict[str, int]:
        """Get count of active sessions by model type"""
        distribution = {}
        for session in self.sessions.values():
            model = session["model_type"]
            distribution[model] = distribution.get(model, 0) + 1
        return distribution

    def _start_cleanup_thread(self) -> None:
        """Start thread for periodic session cleanup"""
        def cleanup_loop():
            while True:
                time.sleep(config_manager.get('CLEANUP_INTERVAL_MINUTES') * 60)
                self._cleanup_expired_sessions()

        thread = threading.Thread(target=cleanup_loop, daemon=True)
        thread.start()

    def _cleanup_expired_sessions(self) -> None:
        """Remove expired sessions"""
        with self._lock:
            now = datetime.now()
            timeout = timedelta(minutes=config_manager.get('SESSION_TIMEOUT_MINUTES'))
            expired = [
                sid for sid, session in self.sessions.items()
                if now - session["last_accessed"] > timeout
            ]
            for sid in expired:
                del self.sessions[sid]
                self.session_stats["expired_total"] += 1

session_manager = SessionManager()
