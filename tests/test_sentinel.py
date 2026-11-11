"""Unit tests for NEXORA Sentinel execution guardrails."""

import pytest
from nexora import (
    NexoraSentinel,
    ExecutionLoopError,
    BudgetExceededError,
    IdempotencyViolationError,
)


def test_infinite_loop_interception():
    sentinel = NexoraSentinel(loop_threshold=3)

    @sentinel.tool(name="query_db")
    def query_db(prompt: str):
        return f"Data for {prompt}"

    # First 3 identical calls succeed
    for _ in range(3):
        assert query_db("select_all", _nexora_session_id="s1") == "Data for select_all"

    # 4th identical call triggers loop interception
    with pytest.raises(ExecutionLoopError) as exc_info:
        query_db("select_all", _nexora_session_id="s1")
    assert "Intercepted Infinite Loop" in str(exc_info.value)


def test_budget_circuit_breaker():
    sentinel = NexoraSentinel(default_session_cap=1.00)

    @sentinel.tool(name="expensive_call", estimated_cost=0.40)
    def expensive_call():
        return "OK"

    # First two calls cost $0.80 total (under $1.00 cap)
    assert expensive_call(_nexora_session_id="s2") == "OK"
    assert expensive_call(_nexora_session_id="s2") == "OK"

    # 3rd call brings total to $1.20 and gets blocked
    with pytest.raises(BudgetExceededError) as exc_info:
        expensive_call(_nexora_session_id="s2")
    assert "exceeds session budget cap" in str(exc_info.value)


def test_idempotency_protection():
    sentinel = NexoraSentinel()

    @sentinel.tool(name="process_payment", is_side_effect=True, idempotency_key_param="tx_id")
    def process_payment(tx_id: str, amount: float):
        return f"Processed {tx_id}"

    # Initial call succeeds
    assert process_payment("tx_999", 50.00) == "Processed tx_999"

    # Duplicate call with same key is blocked
    with pytest.raises(IdempotencyViolationError) as exc_info:
        process_payment("tx_999", 50.00)
    assert "Blocked duplicate execution" in str(exc_info.value)
