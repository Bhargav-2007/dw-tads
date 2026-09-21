"""structlog with correlation_id propagation via contextvars."""

import logging
import uuid
import structlog
from contextvars import ContextVar

_cid: ContextVar[str] = ContextVar("correlation_id", default="")


def set_correlation_id(cid: str) -> None:
    """Set the current correlation ID in the context."""
    _cid.set(cid or str(uuid.uuid4()))


def get_correlation_id() -> str:
    """Get the current correlation ID, generating one if not set."""
    cid = _cid.get()
    if not cid:
        cid = str(uuid.uuid4())
        _cid.set(cid)
    return cid


def _add_cid(_, __, event_dict):
    event_dict["correlation_id"] = get_correlation_id()
    return event_dict


def configure_logging(level: str = "INFO", service: str = "unknown") -> None:
    """Configure structlog for JSON output with correlation_id."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            _add_cid,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        cache_logger_on_first_use=True,
    )
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(message)s",
    )


def get_logger(name: str = "dwtds"):
    """Return a structlog logger bound to the given name."""
    return structlog.get_logger(name)
