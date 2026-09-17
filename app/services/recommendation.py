from sqlalchemy.orm import Session
from app.db import models
from app.graph.neo4j_client import neo4j_client


async def generate_intern_roadmap(student_id: int, db: Session):
    # 1. Fetch Student Profile & Signals from SQLite
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        return None

    quiz_results = db.query(models.QuizResult).filter(models.QuizResult.student_id == student_id).all()
    code_reviews = db.query(models.CodeReview).filter(models.CodeReview.student_id == student_id).all()
    activity = db.query(models.ActivityLog).filter(models.ActivityLog.student_id == student_id).first()

    # Map mastered concepts (Threshold: >= 70%)
    mastered_concepts = {q.concept_id for q in quiz_results if q.score >= 0.7}

    # 2. Query Neo4j for All Track Concepts & Prerequisite Relationships
    query_concepts = """
    MATCH (t:Track {id: $track_id})-[:INCLUDES]->(c:Concept)
    OPTIONAL MATCH (c)-[:REQUIRES_PREREQUISITE]->(p:Concept)
    RETURN c.id AS id, c.name AS name, c.difficulty AS difficulty, collect(p.id) AS prereqs
    ORDER BY c.difficulty ASC
    """
    track_concepts = await neo4j_client.query(query_concepts, {"track_id": student.track_id})

    # 3. Classify Concepts: Completed, Next Available, or Locked
    completed = []
    next_up = []
    locked = []

    for item in track_concepts:
        cid = item["id"]
        cname = item["name"]
        difficulty = item["difficulty"]
        prereqs = [p for p in item["prereqs"] if p]

        # Baseline hours scaled by student learning speed (1.0 default, lower = more time needed)
        est_hours = round((difficulty * 6.0) / student.learning_speed, 1)

        concept_payload = {
            "concept_id": cid,
            "name": cname,
            "difficulty": difficulty,
            "estimated_hours": est_hours,
        }

        if cid in mastered_concepts:
            completed.append(concept_payload)
        else:
            # Check if all prerequisites are fulfilled
            unmet = [p for p in prereqs if p not in mastered_concepts]
            if not unmet:
                next_up.append(concept_payload)
            else:
                locked.append({**concept_payload, "waiting_on": unmet})

    # 4. Query Neo4j for Eligible Case Studies
    query_case_studies = """
    MATCH (cs:CaseStudy)-[:TESTS]->(c:Concept)
    RETURN cs.id AS id, cs.title AS title, cs.level AS level, collect(c.id) AS tested_concepts
    """
    all_case_studies = await neo4j_client.query(query_case_studies)

    unlocked_case_studies = []
    upcoming_case_studies = []

    for cs in all_case_studies:
        tested = cs["tested_concepts"]
        missing_skills = [c for c in tested if c not in mastered_concepts]

        cs_payload = {
            "case_study_id": cs["id"],
            "title": cs["title"],
            "level": cs["level"],
            "tested_concepts": tested,
        }

        if not missing_skills:
            unlocked_case_studies.append(cs_payload)
        else:
            upcoming_case_studies.append({**cs_payload, "missing_prerequisites": missing_skills})

    # 5. Composite Engagement Score
    attendance = activity.attendance_rate if activity else 1.0
    commits = activity.github_commits if activity else 0
    avg_quiz = (
        sum(q.score for q in quiz_results) / len(quiz_results) if quiz_results else 0.0
    )
    avg_code_quality = (
        sum(r.code_quality_score for r in code_reviews) / len(code_reviews)
        if code_reviews
        else 0.0
    )

    return {
        "student": {
            "id": student.id,
            "name": student.name,
            "track": student.track_id,
            "learning_speed": student.learning_speed,
        },
        "performance_signals": {
            "average_quiz_score": round(avg_quiz, 2),
            "average_code_review": round(avg_code_quality, 2),
            "attendance_rate": attendance,
            "github_commits": commits,
        },
        "progress": {
            "completed_concepts": completed,
            "recommended_next_concepts": next_up,
            "locked_concepts": locked,
        },
        "case_studies": {
            "ready_to_start": unlocked_case_studies,
            "upcoming": upcoming_case_studies,
        },
    }