# backend/generate_llm_eval_requests.py

import os
import json
import csv
import io  # ← THIS IS MISSING

from datetime import datetime, timezone

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
submissions_path = os.path.join(BASE_DIR, "instance", "submissions", "submissions.jsonl")
requests_path = os.path.join(BASE_DIR, "instance", "requests", "llm_eval_requests.jsonl")

# Placeholder rubric
RUBRIC_CSV = """Skill,Level,Score,Description
Prompt Engineering,Missing,0,No prompt or completely irrelevant
Prompt Engineering,Mastery,4,Clear, efficient, task-optimized
Reflection,Missing,0,No reflection
Reflection,Mastery,4,Insightful and thoughtful reflection"""

EVAL_PROMPT = "Evaluate the clarity and intent of each transcript as if submitted by a student in a technical interview."

# Load all submissions
transcripts = []
if os.path.exists(submissions_path):
    with open(submissions_path, "r") as infile:
        for line in infile:
            try:
                entry = json.loads(line)
                if "email" in entry and "transcript" in entry:
                    transcripts.append({
                        "email": entry["email"],
                        "transcript": entry["transcript"]
                    })
            except json.JSONDecodeError:
                continue
else:
    print(f"❌ No submissions file at: {submissions_path}")
    exit(1)

if not transcripts:
    print("⚠️ No valid transcripts found.")
    exit(0)

# Write new request block
new_request = {
    "rubric_csv": RUBRIC_CSV,
    "evaluation_prompt": EVAL_PROMPT,
    "transcripts": transcripts,
    "received_at": datetime.now(timezone.utc).isoformat()
}

with open(requests_path, "a") as outfile:
    outfile.write(json.dumps(new_request) + "\n")

print(f"✅ Appended {len(transcripts)} transcript(s) to {requests_path}")
