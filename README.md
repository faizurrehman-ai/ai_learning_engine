# AI Learning Engine 

An adaptive curriculum and personalized roadmap recommendation engine built with **FastAPI**, **Neo4j AuraDB**, and **SQLite / SQLAlchemy**. The system ingests multi-dimensional student performance signals, models curriculum prerequisites using a Directed Acyclic Graph (DAG), and dynamically generates custom learning paths based on individual mastery.

---

## System Architecture

* **Relational Storage (SQLite & SQLAlchemy)**: Manages student profiles and performance telemetry—including concept quiz scores, mentor evaluations, GitHub commits, attendance rates, and logged hours.
* **Curriculum Knowledge Graph (Neo4j AuraDB)**: Models the curriculum domain, tracks, and competencies as a Directed Acyclic Graph (DAG) with explicit prerequisite dependencies (`[:REQUIRES_PREREQUISITE]`).
* **REST API Layer (FastAPI & Uvicorn)**: Asynchronous service orchestrating student registration, metric ingestion, recursive prerequisite evaluation, and roadmap recommendation.

---

## Curriculum Graph & Prerequisite DAG

### Core Competencies & Difficulty
* **`python_basics`**: Python Core & OOP (Difficulty: 1)
* **`data_wrangling`**: Pandas & NumPy Data Wrangling (Difficulty: 2)
* **`supervised_ml`**: Supervised Learning & Scikit-Learn (Difficulty: 3)
* **`deep_learning`**: Deep Learning & Neural Networks (Difficulty: 4)
* **`cv_yolo`**: Computer Vision & Object Detection (Difficulty: 5)
* **`fastapi_backend`**: Production APIs with FastAPI (Difficulty: 3)

### Prerequisite Dependencies (`[:REQUIRES_PREREQUISITE]`)
* `data_wrangling` $\rightarrow$ `python_basics`
* `supervised_ml` $\rightarrow$ `data_wrangling`
* `deep_learning` $\rightarrow$ `supervised_ml`
* `cv_yolo` $\rightarrow$ `deep_learning`
* `fastapi_backend` $\rightarrow$ `python_basics`

---

## Core Engine Features

1. **Prerequisite Gap Traversal**: Recursively climbs prerequisite chains in Neo4j. If any upstream concept score falls below the mastery threshold (**70%**), advanced downstream concepts are locked, and remediation is flagged.
2. **Performance Telemetry Aggregation**: Evaluates composite metrics from quizzes, GitHub activity, mentor reviews, and attendance.
3. **Adaptive Roadmapping**: Dynamically organizes modules into *Completed*, *Recommended Next Steps*, and *Locked Behind Prerequisites*.
4. **Pacing Engine**: Calibrates estimated completion time per concept according to individual student `learning_speed` multipliers.

---

## Project Structure

```text
ai_learning_engine/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── router.py            # API endpoints (Profiles, Signals, Roadmaps)
│   ├── core/
│   │   └── config.py               # Environment configuration
│   ├── db/
│   │   ├── models.py               # SQLAlchemy ORM models
│   │   └── session.py              # SQLite session management
│   ├── graph/
│   │   └── neo4j_client.py         # Async Neo4j Aura connection driver
│   ├── schemas/
│   │   └── student.py              # Pydantic validation schemas
│   ├── services/
│   │   └── recommendation.py       # Graph traversal & recommendation algorithms
│   └── main.py                     # FastAPI application factory & lifespan
│
├── tests/
│   └── test_engine.py              # Integration test suite (pytest)
│
├── .gitignore                      # Git exclusion rules
├── README.md                       # Engine documentation
├── requirements.txt                # Pinned dependencies
├── seed_graph.py                   # Graph bootstrapping script
└── simulate_interns.py             # Student journey simulation script