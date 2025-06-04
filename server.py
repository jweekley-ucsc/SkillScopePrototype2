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


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    name = data.get("name")
    # No actual DB validation — assume frontend enforces uniqueness
    return jsonify({"success": True})


@app.route("/interview")
def interview():
    return send_from_directory("templates", "interview.html")


@app.route("/upload-audio", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio = request.files["audio"]
    filename = secure_filename(request.form.get("filename", "recording.webm"))
    audio.save(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify({"success": True})


@app.route("/transcribe")
def transcribe():
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400

    audio_path = os.path.join(UPLOAD_FOLDER, f"{session_id}.webm")
    if not os.path.exists(audio_path):
        return jsonify({"error": "Audio file not found"}), 404

    try:
        audio_file = open(audio_path, "rb")
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="json"
        )
        transcript_text = transcript.get("text", "")

        # Save to disk
        transcript_record = {
            "session_id": session_id,
            "transcript": transcript_text
        }
        output_path = os.path.join(TRANSCRIPT_FOLDER, f"{session_id}.json")
        with open(output_path, "w") as f:
            json.dump(transcript_record, f, indent=2)

        return jsonify(transcript_record)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/submit-transcript", methods=["POST"])
def submit_transcript():
    try:
        data = request.get_json()
        email = data.get("email", "unknown")
        transcript = data.get("transcript", "")
        reflection = data.get("reflection", "")
        if not transcript:
            return jsonify({"error": "Missing transcript"}), 400

        record = {
            "email": email,
            "transcript": transcript,
            "reflection": reflection
        }
        filename = f"{email.replace('@', '_').replace('.', '_')}_{uuid.uuid4().hex[:8]}.jsonl"
        path = os.path.join(TRANSCRIPT_FOLDER, filename)

        with open(path, "w") as f:
            f.write(json.dumps(record) + "\n")

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/evaluate")
def evaluate():
    return send_from_directory("templates", "evaluate.html")


@app.route("/submit-evaluation", methods=["POST"])
def submit_evaluation():
    try:
        data = request.get_json()
        email = data.get("email", "unknown")
        results = data.get("results", [])
        filename = f"llm_eval_responses_{email.replace('@', '_')}_{uuid.uuid4().hex[:6]}.jsonl"
        path = os.path.join(EVALUATION_FOLDER, filename)

        with open(path, "w") as f:
            for item in results:
                f.write(json.dumps(item) + "\n")

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/interviewer")
def interviewer():
    return send_from_directory("templates", "interviewer.html")


@app.route("/submit-rubric", methods=["POST"])
def submit_rubric():
    if "rubric" not in request.files:
        return jsonify({"error": "No rubric file provided"}), 400
    rubric = request.files["rubric"]
    filename = secure_filename(rubric.filename)
    rubric.save(os.path.join(RUBRIC_FOLDER, filename))
    return jsonify({"success": True})


@app.route("/list-transcripts", methods=["GET"])
def list_transcripts():
    try:
        files = os.listdir(TRANSCRIPT_FOLDER)
        json_files = [f for f in files if f.endswith(".json") or f.endswith(".jsonl")]
        return jsonify(json_files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/transcripts", methods=["GET"])
def get_transcripts():
    transcript_dir = os.path.join("instance", "transcripts")
    try:
        files = os.listdir(transcript_dir)
        return jsonify([f for f in files if f.endswith(".json") or f.endswith(".jsonl")])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/evaluate-transcripts", methods=["POST"])
def evaluate_transcripts():
    try:
        rubric_path = os.path.join(RUBRIC_FOLDER, "test_rubric.csv")
        if not os.path.exists(rubric_path):
            return jsonify({"error": "Rubric file not found."}), 400

        with open(rubric_path, "r") as rf:
            rubric = rf.read()

        selected_files = request.json.get("selectedFiles", [])
        summaries = []

        for filename in selected_files:
            path = os.path.join(TRANSCRIPT_FOLDER, filename)
            with open(path, "r") as tf:
                data = json.load(tf)
                transcript = data.get("transcript", "")
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an AI evaluator scoring transcripts."},
                        {"role": "user", "content": f"Rubric:\n{rubric}\n\nTranscript:\n{transcript}"}
                    ]
                )
                summaries.append({
                    "file": filename,
                    "feedback": response.choices[0].message.content
                })

        return jsonify(summaries)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5050, debug=True)
