import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

def run_simulation():
    print("=" * 60)
    print("STARTING INTERN ADAPTIVE SIMULATION ENGINE")
    print("=" * 60)

    # -------------------------------------------------------------
    # 1. Profile 1: Struggling Intern (Needs Remediation)
    # -------------------------------------------------------------
    print("\n[Scenario 1] Creating Struggling Intern: Bilal...")
    res = requests.post(f"{BASE_URL}/students", json={
        "name": "Bilal Ahmed",
        "email": "bilal.remediation@example.com",
        "track_id": "ai_ds",
        "learning_speed": 0.7  # Slower pace, requires more hours
    })
    s1_id = res.json()["id"]

    # Fails python_basics (Score 0.45 < 0.70 threshold)
    requests.post(f"{BASE_URL}/students/quiz", json={
        "student_id": s1_id,
        "concept_id": "python_basics",
        "score": 0.45
    })
    requests.post(f"{BASE_URL}/students/activity", json={
        "student_id": s1_id,
        "attendance_rate": 0.80,
        "github_commits": 3,
        "hours_logged": 12.0
    })

    # Check gap for next module: data_wrangling
    gap_res = requests.get(f"{BASE_URL}/students/{s1_id}/knowledge-gap", params={"target_concept_id": "data_wrangling"}).json()
    print(f" -> Ready for Data Wrangling? {gap_res['ready_for_target']}")
    print(f" -> Unmet Prerequisites: {[g['concept_name'] for g in gap_res['unmet_prerequisites']]}")

    # -------------------------------------------------------------
    # 2. Profile 2: Fast-Track Intern (Accelerated Mastery)
    # -------------------------------------------------------------
    print("\n[Scenario 2] Creating Fast-Track Intern: Sarah...")
    res = requests.post(f"{BASE_URL}/students", json={
        "name": "Sarah Connor",
        "email": "sarah.accelerated@example.com",
        "track_id": "ai_ds",
        "learning_speed": 1.5  # Fast learner, reduced estimated hours
    })
    s2_id = res.json()["id"]

    # Excels in core prerequisites
    for cid, score in [("python_basics", 0.95), ("data_wrangling", 0.92), ("supervised_ml", 0.88)]:
        requests.post(f"{BASE_URL}/students/quiz", json={
            "student_id": s2_id,
            "concept_id": cid,
            "score": score
        })

    requests.post(f"{BASE_URL}/students/activity", json={
        "student_id": s2_id,
        "attendance_rate": 1.0,
        "github_commits": 38,
        "hours_logged": 45.0
    })

    # Roadmap inspect
    roadmap_s2 = requests.get(f"{BASE_URL}/students/{s2_id}/roadmap").json()
    print(f" -> Unlocked Next Concepts: {[c['name'] for c in roadmap_s2['progress']['recommended_next_concepts']]}")
    print(f" -> Eligible Case Studies: {[cs['title'] for cs in roadmap_s2['case_studies']['ready_to_start']]}")

    # -------------------------------------------------------------
    # 3. Profile 3: Intermediate Intern (Mid-Track Progression)
    # -------------------------------------------------------------
    print("\n[Scenario 3] Creating Intermediate Intern: Hamza...")
    res = requests.post(f"{BASE_URL}/students", json={
        "name": "Hamza Tariq",
        "email": "hamza.standard@example.com",
        "track_id": "ai_ds",
        "learning_speed": 1.0
    })
    s3_id = res.json()["id"]

    # Passed basic python & wrangling, working on ML
    for cid, score in [("python_basics", 0.80), ("data_wrangling", 0.75)]:
        requests.post(f"{BASE_URL}/students/quiz", json={
            "student_id": s3_id,
            "concept_id": cid,
            "score": score
        })

    requests.post(f"{BASE_URL}/students/activity", json={
        "student_id": s3_id,
        "attendance_rate": 0.90,
        "github_commits": 12,
        "hours_logged": 25.0
    })

    roadmap_s3 = requests.get(f"{BASE_URL}/students/{s3_id}/roadmap").json()
    print(f" -> Recommended Next: {[c['name'] for c in roadmap_s3['progress']['recommended_next_concepts']]}")
    print(f" -> Locked Behind Prerequisites: {[c['concept_id'] for c in roadmap_s3['progress']['locked_concepts']]}")

    print("\n" + "=" * 60)
    print("SIMULATION COMPLETED SUCCESSFULLY")
    print("=" * 60)

if __name__ == "__main__":
    run_simulation()