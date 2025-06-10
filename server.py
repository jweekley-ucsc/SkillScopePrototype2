import os
import json
import csv
import uuid
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import openai
from datetime import datetime
from backend.llm_assess_interviews import evaluate_transcript_block

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# App and folders
app = Flask(__name__, static_url_path='/static')
CORS(app)

@app.before_request
def debug_route_origin():
    print(f"➡️  Incoming request: {request.method} {request.path}")

UPLOAD_FOLDER = "instance/uploads"
TRANSCRIPT_FOLDER = "instance/transcripts"
RUBRIC_FOLDER = "instance/rubrics"
EVALUATION_FOLDER = "instance/evaluations"

# Ensure folders exist
for folder in [UPLOAD_FOLDER, TRANSCRIPT_FOLDER, RUBRIC_FOLDER, EVALUATION_FOLDER]:
    os.makedirs(folder, exist_ok=True)

#only uploads unscored transcripts based on a persistent index file (e.g., scored_transcripts.jsonl)

def load_scored_filenames():
    scored_path = os.path.join("instance", "responses", "scored_transcripts.jsonl")
    if not os.path.exists(scored_path):
        return set()
    
    scored_filenames = set()
    with open(scored_path, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if "filename" in entry:
                    scored_filenames.add(entry["filename"])
            except json.JSONDecodeError:
                continue
    return scored_filenames
@app.route("/")
@app.route("/login")
def login():
    return send_from_directory("templates", "login.html")


@app.route("/home")
def home():
    return send_from_directory("templates", "index.html")


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    name = data.get("name")
    return jsonify({"success": True})


@app.route("/interview")
def interview():
    return send_from_directory("templates", "interview.html")


@app.route("/interviewer")
def interviewer():
    return send_from_directory("templates", "interviewer.html")


@app.route("/evaluate")
def evaluate():
    return send_from_directory("templates", "evaluate.html")


@app.route("/upload-audio", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"success": False, "error": "No audio file provided"}), 400

    audio = request.files["audio"]
    filename = request.form.get("filename", "interview.webm")

    if not filename:
        return jsonify({"success": False, "error": "Filename is missing"}), 400

    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        audio.save(filepath)
        print(f"✅ Saved audio file to: {filepath}")

        # Placeholder for Whisper or other transcription logic
        transcript_json = {
            "text": "This is a placeholder transcript.",
            "segments": [],
            "speaker_labels": [],
        }

        return jsonify({"success": True, "transcript": transcript_json})
    except Exception as e:
        print(f"❌ Upload or transcription failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    data = request.get_json()
    filename = data.get("filename")

    if not filename:
        return jsonify({"success": False, "error": "No filename provided"}), 400

    audio_path = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(audio_path):
        return jsonify({"success": False, "error": "Audio file not found"}), 404

    try:
        with open(audio_path, "rb") as audio_file:
            result = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return jsonify({"success": True, "transcript": result.text})
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/evaluate-transcript", methods=["POST"])
def evaluate_transcript():
    from backend.llm_assess_interviews import evaluate_single_transcript

    payload = request.get_json()
    print("🧾 Incoming evaluation request payload:")
    print(json.dumps(payload, indent=2))

    transcript_text = payload.get("transcript")
    rubric_csv = payload.get("rubric")

    if not rubric_csv or not transcript_text:
        return jsonify({"error": "Missing rubric or transcript"}), 400

    try:
        result = evaluate_single_transcript(transcript_text, rubric_csv)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/submit-transcript", methods=["POST"])
def submit_transcript():
    import hashlib

    data = request.get_json()
    email = data.get("email")
    transcript = data.get("transcript")
    reflection = data.get("reflection", "")
    submitted_at = datetime.utcnow().isoformat()

    if not email or not transcript:
        return jsonify({"success": False, "error": "Missing email or transcript"}), 400

    # Construct full entry
    name = email.split("@")[0].replace(".", " ").title()
    entry = {
        "name": name,
        "email": email,
        "transcript": transcript,
        "reflection": reflection,
        "submitted_at": submitted_at
    }

    # ---- Part 1: Append to submissions.jsonl (raw log) ----
    submissions_path = os.path.join("instance", "submissions", "submissions.jsonl")
    os.makedirs(os.path.dirname(submissions_path), exist_ok=True)
    with open(submissions_path, "a") as f:
        f.write(json.dumps(entry) + "\n")

    # ---- Part 2: Update transcripts.json (deduplicated list) ----
    transcripts_path = os.path.join("instance", "transcripts", "transcripts.json")
    os.makedirs(os.path.dirname(transcripts_path), exist_ok=True)

    transcripts = []
    if os.path.exists(transcripts_path):
        with open(transcripts_path, "r") as f:
            try:
                transcripts = json.load(f)
            except json.JSONDecodeError:
                transcripts = []

    def entry_hash(e):
        key = f"{e['email']}::{e['transcript']}"
        return hashlib.md5(key.encode()).hexdigest()

    existing_hashes = {entry_hash(e) for e in transcripts}
    new_hash = entry_hash(entry)

    if new_hash not in existing_hashes:
        transcripts.append(entry)
        with open(transcripts_path, "w") as f:
            json.dump(transcripts, f, indent=2)

        # ---- Part 3: Also append to transcripts.jsonl ----
        transcripts_jsonl_path = os.path.join("instance", "transcripts", "transcripts.jsonl")
        with open(transcripts_jsonl_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    return jsonify({"success": True})


    request_block = {
        "rubric_csv": rubric_csv,
        "evaluation_prompt": prompt,
        "transcripts": transcripts
    }

    try:
        results = evaluate_transcript_block(request_block)
        for r in results:
            print(f"🧠 Scoring: {r['email']}...")

        # Save results to instance/responses/
        email = results[0].get("email", "batch") if results else "batch"
        user = re.sub(r"[^\w\-]", "_", email.split("@")[0])
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%MZ")
        log_path = os.path.join("instance", "responses", f"llm_eval_responses_{user}_{timestamp}.jsonl")

        with open(log_path, "a") as f:
            for r in results:
                f.write(json.dumps(r) + "\n")

        print(f"✅ Evaluated {len(results)} transcript(s).")
        return jsonify({
            "success": True,
            "evaluated": len(results),
            "log_path": log_path,
            "evaluations": results
        })

    except Exception as e:
        print(f"❌ Evaluation error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/transcripts", methods=["GET"])
def get_transcripts():
    transcripts_path = os.path.join("instance", "transcripts", "transcripts.jsonl")
    if not os.path.exists(transcripts_path):
        return jsonify([])

    with open(transcripts_path, "r") as f:
        entries = [json.loads(line) for line in f if line.strip()]

    return jsonify(entries)


@app.route("/generate-eval-request", methods=["POST"])
def generate_eval_request():
    import json
    from datetime import datetime, timezone

    submissions_path = os.path.join("instance", "submissions", "submissions.jsonl")
    requests_path = os.path.join("instance", "requests", "llm_eval_requests.jsonl")

    RUBRIC_CSV = """Skill,Level,Score,Description
Prompt Engineering,Missing,0,No prompt or completely irrelevant
Prompt Engineering,Mastery,4,Clear, efficient, task-optimized
Reflection,Missing,0,No reflection
Reflection,Mastery,4,Insightful and thoughtful reflection"""

    EVAL_PROMPT = "Evaluate the clarity and intent of each transcript as if submitted by a student in a technical interview."

    transcripts = []
    try:
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
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "Submissions file not found"}), 404

    if not transcripts:
        return jsonify({"status": "empty", "message": "No valid transcript entries found."}), 200

    request_entry = {
        "rubric_csv": RUBRIC_CSV,
        "evaluation_prompt": EVAL_PROMPT,
        "transcripts": transcripts,
        "received_at": datetime.now(timezone.utc).isoformat()
    }

    with open(requests_path, "a") as outfile:
        outfile.write(json.dumps(request_entry) + "\n")

    return jsonify({
        "status": "success",
        "appended": len(transcripts),
        "saved_to": requests_path
    })
