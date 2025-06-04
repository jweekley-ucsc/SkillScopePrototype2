import os
import json
import uuid
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

UPLOAD_FOLDER = os.path.join("instance", "uploads")
TRANSCRIPT_FOLDER = os.path.join("instance", "transcripts")
RESPONSE_FOLDER = os.path.join("instance", "responses")
DATA_FOLDER = os.path.join("instance", "data")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSCRIPT_FOLDER, exist_ok=True)
os.makedirs(RESPONSE_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

app = Flask(__name__, static_url_path='/static')

CORS(app)

@app.route("/")
@app.route("/login")
def login():
    return send_from_directory("templates", "login.html")

@app.route("/interview")
def interview():
    return send_from_directory("templates", "interview.html")

@app.route("/interviewer")
def interviewer():
    return send_from_directory("templates", "interviewer.html")

@app.route("/evaluate")
def evaluate():
    return send_from_directory("templates", "evaluate.html")

@app.route("/admin")
def admin():
    return send_from_directory("templates", "admin.html")

@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory("static", path)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    if not name or not email:
        return jsonify({"success": False, "error": "Missing name or email"}), 400

    filepath = os.path.join(DATA_FOLDER, "registrations.jsonl")
    existing = set()

    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            for line in f:
                record = json.loads(line.strip())
                existing.add((record["name"], record["email"]))

    if (name, email) in existing:
        return jsonify({"success": False, "error": "Duplicate registration"}), 400

    with open(filepath, "a") as f:
        f.write(json.dumps({"name": name, "email": email}) + "\n")

    return jsonify({"success": True})

@app.route("/upload-audio", methods=["POST"])
def upload_audio():
    audio_file = request.files.get("audio")
    filename = request.form.get("filename")
    if not audio_file or not filename:
        return jsonify({"success": False, "error": "Missing audio or filename"}), 400

    save_path = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
    audio_file.save(save_path)
    return jsonify({"success": True, "filename": filename})

@app.route("/transcribe")
def transcribe():
    session_id = request.args.get("session_id")
    audio_path = os.path.join(UPLOAD_FOLDER, f"{session_id}.webm")

    print(f"[DEBUG] Transcription request for: {session_id}")
    print(f"[DEBUG] Looking for file at: {audio_path}")

    if not os.path.exists(audio_path):
        print("[ERROR] File not found.")
        return jsonify({"error": "Audio file not found"}), 404

    try:
        print("[DEBUG] Uploading audio to OpenAI Whisper API (v1.0.0+)...")
        with open(audio_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="json",
                language="en"
            )
        print("[DEBUG] Transcription received from Whisper API.")
        return jsonify({"text": transcript.text})
    except Exception as e:
        print(f"[ERROR] Whisper API failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/submit-transcript", methods=["POST"])
def submit_transcript():
    data = request.json
    email = data.get("email")
    transcript = data.get("transcript")
    reflection = data.get("reflection")

    if not email or not transcript:
        return jsonify({"success": False, "error": "Missing email or transcript"}), 400

    filename = f"{email.replace('@', '_at_')}_{uuid.uuid4().hex}.json"
    save_path = os.path.join(TRANSCRIPT_FOLDER, filename)

    with open(save_path, "w") as f:
        json.dump({"email": email, "transcript": transcript, "reflection": reflection}, f, indent=2)

    return jsonify({"success": True})

@app.route("/submit-evaluation", methods=["POST"])
def submit_evaluation():
    try:
        data = request.get_json()
        rubric = data.get("rubric")
        transcript_files = data.get("transcripts", [])
        response_records = []

        rubric_csv_path = os.path.join("instance", "rubrics", f"rubric_{uuid.uuid4()}.csv")
        os.makedirs(os.path.dirname(rubric_csv_path), exist_ok=True)
        with open(rubric_csv_path, "w") as f:
            f.write(rubric)

        from backend.llm_assess_interviews import run_batch_evaluation  # make sure path/module matches

        transcript_paths = [
            os.path.join("instance", "transcripts", fname) for fname in transcript_files
        ]

        eval_output = run_batch_evaluation(rubric_csv_path, transcript_paths)

        return jsonify({"success": True, "evaluated": len(eval_output)})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/list-evaluation-files")
def list_evaluation_files():
    files = [f for f in os.listdir(RESPONSE_FOLDER) if f.endswith(".jsonl")]
    return jsonify({"files": files})

@app.route("/list-transcripts")
def list_transcripts():
    transcript_dir = os.path.join("instance", "transcripts")
    if not os.path.exists(transcript_dir):
        return jsonify({"error": "Transcript directory not found."}), 404
    files = [f for f in os.listdir(transcript_dir) if f.endswith(".json")]
    return jsonify(files)


@app.route("/get-evaluation-file")
def get_evaluation_file():
    filename = request.args.get("filename")
    filepath = os.path.join(RESPONSE_FOLDER, filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    with open(filepath, "r") as f:
        lines = f.readlines()
    return jsonify([json.loads(line) for line in lines if line.strip()])

if __name__ == "__main__":
    app.run(debug=True, port=5050)
