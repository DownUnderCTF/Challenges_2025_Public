from flask import Flask, redirect, render_template, request, session
import os
import hashlib
import secrets
import glob
import requests
import time

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

@app.after_request
def after_req(resp):
    resp.headers["Cross-Origin-Opener-Policy"] = "noopener-allow-popups"
    return resp

def h(x):
    return hashlib.sha256(x.encode()).hexdigest()

def get_uploads():
    if os.path.exists(f"./uploads"):
        return glob.glob(f"{h(session['user'])}-*", root_dir="./uploads")
    return []

@app.route('/')
def index():
    if not 'user' in session:
        session['user'] = secrets.token_hex(8)
    uploads = get_uploads()
    return render_template("dashboard.html", uploads=uploads, other_domain=os.getenv("PORT_5000_URL"))

@app.route('/open_file')
def open_file():
    file_id = int(request.args.get('id')) - 1
    return redirect(f"{os.getenv("PORT_5000_URL")}/{get_uploads()[file_id]}")

@app.route('/upload', methods=["POST"])
def upload():
    if not 'user' in session:
        return "Must be logged in"

    if not "file" in request.files or request.files["file"] is None:
        return "Must supply file"

    f = request.files["file"]

    os.makedirs(f"./uploads", exist_ok=True)
    f.save(f"./uploads/{h(session['user'])}-{time.time()}-{secrets.token_hex(16)}")

    return redirect("/")

@app.route('/report', methods=["POST"])
def report():
    requests.post(f"{os.getenv("INTERNAL_XSS_BOT_URL")}/visit", json={
        "url": str(request.form.get("url"))
    }, headers={
        "X-SSRF-Protection": "1"
    })

    return "Reported"

@app.route('/bot-login')
def bot_login():
    if request.args.get("token") != os.getenv("BOT_TOKEN"):
        return "Invalid token! This url is so the bot can login, it's not part of the challenge"

    session['user'] = 'admin'

    return 'success'


if __name__ == '__main__':
    app.run('0.0.0.0', 9000, debug=False)
