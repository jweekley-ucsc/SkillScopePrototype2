import os
import json
import csv
import uuid
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# App and folders
app = Flask(__name__, static_url_path='/static')
CORS(app)

UPLOAD_FOLDER = "instance/uploads"
TRANSCRIPT_FOLDER = "instance/transcripts"
RUBRIC_FOLDER = "instance/rubrics"
EVALUATION_FOLDER = "instance/evaluations"

# Ensure folders exist
for folder in [UPLOAD_FOLDER, TRANSCRIPT_FOLDER, RUBRIC_FOLDER, EVALUATION_FOLDER]:
    os.makedirs(folder, exist_ok=True)


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
    data = request.get_json()
    email = data.get("email")
    transcript = data.get("transcript")
    reflection = data.get("reflection")

    if not email or not transcript:
        return jsonify({"success": False, "error": "Missing email or transcript"}), 400

    try:
        save_dir = os.path.join("submitted_transcripts")
        os.makedirs(save_dir, exist_ok=True)

        base_filename = email.replace("@", "_at_").replace(".", "_")
        with open(os.path.join(save_dir, f"{base_filename}_transcript.txt"), "w") as tf:
            tf.write(transcript)

        with open(os.path.join(save_dir, f"{base_filename}_reflection.txt"), "w") as rf:
            rf.write(reflection or "")

        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error saving submission: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/transcripts", methods=["GET"])
def list_transcripts():
    transcripts_path = os.path.join("instance", "transcripts", "transcripts.jsonl")
    results = []
    try:
        with open(transcripts_path, "r") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    results.append(data)
        return jsonify(results)
    except Exception as e:
        print(f"[ERROR] Failed to load transcripts: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5050, debug=True)
