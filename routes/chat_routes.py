from flask import Blueprint, request, jsonify
from typing import Dict, Any, Tuple
from models.chat_handler import handle_chat_request
from utils.session_manager import session_manager
from werkzeug.utils import secure_filename
import tempfile
import os
import logging
import base64

chat_bp = Blueprint('chat', __name__)

def handle_file_uploads() -> list[str]:
    """Handle file uploads and return temporary file paths"""
    temp_files = []
    if request.files:
        for file in request.files.getlist('files'):
            if file.filename:
                suffix = os.path.splitext(secure_filename(file.filename))[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
                    file.save(temp.name)
                    temp_files.append(temp.name)
    return temp_files

def handle_base64_files(files_data: list) -> list[str]:
    """
    Convert base64 encoded files to temporary files
    
    Args:
        files_data: List of dicts containing base64 data and filename
    Returns:
        List of temporary file paths
    """
    temp_files = []
    try:
        for file_data in files_data or []:
            if file_data.get('base64') and file_data.get('filename'):
                suffix = os.path.splitext(secure_filename(file_data['filename']))[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
                    file_content = base64.b64decode(file_data['base64'])
                    temp.write(file_content)
                    temp_files.append(temp.name)
    except Exception as e:
        logging.error(f"Error processing base64 files: {str(e)}")
    return temp_files

@chat_bp.route('/send', methods=['POST'])
def send_message() -> Tuple[Dict[str, Any], int]:
    """
    Handles chat message requests.
    
    Expected JSON body:
    {
        "model": "gpt|grok",
        "message": "string",
        "session_id": "string" (optional),
        "files": [
            {
                "filename": "image.jpg",
                "base64": "base64_encoded_content"
            }
        ] (optional, Grok only)
    }
    
    Returns:
        Tuple[Dict, int]: Response data and status code
    """
    try:
        data = request.get_json()
        model = data.get('model')
        message = data.get('message')
        session_id = data.get('session_id')
        files_data = data.get('files', [])

        if not model or not message:
            return {
                "status": False,
                "message": "Missing required fields",
                "data": None
            }, 400

        temp_files = []
        try:
            if model == "grok":
                temp_files = handle_base64_files(files_data)

            if not session_id:
                session_id = session_manager.create_session(model)
            
            response = handle_chat_request(model, message, session_id, temp_files)
            return response, 200
        finally:
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass

    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        return {
            "status": False,
            "message": "Internal server error",
            "data": None
        }, 500
