from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for
from flask_cors import CORS
from datetime import datetime, timezone
import json
import os
import traceback
import logging

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')
CORS(app)

# Set up logging
log_dir = "instance/logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "skillscope.log")
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/interview")
def interview():
    return render_template("interview.html")

@app.route("/interviewer")
def interviewer():
    return render_template("interviewer.html")

@app.route("/evaluate")
def evaluate():
    return render_template("evaluate.html")

@app.route("/submit-transcript", methods=["POST"])
def submit_transcript():
    data = request.get_json()
    transcript = data.get("transcript")
    email = data.get("email")
    name = data.get("name")

    if not transcript or not email:
        return jsonify({"error": "Missing transcript or email"}), 400

    entry = {
        "name": name,
        "email": email,
        "transcript": transcript,
        "submitted_at": datetime.now(timezone.utc).isoformat()
    }

    with open("instance/data/submissions.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")

    return jsonify({"status": "ok"})

@app.route("/submissions")
def get_submissions():
    try:
        with open("instance/submissions/submissions.jsonl", "r") as f:
            return jsonify([json.loads(line) for line in f if line.strip()])
    except FileNotFoundError:
        return jsonify([])
    
@app.route("/submit-evaluation", methods=["POST"])
def submit_evaluation():
    data = request.get_json()
    if not isinstance(data, list) or len(data) == 0:
        return jsonify({"error": "Invalid submission payload"}), 400

    rubric_path = data[0].get("rubric_path")
    prompt_path = data[0].get("prompt_path")

    try:
        with open(rubric_path, "r") as f:
            rubric_text = f.read()
        with open(prompt_path, "r") as f:
            prompt_text = f.read()
    except Exception as e:
        return jsonify({"error": f"Failed to read rubric or prompt file: {str(e)}"}), 500

    request_block = {
        "rubric_csv": rubric_text,
        "evaluation_prompt": prompt_text,
        "transcripts": [
            {"email": entry["email"], "transcript": entry["transcript"]}
            for entry in data
        ],
        "received_at": datetime.now(timezone.utc).isoformat()
    }

    # Evaluate with real LLM (replace this call with your actual logic)
    try:
        eval_response = evaluate_with_llm(request_block)
        return jsonify(eval_response)
    except Exception as e:
        return jsonify({"error": f"LLM evaluation failed: {str(e)}"}), 500
@app.route("/evaluation-requests", methods=["GET"])
def get_evaluation_requests():
    try:
        with open("instance/requests/llm_eval_requests.jsonl", "r") as f:
            entries = []
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError as e:
                    app.logger.warning(f"Skipping malformed JSON: {e}")
            return jsonify(entries)
    except FileNotFoundError:
        return jsonify([])
    except Exception as e:
        app.logger.error(f"Unexpected error loading requests: {e}")
        return jsonify({"error": "Failed to load evaluation requests"}), 500

@app.route("/download/<path:filename>")
def download_file(filename):
    directory = os.path.join(app.root_path, "instance", "responses")
    return send_from_directory(directory, filename, as_attachment=True)

@app.route("/list-evaluation-files")
def list_evaluation_files():
    eval_dir = os.path.join("instance", "responses")
    if not os.path.exists(eval_dir):
        return jsonify([])

    files = [f for f in os.listdir(eval_dir) if f.endswith(".jsonl")]
    return jsonify(files)
@app.route("/get-evaluation-file")
def get_evaluation_file():
    filename = request.args.get("filename")
    if not filename:
        return "Filename required", 400

    filepath = os.path.join("instance", "responses", filename)
    if not os.path.exists(filepath):
        return "File not found", 404

    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    app.run(port=5050, debug=True)