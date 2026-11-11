# NEXORA Control (`nexora-control`)

> **Active Inline State Control & Reliability Runtime for Autonomous AI Agents**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-green.svg)](https://www.python.org/)

NEXORA Control provides active execution guardrails for AI agents, multi-agent frameworks, and autonomous LLM workflows. Unlike passive observability dashboards that log failures after money is spent, NEXORA intercepts execution in real-time.

## Key Features

- **Infinite-Loop Interception**: Uses argument-state hashing to halt runaway agent loops before API credits are burned.
- **Budget Circuit Breakers**: Enforces pre-allocation spending caps per tool call and session.
- **Idempotency Protection**: Prevents duplicate real-world side effects (DB writes, payment executions, RFQ submissions).
- **Sub-2ms Overhead**: Local SDK execution ensures zero latency penalty on model calls.

## Quickstart

```bash
pip install nexora-control
