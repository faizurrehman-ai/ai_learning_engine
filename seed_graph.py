import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv(override=True)

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


def seed_database():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    driver.verify_connectivity(database=DATABASE)

    with driver.session(database=DATABASE) as session:
        print("Clearing previous records...")
        session.run("MATCH (n) DETACH DELETE n")

        print("Seeding track, concepts, prerequisites, and case studies...")
        cypher_query = """
        // Track
        CREATE (track:Track {id: 'ai_ds', name: 'Artificial Intelligence & Data Science'})

        // Concepts
        CREATE (c1:Concept {id: 'python_basics', name: 'Python Core & OOP', difficulty: 1})
        CREATE (c2:Concept {id: 'data_wrangling', name: 'Pandas & NumPy Data Wrangling', difficulty: 2})
        CREATE (c3:Concept {id: 'supervised_ml', name: 'Supervised Learning & Scikit-Learn', difficulty: 3})
        CREATE (c4:Concept {id: 'deep_learning', name: 'Deep Learning & Neural Networks', difficulty: 4})
        CREATE (c5:Concept {id: 'cv_yolo', name: 'Computer Vision & YOLO Architectures', difficulty: 5})
        CREATE (c6:Concept {id: 'fastapi_backend', name: 'Production APIs with FastAPI', difficulty: 3})

        // Track includes Concepts
        CREATE (track)-[:INCLUDES]->(c1)
        CREATE (track)-[:INCLUDES]->(c2)
        CREATE (track)-[:INCLUDES]->(c3)
        CREATE (track)-[:INCLUDES]->(c4)
        CREATE (track)-[:INCLUDES]->(c5)
        CREATE (track)-[:INCLUDES]->(c6)

        // Prerequisite Dependencies (Skill DAG)
        CREATE (c2)-[:REQUIRES_PREREQUISITE]->(c1)
        CREATE (c3)-[:REQUIRES_PREREQUISITE]->(c2)
        CREATE (c4)-[:REQUIRES_PREREQUISITE]->(c3)
        CREATE (c5)-[:REQUIRES_PREREQUISITE]->(c4)
        CREATE (c6)-[:REQUIRES_PREREQUISITE]->(c1)

        // Case Studies
        CREATE (cs1:CaseStudy {id: 'cs_churn', title: 'Customer Churn Prediction Pipeline', level: 'Intermediate'})
        CREATE (cs2:CaseStudy {id: 'cs_face_rec', title: 'Smart Attendance & Vision System', level: 'Advanced'})
        CREATE (cs3:CaseStudy {id: 'cs_ai_engine', title: 'AI Personalized Curriculum Engine (AI-009)', level: 'Capstone'})

        // Case Study Assessments
        CREATE (cs1)-[:TESTS]->(c2)
        CREATE (cs1)-[:TESTS]->(c3)
        CREATE (cs2)-[:TESTS]->(c4)
        CREATE (cs2)-[:TESTS]->(c5)
        CREATE (cs3)-[:TESTS]->(c3)
        CREATE (cs3)-[:TESTS]->(c6)
        """
        session.run(cypher_query)
        print("Neo4j Cloud database seeded successfully!")

    driver.close()


if __name__ == "__main__":
    seed_database()