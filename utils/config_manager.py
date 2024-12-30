from typing import Set, Any, Dict
from dotenv import load_dotenv
import os
import threading
import time
import ipaddress

class ConfigManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.last_load_time = 0
            self.config: Dict[str, Any] = {}
            self.load_config()
            
            if self.get_bool('RELOAD_ENV'):
                self._start_reload_thread()

    def load_config(self) -> None:
        """Load or reload configuration from .env file"""
        load_dotenv(override=True)
        
        self.config = {
            'HOST': os.getenv('HOST', '0.0.0.0'),
            'PORT': int(os.getenv('PORT', '5000')),
            'DEBUG': os.getenv('DEBUG', 'false').lower() == 'true',
            'RELOAD_ENV': os.getenv('RELOAD_ENV', 'true').lower() == 'true',
            'AUTH_TOKEN': os.getenv('AUTH_TOKEN'),
            'ALLOWED_IPS': self._parse_allowed_ips(),
            'LOCAL_ONLY': os.getenv('LOCAL_ONLY', 'true').lower() == 'true',
            'MAX_SESSIONS': int(os.getenv('MAX_SESSIONS', '100')),
            'SESSION_TIMEOUT_MINUTES': int(os.getenv('SESSION_TIMEOUT_MINUTES', '30')),
            'CLEANUP_INTERVAL_MINUTES': int(os.getenv('CLEANUP_INTERVAL_MINUTES', '5')),
            # Model specific configs
            'GROK_BEARER_TOKEN': os.getenv('GROK_BEARER_TOKEN'),
            'GROK_CSRF_TOKEN': os.getenv('GROK_CSRF_TOKEN'),
            'GROK_COOKIES': os.getenv('GROK_COOKIES'),
        }
        self.last_load_time = time.time()

    def _parse_allowed_ips(self) -> Set[str]:
        """Parse allowed IPs from environment"""
        allowed_ips = set()
        ips = os.getenv('ALLOWED_IPS', '127.0.0.1,::1').split(',')
        
        for ip in ips:
            ip = ip.strip()
            try:
                ipaddress.ip_address(ip)
                allowed_ips.add(ip)
            except ValueError:
                print(f"Invalid IP address in config: {ip}")
                
        return allowed_ips

    def _start_reload_thread(self) -> None:
        """Start thread for periodic config reloading"""
        def reload_loop():
            while True:
                time.sleep(60)
                try:
                    if os.path.getmtime('.env') > self.last_load_time:
                        self.load_config()
                except Exception as e:
                    print(f"Error reloading config: {e}")

        thread = threading.Thread(target=reload_loop, daemon=True)
        thread.start()

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by key"""
        return self.config.get(key, default)

    def get_bool(self, key: str) -> bool:
        """Get boolean config value"""
        return self.config.get(key, False)

config_manager = ConfigManager()
