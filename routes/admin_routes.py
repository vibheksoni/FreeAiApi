from flask import Blueprint, jsonify
from typing import Dict, Any, Tuple
from utils.session_manager import session_manager

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/sessions', methods=['GET'])
def get_sessions() -> Tuple[Dict[str, Any], int]:
    """Get all active sessions info"""
    sessions = session_manager.get_all_sessions()
    return {
        "status": True,
        "message": "Active sessions retrieved",
        "data": {
            "count": len(sessions),
            "sessions": sessions
        }
    }, 200

@admin_bp.route('/sessions/clear', methods=['POST'])
def clear_sessions() -> Tuple[Dict[str, Any], int]:
    """Clear all active sessions"""
    count = session_manager.clear_all_sessions()
    return {
        "status": True,
        "message": "All sessions cleared",
        "data": {
            "cleared_count": count
        }
    }, 200

@admin_bp.route('/sessions/stats', methods=['GET'])
def session_stats() -> Tuple[Dict[str, Any], int]:
    """Get session statistics"""
    stats = session_manager.get_session_stats()
    return {
        "status": True,
        "message": "Session statistics retrieved",
        "data": stats
    }, 200
