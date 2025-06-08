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
        return jsonify({"error": "No audio file provided"}), 400
    audio = request.files["audio"]
    filename = secure_filename(audio.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    audio.save(save_path)
    return jsonify({"success": True, "filename": filename})


@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        data = request.get_json()
        filename = data.get("filename")
        if not filename:
            return jsonify({"error": "No filename provided"}), 400

        path = os.path.join(UPLOAD_FOLDER, filename)
        with open(path, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)

        # Save to JSON
        transcript_data = {
            "filename": filename,
            "email": data.get("email"),
            "name": data.get("name"),
            "transcript": transcript["text"],
            "timestamp": data.get("timestamp")
        }

        json_path = os.path.join(TRANSCRIPT_FOLDER, filename.replace(".webm", ".json"))
        with open(json_path, "w") as f:
            json.dump(transcript_data, f, indent=2)

        return jsonify({"success": True, "transcript": transcript["text"]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
