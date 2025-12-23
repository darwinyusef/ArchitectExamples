"""
OBSERVABILIDAD - Sistema de métricas para concurrencia
"""

import time
import threading
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import psutil
import os


@dataclass
class Metric:
    """Métrica individual"""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class ExecutionMetrics:
    """Métricas de ejecución"""
    operation: str
    duration: float
    success: bool
    threads_used: int
    processes_used: int
    cpu_percent: float
    memory_mb: float
    timestamp: datetime = field(default_factory=datetime.now)


class MetricsCollector:
    """Recolector de métricas centralizado"""

    def __init__(self):
        self._metrics: List[Metric] = []
        self._executions: List[ExecutionMetrics] = []
        self._counters: Dict[str, int] = defaultdict(int)
        self._lock = threading.Lock()

    def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Registrar una métrica"""
        with self._lock:
            metric = Metric(name=name, value=value, labels=labels or {})
            self._metrics.append(metric)

    def record_execution(
        self,
        operation: str,
        duration: float,
        success: bool = True,
        threads_used: int = 0,
        processes_used: int = 0
    ):
        """Registrar ejecución de operación"""
        with self._lock:
            process = psutil.Process(os.getpid())
            metrics = ExecutionMetrics(
                operation=operation,
                duration=duration,
                success=success,
                threads_used=threads_used,
                processes_used=processes_used,
                cpu_percent=process.cpu_percent(),
                memory_mb=process.memory_info().rss / 1024 / 1024
            )
            self._executions.append(metrics)

    def increment_counter(self, name: str, value: int = 1):
        """Incrementar contador"""
        with self._lock:
            self._counters[name] += value

    def get_metrics_summary(self) -> dict:
        """Obtener resumen de métricas"""
        with self._lock:
            if not self._executions:
                return {"message": "No metrics collected yet"}

            total_executions = len(self._executions)
            successful = sum(1 for e in self._executions if e.success)
            failed = total_executions - successful

            avg_duration = sum(e.duration for e in self._executions) / total_executions
            avg_cpu = sum(e.cpu_percent for e in self._executions) / total_executions
            avg_memory = sum(e.memory_mb for e in self._executions) / total_executions

            operations_count = defaultdict(int)
            for execution in self._executions:
                operations_count[execution.operation] += 1

            return {
                "total_executions": total_executions,
                "successful": successful,
                "failed": failed,
                "success_rate": f"{(successful / total_executions * 100):.2f}%",
                "avg_duration": f"{avg_duration:.3f}s",
                "avg_cpu_percent": f"{avg_cpu:.2f}%",
                "avg_memory_mb": f"{avg_memory:.2f} MB",
                "operations": dict(operations_count),
                "counters": dict(self._counters),
                "latest_executions": [
                    {
                        "operation": e.operation,
                        "duration": f"{e.duration:.3f}s",
                        "cpu": f"{e.cpu_percent:.1f}%",
                        "memory": f"{e.memory_mb:.1f} MB",
                        "threads": e.threads_used,
                        "processes": e.processes_used,
                        "success": e.success
                    }
                    for e in self._executions[-10:]
                ]
            }

    def get_operation_stats(self, operation: str) -> dict:
        """Estadísticas de una operación específica"""
        with self._lock:
            ops = [e for e in self._executions if e.operation == operation]

            if not ops:
                return {"error": f"No data for operation: {operation}"}

            return {
                "operation": operation,
                "total_runs": len(ops),
                "avg_duration": f"{sum(e.duration for e in ops) / len(ops):.3f}s",
                "min_duration": f"{min(e.duration for e in ops):.3f}s",
                "max_duration": f"{max(e.duration for e in ops):.3f}s",
                "avg_cpu": f"{sum(e.cpu_percent for e in ops) / len(ops):.2f}%",
                "avg_memory": f"{sum(e.memory_mb for e in ops) / len(ops):.2f} MB",
                "success_rate": f"{sum(1 for e in ops if e.success) / len(ops) * 100:.2f}%"
            }

    def reset(self):
        """Limpiar todas las métricas"""
        with self._lock:
            self._metrics.clear()
            self._executions.clear()
            self._counters.clear()


class PerformanceMonitor:
    """Monitor de rendimiento para operaciones concurrentes"""

    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.operation_name: Optional[str] = None
        self.start_time: Optional[float] = None
        self.threads_count: int = 0
        self.processes_count: int = 0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        success = exc_type is None

        if self.operation_name:
            self.collector.record_execution(
                operation=self.operation_name,
                duration=duration,
                success=success,
                threads_used=self.threads_count,
                processes_used=self.processes_count
            )

        return False  # No suprimir excepciones

    def set_operation(self, name: str):
        """Establecer nombre de operación"""
        self.operation_name = name
        return self

    def set_threads(self, count: int):
        """Establecer cantidad de threads"""
        self.threads_count = count
        return self

    def set_processes(self, count: int):
        """Establecer cantidad de procesos"""
        self.processes_count = count
        return self


class AsyncPerformanceMonitor:
    """Monitor de rendimiento para operaciones async"""

    def __init__(self, collector: MetricsCollector, operation_name: str):
        self.collector = collector
        self.operation_name = operation_name
        self.start_time: Optional[float] = None

    async def __aenter__(self):
        self.start_time = time.time()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        success = exc_type is None

        self.collector.record_execution(
            operation=self.operation_name,
            duration=duration,
            success=success
        )

        return False


# Instancia global del collector
metrics_collector = MetricsCollector()


def get_system_metrics() -> dict:
    """Obtener métricas del sistema"""
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    process = psutil.Process(os.getpid())

    return {
        "system": {
            "cpu_percent": f"{cpu_percent}%",
            "cpu_count": psutil.cpu_count(),
            "memory_total_mb": f"{memory.total / 1024 / 1024:.2f} MB",
            "memory_available_mb": f"{memory.available / 1024 / 1024:.2f} MB",
            "memory_percent": f"{memory.percent}%"
        },
        "process": {
            "pid": process.pid,
            "cpu_percent": f"{process.cpu_percent()}%",
            "memory_mb": f"{process.memory_info().rss / 1024 / 1024:.2f} MB",
            "threads": process.num_threads(),
            "status": process.status()
        }
    }


def compare_approaches(results: List[Dict]) -> dict:
    """Comparar diferentes enfoques de concurrencia"""
    if not results:
        return {"error": "No results to compare"}

    comparison = []
    fastest = min(results, key=lambda x: x.get("duration", float('inf')))

    for result in results:
        duration = result.get("duration", 0)
        speedup = fastest.get("duration", 1) / duration if duration > 0 else 0

        comparison.append({
            "approach": result.get("approach", "unknown"),
            "duration": f"{duration:.3f}s",
            "speedup": f"{speedup:.2f}x",
            "is_fastest": result == fastest
        })

    return {
        "comparison": comparison,
        "recommendation": fastest.get("approach", "unknown")
    }
