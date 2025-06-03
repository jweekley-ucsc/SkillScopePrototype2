from flask import Flask, render_template, request, jsonify, session, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')
CORS(app)
app.secret_key = "your-secret-key"  # Replace with a secure value in production

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    if not name or not email:
        return jsonify({"status": "error", "message": "Missing name or email"}), 400
    session["user"] = {"name": name, "email": email}
    return jsonify({"status": "success"})

@app.route("/interview")
def interview():
    return render_template("interview.html")

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == "__main__":
    app.run(port=5050, debug=True)
