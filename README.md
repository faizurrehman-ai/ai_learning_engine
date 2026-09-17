# AI Learning Engine 

An enterprise-ready adaptive curriculum and personalized roadmap recommendation engine built with **FastAPI**, **Neo4j AuraDB**, and **SQLite / SQLAlchemy**. The system ingests multi-dimensional intern performance signals, enforces prerequisite mastery via Directed Acyclic Graph (DAG) dependencies, and dynamically generates tailored learning roadmaps.

---

## System Architecture

* **Relational Storage (SQLite & SQLAlchemy)**: Stores intern profiles and granular operational performance signals—including quiz results, code reviews, GitHub commits, attendance rates, and logged hours.
* **Curriculum Knowledge Graph (Neo4j AuraDB)**: Models competencies, tracks, and case studies as a Directed Acyclic Graph (DAG) using `[:INCLUDES]`, `[:REQUIRES_PREREQUISITE]`, and `[:TESTS]` relationships.
* **REST API Layer (FastAPI & Uvicorn)**: Asynchronous service orchestrating student onboarding, telemetry ingestion, recursive prerequisite traversal, and roadmap synthesis.

---

## Graph Schema & Curriculum DAG

### Concepts & Difficulty Weights
* **`python_basics`**: Python Core & OOP (Difficulty: 1)
* **`data_wrangling`**: Pandas & NumPy Data Wrangling (Difficulty: 2)
* **`supervised_ml`**: Supervised Learning & Scikit-Learn (Difficulty: 3)
* **`deep_learning`**: Deep Learning & Neural Networks (Difficulty: 4)
* **`cv_yolo`**: Computer Vision & Real-Time Object Detection (Difficulty: 5)
* **`fastapi_backend`**: Production APIs with FastAPI (Difficulty: 3)

### Prerequisite Dependencies (`[:REQUIRES_PREREQUISITE]`)
* `data_wrangling` $\rightarrow$ `python_basics`
* `supervised_ml` $\rightarrow$ `data_wrangling`
* `deep_learning` $\rightarrow$ `supervised_ml`
* `cv_yolo` $\rightarrow$ `deep_learning`
* `fastapi_backend` $\rightarrow$ `python_basics`

### Industry Case Studies (`[:TESTS]`)
* **Customer Churn Prediction Pipeline**: Tests `data_wrangling` and `supervised_ml`
* **Smart Attendance Vision System**: Tests `deep_learning` and `cv_yolo`
* **AI Curriculum Engine**: Tests `supervised_ml` and `fastapi_backend`

---

## Key Capabilities

1. **Prerequisite Gap Traversal**: Recursively climbs backward along dependency chains in Neo4j. If any upstream concept score falls below **70% (0.70)**, downstream concepts are locked, and remediation actions are issued.
2. **Multi-Signal Aggregation**: Evaluates composite metrics from quizzes, GitHub commits, mentor code reviews, and attendance.
3. **Adaptive Roadmapping**: Dynamically categorizes concepts into *Completed*, *Recommended Next Steps*, and *Locked Behind Prerequisites*.
4. **Pacing Engine**: Recalculates estimated completion time per concept based on individual intern `learning_speed` multipliers.

---

## Project Structure

```text
ai_learning_engine/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── router.py            # API routes (Profiles, Signals, Roadmaps)
│   ├── core/
│   │   └── config.py               # Environment configuration settings
│   ├── db/
│   │   ├── models.py               # SQLAlchemy ORM models
│   │   └── session.py              # SQLite session management
│   ├── graph/
│   │   └── neo4j_client.py         # Async Neo4j Aura connection driver
│   ├── schemas/
│   │   └── student.py              # Pydantic validation schemas
│   ├── services/
│   │   └── recommendation.py       # DAG traversal and adaptive roadmap logic
│   └── main.py                     # FastAPI application factory & lifespan
│
├── tests/
│   └── test_engine.py              # Integration test suite (pytest)
│
├── .env.example                    # Template for environment variables
├── .gitignore                      # Git exclusion rules
├── README.md                       # Comprehensive documentation
├── requirements.txt                # Pinned project dependencies
├── seed_graph.py                   # Neo4j graph bootstrapping script
└── simulate_interns.py             # Multi-persona simulation script