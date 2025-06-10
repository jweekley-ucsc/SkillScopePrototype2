import os
import json
import hashlib

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

submissions_path = os.path.join(BASE_DIR, "instance", "submissions", "submissions.jsonl")
transcripts_path = os.path.join(BASE_DIR, "instance", "transcripts", "transcripts.json")
print(f"🔍 Checking: {submissions_path}")

transcripts = []
seen_hashes = set()

if not os.path.exists(submissions_path):
    print("❌ No submissions.jsonl found.")
    exit(1)

with open(submissions_path, "r") as infile:
    for line in infile:
        try:
            entry = json.loads(line)
            email = entry.get("email")
            transcript = entry.get("transcript")
            reflection = entry.get("reflection", "")
            submitted_at = entry.get("submitted_at")

            if not email or not transcript:
                continue

            # Deduplicate using hash of email + transcript
            key = f"{email}::{transcript}"
            hashkey = hashlib.md5(key.encode()).hexdigest()
            if hashkey in seen_hashes:
                continue

            seen_hashes.add(hashkey)
            transcripts.append({
                "name": email.split("@")[0].replace(".", " ").title(),
                "email": email,
                "transcript": transcript,
                "reflection": reflection,
                "submitted_at": submitted_at
            })

        except json.JSONDecodeError:
            continue

# Ensure output directory exists
os.makedirs(os.path.dirname(transcripts_path), exist_ok=True)

with open(transcripts_path, "w") as outfile:
    json.dump(transcripts, outfile, indent=2)

print(f"✅ Rebuilt {len(transcripts)} transcripts into {transcripts_path}")
