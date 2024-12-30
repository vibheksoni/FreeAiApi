from flask import request, abort
from functools import wraps
import os
from typing import Callable, Any
from utils.config_manager import config_manager
import ipaddress

def auth_middleware() -> None:
    """Validate authentication and IP restrictions"""
    auth_token = request.headers.get('X-Auth-Token')
    if not auth_token or auth_token != config_manager.get('AUTH_TOKEN'):
        abort(401, description="Invalid or missing authentication token")
    
    client_ip = request.remote_addr
    if config_manager.get_bool('LOCAL_ONLY'):
        if not _is_local_ip(client_ip):
            abort(403, description="Access restricted to local addresses")
    elif client_ip not in config_manager.get('ALLOWED_IPS'):
        abort(403, description="IP address not allowed")

def _is_local_ip(ip: str) -> bool:
    """Check if IP is local"""
    try:
        ip_obj = ipaddress.ip_address(ip)
        return (
            ip_obj.is_loopback or
            ip_obj.is_private or
            ip_obj.is_link_local
        )
    except ValueError:
        return False
