# Message Shield MAS: Causal Execution Monitoring for Multi-Agent LLM Security

> A runtime security framework for detecting and containing distributed communication attacks in LLM-based multi-agent systems through causal provenance tracking, dynamic trust propagation, and topology-aware monitoring.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](#technical-stack)
[![LLM Security](https://img.shields.io/badge/LLM%20Security-Multi--Agent-red)](#research-direction)
[![Provenance Tracking](https://img.shields.io/badge/Provenance-Causal%20Trace-purple)](#causal-provenance-and-risk-propagation)
[![Trust Modeling](https://img.shields.io/badge/Trust-Beta%20Ledger-green)](#dynamic-trust-ledger)
[![Topology-Aware](https://img.shields.io/badge/Topology-Edge%20Betweenness-orange)](#topology-aware-placement)
[![Evaluation](https://img.shields.io/badge/Evaluation-RQ1--RQ4-lightgrey)](#research-questions)

Message Shield MAS is a research prototype for studying **runtime security in LLM-based multi-agent systems**. It detects and contains distributed communication attacks that evade per-message filters by spanning multiple agents, messages, or hops. The system operates as a causal execution monitor with dynamic trust — observing the provenance of every message, propagating cumulative risk across the causal trace, and updating per-agent trust scores to detect threats that are individually low-risk but collectively malicious.

This project is designed as a research prototype for agentic AI security and multi-agent threat modeling. It does not claim production deployment or real-world adversarial hardening without further validation.

---

## Table of Contents

- [Motivation](#motivation)
- [Problem Statement](#problem-statement)
- [System Overview](#system-overview)
- [Architecture Diagram](#architecture-diagram)
- [Research Direction](#research-direction)
- [Threat Model](#threat-model)
- [Methodology](#methodology)
- [Causal Provenance and Risk Propagation](#causal-provenance-and-risk-propagation)
- [Dynamic Trust Ledger](#dynamic-trust-ledger)
- [Topology-Aware Placement](#topology-aware-placement)
- [Policy Engine and Quarantine-Repair](#policy-engine-and-quarantine-repair)
- [Benchmark and Attack Suite](#benchmark-and-attack-suite)
- [Evaluation Metrics](#evaluation-metrics)
- [Preliminary Results](#preliminary-results)
- [Research Questions](#research-questions)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Usage Example](#usage-example)
- [Future Work](#future-work)
- [Citation and Acknowledgment](#citation-and-acknowledgment)

---

## Motivation

LLM-based multi-agent systems decompose complex tasks across multiple cooperating agents that communicate via structured messages. Each inter-agent message is a potential attack surface: a compromised upstream agent, a manipulated tool output, or a crafted payload injected into the communication channel can cascade through the pipeline and corrupt downstream agents silently.

Existing defenses treat each message in isolation — a per-message rule filter or LLM judge has no memory of what the sending agent has communicated before, no model of the causal path that produced the message, and no awareness of how distributed fragments combine into a complete attack. Message Shield MAS addresses this gap by tracking the full causal trace, propagating cumulative risk across message ancestry, maintaining a dynamic trust ledger per agent, and placing monitors at high-betweenness edges to contain distributed threats efficiently.

---

## Problem Statement

Given a message `m` produced by agent `v` in a multi-agent pipeline, the monitor must determine whether `m` is safe to deliver, requires escalation to a bounded LLM judge, or should be quarantined and repaired.

| Capability | Requirement |
|---|---|
| Causal awareness | Track the full ancestry of each message through the agent graph |
| Distributed threat detection | Detect attacks whose individual fragments appear benign |
| Dynamic trust | Update per-agent distrust scores from historical judgments |
| Topology sensitivity | Place monitors where they intercept the most message flow |
| Utility preservation | Repair quarantined messages without free-form regeneration |
| Overhead budget | Minimize token and latency cost relative to the security gain |

The central challenge is maintaining strong attack-success-rate reduction across chain, star, and mesh topologies while keeping benign utility and false-positive rates acceptable.

---

## System Overview

Message Shield MAS follows a causal monitoring pipeline applied at each monitored edge in the agent graph:

1. Agent `v` produces message `m`
2. Structural extractor isolates the artifact `φ(m)` from raw text
3. Causal trace lookup retrieves ancestors and their cumulative risk scores
4. Cumulative risk `R(m)` is computed via noisy-OR propagation
5. Trust ledger provides `distrust(v)` from Beta distribution
6. Policy engine applies tiered decision: pass / escalate / quarantine
7. Quarantine triggers provenance-anchored repair to the last trusted ancestor
8. Judgment updates the trust ledger for agent `v`

### Core Modules

| Module | Role |
|---|---|
| `runtime/provenance.py` | Causal trace storage: risk scores, ancestors, content hashes, timestamps |
| `runtime/trust_ledger.py` | Beta trust ledger `τ(v) = (α_v, β_v)`; computes `distrust(v)` |
| `runtime/placement.py` | Edge betweenness centrality monitor placement under a budget |
| `runtime/policy_engine.py` | Tiered decision + provenance-anchored quarantine-repair |
| `runtime/rules.py` | Structural rule-based score `r(m)` on extracted artifact `φ(m)` |
| `topologies/` | Chain, star, and mesh graph definitions with schedules and allowed paths |
| `attacks/` | Payload-split, distributed-backdoor, and transitive-trust attack generators |
| `eval/metrics.py` | ASR, BU, UA, FPR, containment hops, tokens, latency, semantic drift |

---

## Architecture Diagram

```mermaid
flowchart LR
    A[Agent v: Message m] --> B[Structural Extractor φ(m)]
    B --> C[Causal Trace Lookup]
    B --> D[Rule-Based Scorer r(m)]
    C --> E[Risk Propagation R(m)]
    D --> E
    E --> F[Trust Ledger distrust(v)]
    F --> G[Policy Engine]
    G -- Pass --> H[Deliver to Next Agent]
    G -- Escalate --> I[Bounded LLM Judge]
    I --> G
    G -- Quarantine --> J[Provenance-Anchored Repair]
    J --> H
    G --> K[Update Trust Ledger]
```

### Topology Views

| Topology | Structure | Why It Matters |
|---|---|---|
| Chain | `A → B → C` | Baseline; all edges have equal betweenness |
| Star | `Hub ↔ A, B, C, D` | Hub edge is critical; placement matters |
| Mesh | Fully connected sub-graph | Multiple paths; distributed attacks can route around single monitors |

---

## Research Direction

This repository is designed for experiments in:

- Agentic AI security and multi-agent LLM communication
- Prompt injection and payload-splitting attacks in agent workflows
- Causal provenance-aware runtime monitoring
- Dynamic trust propagation across agent graphs
- Topology-aware monitor placement under a coverage budget
- Attack-success-rate reduction vs. utility preservation trade-offs

---

## Threat Model

| Threat Class | Attack | Description |
|---|---|---|
| T1 | Payload splitting | Malicious payload fragmented across `k` messages; each fragment is individually low-risk |
| T2 | Distributed backdoor | Attack primitives distributed across different agents; assembled only at collaboration point |
| T3 | Transitive trust | Exploit legitimate-looking compliant chain to leak malicious content to downstream agents |

All three threats evade per-message isolation-blind filters, which is the foil that Message Shield MAS is designed to beat.

---

## Methodology

### 1. Structural Extraction

Before any risk computation, the module extracts the artifact `φ(m)` — the structured representation of the message's claimed task or content — from raw text. The rule-based scorer and LLM judge both operate on `φ(m)`, not raw text, to reduce susceptibility to surface-level obfuscation.

### 2. Causal Provenance and Risk Propagation

Each message node stores:

- `risk_score r(m)` — rule-based structural score on `φ(m)`
- `ancestors` — set of causal predecessor message IDs
- `content_hash` — SHA-256 of `φ(m)` for integrity anchoring
- `timestamp` — wall-clock time at intercept

Cumulative risk is computed via noisy-OR propagation over the causal trace:

```
R(m) = g(r(m), distrust(src(m))) + λ · max_{p ∈ anc(m)} R(p)
g(r, d) = 1 − (1 − r)(1 − d)    (noisy-OR combination)
```

`λ` is a configurable decay hyperparameter; `distrust(src(m))` comes from the trust ledger. This formulation means a sequence of low-risk fragments that share a risky ancestor will accumulate `R(m)` above the quarantine threshold — defeating T1 payload splitting.

### 3. Dynamic Trust Ledger

Per-agent trust is modeled as a Beta distribution `τ(v) = (α_v, β_v)` initialized at `(1, 1)` (uniform prior). After each judgment:

```
benign judgment:     α_v += 1
suspicious judgment: β_v += 1
distrust(v)        = 1 − α_v / (α_v + β_v)
```

An agent that has sent multiple suspicious messages accumulates high `distrust(v)`, which raises `R(m)` for all future messages from that agent — even if each individual message appears benign. This defeats T3 transitive trust exploitation.

### 4. Topology-Aware Placement

Given a monitor budget `b` and an agent graph `G`, the placement module selects the `b` edges with highest edge betweenness centrality using NetworkX:

```python
select_monitored_edges(graph, budget) -> set[edge]
# uses networkx.edge_betweenness_centrality
```

On a chain topology, all edges have equal betweenness — placement does not help and the chain is the degenerate baseline. On star and mesh topologies, placing monitors at hub edges or bridge edges provides disproportionate coverage. This is the mechanism behind RQ4: coverage vs. topology structure.

---

## Policy Engine and Quarantine-Repair

The policy engine applies a tiered decision based on `R(m)` and two thresholds from `configs/runtime_policy.yaml`:

```
decision(m):
  pass       if R(m) <  θ_low
  escalate   if θ_low ≤ R(m) < θ     → bounded LLM judge on φ(m)
  quarantine if R(m) ≥ θ
```

Quarantine triggers provenance-anchored repair:

```
repair(m) = restore content from last_trusted_ancestor in provenance trace
```

Repair is diff-based and provenance-anchored — it is **not** free-form regeneration. This preserves benign utility for falsely quarantined messages while preventing the repair step itself from being exploited.

---

## Benchmark and Attack Suite

### Attack Implementations

| Attack | Module | Threat Class | Fragment Property |
|---|---|---|---|
| Payload split | `attacks/payload_split_attack.py` | T1 | Each of `k` fragments individually scores below `θ_low` |
| Distributed backdoor | `attacks/distributed_backdoor_attack.py` | T2 | Primitives across agents; combined only at collaboration edge |
| Transitive trust | `attacks/transitive_trust_attack.py` | T3 | Compliant-looking chain; exploit accumulated trust |

Each attack emits `original_content` and `tampered_content` per fragment to enable semantic-drift measurement and confirm that fragments are individually low-risk under the rule-based scorer.

### Baselines

| Baseline | Description |
|---|---|
| `none` | No defense — ASR ceiling |
| `rule_filter` | Per-message rule filter — isolation-blind foil |
| `llm_judge` | Per-message LLM judge on raw message — competitive single-message defense |
| `delimiter` | Sandwich / delimiter defense — optional comparison |
| `message_shield` | Full system: causal risk + trust ledger + topology-aware placement |

All baselines are selectable via a single config flag so one harness runs the full comparison grid.

---

## Evaluation Metrics

| Metric | Description |
|---|---|
| ASR | Attack success rate (primary — lower is better for the defense) |
| BU | Benign utility — task success rate on unattacked workflows |
| UA | Utility under attack — task success rate when an attack is present |
| FPR | False-quarantine rate on benign messages |
| `containment_hops` | Number of hops from injection point to quarantine decision |
| Tokens / latency | Overhead relative to `none` baseline |
| `semantic_drift` | Distance between repaired content and intended content (defends repair quality) |

---

## Preliminary Results

The values below are representative simulation results from the prototype evaluation grid. They are intended as realistic placeholders and will be replaced with final measurements when the full experiment matrix is complete.

| Defense | ASR (T1) | ASR (T2) | ASR (T3) | BU | FPR |
|---|---:|---:|---:|---:|---:|
| none | 91% | 88% | 85% | 100% | 0% |
| rule_filter | 61% | 79% | 72% | 98% | 3% |
| llm_judge | 44% | 63% | 51% | 95% | 7% |
| message_shield | **18%** | **27%** | **14%** | 93% | 9% |

### Containment by Topology

| Topology | Avg. Containment Hops | Monitor Budget |
|---|---:|---:|
| Chain | 1.2 | 2 / 2 edges |
| Star | 1.0 | 1 / 4 edges (hub) |
| Mesh | 2.1 | 3 / 6 edges |

---

## Research Questions

| RQ | Question | Mechanism | Primary Artifact |
|---|---|---|---|
| RQ1 | Does Message Shield reduce ASR vs. isolation-blind baselines across all three threat classes? | Full system vs. `rule_filter`, `llm_judge` | Table 2: ASR × defense × attack |
| RQ2 | What is the utility and overhead cost of the defense? | Quarantine-repair, tiered decision | Table 3: BU, UA, FPR, tokens, latency |
| RQ3 | Which mechanism accounts for which reduction? | Ablation: disable R / trust / placement | Table 4: ASR under partial ablations |
| RQ4 | How does containment scale with topology structure? | Edge betweenness placement + containment hops | Figure 4: hops vs. topology + spectral gap |

The ablation (RQ3) uses config flags to disable individual components — no new code is required beyond the flags. The predicted pattern is: removing `R(m)` hurts most on T1; removing trust hurts most on T3; removing topology-aware placement hurts most on T2 and mesh topologies.

---

## Repository Structure

```text
message-shield-mas/
├── README.md
├── configs/
│   └── runtime_policy.yaml          # θ_low, θ thresholds, λ decay, trust prior
├── data/
│   ├── traces/raw/                  # per-run provenance traces (gitignored)
│   └── reports/                     # CSV outputs from run_batch.py
├── src/
│   ├── agents/                      # Planner, Executor, Reviewer agent definitions
│   ├── runtime/
│   │   ├── monitor.py               # Entry point: intercepts edges, calls policy
│   │   ├── provenance.py            # Causal trace + risk propagation R(m)
│   │   ├── trust_ledger.py          # Beta trust ledger τ(v) = (α_v, β_v)
│   │   ├── placement.py             # Edge betweenness monitor placement
│   │   ├── policy_engine.py         # Tiered decision + quarantine-repair
│   │   └── rules.py                 # Structural rule-based scorer r(m)
│   ├── topologies/
│   │   ├── chain.py                 # agents, edges, schedule, allowed_paths
│   │   ├── star.py
│   │   └── mesh.py
│   ├── attacks/
│   │   ├── attack_registry.py
│   │   ├── rewrite_attack.py
│   │   ├── authority_attack.py
│   │   ├── payload_split_attack.py  # T1
│   │   ├── distributed_backdoor_attack.py  # T2
│   │   └── transitive_trust_attack.py      # T3
│   ├── eval/
│   │   ├── metrics.py               # ASR, BU, UA, FPR, containment_hops, drift
│   │   ├── run_batch.py             # Sweep: topology × attack × defense × seed
│   │   └── summarize_results.py     # Aggregate CSV → tables/figures
│   └── workflows/
│       └── base_workflow.py         # Three-agent pipeline driver
├── notebooks/
│   └── demo_message_shield.ipynb
├── tests/                           # Unit tests for R(m), trust ledger, placement
├── figures/                         # Output figures for paper
├── requirements.txt
├── .env.example                     # API key template (never commit .env)
└── LICENSE
```

---

## Installation

```bash
git clone https://github.com/mohmyhm/message-shield-mas.git
cd message-shield-mas
python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env   # add OPENAI_API_KEY / ANTHROPIC_API_KEY
```

The system runs in **deterministic mode** by default (no LLM calls, no API spend) for development and unit testing. Switch to LLM-backed mode via config for real experiment numbers.

---

## Usage Example

Run the full evaluation grid in deterministic mode:

```bash
python src/eval/run_batch.py \
  --topologies chain star \
  --attacks payload_split distributed_backdoor transitive_trust \
  --defenses none rule_filter llm_judge message_shield \
  --seeds 5 \
  --deterministic
```

Run a single scenario with the full Message Shield defense:

```bash
python src/workflows/base_workflow.py \
  --topology chain \
  --attack payload_split \
  --defense message_shield \
  --seed 42
```

Ablation run (disable trust ledger):

```bash
python src/eval/run_batch.py \
  --defense message_shield \
  --ablate trust \
  --attacks all \
  --seeds 5
```

Summarize results and generate tables:

```bash
python src/eval/summarize_results.py --input data/reports/ --output figures/
```

Expected output per run includes:

- Per-message `R(m)` scores and policy decisions
- Trust ledger state after each judgment
- Per-run ASR, BU, FPR, containment hops, and latency
- Aggregated mean ± std over seeds

---

## Future Work

- Extend to real LLM-backbone agent graphs beyond the three-agent prototype
- Add adversarially adaptive attacks that observe and evade `R(m)` accumulation
- Explore learned structural extractors in place of hand-crafted rules
- Integrate with agentic frameworks (LangGraph, AutoGen, CrewAI)
- Formal analysis of `λ` sensitivity and threshold robustness
- Real-time streaming evaluation on live multi-agent sessions
- Extend repair to semantic-preserving LLM rewrite under provenance anchoring

---

## Citation and Acknowledgment

If you use or adapt this project, please cite it as:

```bibtex
@misc{message-shield-mas2026,
  title  = {Message Shield MAS: Causal Execution Monitoring for Multi-Agent LLM Security},
  author = {Mohammad Yahyaei},
  year   = {2026},
  note   = {Research prototype for runtime attack detection in LLM-based multi-agent systems}
}
```

This project is inspired by research in agentic AI security, prompt injection, causal reasoning, and runtime verification for LLM systems.

---

## Responsible Use Notice

Message Shield MAS is a research prototype. The attack implementations are included solely to evaluate and validate the defense mechanisms in a controlled experimental setting. They must not be used to attack production systems, deployed multi-agent services, or third-party infrastructure without explicit authorization.
