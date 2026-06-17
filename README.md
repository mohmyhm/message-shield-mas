# Message-Level Runtime Detection for Communication Attacks in LLM Multi-Agent Systems

Message Shield MAS is a research prototype for studying **message-level runtime security** in LLM-based multi-agent systems.

The project focuses on a small three-agent workflow:

1. Planner Agent
2. Executor Agent
3. Reviewer Agent

The goal is to test how malicious or manipulated inter-agent messages can affect the workflow, and how a runtime monitor can detect, warn, or block suspicious messages.

## Research Direction

This repository is designed for experiments in:

- Agentic AI security
- Multi-agent LLM communication
- Prompt injection in agent workflows
- Message-level runtime monitoring
- Provenance-aware agent communication
- Attack and defense evaluation

## Repository Structure

```text
message-shield-mas/
+-- configs/
+-- data/
+-- notebooks/
+-- src/
|   +-- agents/
|   +-- runtime/
|   +-- attacks/
|   +-- workflows/
|   +-- eval/
+-- tests/
+-- figures/
```
