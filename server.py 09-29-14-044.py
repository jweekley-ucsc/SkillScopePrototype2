
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
import uuid
from datetime import datetime

app = Flask(__name__, static_url_path='/static')

# Existing routes...

@app.route('/interview')
def interview():
    return render_template('interview.html')

# Keep the rest of your existing routes and logic here...

if __name__ == '__main__':
    app.run(port=5050, debug=True)
