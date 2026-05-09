# ResearchFlow

## P3 — Agentic Research Assistant with Adaptive RAG and Multi-Agent Orchestration

### Project Overview

**Project Title:**  
*ResearchFlow* — An Adaptive Multi-Agent Research Assistant

**Team Size:** 2 developers  
Created by : Andy Mei, Lucas Holler

---

### Executive Summary

**ResearchFlow** is a multi-agent research assistant powered by LangGraph, LangChain, and AWS Bedrock. The system ingests a corpus of documents into a Pinecone vector store, then orchestrates specialized sub-agents — a **Retriever Agent**, an **Analyst Agent**, and a **Fact-Checker Agent** — under a **Supervisor** graph to answer complex, multi-hop research questions. The workflow incorporates **Adaptive RAG** (dynamically choosing retrieval strategies), **Human-in-the-Loop (HITL) approval** for sensitive outputs, **cross-thread memory** via the LangGraph `Store` interface, and a **Plan-and-Execute** reasoning loop with Critique Nodes for self-refinement. The project culminates in an evaluation suite using **RAGAS** and **Evaluation-Driven Development (EDD)** practices, and is deployed as a serverless API via **AWS Lambda + API Gateway**.

Our project in particular focuses on the over 12k+ pages of data stored in the minecraft wiki. It aims to be an assistant for everything Minecraft in a way that normal LLMs would be unable to answer.
---

## System Architecture

```code
┌──────────────────────────────────────────────────────────────┐
│                        CLIENT (CLI / API)                    │
│                  POST /research  { "question": "..." }       │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                   SUPERVISOR GRAPH (LangGraph)               │
│                                                              │
│  ┌────────────┐   ┌────────────┐    ┌────────────────────┐   │
│  │  Planner   │──▶│  Router    │──▶│  Aggregator /      │   │
│  │  Node      │   │  (Cond.    │    │  Critique Node     │   │
│  │            │   │   Edges)   │    │  (Self-Refinement) │   │
│  └────────────┘   └─────┬──┬──┘     └────────────────────┘   │
│                     ┌───┘  └───┐                             │
│                     ▼          ▼                             │
│  ┌──────────────────────┐ ┌──────────────────────────┐       │
│  │  RETRIEVER AGENT     │ │  ANALYST AGENT           │       │
│  │  • Pinecone Query    │ │  • Bedrock LLM Synthesis │       │
│  │  • Re-ranking        │ │  • Structured Output     │       │
│  │  • Context Compress. │ │  • Citation Generation   │       │
│  └──────────────────────┘ └──────────────────────────┘       │
│                    ┌───────────┐                             │
│                    ▼           │                             │
│  ┌──────────────────────┐      │                             │
│  │  FACT-CHECKER AGENT  │──────┘                             │
│  │  • Cross-reference   │                                    │
│  │  • Confidence Score  │                                    │
│  │  • HITL Interrupt    │                                    │
│  └──────────────────────┘                                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  STORE (Cross-Thread Memory)                         │    │
│  │  • User preferences & past queries via namespaces    │    │
│  │  • Session scratchpad for Plan-and-Execute state     │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│              PINECONE (Serverless Index)                     │
│  Namespaces: "primary-corpus" | "fact-check-sources"         │
└──────────────────────────────────────────────────────────────┘
```

---

## Functional Requirements. Also served as our backlog

### FR-1: Document Ingestion Pipeline

- Accept a directory of PDF and/or text documents as input.
- Chunk documents using sentence-level or recursive character splitting.
- Generate vector embeddings in batches using a Sentence Transformer model or Bedrock embedding model.
- Upsert embeddings into a **Pinecone serverless index** with rich metadata (source filename, page number, chunk ID, timestamp).
- Support at least **two namespaces**: one for the primary research corpus and one for fact-checking reference material.

### FR-2: Supervisor Graph (LangGraph)

