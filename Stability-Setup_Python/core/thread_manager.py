"""
Thread Management Module

Provides safe and efficient thread management for Arduino operations and data processing.
Replaces manual thread handling with a proper abstraction layer.
"""
import threading
import time
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any, Optional, Dict, List
from dataclasses import dataclass
from enum import Enum
from PySide6.QtCore import QObject, Signal, QTimer
from helper.global_helpers import get_logger
from core.error_handler import get_error_handler


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskInfo:
    """Information about a running task."""
    task_id: str
    name: str
    status: TaskStatus
    future: Optional[Future] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    result: Any = None
    error: Optional[Exception] = None

    @property
    def duration(self) -> Optional[float]:
        """Get task duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    @property
    def is_running(self) -> bool:
        """Check if task is currently running."""
        return self.status == TaskStatus.RUNNING


class ThreadManager(QObject):
    """
    Thread manager for safe and efficient thread operations.

    Provides a high-level interface for managing background tasks
    with proper error handling and resource cleanup.
    """

    task_started = Signal(str)  # task_id
    task_completed = Signal(str, object)  # task_id, result
    task_failed = Signal(str, Exception)  # task_id, error
    task_cancelled = Signal(str)  # task_id

    def __init__(self, max_workers: int = 4):
        super().__init__()
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, TaskInfo] = {}
        self.task_counter = 0
        self.shutdown_requested = False

        # Monitor timer for task status updates
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._monitor_tasks)
        self.monitor_timer.start(100)  # Check every 100ms

    def submit_task(self,
                   func: Callable,
                   *args,
                   task_name: str = "",
                   task_id: str = "",
                   **kwargs) -> str:
        """
        Submit a task for background execution.

        Args:
            func: Function to execute
            *args: Function arguments
            task_name: Human-readable task name
            task_id: Optional custom task ID
            **kwargs: Function keyword arguments

        Returns:
            Task ID for tracking
        """
        if self.shutdown_requested:
            raise RuntimeError("ThreadManager is shutting down")

        # Generate task ID if not provided
        if not task_id:
            self.task_counter += 1
            task_id = f"task_{self.task_counter}"

        if not task_name:
            task_name = func.__name__

        # Create task info
        task_info = TaskInfo(
            task_id=task_id,
            name=task_name,
            status=TaskStatus.PENDING
        )

        # Submit to executor
        try:
            future = self.executor.submit(self._execute_task, task_info, func, *args, **kwargs)
            task_info.future = future
            self.tasks[task_id] = task_info

            get_logger().log(f"Task submitted: {task_name} (ID: {task_id})")
            return task_id

        except Exception as e:
            get_error_handler().handle_exception(e, f"Failed to submit task: {task_name}")
            raise

    def _execute_task(self, task_info: TaskInfo, func: Callable, *args, **kwargs) -> Any:
        """Execute a task with proper error handling and status tracking."""
        task_info.status = TaskStatus.RUNNING
        task_info.start_time = time.time()

        try:
            get_logger().log(f"Task started: {task_info.name} (ID: {task_info.task_id})")
            self.task_started.emit(task_info.task_id)

            # Execute the function
            result = func(*args, **kwargs)

            # Update task info
            task_info.status = TaskStatus.COMPLETED
            task_info.end_time = time.time()
            task_info.result = result

            get_logger().log(f"Task completed: {task_info.name} (ID: {task_info.task_id}, "
                           f"Duration: {task_info.duration:.2f}s)")

            return result

        except Exception as e:
            task_info.status = TaskStatus.FAILED
            task_info.end_time = time.time()
            task_info.error = e

            get_error_handler().handle_exception(e, f"Task failed: {task_info.name}")
            raise

    def _monitor_tasks(self) -> None:
        """Monitor task status and emit signals for completed/failed tasks.
        Runs based on time based Qtimer
        Iterates through list of tasks and handles cleanup when they are completed"""
        completed_tasks = []

        for task_id, task_info in self.tasks.items():
            if not task_info.future:
                continue

            if task_info.future.done():
                try:
                    if task_info.status == TaskStatus.COMPLETED:
                        self.task_completed.emit(task_id, task_info.result)
                    elif task_info.status == TaskStatus.FAILED:
                        self.task_failed.emit(task_id, task_info.error)
                    elif task_info.future.cancelled():
                        task_info.status = TaskStatus.CANCELLED
                        self.task_cancelled.emit(task_id)

                except Exception as e:
                    get_error_handler().handle_exception(e, "Task monitoring error")

                completed_tasks.append(task_id)

        # Clean up completed tasks
        for task_id in completed_tasks:
            if task_id in self.tasks:
                del self.tasks[task_id]

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task.

        Args:
            task_id: ID of task to cancel

        Returns:
            True if task was cancelled, False otherwise
        """
        if task_id not in self.tasks:
            return False

        task_info = self.tasks[task_id]
        if task_info.future and not task_info.future.done():
            cancelled = task_info.future.cancel()
            if cancelled:
                task_info.status = TaskStatus.CANCELLED
                get_logger().log(f"Task cancelled: {task_info.name} (ID: {task_id})")
            return cancelled

        return False

    def cancel_all_tasks(self) -> int:
        """
        Cancel all running tasks.

        Returns:
            Number of tasks cancelled
        """
        cancelled_count = 0
        task_ids = list(self.tasks.keys())

        for task_id in task_ids:
            if self.cancel_task(task_id):
                cancelled_count += 1

        return cancelled_count

    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """
        Wait for a task to complete and return its result.

        Args:
            task_id: ID of task to wait for
            timeout: Maximum time to wait in seconds

        Returns:
            Task result

        Raises:
            KeyError: If task ID not found
            TimeoutError: If timeout exceeded
            Exception: If task failed
        """
        if task_id not in self.tasks:
            raise KeyError(f"Task not found: {task_id}")

        task_info = self.tasks[task_id]
        if not task_info.future:
            raise RuntimeError(f"Task has no future: {task_id}")

        try:
            return task_info.future.result(timeout=timeout)
        except Exception as e:
            get_error_handler().handle_exception(e, f"Error waiting for task: {task_id}")
            raise

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get status of a task."""
        task_info = self.tasks.get(task_id)
        return task_info.status if task_info else None

    def get_running_tasks(self) -> List[TaskInfo]:
        """Get list of currently running tasks."""
        return [task for task in self.tasks.values() if task.is_running]

    def get_task_count(self) -> int:
        """Get number of active tasks."""
        return len(self.tasks)

    def shutdown(self, wait: bool = True, timeout: float = 30.0) -> None:
        """
        Shutdown the thread manager.

        Args:
            wait: Whether to wait for running tasks to complete
            timeout: Maximum time to wait for shutdown
        """
        self.shutdown_requested = True
        self.monitor_timer.stop()

        get_logger().log("ThreadManager shutting down...")

        if not wait:
            # Cancel all running tasks
            cancelled = self.cancel_all_tasks()
            if cancelled > 0:
                get_logger().log(f"Cancelled {cancelled} running tasks")

        # Shutdown executor
        self.executor.shutdown(wait=wait, timeout=timeout)

        # Clear tasks
        self.tasks.clear()

        get_logger().log("ThreadManager shutdown complete")


# Global thread manager instance
_global_thread_manager: Optional[ThreadManager] = None


def get_thread_manager() -> ThreadManager:
    """Get the global thread manager instance."""
    global _global_thread_manager
    if _global_thread_manager is None:
        _global_thread_manager = ThreadManager()
    return _global_thread_manager


def shutdown_thread_manager() -> None:
    """Shutdown the global thread manager."""
    global _global_thread_manager
    if _global_thread_manager:
        _global_thread_manager.shutdown()
        _global_thread_manager = None
