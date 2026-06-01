import json
import time
import tracemalloc
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from config import MONITORING_EVENTS_PATH
from services.phoenix_tracing import PhoenixTracing
from utils.file_utils import ensure_dir


class PipelineMonitor:
    def __init__(self, events_path: Path = MONITORING_EVENTS_PATH):
        self.events_path = events_path
        self.phoenix = PhoenixTracing()

    @contextmanager
    def track(self, event_type: str, **metadata: Any) -> Iterator[Dict[str, Any]]:
        event: Dict[str, Any] = {
            "event_type": event_type,
            "status": "ok",
            "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            **metadata,
        }
        tracemalloc.start()
        wall_start = time.perf_counter()
        cpu_start = time.process_time()
        try:
            with self.phoenix.span(event_type, metadata):
                yield event
        except Exception as exc:
            event["status"] = "failed"
            event["error"] = str(exc)
            raise
        finally:
            _, peak_bytes = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            event["wall_seconds"] = round(time.perf_counter() - wall_start, 4)
            event["cpu_seconds"] = round(time.process_time() - cpu_start, 4)
            event["peak_memory_mb"] = round(peak_bytes / (1024 * 1024), 3)
            self.write(event)

    def write(self, event: Dict[str, Any]) -> None:
        ensure_dir(self.events_path.parent)
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    def read_events(self, limit: Optional[int] = 200) -> List[Dict[str, Any]]:
        if not self.events_path.exists():
            return []
        lines = self.events_path.read_text(encoding="utf-8").splitlines()
        if limit is not None:
            lines = lines[-limit:]
        events = []
        for line in lines:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return events

    def clear(self) -> None:
        ensure_dir(self.events_path.parent)
        self.events_path.write_text("", encoding="utf-8")