- Implement the main orchestration layer as a LangGraph `StateGraph`.
- The graph state must be defined as a `TypedDict` containing at minimum: the user question, the current plan, retrieved chunks, analysis output, fact-check results, confidence score, and iteration count.
- Implement the **Planner Node** that decomposes a complex question into sub-tasks (Plan-and-Execute pattern).
- Implement **conditional edges** that route sub-tasks to the appropriate sub-agent based on task type.
- Implement a **Critique Node** that evaluates the aggregated response and decides whether to accept, retry (loop back to Retriever or Analyst), or escalate to HITL.
- Limit self-refinement loops to a configurable maximum (e.g., 3 iterations).

### FR-3: Retriever Agent

- Query the Pinecone index using semantic search with metadata filtering.
- Apply **context compression** to reduce token noise in retrieved chunks.
- Apply **re-ranking** to prioritize the most relevant results before passing to the Analyst.
- Return a structured payload: list of retrieved chunks with relevance scores and source metadata.

### FR-4: Analyst Agent

- Receive retrieved context and the original sub-task from the Supervisor.
- Use **AWS Bedrock** (Claude or another supported model) to synthesize a structured response.
- Enforce **Pydantic-validated structured output** containing: answer text, supporting citations (source + page), and a self-assessed confidence score.
- Support **streaming responses** for real-time feedback during long synthesis operations.

### FR-5: Fact-Checker Agent

- Cross-reference the Analyst's claims against the `fact-check-sources` namespace.
- Produce a verification report with per-claim verdicts (Supported / Unsupported / Inconclusive) and evidence snippets.
- If any claim is flagged as **Unsupported** and the overall confidence is below a configurable threshold, trigger a **HITL interrupt** for human review.
- Support **Time Travel** — allow a reviewer to rewind graph state to a prior checkpoint and re-execute from that point.

### FR-6: Security Middleware

- Implement at least one custom middleware layer:
  - **PII Masking**: Scan user inputs and agent outputs for personally identifiable information (emails, phone numbers, SSNs) and redact before processing or returning.
- Apply **injection/stuffing guardrails** on user input to prevent prompt injection attacks.

### FR-7: Memory and Persistence

- Use the LangGraph **`Store` interface** with namespaces and scopes to persist:
  - **User preferences** (e.g., preferred verbosity level, trusted sources) across threads.
  - **Query history** for contextual few-shot prompting on repeat interactions.
- Implement a **step-wise scratchpad** that logs each node's intermediate output for debugging and observability.
- Use **sliding window** message trimming to manage token budgets within long research sessions.

### FR-8: Serverless Deployment

- Package the LangGraph agent for deployment to **AWS Lambda** behind **API Gateway**.
- Provide an Infrastructure-as-Code template (AWS SAM `template.yaml` or equivalent).
- Expose a `POST /research` endpoint that accepts a JSON body `{ "question": "..." }` and returns the structured research report.
- Include a deployment script (`deploy.sh` or equivalent) with clear instructions.

---

## Non-Functional Requirements

### NFR-1: Evaluation Suite (RAGAS + EDD)

- Create a **Golden Dataset** of at least 10 question-answer-context triples for benchmarking.
- Run a formal **RAGAS evaluation** measuring at minimum:
  - **Faithfulness** — Are the answers grounded in the retrieved context?
  - **Answer Relevancy** — Does the answer address the original question?
  - **Context Precision** — Is the retrieved context precise and not noisy?
- All RAGAS scores must be logged and reported in the project documentation.

### NFR-2: Unit Testing and Mocking

- Write **unit tests** for at least the following:
  - The Retriever Agent (mock Pinecone calls, assert correct re-ranking behavior).
  - The Analyst Agent (mock Bedrock calls, validate structured output schema).
  - The Supervisor Graph routing logic (mock sub-agents, verify conditional edge decisions).
- Use **mocked tool calls** to enable tests to run without live cloud dependencies.
- Validate agent outputs against the Golden Dataset using LangSmith evaluators or equivalent.

### NFR-3: Observability

- Integrate **LangSmith** tracing for all agent invocations (or document how to enable it via environment variables).
- The step-wise scratchpad (FR-7) serves as an additional observability layer.

### NFR-4: Code Quality

