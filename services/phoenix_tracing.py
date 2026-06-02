import os
import socket
from contextlib import contextmanager
from urllib.parse import urlparse
from typing import Any, Dict, Iterator, Optional

from config import PHOENIX_COLLECTOR_ENDPOINT, PHOENIX_ENABLED, PHOENIX_PROJECT_NAME


class PhoenixTracing:
    _initialized = False
    _error: Optional[str] = None

    def setup(self) -> Dict[str, Any]:
        if not PHOENIX_ENABLED:
            self.__class__._error = "Phoenix tracing is disabled. Set PHOENIX_ENABLED=true to enable it."
            return self.status()
        if not self._collector_reachable():
            self.__class__._error = f"Phoenix collector is not reachable at {PHOENIX_COLLECTOR_ENDPOINT}. Run `phoenix serve` first."
            return self.status()
        if self._initialized:
            return self.status()
        try:
            from openinference.instrumentation.langchain import LangChainInstrumentor
            from openinference.instrumentation.openai import OpenAIInstrumentor
            from phoenix.otel import register

            tracer_provider = register(
                project_name=PHOENIX_PROJECT_NAME,
                endpoint=PHOENIX_COLLECTOR_ENDPOINT,
            )
            LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
            OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
            self.__class__._initialized = True
            self.__class__._error = None
        except Exception as exc:
            self.__class__._error = str(exc)
        return self.status()

    def status(self) -> Dict[str, Any]:
        available = self._packages_available() if PHOENIX_ENABLED else False
        return {
            "available": available,
            "enabled": PHOENIX_ENABLED,
            "initialized": self._initialized,
            "project_name": PHOENIX_PROJECT_NAME,
            "endpoint": PHOENIX_COLLECTOR_ENDPOINT,
            "error": self._error,
            "ui": os.getenv("PHOENIX_UI_URL", "http://localhost:6006"),
        }

    @contextmanager
    def span(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> Iterator[None]:
        if not self._initialized:
            yield
            return
        try:
            from opentelemetry import trace

            tracer = trace.get_tracer("resume-rag-system")
            with tracer.start_as_current_span(name) as active_span:
                for key, value in (attributes or {}).items():
                    if value is not None:
                        active_span.set_attribute(key, str(value))
                yield
        except Exception:
            yield

    def _packages_available(self) -> bool:
        try:
            import openinference.instrumentation.langchain  # noqa: F401
            import phoenix.otel  # noqa: F401
            return True
        except Exception:
            return False

    def _collector_reachable(self) -> bool:
        parsed = urlparse(PHOENIX_COLLECTOR_ENDPOINT)
        host = parsed.hostname or "localhost"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return True
        except OSError:
            return False
