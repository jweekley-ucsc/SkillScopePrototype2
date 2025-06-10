# backend/llm_assess_interviews.py

"""
Batch-assess SkillScope interview transcripts using OpenAI's LLM (v1.x SDK).
Reads requests from instance/requests/ and writes results to instance/responses/
with smart filenames.
"""

import os
import json
import argparse
from datetime import datetime, timezone
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
import re

# Load environment and initialize OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Resolve project base directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def evaluate_single_transcript(transcript_text, rubric_csv):
    """
    Apply a simple heuristic scoring to a transcript using the rubric definition.

    Args:
        transcript_text (str): The interview transcript to evaluate.
        rubric_csv (str): Rubric in CSV format with columns: Skill, Level, Score, Description

    Returns:
        dict: Evaluation summary per skill
    """
    rubric = []

    # Parse CSV rubric
    f = io.StringIO(rubric_csv)
    reader = csv.DictReader(f)
    for row in reader:
        try:
            row['Score'] = int(row['Score'])
        except ValueError:
            row['Score'] = 0
        rubric.append(row)

    # Group rubric by skill
    skills = {}
    for row in rubric:
        skill = row['Skill']
        if skill not in skills:
            skills[skill] = []
        skills[skill].append(row)

    # Dummy heuristic: assign highest level if transcript mentions the skill keyword
    evaluation = {}
    lower_text = transcript_text.lower()

    for skill, levels in skills.items():
        matched = any(skill.lower() in lower_text for skill in skill.split())  # naive match
        if matched:
            best = max(levels, key=lambda x: x['Score'])
        else:
            best = min(levels, key=lambda x: x['Score'])

        evaluation[skill] = {
            "level": best["Level"],
            "score": best["Score"],
            "description": best["Description"]
        }

    return evaluation

# Argument parser
parser = argparse.ArgumentParser(description="Evaluate SkillScope interviews using an LLM.")
parser.add_argument("--input", required=False, help="Path to llm_eval_requests.jsonl")
parser.add_argument("--output", required=False, help="Optional path to write output .jsonl")
parser.add_argument("--model", default="gpt-4", help="LLM model to use (default: gpt-4)")
args = parser.parse_args()

# Default input path
default_input_path = os.path.join(BASE_DIR, "instance", "requests", "llm_eval_requests.jsonl")

# Smart default output name
def generate_output_filename(transcripts):
    email = transcripts[0].get("email", "batch") if transcripts else "batch"
    user = email.split("@")[0]
    user = re.sub(r"[^\w\-]", "_", user)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%MZ")
    return os.path.join(BASE_DIR, "instance", "responses", f"llm_eval_responses_{user}_{timestamp}.jsonl")

# Build system prompt
def build_system_prompt(rubric_csv, custom_prompt):
    lines = rubric_csv.strip().split("\n")
    readable_rubric = "\n".join(f"• {line}" for line in lines[1:] if line.strip())
    return f"""You are an expert evaluator for undergraduate student interviews.

Use the following rubric to assess the quality of the responses:

{readable_rubric}

Evaluation task:
{custom_prompt}

Return a score and 1–2 sentences of feedback.
"""

# Call OpenAI API
def score_transcript(system_prompt, transcript_text, model):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Student's transcript:\n\n{transcript_text}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except OpenAIError as e:
        return f"[ERROR] OpenAI API call failed: {str(e)}"

# Load requests
input_path = args.input if args.input else default_input_path
if not os.path.exists(input_path):
    raise FileNotFoundError(f"❌ Input file not found: {input_path}")

with open(input_path, "r") as infile:
    requests = [json.loads(line) for line in infile]

results = []
output_path = args.output  # Can still be overridden by CLI

# Evaluate
for request in requests:
    rubric = request["rubric_csv"]
    prompt = request["evaluation_prompt"]
    transcripts = request.get("transcripts", [])
    system_prompt = build_system_prompt(rubric, prompt)

    if output_path is None:
        output_path = generate_output_filename(transcripts)

    for entry in transcripts:
        email = entry.get("email", "unknown")
        transcript_text = entry.get("transcript", "")
        print(f"🧠 Scoring: {email}...")

        feedback = score_transcript(system_prompt, transcript_text, model=args.model)

        results.append({
            "email": email,
            "feedback": feedback,
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        })

# Save results
with open(output_path, "a") as outfile:
    for entry in results:
        outfile.write(json.dumps(entry) + "\n")

print(f"✅ Evaluated {len(results)} transcript(s). Results saved to {output_path}")
