"""Custom exceptions for NEXORA Control execution guardrails."""


class NexoraError(Exception):
    """Base exception for NEXORA Control errors."""
    pass


class ExecutionLoopError(NexoraError):
    """Raised when an agent enters an unrecoverable infinite loop."""
    pass


class BudgetExceededError(NexoraError):
    """Raised when an agent call or session exceeds pre-allocated budget limits."""
    pass


class IdempotencyViolationError(NexoraError):
    """Raised when a side-effect tool is called repeatedly with an identical key."""
    pass
