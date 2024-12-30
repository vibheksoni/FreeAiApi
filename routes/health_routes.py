from flask import Blueprint, jsonify
from typing import Dict, Any, Tuple

health_bp = Blueprint('health', __name__)

@health_bp.route('/', methods=['GET'])
def health_check() -> Tuple[Dict[str, Any], int]:
    """
    Basic health check endpoint
    Returns:
        Tuple[Dict, int]: Health status and HTTP code
    """
    return {
        "status": True,
        "message": "API is running",
        "data": {"service": "healthy"}
    }, 200
