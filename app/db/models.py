from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    track_id = Column(String(50), default="ai_ds")
    learning_speed = Column(Float, default=1.0)  # Multiplier (1.0 = normal, <1.0 = slow, >1.0 = fast)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Signal relationships
    activities = relationship("ActivityLog", back_populates="student")
    quiz_results = relationship("QuizResult", back_populates="student")
    code_reviews = relationship("CodeReview", back_populates="student")

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    attendance_rate = Column(Float, default=1.0)  # 0.0 to 1.0
    github_commits = Column(Integer, default=0)
    hours_logged = Column(Float, default=0.0)
    log_date = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="activities")

class QuizResult(Base):
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    concept_id = Column(String(50), nullable=False)  # Corresponds to Concept.id in Neo4j
    score = Column(Float, nullable=False)  # 0.0 to 1.0 (e.g., 0.85 = 85%)
    date_taken = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="quiz_results")

class CodeReview(Base):
    __tablename__ = "code_reviews"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    case_study_id = Column(String(50), nullable=False)  # Corresponds to CaseStudy.id in Neo4j
    code_quality_score = Column(Float, nullable=False)   # 0.0 to 1.0
    mentor_feedback = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="code_reviews")