- All Python code must include type hints and docstrings. (check out Ruff or PyLint to help you with this!)
- The project must include a `requirements.txt` or `pyproject.toml` with pinned dependency versions.
- Provide a `.env.example` file documenting all required environment variables (API keys, AWS region, Pinecone index name, etc.).


---

## Deliverables Checklist

- [ ] **Source Code Repository** with clear folder structure and README
- [ ] **Document Ingestion Script** — end-to-end pipeline from raw documents to Pinecone index
- [ ] **LangGraph Supervisor** — fully wired `StateGraph` with conditional routing, Plan-and-Execute, and Critique Nodes
- [ ] **Three Sub-Agents** — Retriever, Analyst, and Fact-Checker with defined interfaces
- [ ] **Security Middleware** — PII masking and injection guardrails
- [ ] **Cross-Thread Memory** — `Store` interface with namespace-scoped user preferences
- [ ] **HITL Workflow** — interrupt-based human approval with Time Travel support
- [ ] **RAGAS Evaluation Report** — faithfulness, relevancy, and context precision scores
- [ ] **Unit Test Suite** — mocked tests for agents and routing logic with golden dataset validation
- [ ] **Deployment Artifacts** — SAM template, Lambda handler, deploy script, API Gateway config
- [ ] **Presentation** — 10-minute recorded or live demo covering architecture, key design decisions, evaluation results, and lessons learned

---

## Recommended Technology Stack

| Component | Technology |
| ----------- | ------------ |
| LLM Runtime | AWS Bedrock (Claude 3 Sonnet/Haiku or equivalent) |
| Agent Framework | LangChain + LangGraph |
| Vector Database | Pinecone (Serverless) |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) or Bedrock Titan Embeddings |
| Evaluation | RAGAS, LangSmith |
| Testing | pytest, unittest.mock |
| Deployment | AWS Lambda, API Gateway, AWS SAM |
| Language | Python 3.11+ |

---

## Getting Started

```bash
# 1. Clone the repository
git clone <repo-url> && cd researchflow

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env .env
# Edit .env with your API keys (AWS, Pinecone, LangSmith)

# 5. Ingest documents
python scripts/ingest.py --input-dir ./data/corpus --namespace primary-corpus

# 6. Run the research assistant locally
python main.py --question "What are the key findings on X?"

# 7. Run tests
pytest tests/ -v

# 8. Run RAGAS evaluation
python scripts/evaluate.py --golden-dataset ./data/golden_dataset.json

# 9. Deploy to AWS
cd deployment && bash deploy.sh
```

## Project Structure

```code
researchflow/
├── README.md                      # Project specification
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variable template
├── main.py                        # CLI entry point
│
├── agents/                        # Agent modules
│   ├── __init__.py
│   ├── state.py                   # ResearchState TypedDict
│   ├── supervisor.py              # Supervisor StateGraph
│   ├── retriever.py               # Retriever agent (Pinecone)
│   ├── analyst.py                 # Analyst agent (Bedrock)
│   └── fact_checker.py            # Fact-Checker agent
│
├── middleware/                    # Security middleware
│   ├── __init__.py
│   ├── pii_masking.py             # PII detection and redaction
│   └── guardrails.py              # Prompt injection guardrails
│
├── memory/                        # Cross-thread memory
│   ├── __init__.py
│   └── store.py                   # LangGraph Store interface
│
├── scripts/                       # Utility scripts
│   ├── ingest.py                  # Document ingestion pipeline
│   └── evaluate.py                # RAGAS evaluation pipeline
│
├── data/                          # Data files
│   ├── corpus/                    # Place your source documents here
│   │   └── README.md
│   └── golden_dataset.json        # Evaluation benchmark (10+ entries)
│
├── deployment/                    # AWS deployment artifacts
│   ├── app.py                     # Lambda handler
│   ├── template.yaml              # AWS SAM template
│   └── deploy.sh                  # Deployment script
│
└── tests/                         # Unit tests
    ├── __init__.py
    ├── test_retriever.py
    ├── test_analyst.py
    └── test_supervisor.py
```
