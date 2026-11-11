"""Quickstart demonstration of NEXORA Control agentic guardrails."""

from nexora import (
    NexoraSentinel,
    ExecutionLoopError,
    BudgetExceededError,
    IdempotencyViolationError,
)

# Initialize Sentinel with a 3-repeat loop limit and $2.00 session budget cap
sentinel = NexoraSentinel(loop_threshold=3, default_session_cap=2.00)


@sentinel.tool(name="search_docs", estimated_cost=0.25)
def search_docs(query: str):
    return f"Results for '{query}'"


@sentinel.tool(
    name="execute_transfer",
    estimated_cost=0.50,
    is_side_effect=True,
    idempotency_key_param="transfer_id",
)
def execute_transfer(transfer_id: str, amount: float):
    return f"Transferred ${amount:.2f} (ID: {transfer_id})"


if __name__ == "__main__":
    print("--- 1. Standard Tool Execution ---")
    print(search_docs("NEXORA architecture", _nexora_session_id="demo_1"))

    print("\n--- 2. Idempotency Protection ---")
    print(execute_transfer("tx_1001", 75.00, _nexora_session_id="demo_1"))
    try:
        execute_transfer("tx_1001", 75.00, _nexora_session_id="demo_1")
    except IdempotencyViolationError as e:
        print(f"Caught duplicate side-effect: {e}")

    print("\n--- 3. Infinite Loop Interception ---")
    try:
        for attempt in range(1, 6):
            print(f"Loop attempt {attempt}...")
            search_docs("stuck_query", _nexora_session_id="loop_demo")
    except ExecutionLoopError as e:
        print(f"Caught infinite loop: {e}")

    print("\n--- 4. Budget Circuit Breaker ---")
    try:
        for i in range(1, 10):
            search_docs(f"unique_query_{i}", _nexora_session_id="budget_demo")
    except BudgetExceededError as e:
        print(f"Caught budget breach: {e}")