@app.route("/evaluate-transcripts", methods=["POST"])
def evaluate_multiple_transcripts():
    from backend.llm_assess_interviews import evaluate_single_transcript

    payload = request.get_json()
    print("📥 Full incoming JSON payload:")
    print(json.dumps(payload, indent=2))
    rubric_csv = payload.get("rubric_csv")
    transcripts = payload.get("transcripts")

    if not rubric_csv or not transcripts:
        print("🚨 Missing rubric or transcripts in payload.")
        return jsonify({"success": False, "error": "Missing rubric or transcripts"}), 400

    print(f"🔍 Called /evaluate-transcripts with {len(transcripts)} transcript(s).")
    print("🔎 Payload emails:")
    for i, t in enumerate(transcripts):
        print(f"  {i+1:02d}. {t.get('email', 'unknown')}")

    results = []
    for entry in transcripts:
        try:
            name = entry.get("name", "Unknown")
            email = entry.get("email", "unknown@none.edu")
            text = entry.get("transcript", "")
            result = evaluate_single_transcript(text, rubric_csv)
            results.append({ "name": name, "email": email, "score": result })
            print(f"🧠 Scoring: {email}...")
        except Exception as e:
            print(f"❌ Error scoring {email}: {e}")
            results.append({ "name": name, "email": email, "error": str(e) })

    print(f"✅ Evaluated {len(results)} transcript(s).")
    return jsonify({
        "success": True,
        "result": f"Evaluated {len(results)} transcript(s).",
        "evaluations": results
    })

if __name__ == "__main__":
    app.run(port=5050, debug=True)
