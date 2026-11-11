"""Core Sentinel Decorator and Execution Manager."""

import hashlib
import inspect
import json
import time
from typing import Callable, Any, Dict, Optional
from nexora.exceptions import (
    ExecutionLoopError,
    BudgetExceededError,
    IdempotencyViolationError,
)


class NexoraSentinel:
    def __init__(self, loop_threshold: int = 3, default_session_cap: float = 10.00):
        self.loop_threshold = loop_threshold
        self.default_session_cap = default_session_cap
        
        # State tracking in-memory (swappable with Redis for distributed nodes)
        self._tool_history: Dict[str, list] = {}
        self._session_spend: Dict[str, float] = {}
        self._executed_idempotency_keys: set = set()

    def _hash_state(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Computes a deterministic hash of tool arguments to detect identical state loops."""
        clean_kwargs = {k: v for k, v in kwargs.items() if not k.startswith("_nexora_")}
        payload = json.dumps({"func": func_name, "args": args, "kwargs": clean_kwargs}, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def tool(
        self,
        name: Optional[str] = None,
        estimated_cost: float = 0.00,
        is_side_effect: bool = False,
        idempotency_key_param: Optional[str] = None,
    ):
        def decorator(func: Callable) -> Callable:
            tool_name = name or func.__name__
            sig = inspect.signature(func)

            def wrapper(*args, **kwargs) -> Any:
                session_id = kwargs.pop("_nexora_session_id", "default_session")

                # Bind positional and keyword arguments into one lookup dictionary
                bound_args = sig.bind_partial(*args, **kwargs)
                bound_args.apply_defaults()
                all_args = bound_args.arguments

                # 1. Budget Circuit Breaker Check
                current_spend = self._session_spend.get(session_id, 0.0)
                if current_spend + estimated_cost > self.default_session_cap:
                    raise BudgetExceededError(
                        f"Action '{tool_name}' (Est: ${estimated_cost:.4f}) exceeds session budget cap "
                        f"(${self.default_session_cap:.2f}). Current spend: ${current_spend:.4f}."
                    )

                # 2. Idempotency Check for Side-Effect Tools
                idem_key = None
                if is_side_effect and idempotency_key_param:
                    idem_key = all_args.get(idempotency_key_param)
                    if not idem_key:
                        raise IdempotencyViolationError(
                            f"Side-effect tool '{tool_name}' requires parameter '{idempotency_key_param}'."
                        )
                    if idem_key in self._executed_idempotency_keys:
                        raise IdempotencyViolationError(
                            f"Blocked duplicate execution of side-effect tool '{tool_name}' "
                            f"with idempotency key: {idem_key}."
                        )

                # 3. State Hash & Infinite Loop Interception
                state_hash = self._hash_state(tool_name, args, kwargs)
                history = self._tool_history.setdefault(session_id, [])
                
                # Check how many times this exact state was called sequentially
                consecutive_repeat_count = 0
                for prev_hash in reversed(history):
                    if prev_hash == state_hash:
                        consecutive_repeat_count += 1
                    else:
                        break

                if consecutive_repeat_count >= self.loop_threshold:
                    raise ExecutionLoopError(
                        f"NEXORA Intercepted Infinite Loop! Tool '{tool_name}' attempted identical state "
                        f"{consecutive_repeat_count + 1} times consecutively."
                    )

                # Execute original function
                start_time = time.perf_counter()
                result = func(*args, **kwargs)
                latency_ms = (time.perf_counter() - start_time) * 1000

                # Record state and spend post-success
                history.append(state_hash)
                self._session_spend[session_id] = current_spend + estimated_cost
                if is_side_effect and idempotency_key_param and idem_key:
                    self._executed_idempotency_keys.add(idem_key)

                return result

            return wrapper
        return decorator
