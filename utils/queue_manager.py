from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import threading
import logging
from queue import Queue
from dataclasses import dataclass, asdict
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class QueueTask:
    transaction_id: str
    model: str
    message: str
    session_id: Optional[str]
    files: list
    status: TaskStatus
    result: Optional[Dict[str, Any]]
    created_at: datetime
    completed_at: Optional[datetime]

class QueueManager:
    def __init__(self, max_queue_size: int = 1000):
        self.tasks: Dict[str, QueueTask] = {}
        self.queue = Queue(maxsize=max_queue_size)
        self._lock = threading.Lock()
        self._start_worker()
    
    def add_task(self, model: str, message: str, session_id: Optional[str] = None, 
                 files: list = None) -> str:
        """Add new task to queue and return transaction ID"""
        transaction_id = str(uuid.uuid4())
        task = QueueTask(
            transaction_id=transaction_id,
            model=model,
            message=message,
            session_id=session_id,
            files=files or [],
            status=TaskStatus.PENDING,
            result=None,
            created_at=datetime.now(),
            completed_at=None
        )
        
        with self._lock:
            self.tasks[transaction_id] = task
            self.queue.put(task)
            
        return transaction_id
    
    def get_task_status(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get task status and result if completed"""
        with self._lock:
            task = self.tasks.get(transaction_id)
            if not task:
                return None
            
            data = asdict(task)
            data['status'] = task.status.value
            return data
            
    def _start_worker(self) -> None:
        """Start background worker thread"""
        def worker():
            while True:
                task: QueueTask = self.queue.get()
                try:
                    with self._lock:
                        task.status = TaskStatus.PROCESSING
                    
                    from models.chat_handler import handle_chat_request
                    result = handle_chat_request(
                        task.model,
                        task.message,
                        task.session_id,
                        task.files
                    )
                    
                    with self._lock:
                        task.status = TaskStatus.COMPLETED if result["status"] else TaskStatus.FAILED
                        task.result = result
                        task.completed_at = datetime.now()
                        
                except Exception as e:
                    logging.error(f"Queue worker error: {str(e)}")
                    with self._lock:
                        task.status = TaskStatus.FAILED
                        task.result = {
                            "status": False,
                            "message": str(e),
                            "data": None
                        }
                        task.completed_at = datetime.now()
                finally:
                    self.queue.task_done()

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

queue_manager = QueueManager()
