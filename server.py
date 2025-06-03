
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from flask_cors import CORS
import os, json, time, uuid
from datetime import datetime
import openai

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')
CORS(app)

UPLOAD_FOLDER = os.path.join("instance", "uploads")
TRANSCRIPTS_FOLDER = os.path.join("instance", "transcripts")
RESPONSES_FOLDER = os.path.join("instance", "responses")
SUBMISSIONS_FILE = os.path.join("instance", "data", "submissions.jsonl")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSCRIPTS_FOLDER, exist_ok=True)
os.makedirs(RESPONSES_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(SUBMISSIONS_FILE), exist_ok=True)

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/interview")
def interview():
    return render_template("interview.html")

@app.route("/interviewer")
def interviewer():
    return render_template("interviewer.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/evaluate")
def evaluate():
    return render_template("evaluate.html")

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    if not name or not email:
        return jsonify({"success": False, "error": "Missing fields"}), 400
    return jsonify({"success": True})

@app.route("/upload-audio", methods=["POST"])
def upload_audio():
    audio = request.files.get("audio")
    filename = request.form.get("filename")
    if not audio or not filename:
        return jsonify({"success": False, "error": "Missing audio file or filename"}), 400
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    audio.save(filepath)
    return jsonify({"success": True, "path": filepath})

@app.route("/transcribe")
def transcribe():
    session_id = request.args.get("session_id")
    audio_path = os.path.join("instance", "uploads", f"{session_id}.webm")
    print(f"[DEBUG] Looking for file at: {audio_path}")

    if not os.path.exists(audio_path):
        return jsonify({"error": "Audio file not found"}), 404

    try:
        with open(audio_path, "rb") as audio_file:
            print("[DEBUG] Uploading audio to OpenAI Whisper API...")
            transcript = openai.Audio.transcribe(
                file=audio_file,
                model="whisper-1",  # OpenAI hosted Whisper model
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
            print("[DEBUG] Transcription successful.")
            return jsonify({
                "text": transcript.get("text", ""),
                "segments": transcript.get("segments", [])
            })
    except Exception as e:
        print("[ERROR] Whisper API failed:", str(e))
        return jsonify({"error": str(e)}), 500
    
@app.route("/submit-transcript", methods=["POST"])
def submit_transcript():
    try:
        data = request.get_json()
        email = data.get("email")
        transcript = data.get("transcript")
        reflection = data.get("reflection", "")

        if not email or not transcript:
            return jsonify({"success": False, "error": "Missing fields"}), 400

        entry = {
            "email": email,
            "transcript": transcript,
            "reflection": reflection,
            "submitted_at": datetime.utcnow().isoformat()
        }
        session_file = f"submission_{uuid.uuid4().hex}.json"
        filepath = os.path.join(TRANSCRIPTS_FOLDER, session_file)
        with open(filepath, "w") as f:
            json.dump(entry, f)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5050)
