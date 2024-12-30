from typing import Dict, Any, Optional, List
from gpt import ChatGPTClient
from grok import Grok, GrokMessages
import os
import logging
from utils.session_manager import session_manager

class ModelHandler:
    """Handles chat interactions with different AI models"""
    
    def __init__(self) -> None:
        self.grok_client = None
        self.gpt_client = None
        
    def get_grok_client(self) -> Grok:
        """Initialize Grok client if not exists"""
        if not self.grok_client:
            self.grok_client = Grok(
                account_bearer_token=os.getenv('GROK_BEARER_TOKEN'),
                x_csrf_token=os.getenv('GROK_CSRF_TOKEN'),
                cookies=os.getenv('GROK_COOKIES')
            )
            self.grok_client.create_conversation()
        return self.grok_client
        
    def get_gpt_client(self) -> ChatGPTClient:
        """Initialize ChatGPT client if not exists"""
        if not self.gpt_client:
            self.gpt_client = ChatGPTClient()
        return self.gpt_client

def handle_chat_request(model: str, message: str, session_id: str, files: List[str] = None) -> Dict[str, Any]:
    """
    Handle chat requests for different models
    
    Args:
        model: Model type ('gpt' or 'grok')
        message: User message
        session_id: Session identifier
        files: List of temporary file paths (for Grok only)
    
    Returns:
        Dict containing status, message and response data
    """
    try:
        session = session_manager.get_session(session_id)
        if not session:
            return {
                "status": False,
                "message": "Session expired or invalid",
                "data": None
            }

        if model == "grok":
            return handle_grok_chat(message, session, files)
        elif model == "gpt":
            return handle_gpt_chat(message, session)
        else:
            return {
                "status": False,
                "message": f"Unsupported model: {model}",
                "data": None
            }

    except Exception as e:
        logging.error(f"Chat handling error: {str(e)}")
        return {
            "status": False,
            "message": f"Error processing chat: {str(e)}",
            "data": None
        }

def handle_grok_chat(message: str, session: Dict[str, Any], files: List[str] = None) -> Dict[str, Any]:
    """Handle Grok model chat with optional file attachments"""
    try:
        client = session.get("client")
        if not client:
            client = ModelHandler().get_grok_client()
            session["client"] = client
            session["conversation"] = []

        msg_data = client.create_message("grok-2")
        
        session["conversation"].append({"role": "user", "content": message})
        
        file_attachments = []
        if files:
            for file_path in files:
                try:
                    response = client.upload_file(file_path)
                    if response and response[0]:
                        file_attachments.append(response[0])
                except Exception as e:
                    logging.error(f"Failed to upload file {file_path}: {str(e)}")

        client.add_user_message(msg_data, message, file_attachments=file_attachments)
        
        response = client.send(msg_data)
        response_message = GrokMessages(response)

        if response_message.get_full_message():
            session["conversation"].append({
                "role": "assistant", 
                "content": response_message.get_full_message()
            })

        return {
            "status": True,
            "message": "Success",
            "data": {
                "response": response_message.get_full_message(),
                "session_id": session["session_id"],
                "attachments": file_attachments
            }
        }

    except Exception as e:
        logging.error(f"Grok chat error: {str(e)}")
        return {
            "status": False,
            "message": str(e),
            "data": None
        }

def handle_gpt_chat(message: str, session: Dict[str, Any]) -> Dict[str, Any]:
    """Handle ChatGPT model chat"""
    try:
        client = session.get("client")
        if not client:
            client = ModelHandler().get_gpt_client()
            session["client"] = client
            session["conversation"] = []
        
        session["conversation"].append({"role": "user", "content": message})
        
        success = client.send_message(message)
        if not success:
            raise Exception("Failed to get response from ChatGPT")

        messages = client.get_messages()
        if not messages:
            raise Exception("No response received")

        if messages and messages[-1].content:
            session["conversation"].append({
                "role": "assistant",
                "content": messages[-1].content
            })

        return {
            "status": True,
            "message": "Success",
            "data": {
                "response": messages[-1].content,
                "session_id": session["session_id"]
            }
        }

    except Exception as e:
        logging.error(f"GPT chat error: {str(e)}")
        return {
            "status": False,
            "message": str(e),
            "data": None
        }
