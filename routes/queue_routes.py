from flask import Blueprint, request, jsonify
from typing import Dict, Any, Tuple
from utils.queue_manager import queue_manager
import logging

queue_bp = Blueprint('queue', __name__)

@queue_bp.route('/submit', methods=['POST'])
def submit_task() -> Tuple[Dict[str, Any], int]:
    """Submit new task to queue"""
    try:
        data = request.get_json()
        model = data.get('model')
        message = data.get('message')
        session_id = data.get('session_id')
        files = data.get('files', [])

        if not model or not message:
            return {
                "status": False,
                "message": "Missing required fields",
                "data": None
            }, 400

        transaction_id = queue_manager.add_task(model, message, session_id, files)
        
        return {
            "status": True,
            "message": "Task queued successfully",
            "data": {
                "transaction_id": transaction_id
            }
        }, 200

    except Exception as e:
        logging.error(f"Error in queue submit: {str(e)}")
        return {
            "status": False,
            "message": "Internal server error",
            "data": None
        }, 500

@queue_bp.route('/status/<transaction_id>', methods=['GET'])
def get_task_status(transaction_id: str) -> Tuple[Dict[str, Any], int]:
    """Get status of queued task"""
    try:
        task_info = queue_manager.get_task_status(transaction_id)
        if not task_info:
            return {
                "status": False,
                "message": "Task not found",
                "data": None
            }, 404
            
        return {
            "status": True,
            "message": "Task status retrieved",
            "data": task_info
        }, 200

    except Exception as e:
        logging.error(f"Error in queue status: {str(e)}")
        return {
            "status": False,
            "message": "Internal server error",
            "data": None
        }, 500
