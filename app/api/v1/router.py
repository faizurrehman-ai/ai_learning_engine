from app.services.recommendation import generate_intern_roadmap
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.db import models
from app.schemas.student import (
    StudentCreate,
    StudentResponse,
    QuizSubmission,
    CodeReviewSubmission,
    ActivityLogCreate,
)
from app.graph.neo4j_client import neo4j_client

api_router = APIRouter()

# --- Health Check ---
@api_router.get("/health", tags=["Health"])
async def health_check():
    neo4j_status = "unhealthy"
    try:
        res = await neo4j_client.query("RETURN 1 AS status")
        if res and res[0].get("status") == 1:
            neo4j_status = "connected"
    except Exception as e:
        neo4j_status = f"error: {str(e)}"

    return {
        "status": "online",
        "services": {
            "neo4j": neo4j_status,
            "sqlite": "connected"
        }
    }

# --- Curriculum Endpoints (Neo4j) ---
@api_router.get("/curriculum/concepts", tags=["Curriculum"])
async def get_all_concepts():
    """Retrieve all curriculum concepts and their prerequisite chains."""
    query = """
    MATCH (c:Concept)
    OPTIONAL MATCH (c)-[:REQUIRES_PREREQUISITE]->(p:Concept)
    RETURN c.id AS concept_id, 
           c.name AS concept_name, 
           c.difficulty AS difficulty,
           collect(p.name) AS prerequisites
    ORDER BY c.difficulty ASC
    """
    records = await neo4j_client.query(query)
    return {"concepts": records}

@api_router.get("/curriculum/case-studies", tags=["Curriculum"])
async def get_case_studies():
    """Retrieve all case studies and the concepts they test."""
    query = """
    MATCH (cs:CaseStudy)-[:TESTS]->(c:Concept)
    RETURN cs.id AS case_study_id,
           cs.title AS title,
           cs.level AS level,
           collect(c.name) AS tested_concepts
    """
    records = await neo4j_client.query(query)
    return {"case_studies": records}

# --- Student Profile Endpoints (SQLite) ---
@api_router.post("/students", response_model=StudentResponse, tags=["Students"])
def enroll_student(student_in: StudentCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Student).filter(models.Student.email == student_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student with this email already registered.")
    
    student = models.Student(
        name=student_in.name,
        email=student_in.email,
        track_id=student_in.track_id,
        learning_speed=student_in.learning_speed
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

@api_router.get("/students", response_model=List[StudentResponse], tags=["Students"])
def list_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()

# --- Performance Signal Ingestion ---
# --- Performance Signal Ingestion ---
@api_router.post("/students/quiz", tags=["Performance Ingestion"])
def submit_quiz_score(submission: QuizSubmission, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == submission.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    
    record = models.QuizResult(
        student_id=submission.student_id,
        concept_id=submission.concept_id,
        score=submission.score
    )
    db.add(record)
    db.commit()
    return {"message": "Quiz score recorded", "concept": submission.concept_id, "score": submission.score}

@api_router.post("/students/code-review", tags=["Performance Ingestion"])
def submit_code_review(submission: CodeReviewSubmission, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == submission.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    
    record = models.CodeReview(
        student_id=submission.student_id,
        case_study_id=submission.case_study_id,
        code_quality_score=submission.code_quality_score,
        mentor_feedback=submission.mentor_feedback
    )
    db.add(record)
    db.commit()
    return {"message": "Code review saved", "case_study": submission.case_study_id}

@api_router.post("/students/activity", tags=["Performance Ingestion"])
def log_student_activity(activity_in: ActivityLogCreate, db: Session = Depends(get_db)):
    """
    Ingest daily student activity signals: attendance, GitHub commits, and logged hours.
    """
    student = db.query(models.Student).filter(models.Student.id == activity_in.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    record = models.ActivityLog(
        student_id=activity_in.student_id,
        attendance_rate=activity_in.attendance_rate,
        github_commits=activity_in.github_commits,
        hours_logged=activity_in.hours_logged
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "message": "Activity logged successfully",
        "student_id": activity_in.student_id,
        "github_commits": record.github_commits,
        "attendance_rate": record.attendance_rate,
        "hours_logged": record.hours_logged
    }


# --- Adaptive Analysis: Missing Knowledge & Skill Gaps ---
@api_router.get("/students/{student_id}/knowledge-gap", tags=["Adaptive Engine"])
async def analyze_student_knowledge_gap(student_id: int, target_concept_id: str, db: Session = Depends(get_db)):
    """
    Checks if a student has mastered all prerequisite concepts before attempting a target concept.
    Traverses backwards along Neo4j graph dependencies and compares with student quiz mastery in SQLite.
    """
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    # 1. Fetch all recursive prerequisites from Neo4j
    query = """
    MATCH path = (target:Concept {id: $target_id})-[:REQUIRES_PREREQUISITE*]->(prereq:Concept)
    RETURN prereq.id AS id, prereq.name AS name, length(path) AS depth
    ORDER BY depth DESC
    """
    prereqs = await neo4j_client.query(query, {"target_id": target_concept_id})

    # 2. Get student quiz scores for these concepts from SQLite (FIXED HERE)
    scores = db.query(models.QuizResult).filter(models.QuizResult.student_id == student_id).all()
    score_map = {item.concept_id: item.score for item in scores}

    gaps = []
    ready = True
    for item in prereqs:
        cid = item["id"]
        cname = item["name"]
        score = score_map.get(cid, 0.0)
        # Passing threshold is 70% (0.7)
        if score < 0.7:
            ready = False
            gaps.append({
                "concept_id": cid,
                "concept_name": cname,
                "current_score": score,
                "status": "Failed" if cid in score_map else "Not Attempted",
                "recommendation": f"Must review and achieve >= 70% in '{cname}' first."
            })

    return {
        "student_id": student_id,
        "target_concept": target_concept_id,
        "ready_for_target": ready,
        "unmet_prerequisites": gaps
    }

@api_router.get("/students/{student_id}/roadmap", tags=["Adaptive Engine"])
async def get_student_roadmap(student_id: int, db: Session = Depends(get_db)):
    """
    Generates a personalized, adaptive curriculum roadmap for an intern.
    Calculates completed concepts, unlocked next steps, pacing, and eligible case studies.
    """
    roadmap = await generate_intern_roadmap(student_id, db)
    if not roadmap:
        raise HTTPException(status_code=404, detail="Student not found.")
    return roadmap